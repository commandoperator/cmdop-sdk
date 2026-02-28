"""Base utilities for skills service."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Type, TypeVar

from cmdop.models.agent import AgentUsage
from cmdop.models.skills import SkillDetail, SkillInfo, SkillRunResult

if TYPE_CHECKING:
    from pydantic import BaseModel

T = TypeVar("T", bound="BaseModel")


def parse_skill_info(proto_skill: Any) -> SkillInfo:
    """Convert proto SkillInfo to Pydantic model."""
    return SkillInfo(
        name=proto_skill.name,
        description=proto_skill.description or "",
        author=proto_skill.author or "",
        version=proto_skill.version or "",
        model=proto_skill.model or "",
        origin=proto_skill.origin or "",
        required_bins=list(proto_skill.required_bins),
        required_env=list(proto_skill.required_env),
    )


def parse_skill_detail(response: Any) -> SkillDetail:
    """Convert proto SkillShowResponse to Pydantic model."""
    info = parse_skill_info(response.info) if response.found and response.info else None

    return SkillDetail(
        found=response.found,
        info=info,
        content=response.content or "",
        source=response.source or "",
        error=response.error or "",
    )


def parse_skill_run_result(
    response: Any,
    output_model: Type[T] | None = None,
) -> SkillRunResult[T]:
    """Convert proto SkillRunResponse to Pydantic model.

    Reuses parse_tool_result logic from agent/base.py for tool_results.
    """
    from cmdop.services.agent.base import parse_tool_result

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
            if response.success:
                return SkillRunResult(
                    request_id=response.request_id,
                    success=False,
                    text=response.text,
                    error=f"Failed to parse structured output: {e}",
                    tool_results=tool_results,
                    usage=usage,
                    duration_ms=response.duration_ms,
                    output_json=output_json,
                )

    return SkillRunResult(
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
