"""
Tests for CMDOP SDK Agent service and models.
"""

from unittest.mock import MagicMock, patch

import pytest

from cmdop.models.agent import (
    AgentEventType,
    AgentResult,
    AgentRunOptions,
    AgentRunRequest,
    AgentStreamEvent,
    AgentToolResult,
    AgentType,
    AgentUsage,
)
from cmdop.services.agent import (
    AgentService,
    AsyncAgentService,
    _map_agent_type,
    _parse_agent_result,
)


class TestAgentEnums:
    """Test Agent enums."""

    def test_agent_type_values(self):
        """Test AgentType enum values."""
        assert AgentType.CHAT.value == "chat"
        assert AgentType.TERMINAL.value == "terminal"
        assert AgentType.COMMAND.value == "command"
        assert AgentType.ROUTER.value == "router"
        assert AgentType.PLANNER.value == "planner"

    def test_agent_event_type_values(self):
        """Test AgentEventType enum values."""
        assert AgentEventType.TOKEN.value == "token"
        assert AgentEventType.TOOL_START.value == "tool_start"
        assert AgentEventType.TOOL_END.value == "tool_end"
        assert AgentEventType.THINKING.value == "thinking"
        assert AgentEventType.ERROR.value == "error"
        assert AgentEventType.HANDOFF.value == "handoff"


class TestAgentUsage:
    """Test AgentUsage model."""

    def test_defaults(self):
        """Test default values."""
        usage = AgentUsage()
        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0
        assert usage.total_tokens == 0

    def test_custom_values(self):
        """Test with custom values."""
        usage = AgentUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
        )
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150


class TestAgentToolResult:
    """Test AgentToolResult model."""

    def test_success(self):
        """Test successful tool result."""
        result = AgentToolResult(
            tool_name="execute_command",
            tool_call_id="call_123",
            success=True,
            result="Command output",
            duration_ms=500,
        )
        assert result.tool_name == "execute_command"
        assert result.tool_call_id == "call_123"
        assert result.success is True
        assert result.result == "Command output"
        assert result.error == ""
        assert result.duration_ms == 500

    def test_failure(self):
        """Test failed tool result."""
        result = AgentToolResult(
            tool_name="read_file",
            tool_call_id="call_456",
            success=False,
            error="File not found",
        )
        assert result.tool_name == "read_file"
        assert result.success is False
        assert result.error == "File not found"
        assert result.result == ""


class TestAgentRunOptions:
    """Test AgentRunOptions model."""

    def test_defaults(self):
        """Test default values."""
        opts = AgentRunOptions()
        assert opts.model is None
        assert opts.max_turns == 10
        assert opts.max_retries == 3
        assert opts.timeout_seconds == 300
        assert opts.stream_events is False

    def test_custom_values(self):
        """Test with custom values."""
        opts = AgentRunOptions(
            model="openai/gpt-4o",
            max_turns=20,
            max_retries=5,
            timeout_seconds=600,
            stream_events=True,
        )
        assert opts.model == "openai/gpt-4o"
        assert opts.max_turns == 20
        assert opts.max_retries == 5
        assert opts.timeout_seconds == 600
        assert opts.stream_events is True

    def test_to_options_map(self):
        """Test conversion to options map."""
        opts = AgentRunOptions(model="custom/model", max_turns=15)
        opts_map = opts.to_options_map()
        assert opts_map["model"] == "custom/model"
        assert opts_map["max_turns"] == "15"
        assert opts_map["max_retries"] == "3"
        assert opts_map["timeout_seconds"] == "300"

    def test_to_options_map_no_model(self):
        """Test options map without model."""
        opts = AgentRunOptions()
        opts_map = opts.to_options_map()
        assert "model" not in opts_map


class TestAgentStreamEvent:
    """Test AgentStreamEvent model."""

    def test_basic(self):
        """Test basic event."""
        event = AgentStreamEvent(
            request_id="req_123",
            type=AgentEventType.TOKEN,
            payload='{"token": "Hello"}',
            timestamp=1704067200000,
        )
        assert event.request_id == "req_123"
        assert event.type == AgentEventType.TOKEN
        assert event.payload == '{"token": "Hello"}'
        assert event.timestamp == 1704067200000

    def test_payload_data_valid_json(self):
        """Test payload_data with valid JSON."""
        event = AgentStreamEvent(
            request_id="req_123",
            type=AgentEventType.TOKEN,
            payload='{"token": "World", "index": 1}',
        )
        data = event.payload_data
        assert data["token"] == "World"
        assert data["index"] == 1

    def test_payload_data_invalid_json(self):
        """Test payload_data with invalid JSON."""
        event = AgentStreamEvent(
            request_id="req_123",
            type=AgentEventType.TOKEN,
            payload="not json",
        )
        data = event.payload_data
        assert data == {"raw": "not json"}

    def test_payload_data_empty(self):
        """Test payload_data with empty payload."""
        event = AgentStreamEvent(
            request_id="req_123",
            type=AgentEventType.TOKEN,
        )
        assert event.payload_data == {}


