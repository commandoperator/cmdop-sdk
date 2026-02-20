"""Base utilities for agent service."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Type, TypeVar

from cmdop.models.agent import (
    AgentResult,
    AgentToolResult,
    AgentType,
    AgentUsage,
)
from cmdop.models.terminal import SessionListItem

if TYPE_CHECKING:
    from pydantic import BaseModel

T = TypeVar("T", bound="BaseModel")


def map_agent_type(agent_type: AgentType) -> int:
    """Map SDK AgentType to proto enum value."""
    return {
        AgentType.CHAT: 0,
        AgentType.TERMINAL: 1,
        AgentType.COMMAND: 2,
        AgentType.ROUTER: 3,
        AgentType.PLANNER: 4,
    }.get(agent_type, 0)


def parse_tool_result(tr: Any) -> AgentToolResult:
    """Parse proto AgentToolResult to SDK model."""
    return AgentToolResult(
        tool_name=tr.tool_name,
        tool_call_id=tr.tool_call_id,
        success=tr.success,
        result=tr.result,
        error=tr.error or "",
        duration_ms=tr.duration_ms,
    )


def model_to_json_schema(model_class: Type[T]) -> str:
    """Convert Pydantic model to JSON Schema string."""
    try:
        schema = model_class.model_json_schema()
        return json.dumps(schema)
    except AttributeError:
        # Pydantic v1 fallback
        schema = model_class.schema()
        return json.dumps(schema)


def parse_agent_result(
    response: Any,
    output_model: Type[T] | None = None,
) -> AgentResult[T]:
    """Parse proto RunAgentResponse to SDK model."""
    tool_results = [parse_tool_result(tr) for tr in response.tool_results]

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


def parse_session_response(response: Any) -> SessionListItem:
    """Parse GetSessionByHostname response to SessionListItem."""
    connected_at = None
    if response.connected_at and response.connected_at.seconds > 0:
        connected_at = datetime.fromtimestamp(
            response.connected_at.seconds, tz=timezone.utc
        )

    return SessionListItem(
        session_id=response.session_id,
        machine_hostname=response.machine_hostname,
        machine_name=response.machine_name,
        status=response.status,
        os=response.os,
        agent_version=response.agent_version,
        heartbeat_age_seconds=response.heartbeat_age_seconds,
        has_shell=response.has_shell,
        shell=response.shell,
        working_directory=response.working_directory,
        connected_at=connected_at,
    )
