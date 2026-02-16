"""
Agent service for CMDOP SDK.

Provides AI agent execution capabilities via RunAgent RPC.
Supports structured output via Pydantic models.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, Type, TypeVar, overload

from cmdop.models.agent import (
    AgentEventType,
    AgentResult,
    AgentRunOptions,
    AgentStreamEvent,
    AgentToolResult,
    AgentType,
    AgentUsage,
)
from cmdop.services.base import BaseService

if TYPE_CHECKING:
    from pydantic import BaseModel
    from cmdop.transport.base import BaseTransport

T = TypeVar("T", bound="BaseModel")


def _map_agent_type(agent_type: AgentType) -> int:
    """Map SDK AgentType to proto enum value."""
    return {
        AgentType.CHAT: 0,
        AgentType.TERMINAL: 1,
        AgentType.COMMAND: 2,
        AgentType.ROUTER: 3,
        AgentType.PLANNER: 4,
    }.get(agent_type, 0)


def _parse_tool_result(tr: Any) -> AgentToolResult:
    """Parse proto AgentToolResult to SDK model."""
    return AgentToolResult(
        tool_name=tr.tool_name,
        tool_call_id=tr.tool_call_id,
        success=tr.success,
        result=tr.result,
        error=tr.error or "",
        duration_ms=tr.duration_ms,
    )


def _model_to_json_schema(model_class: Type[T]) -> str:
    """Convert Pydantic model to JSON Schema string."""
    try:
        schema = model_class.model_json_schema()
        return json.dumps(schema)
    except AttributeError:
        # Pydantic v1 fallback
        schema = model_class.schema()
        return json.dumps(schema)


def _parse_agent_result(
    response: Any,
    output_model: Type[T] | None = None,
) -> AgentResult[T]:
    """Parse proto RunAgentResponse to SDK model."""
    tool_results = [_parse_tool_result(tr) for tr in response.tool_results]

    usage = AgentUsage(
        prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
        completion_tokens=response.usage.completion_tokens if response.usage else 0,
        total_tokens=response.usage.total_tokens if response.usage else 0,
    )

    # Parse structured output if model provided and output_json exists
    data: T | None = None
    output_json = getattr(response, "output_json", "") or ""

    if output_model and output_json:
        try:
            data_dict = json.loads(output_json)
            data = output_model.model_validate(data_dict)
        except (json.JSONDecodeError, Exception) as e:
            # If parsing fails, keep data as None and include error
            if response.success:
                return AgentResult(
                    request_id=response.request_id,
                    success=False,
                    text=response.text,
                    error=f"Failed to parse structured output: {e}",
                    tool_results=tool_results,
                    usage=usage,
                    duration_ms=response.duration_ms,
                    output_json=output_json,
                )

    return AgentResult(
        request_id=response.request_id,
        success=response.success,
        text=response.text,
        error=response.error or "",
        tool_results=tool_results,
        usage=usage,
        duration_ms=response.duration_ms,
        data=data,
        output_json=output_json,
    )


class AgentService(BaseService):
    """
    Synchronous agent service.

    Provides AI agent execution.

    Example:
        >>> # Local IPC - session_id is optional
        >>> result = client.agent.run("What is 2 + 2?")
        >>> print(result.text)
        >>>
        >>> # Remote - set session_id from terminal.create()
        >>> client.agent.set_session_id(session_id)
        >>> result = client.agent.run("What files are in /tmp?")
    """

    def __init__(self, transport: BaseTransport) -> None:
        super().__init__(transport)
        self._stub: Any = None
        self._session_id: str | None = None

    @property
    def _get_stub(self) -> Any:
        """Lazy-load gRPC stub."""
        if self._stub is None:
            from cmdop._generated.service_pb2_grpc import (
                TerminalStreamingServiceStub,
            )

            self._stub = TerminalStreamingServiceStub(self._channel)
        return self._stub

    def set_session_id(self, session_id: str) -> None:
        """
        Set session ID for agent operations.

        Args:
            session_id: Session ID from terminal.create()
        """
        self._session_id = session_id

    def run(
        self,
        prompt: str,
        agent_type: AgentType = AgentType.CHAT,
        options: AgentRunOptions | None = None,
        session_id: str | None = None,
        output_model: Type[T] | None = None,
    ) -> AgentResult[T]:
        """
        Run an AI agent with the given prompt.

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
            >>> result = client.agent.run("What is 2+2?", output_model=Answer)
            >>> print(result.data.value)  # 4
        """
        from cmdop._generated.rpc_messages.agent_pb2 import RunAgentRequest

        # Use provided session_id, or stored one, or default placeholder
        # (local IPC server ignores session_id for agent operations)
        sid = session_id or self._session_id or "local"

        options = options or AgentRunOptions()

        # Convert Pydantic model to JSON Schema if provided
        output_schema = ""
        if output_model:
            output_schema = _model_to_json_schema(output_model)

        request = RunAgentRequest(
            session_id=sid,
            request_id=str(uuid.uuid4()),
            prompt=prompt,
            agent_type=_map_agent_type(agent_type),
            timeout_seconds=options.timeout_seconds or 300,
            output_schema=output_schema,
        )

        # Add options to map
        opts = options.to_options_map()
        for key, value in opts.items():
            request.options[key] = value

        response = self._call_sync(self._get_stub.RunAgent, request)
        return _parse_agent_result(response, output_model)


class AsyncAgentService(BaseService):
    """
    Asynchronous agent service.

    Provides async AI agent execution.

    Example:
        >>> # Local IPC - session_id is optional
        >>> result = await client.agent.run("What is 2 + 2?")
        >>> print(result.text)
        >>>
        >>> # Remote - set session_id from terminal.create()
        >>> client.agent.set_session_id(session_id)
        >>> result = await client.agent.run("Deploy the app")
    """

    def __init__(self, transport: BaseTransport) -> None:
        super().__init__(transport)
        self._stub: Any = None
        self._session_id: str | None = None

    @property
    def _get_stub(self) -> Any:
        """Lazy-load async gRPC stub."""
        if self._stub is None:
            from cmdop._generated.service_pb2_grpc import (
                TerminalStreamingServiceStub,
            )

            self._stub = TerminalStreamingServiceStub(self._async_channel)
        return self._stub

    def set_session_id(self, session_id: str) -> None:
        """
        Set session ID for agent operations.

        Args:
            session_id: Session ID from terminal.create()
        """
        self._session_id = session_id

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
        from cmdop._generated.rpc_messages.agent_pb2 import RunAgentRequest

        # Use provided session_id, or stored one, or default placeholder
        # (local IPC server ignores session_id for agent operations)
        sid = session_id or self._session_id or "local"

        options = options or AgentRunOptions()

        # Convert Pydantic model to JSON Schema if provided
        output_schema = ""
        if output_model:
            output_schema = _model_to_json_schema(output_model)

        request = RunAgentRequest(
            session_id=sid,
            request_id=str(uuid.uuid4()),
            prompt=prompt,
            agent_type=_map_agent_type(agent_type),
            timeout_seconds=options.timeout_seconds or 300,
            output_schema=output_schema,
        )

        # Add options to map
        opts = options.to_options_map()
        for key, value in opts.items():
            request.options[key] = value

        response = await self._call_async(self._get_stub.RunAgent, request)
        return _parse_agent_result(response, output_model)

    async def run_stream(
        self,
        prompt: str,
        agent_type: AgentType = AgentType.CHAT,
        options: AgentRunOptions | None = None,
    ) -> AsyncIterator[AgentStreamEvent | AgentResult]:
        """
        Run an AI agent with streaming events.

        NOT YET IMPLEMENTED - streaming requires server-side changes.

        Args:
            prompt: The prompt/question for the agent
            agent_type: Type of agent to run
            options: Execution options

        Raises:
            NotImplementedError: Streaming not yet implemented
        """
        raise NotImplementedError(
            "Agent streaming not yet implemented. Use run() for non-streaming execution."
        )
        # Make this an async generator (required for return type)
        yield  # type: ignore  # pragma: no cover
