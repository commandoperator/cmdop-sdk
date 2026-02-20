"""Agent service for CMDOP SDK.

Provides AI agent execution capabilities via RunAgent RPC.
Supports structured output via Pydantic models.
"""

from cmdop.services.agent.sync import AgentService
from cmdop.services.agent.async_ import AsyncAgentService
from cmdop.services.agent.base import (
    map_agent_type,
    parse_agent_result,
    parse_tool_result,
    model_to_json_schema,
    parse_session_response,
)

# Backwards compatibility aliases (used in tests)
_map_agent_type = map_agent_type
_parse_agent_result = parse_agent_result
_parse_tool_result = parse_tool_result
_model_to_json_schema = model_to_json_schema

__all__ = [
    "AgentService",
    "AsyncAgentService",
    # Public helpers
    "map_agent_type",
    "parse_agent_result",
    "parse_tool_result",
    "model_to_json_schema",
    "parse_session_response",
    # Backwards compat
    "_map_agent_type",
    "_parse_agent_result",
    "_parse_tool_result",
    "_model_to_json_schema",
]
