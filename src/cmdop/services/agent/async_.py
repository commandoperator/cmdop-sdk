"""Asynchronous agent service."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, Type, TypeVar

from cmdop.models.agent import (
    AgentEventType,
    AgentResult,
    AgentRunOptions,
    AgentStreamEvent,
    AgentType,
)
from cmdop.models.terminal import SessionListItem
from cmdop.services.base import BaseService
from cmdop.services.agent.base import (
    map_agent_type,
    model_to_json_schema,
    parse_agent_result,
    parse_session_response,
)

if TYPE_CHECKING:
    from pydantic import BaseModel
    from cmdop.transport.base import BaseTransport

T = TypeVar("T", bound="BaseModel")


class AsyncAgentService(BaseService):
    """
    Asynchronous agent service.

    Provides async AI agent execution.

    Example:
        >>> # Using set_machine (recommended)
        >>> await client.agent.set_machine("my-server")
        >>> result = await client.agent.run("What files are in /tmp?")
        >>>
        >>> # Local IPC - session_id is optional
        >>> result = await client.agent.run("What is 2 + 2?")
        >>> print(result.text)
    """

    def __init__(self, transport: BaseTransport) -> None:
        super().__init__(transport)
        self._stub: Any = None
        self._session_id: str | None = None
        self._cached_hostname: str | None = None
        self._cached_session_info: SessionListItem | None = None

    @property
    def _get_stub(self) -> Any:
        """Lazy-load async gRPC stub."""
        if self._stub is None:
            from cmdop.grpc.generated.service_pb2_grpc import (
                TerminalStreamingServiceStub,
            )

            self._stub = TerminalStreamingServiceStub(self._async_channel)
        return self._stub

    async def set_machine(self, hostname: str, partial_match: bool = True) -> SessionListItem:
        """
        Set target machine by hostname for agent operations.

        Uses GetSessionByHostname RPC for efficient server-side resolution.
        Caches session_id for all subsequent agent operations.

        Args:
            hostname: Machine hostname.
            partial_match: If True, allows partial hostname matching (default).

        Returns:
            SessionListItem for the found session.

        Raises:
            CMDOPError: If no active session found, or hostname is ambiguous.

        Example:
            >>> await client.agent.set_machine("my-server")
            >>> result = await client.agent.run("List files in /tmp")
        """
        from cmdop.grpc.generated.rpc_messages.session_pb2 import (
            GetSessionByHostnameRequest,
        )
        from cmdop.exceptions import CMDOPError

        request = GetSessionByHostnameRequest(
            hostname=hostname,
            partial_match=partial_match,
        )
        response = await self._call_async(self._get_stub.GetSessionByHostname, request)

        if not response.found:
            if response.ambiguous:
                raise CMDOPError(
                    f"Ambiguous hostname '{hostname}' matches {response.matches_count} machines. "
                    "Use a more specific hostname or set partial_match=False."
                )
            raise CMDOPError(response.error or f"No active session found for hostname: {hostname}")

        session = parse_session_response(response)

        # Cache session info
        self._cached_hostname = response.machine_hostname
        self._session_id = response.session_id
        self._cached_session_info = session
        return session

    def set_session_id(self, session_id: str) -> None:
        """
        Set session ID for agent operations.

        Prefer set_machine() for hostname-based targeting.

        Args:
            session_id: Session ID from terminal.create()
        """
        self._session_id = session_id

    def clear_session(self) -> None:
        """Clear cached session and hostname."""
        self._session_id = None
        self._cached_hostname = None
        self._cached_session_info = None

    @property
    def current_session(self) -> SessionListItem | None:
        """Get currently cached session info."""
        return self._cached_session_info

    @property
    def current_hostname(self) -> str | None:
        """Get currently cached hostname."""
        return self._cached_hostname

    async def run(
        self,
        prompt: str,
        agent_type: AgentType = AgentType.CHAT,
        options: AgentRunOptions | None = None,
        session_id: str | None = None,
        output_model: Type[T] | None = None,
    ) -> AgentResult[T]:
        """
        Run an AI agent and wait for completion.

        Args:
            prompt: The prompt/question for the agent
            agent_type: Type of agent to run
            options: Execution options
            session_id: Session ID (optional for local IPC, required for remote)
            output_model: Optional Pydantic model for structured output.
                         If provided, the agent will return data matching this schema.

        Returns:
            Agent execution result. If output_model is provided,
            result.data will contain the parsed Pydantic model.

        Example:
            >>> class Answer(BaseModel):
            ...     value: int
            ...     explanation: str
            >>>
            >>> result = await client.agent.run(
            ...     "What is 2+2?",
            ...     output_model=Answer,
            ... )
            >>> print(result.data.value)  # 4
        """
        from cmdop.grpc.generated.rpc_messages.agent_pb2 import RunAgentRequest

        # Use provided session_id, or stored one, or default placeholder
        sid = session_id or self._session_id or "local"

        options = options or AgentRunOptions()

        # Convert Pydantic model to JSON Schema if provided
        output_schema = ""
        if output_model:
            output_schema = model_to_json_schema(output_model)

        request = RunAgentRequest(
            session_id=sid,
            request_id="",  # Empty = use session_id as conversation_id for history
            prompt=prompt,
            agent_type=map_agent_type(agent_type),
            timeout_seconds=options.timeout_seconds or 300,
            output_schema=output_schema,
        )

        # Add options to map
        opts = options.to_options_map()
        for key, value in opts.items():
            request.options[key] = value

        response = await self._call_async(self._get_stub.RunAgent, request)
        return parse_agent_result(response, output_model)

    async def run_stream(
        self,
        prompt: str,
        agent_type: AgentType = AgentType.CHAT,
        options: AgentRunOptions | None = None,
        session_id: str | None = None,
    ) -> AsyncIterator[AgentStreamEvent | AgentResult]:
        """
        Run an AI agent with streaming events.

        Yields events as the agent executes (tokens, tool calls, etc.),
        then yields the final result.

        Args:
            prompt: The prompt/question for the agent
            agent_type: Type of agent to run
            options: Execution options
            session_id: Session ID (optional for local IPC, required for remote)

        Yields:
            AgentStreamEvent for intermediate events (tokens, tool_start, tool_end, etc.)
            AgentResult as the final item when execution completes

        Example:
            >>> async for event in client.agent.run_stream("What is 2+2?"):
            ...     if isinstance(event, AgentStreamEvent):
            ...         if event.type == "token":
            ...             print(event.payload, end="", flush=True)
            ...         elif event.type == "tool_start":
            ...             print(f"\\nUsing tool: {event.payload['tool_name']}")
            ...     else:
            ...         # Final AgentResult
            ...         print(f"\\nFinal: {event.text}")
        """
        from cmdop.grpc.generated.rpc_messages.agent_pb2 import RunAgentRequest

        # Use provided session_id, or stored one, or default placeholder
        sid = session_id or self._session_id or "local"

        options = options or AgentRunOptions()

        request = RunAgentRequest(
            session_id=sid,
            request_id="",  # Empty = use session_id as conversation_id for history
            prompt=prompt,
            agent_type=map_agent_type(agent_type),
            timeout_seconds=options.timeout_seconds or 300,
        )

        # Add options to map
        opts = options.to_options_map()
        for key, value in opts.items():
            request.options[key] = value

        # Call streaming RPC with metadata for auth
        try:
            stream = self._get_stub.RunAgentStream(
                request,
                metadata=self._metadata,
                timeout=options.timeout_seconds or 300,
            )

            async for response in stream:
                if response.is_final:
                    # Final result - parse and yield AgentResult
                    yield parse_agent_result(response.result, None)
                else:
                    # Streaming event - parse and yield AgentStreamEvent
                    yield _parse_stream_event(response.event)
        except Exception as e:
            raise self._handle_error(e) from None


def _parse_stream_event(event) -> AgentStreamEvent:
    """Parse protobuf AgentStreamEvent to model."""
    import json

    # Map protobuf enum to AgentEventType
    event_type_map = {
        0: AgentEventType.TOKEN,
        1: AgentEventType.TOOL_START,
        2: AgentEventType.TOOL_END,
        3: AgentEventType.THINKING,
        4: AgentEventType.ERROR,
        5: AgentEventType.HANDOFF,
        6: AgentEventType.CANCELLED,
        # Browser events
        10: AgentEventType.BROWSER_NAVIGATE,
        11: AgentEventType.BROWSER_CLICK,
        12: AgentEventType.BROWSER_TYPE,
        13: AgentEventType.BROWSER_STATE,
        14: AgentEventType.BROWSER_SCREENSHOT,
        15: AgentEventType.BROWSER_ERROR,
        16: AgentEventType.BROWSER_DETECTION,
        17: AgentEventType.BROWSER_ESCALATION,
        18: AgentEventType.BROWSER_SESSION,
    }
    event_type = event_type_map.get(event.type, AgentEventType.TOKEN)

    # Parse payload JSON
    payload: Any = None
    if event.payload:
        try:
            payload = json.loads(event.payload)
        except json.JSONDecodeError:
            payload = event.payload

    return AgentStreamEvent(
        request_id=event.request_id,
        type=event_type,
        payload=payload,
        timestamp=event.timestamp,
    )