class TestAgentResult:
    """Test AgentResult model."""

    def test_success(self):
        """Test successful result."""
        result = AgentResult(
            request_id="req_123",
            success=True,
            text="The command completed successfully.",
            duration_ms=5000,
        )
        assert result.request_id == "req_123"
        assert result.success is True
        assert result.text == "The command completed successfully."
        assert result.error == ""
        assert result.tool_results == []
        assert result.usage.total_tokens == 0
        assert result.duration_ms == 5000

    def test_failure(self):
        """Test failed result."""
        result = AgentResult(
            request_id="req_456",
            success=False,
            error="Agent execution failed",
        )
        assert result.success is False
        assert result.error == "Agent execution failed"
        assert result.text == ""

    def test_with_tool_results(self):
        """Test result with tool results."""
        tool_result = AgentToolResult(
            tool_name="execute_command",
            tool_call_id="call_1",
            success=True,
            result="output",
        )
        result = AgentResult(
            request_id="req_789",
            success=True,
            text="Done",
            tool_results=[tool_result],
        )
        assert len(result.tool_results) == 1
        assert result.tool_results[0].tool_name == "execute_command"

    def test_duration_seconds(self):
        """Test duration_seconds property."""
        result = AgentResult(
            request_id="req_123",
            success=True,
            duration_ms=2500,
        )
        assert result.duration_seconds == 2.5


class TestAgentRunRequest:
    """Test AgentRunRequest model."""

    def test_minimal(self):
        """Test minimal request."""
        request = AgentRunRequest(prompt="What time is it?")
        assert request.prompt == "What time is it?"
        assert request.agent_type == AgentType.CHAT
        assert request.options.max_turns == 10

    def test_full(self):
        """Test full request."""
        opts = AgentRunOptions(model="gpt-4", stream_events=True)
        request = AgentRunRequest(
            prompt="Deploy the app",
            agent_type=AgentType.TERMINAL,
            options=opts,
        )
        assert request.prompt == "Deploy the app"
        assert request.agent_type == AgentType.TERMINAL
        assert request.options.model == "gpt-4"
        assert request.options.stream_events is True


class TestMapAgentType:
    """Test _map_agent_type helper."""

    def test_chat(self):
        assert _map_agent_type(AgentType.CHAT) == 0

    def test_terminal(self):
        assert _map_agent_type(AgentType.TERMINAL) == 1

    def test_command(self):
        assert _map_agent_type(AgentType.COMMAND) == 2

    def test_router(self):
        assert _map_agent_type(AgentType.ROUTER) == 3

    def test_planner(self):
        assert _map_agent_type(AgentType.PLANNER) == 4


class TestParseAgentResult:
    """Test _parse_agent_result helper."""

    def test_parse(self):
        """Test parsing proto result."""
        pb_tool = MagicMock()
        pb_tool.tool_name = "execute_command"
        pb_tool.tool_call_id = "call_1"
        pb_tool.success = True
        pb_tool.result = "output"
        pb_tool.error = ""
        pb_tool.duration_ms = 100

        pb_usage = MagicMock()
        pb_usage.prompt_tokens = 100
        pb_usage.completion_tokens = 50
        pb_usage.total_tokens = 150

        pb_result = MagicMock()
        pb_result.request_id = "req_123"
        pb_result.success = True
        pb_result.text = "Done"
        pb_result.error = ""
        pb_result.tool_results = [pb_tool]
        pb_result.usage = pb_usage
        pb_result.duration_ms = 5000
        pb_result.output_json = ""  # Required for structured output

        result = _parse_agent_result(pb_result)
        assert result.request_id == "req_123"
        assert result.success is True
        assert result.text == "Done"
        assert len(result.tool_results) == 1
        assert result.tool_results[0].tool_name == "execute_command"
        assert result.usage.total_tokens == 150
        assert result.duration_ms == 5000


class TestAgentService:
    """Test AgentService."""

    def test_initialization(self):
        """Test service initialization."""
        transport = MagicMock()
        service = AgentService(transport)
        assert service._transport == transport


class TestAsyncAgentService:
    """Test AsyncAgentService."""

    def test_initialization(self):
        """Test service initialization."""
        transport = MagicMock()
        service = AsyncAgentService(transport)
        assert service._transport == transport
        assert service._stub is None
