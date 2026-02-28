"""Asynchronous skills service."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Type, TypeVar

from cmdop.models.skills import (
    SkillDetail,
    SkillInfo,
    SkillRunOptions,
    SkillRunResult,
)
from cmdop.models.terminal import SessionListItem
from cmdop.services.base import BaseService
from cmdop.services.skills.base import (
    parse_skill_detail,
    parse_skill_info,
    parse_skill_run_result,
)

if TYPE_CHECKING:
    from pydantic import BaseModel
    from cmdop.transport.base import BaseTransport

T = TypeVar("T", bound="BaseModel")


class AsyncSkillsService(BaseService):
    """
    Asynchronous skills service.

    Provides async skill listing, inspection, and execution.

    Example:
        >>> await client.skills.set_machine("my-server")
        >>> skills = await client.skills.list()
        >>> result = await client.skills.run("code-review", "Review this PR")
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
        Set target machine by hostname for skill operations.

        Args:
            hostname: Machine hostname.
            partial_match: If True, allows partial hostname matching (default).

        Returns:
            SessionListItem for the found session.

        Raises:
            CMDOPError: If no active session found, or hostname is ambiguous.

        Example:
            >>> await client.skills.set_machine("my-server")
            >>> skills = await client.skills.list()
        """
        from cmdop.grpc.generated.rpc_messages.session_pb2 import (
            GetSessionByHostnameRequest,
        )
        from cmdop.exceptions import CMDOPError
        from cmdop.services.agent.base import parse_session_response

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
        Set session ID for skill operations.

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

    async def list(self, session_id: str | None = None) -> list[SkillInfo]:
        """
        List available skills on the machine.

        Args:
            session_id: Session ID (optional for local IPC, required for remote)

        Returns:
            List of SkillInfo objects.

        Raises:
            CMDOPError: If no active session or other error.

        Example:
            >>> skills = await client.skills.list()
            >>> for skill in skills:
            ...     print(f"{skill.name}: {skill.description}")
        """
        from cmdop.exceptions import CMDOPError
        from cmdop.grpc.generated.rpc_messages.skills_pb2 import SkillListRequest

        sid = session_id or self._session_id or "local"
        request = SkillListRequest(session_id=sid)
        response = await self._call_async(self._get_stub.SkillList, request)

        if response.error:
            raise CMDOPError(response.error)

        return [parse_skill_info(s) for s in response.skills]

    async def show(self, skill_name: str, session_id: str | None = None) -> SkillDetail:
        """
        Show detailed information about a skill.

        Args:
            skill_name: Name of the skill to inspect.
            session_id: Session ID (optional for local IPC, required for remote)

        Returns:
            SkillDetail with metadata, content, and source path.

        Example:
            >>> detail = await client.skills.show("code-review")
            >>> if detail.found:
            ...     print(detail.content)
        """
        from cmdop.grpc.generated.rpc_messages.skills_pb2 import SkillShowRequest

        sid = session_id or self._session_id or "local"
        request = SkillShowRequest(session_id=sid, skill_name=skill_name)
        response = await self._call_async(self._get_stub.SkillShow, request)
        return parse_skill_detail(response)

    async def run(
        self,
        skill_name: str,
        prompt: str,
        options: SkillRunOptions | None = None,
        session_id: str | None = None,
        output_model: Type[T] | None = None,
    ) -> SkillRunResult[T]:
        """
        Run a skill and wait for completion.

        Args:
            skill_name: Name of the skill to run.
            prompt: The prompt/input for the skill.
            options: Execution options (model, timeout).
            session_id: Session ID (optional for local IPC, required for remote)
            output_model: Optional Pydantic model for structured output.

        Returns:
            SkillRunResult with text response and optional structured data.

        Example:
            >>> result = await client.skills.run("code-review", "Review this PR")
            >>> print(result.text)
            >>>
            >>> # With structured output
            >>> class Review(BaseModel):
            ...     score: int
            ...     summary: str
            >>> result = await client.skills.run(
            ...     "code-review", "Review this PR",
            ...     output_model=Review,
            ... )
            >>> print(result.data.score)
        """
        from cmdop.grpc.generated.rpc_messages.skills_pb2 import SkillRunRequest
        from cmdop.services.agent.base import model_to_json_schema

        sid = session_id or self._session_id or "local"
        options = options or SkillRunOptions()

        # Convert Pydantic model to JSON Schema if provided
        output_schema = ""
        if output_model:
            output_schema = model_to_json_schema(output_model)

        request = SkillRunRequest(
            session_id=sid,
            request_id="",
            skill_name=skill_name,
            prompt=prompt,
            timeout_seconds=options.timeout_seconds or 300,
            output_schema=output_schema,
        )

        # Add options to map
        opts = options.to_options_map()
        for key, value in opts.items():
            request.options[key] = value

        response = await self._call_async(self._get_stub.SkillRun, request)
        return parse_skill_run_result(response, output_model)
