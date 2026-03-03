"""
Tests for CMDOP SDK Skills service and models.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from cmdop.models.agent import AgentToolResult, AgentUsage
from cmdop.models.skills import (
    SkillDetail,
    SkillInfo,
    SkillRunOptions,
    SkillRunResult,
)
from cmdop.services.skills import (
    AsyncSkillsService,
    SkillsService,
    parse_skill_detail,
    parse_skill_info,
    parse_skill_run_result,
)


# ============================================================================
# Model Tests
# ============================================================================


class TestSkillInfo:
    """Test SkillInfo model."""

    def test_minimal(self):
        """Test with only required fields."""
        info = SkillInfo(name="code-review")
        assert info.name == "code-review"
        assert info.description == ""
        assert info.author == ""
        assert info.version == ""
        assert info.model == ""
        assert info.origin == ""
        assert info.required_bins == []
        assert info.required_env == []

    def test_full(self):
        """Test with all fields."""
        info = SkillInfo(
            name="code-review",
            description="Reviews code for quality",
            author="cmdop",
            version="1.0.0",
            model="openai/gpt-4o",
            origin="builtin",
            required_bins=["git", "diff"],
            required_env=["OPENAI_API_KEY"],
        )
        assert info.name == "code-review"
        assert info.description == "Reviews code for quality"
        assert info.author == "cmdop"
        assert info.version == "1.0.0"
        assert info.model == "openai/gpt-4o"
        assert info.origin == "builtin"
        assert info.required_bins == ["git", "diff"]
        assert info.required_env == ["OPENAI_API_KEY"]

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(Exception):
            SkillInfo(name="test", unknown_field="value")


class TestSkillDetail:
    """Test SkillDetail model."""

    def test_found(self):
        """Test found skill."""
        info = SkillInfo(name="code-review", description="Reviews code")
        detail = SkillDetail(
            found=True,
            info=info,
            content="# Code Review\nYou are a code reviewer.",
            source="/home/user/.cmdop/skills/code-review.md",
        )
        assert detail.found is True
        assert detail.info is not None
        assert detail.info.name == "code-review"
        assert detail.content == "# Code Review\nYou are a code reviewer."
        assert detail.source == "/home/user/.cmdop/skills/code-review.md"
        assert detail.error == ""

    def test_not_found(self):
        """Test not found skill."""
        detail = SkillDetail(
            found=False,
            error="Skill 'nonexistent' not found",
        )
        assert detail.found is False
        assert detail.info is None
        assert detail.content == ""
        assert detail.source == ""
        assert detail.error == "Skill 'nonexistent' not found"

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(Exception):
            SkillDetail(found=True, unknown="value")


class TestSkillRunOptions:
    """Test SkillRunOptions model."""

    def test_defaults(self):
        """Test default values."""
        opts = SkillRunOptions()
        assert opts.model is None
        assert opts.timeout_seconds == 300

    def test_custom_values(self):
        """Test with custom values."""
        opts = SkillRunOptions(
            model="openai/gpt-4o",
            timeout_seconds=600,
        )
        assert opts.model == "openai/gpt-4o"
        assert opts.timeout_seconds == 600

    def test_to_options_map_with_model(self):
        """Test conversion to options map with model."""
        opts = SkillRunOptions(model="custom/model", timeout_seconds=120)
        opts_map = opts.to_options_map()
        assert opts_map["model"] == "custom/model"
        assert opts_map["timeout_seconds"] == "120"

    def test_to_options_map_no_model(self):
        """Test options map without model."""
        opts = SkillRunOptions()
        opts_map = opts.to_options_map()
        assert "model" not in opts_map
        assert opts_map["timeout_seconds"] == "300"

    def test_timeout_validation_min(self):
        """Test timeout minimum validation."""
        with pytest.raises(Exception):
            SkillRunOptions(timeout_seconds=5)

    def test_timeout_validation_max(self):
        """Test timeout maximum validation."""
        with pytest.raises(Exception):
            SkillRunOptions(timeout_seconds=700)

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(Exception):
            SkillRunOptions(unknown="value")


class TestSkillRunResult:
    """Test SkillRunResult model."""

    def test_success(self):
        """Test successful result."""
        result = SkillRunResult(
            request_id="req_123",
            success=True,
            text="Code review complete. Score: 8/10.",
            duration_ms=5000,
        )
        assert result.request_id == "req_123"
        assert result.success is True
        assert result.text == "Code review complete. Score: 8/10."
        assert result.error == ""
        assert result.tool_results == []
        assert result.usage.total_tokens == 0
        assert result.duration_ms == 5000
        assert result.data is None
        assert result.output_json == ""

    def test_failure(self):
        """Test failed result."""
        result = SkillRunResult(
            request_id="req_456",
            success=False,
            error="Skill execution timed out",
        )
        assert result.success is False
        assert result.error == "Skill execution timed out"
        assert result.text == ""

    def test_with_tool_results(self):
        """Test result with tool results."""
        tool_result = AgentToolResult(
            tool_name="execute_command",
            tool_call_id="call_1",
            success=True,
            result="output",
        )
        result = SkillRunResult(
            request_id="req_789",
            success=True,
            text="Done",
            tool_results=[tool_result],
        )
        assert len(result.tool_results) == 1
        assert result.tool_results[0].tool_name == "execute_command"

    def test_with_usage(self):
        """Test result with usage stats."""
        usage = AgentUsage(
            prompt_tokens=500,
            completion_tokens=200,
            total_tokens=700,
        )
        result = SkillRunResult(
            request_id="req_101",
            success=True,
            text="Done",
            usage=usage,
        )
        assert result.usage.prompt_tokens == 500
        assert result.usage.completion_tokens == 200
        assert result.usage.total_tokens == 700

    def test_duration_seconds(self):
        """Test duration_seconds property."""
        result = SkillRunResult(
            request_id="req_123",
            success=True,
            duration_ms=2500,
        )
        assert result.duration_seconds == 2.5

    def test_duration_seconds_zero(self):
        """Test duration_seconds with zero."""
        result = SkillRunResult(
            request_id="req_123",
            success=True,
        )
        assert result.duration_seconds == 0.0

    def test_with_structured_output(self):
        """Test result with structured output data."""
        result = SkillRunResult(
            request_id="req_123",
            success=True,
            text="Review complete",
            data={"score": 8, "summary": "Good code"},
            output_json='{"score": 8, "summary": "Good code"}',
        )
        assert result.data == {"score": 8, "summary": "Good code"}
        assert result.output_json == '{"score": 8, "summary": "Good code"}'

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(Exception):
            SkillRunResult(request_id="req", success=True, unknown="value")


# ============================================================================
# Parser Tests
# ============================================================================


class TestParseSkillInfo:
    """Test parse_skill_info helper."""

    def test_parse(self):
        """Test parsing proto SkillInfo."""
        pb_skill = MagicMock()
        pb_skill.name = "code-review"
        pb_skill.description = "Reviews code"
        pb_skill.author = "cmdop"
        pb_skill.version = "1.0.0"
        pb_skill.model = "openai/gpt-4o"
        pb_skill.origin = "builtin"
        pb_skill.required_bins = ["git"]
        pb_skill.required_env = ["OPENAI_API_KEY"]

        result = parse_skill_info(pb_skill)
        assert isinstance(result, SkillInfo)
        assert result.name == "code-review"
        assert result.description == "Reviews code"
        assert result.author == "cmdop"
        assert result.version == "1.0.0"
        assert result.model == "openai/gpt-4o"
        assert result.origin == "builtin"
        assert result.required_bins == ["git"]
        assert result.required_env == ["OPENAI_API_KEY"]

    def test_parse_empty_fields(self):
        """Test parsing proto SkillInfo with empty optional fields."""
        pb_skill = MagicMock()
        pb_skill.name = "simple"
        pb_skill.description = ""
        pb_skill.author = ""
        pb_skill.version = ""
        pb_skill.model = ""
        pb_skill.origin = ""
        pb_skill.required_bins = []
        pb_skill.required_env = []

        result = parse_skill_info(pb_skill)
        assert result.name == "simple"
        assert result.description == ""
        assert result.required_bins == []
        assert result.required_env == []


class TestParseSkillDetail:
    """Test parse_skill_detail helper."""

    def test_parse_found(self):
        """Test parsing found skill."""
        pb_info = MagicMock()
        pb_info.name = "code-review"
        pb_info.description = "Reviews code"
        pb_info.author = "cmdop"
        pb_info.version = "1.0.0"
        pb_info.model = ""
        pb_info.origin = "builtin"
        pb_info.required_bins = []
        pb_info.required_env = []

        pb_response = MagicMock()
        pb_response.found = True
        pb_response.info = pb_info
        pb_response.content = "# System Prompt\nYou review code."
        pb_response.source = "/path/to/skill.md"
        pb_response.error = ""

        result = parse_skill_detail(pb_response)
        assert isinstance(result, SkillDetail)
        assert result.found is True
        assert result.info is not None
        assert result.info.name == "code-review"
        assert result.content == "# System Prompt\nYou review code."
        assert result.source == "/path/to/skill.md"
        assert result.error == ""

    def test_parse_not_found(self):
        """Test parsing not found skill."""
        pb_response = MagicMock()
        pb_response.found = False
        pb_response.info = None
        pb_response.content = ""
        pb_response.source = ""
        pb_response.error = "Skill not found"

        result = parse_skill_detail(pb_response)
        assert result.found is False
        assert result.info is None
        assert result.error == "Skill not found"


class TestParseSkillRunResult:
    """Test parse_skill_run_result helper."""

    def test_parse_success(self):
        """Test parsing successful run result."""
        pb_tool = MagicMock()
        pb_tool.tool_name = "execute_command"
        pb_tool.tool_call_id = "call_1"
        pb_tool.success = True
        pb_tool.result = "output"
        pb_tool.error = ""
        pb_tool.duration_ms = 100

        pb_usage = MagicMock()
        pb_usage.prompt_tokens = 500
        pb_usage.completion_tokens = 200
        pb_usage.total_tokens = 700

        pb_response = MagicMock()
        pb_response.request_id = "req_123"
        pb_response.success = True
        pb_response.text = "Review complete"
        pb_response.error = ""
        pb_response.tool_results = [pb_tool]
        pb_response.usage = pb_usage
        pb_response.duration_ms = 5000
        pb_response.output_json = ""

        result = parse_skill_run_result(pb_response)
        assert isinstance(result, SkillRunResult)
        assert result.request_id == "req_123"
        assert result.success is True
        assert result.text == "Review complete"
        assert len(result.tool_results) == 1
        assert result.tool_results[0].tool_name == "execute_command"
        assert result.usage.total_tokens == 700
        assert result.duration_ms == 5000
        assert result.data is None

    def test_parse_failure(self):
        """Test parsing failed run result."""
        pb_usage = MagicMock()
        pb_usage.prompt_tokens = 0
        pb_usage.completion_tokens = 0
        pb_usage.total_tokens = 0

        pb_response = MagicMock()
        pb_response.request_id = "req_456"
        pb_response.success = False
        pb_response.text = ""
        pb_response.error = "Skill timed out"
        pb_response.tool_results = []
        pb_response.usage = pb_usage
        pb_response.duration_ms = 300000
        pb_response.output_json = ""

        result = parse_skill_run_result(pb_response)
        assert result.success is False
        assert result.error == "Skill timed out"
        assert result.tool_results == []

    def test_parse_with_structured_output(self):
        """Test parsing with structured output model."""
        from pydantic import BaseModel

        class Review(BaseModel):
            score: int
            summary: str

        pb_usage = MagicMock()
        pb_usage.prompt_tokens = 100
        pb_usage.completion_tokens = 50
        pb_usage.total_tokens = 150

        pb_response = MagicMock()
        pb_response.request_id = "req_789"
        pb_response.success = True
        pb_response.text = "Review done"
        pb_response.error = ""
        pb_response.tool_results = []
        pb_response.usage = pb_usage
        pb_response.duration_ms = 2000
        pb_response.output_json = json.dumps({"score": 9, "summary": "Excellent code"})

        result = parse_skill_run_result(pb_response, output_model=Review)
        assert result.success is True
        assert result.data is not None
        assert isinstance(result.data, Review)
        assert result.data.score == 9
        assert result.data.summary == "Excellent code"
        assert result.output_json != ""

    def test_parse_with_invalid_structured_output(self):
        """Test parsing with invalid structured output JSON."""
        from pydantic import BaseModel

        class Review(BaseModel):
            score: int
            summary: str

        pb_usage = MagicMock()
        pb_usage.prompt_tokens = 100
        pb_usage.completion_tokens = 50
        pb_usage.total_tokens = 150

        pb_response = MagicMock()
        pb_response.request_id = "req_err"
        pb_response.success = True
        pb_response.text = "Review done"
        pb_response.error = ""
        pb_response.tool_results = []
        pb_response.usage = pb_usage
        pb_response.duration_ms = 2000
        pb_response.output_json = "not valid json"

        result = parse_skill_run_result(pb_response, output_model=Review)
        # Should return failure when output parsing fails on a success response
        assert result.success is False
        assert "Failed to parse structured output" in result.error
        assert result.data is None

    def test_parse_no_usage(self):
        """Test parsing when usage is None."""
        pb_response = MagicMock()
        pb_response.request_id = "req_no_usage"
        pb_response.success = True
        pb_response.text = "Done"
        pb_response.error = ""
        pb_response.tool_results = []
        pb_response.usage = None
        pb_response.duration_ms = 1000
        pb_response.output_json = ""

        result = parse_skill_run_result(pb_response)
        assert result.usage.prompt_tokens == 0
        assert result.usage.completion_tokens == 0
        assert result.usage.total_tokens == 0


# ============================================================================
# Service Tests
# ============================================================================


class TestSkillsService:
    """Test SkillsService (sync wrapper)."""

    def test_initialization(self):
        """Test service initialization."""
        transport = MagicMock()
        service = SkillsService(transport)
        assert service._transport == transport


class TestAsyncSkillsService:
    """Test AsyncSkillsService."""

    def test_initialization(self):
        """Test service initialization."""
        transport = MagicMock()
        service = AsyncSkillsService(transport)
        assert service._transport == transport
        assert service._stub is None
        assert service._session_id is None
        assert service._cached_hostname is None
        assert service._cached_session_info is None

    def test_set_session_id(self):
        """Test setting session ID directly."""
        transport = MagicMock()
        service = AsyncSkillsService(transport)
        service.set_session_id("session-123")
        assert service._session_id == "session-123"

    def test_clear_session(self):
        """Test clearing session cache."""
        transport = MagicMock()
        service = AsyncSkillsService(transport)
        service._session_id = "session-123"
        service._cached_hostname = "my-server"
        service._cached_session_info = MagicMock()

        service.clear_session()
        assert service._session_id is None
        assert service._cached_hostname is None
        assert service._cached_session_info is None

    def test_current_session_none(self):
        """Test current_session when not set."""
        transport = MagicMock()
        service = AsyncSkillsService(transport)
        assert service.current_session is None

    def test_current_hostname_none(self):
        """Test current_hostname when not set."""
        transport = MagicMock()
        service = AsyncSkillsService(transport)
        assert service.current_hostname is None

    @pytest.mark.asyncio
    async def test_list(self):
        """Test listing skills."""
        transport = MagicMock()
        service = AsyncSkillsService(transport)

        # Mock proto skills
        pb_skill1 = MagicMock()
        pb_skill1.name = "code-review"
        pb_skill1.description = "Reviews code"
        pb_skill1.author = "cmdop"
        pb_skill1.version = "1.0.0"
        pb_skill1.model = ""
        pb_skill1.origin = "builtin"
        pb_skill1.required_bins = []
        pb_skill1.required_env = []

        pb_skill2 = MagicMock()
        pb_skill2.name = "summarize"
        pb_skill2.description = "Summarizes text"
        pb_skill2.author = ""
        pb_skill2.version = ""
        pb_skill2.model = ""
        pb_skill2.origin = "workspace"
        pb_skill2.required_bins = []
        pb_skill2.required_env = []

        mock_response = MagicMock()
        mock_response.skills = [pb_skill1, pb_skill2]
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.SkillList = AsyncMock(return_value=mock_response)
        service._stub = mock_stub

        # Patch _call_async to call the stub directly
        async def fake_call_async(method, request, timeout=None):
            return await method(request)

        service._call_async = fake_call_async

        skills = await service.list()
        assert len(skills) == 2
        assert skills[0].name == "code-review"
        assert skills[0].description == "Reviews code"
        assert skills[0].origin == "builtin"
        assert skills[1].name == "summarize"
        assert skills[1].origin == "workspace"

    @pytest.mark.asyncio
    async def test_list_uses_cached_session(self):
        """Test list uses cached session ID."""
        transport = MagicMock()
        service = AsyncSkillsService(transport)
        service._session_id = "cached-session"

        mock_response = MagicMock()
        mock_response.skills = []
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.SkillList = AsyncMock(return_value=mock_response)
        service._stub = mock_stub

        captured_request = None

        async def fake_call_async(method, request, timeout=None):
            nonlocal captured_request
            captured_request = request
            return await method(request)

        service._call_async = fake_call_async

        await service.list()
        assert captured_request.session_id == "cached-session"

    @pytest.mark.asyncio
    async def test_list_session_id_override(self):
        """Test list with explicit session_id overrides cached."""
        transport = MagicMock()
        service = AsyncSkillsService(transport)
        service._session_id = "cached-session"

        mock_response = MagicMock()
        mock_response.skills = []
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.SkillList = AsyncMock(return_value=mock_response)
        service._stub = mock_stub

        captured_request = None

        async def fake_call_async(method, request, timeout=None):
            nonlocal captured_request
            captured_request = request
            return await method(request)

        service._call_async = fake_call_async

        await service.list(session_id="explicit-session")
        assert captured_request.session_id == "explicit-session"

    @pytest.mark.asyncio
    async def test_show(self):
        """Test showing skill detail."""
        transport = MagicMock()
        service = AsyncSkillsService(transport)

        pb_info = MagicMock()
        pb_info.name = "code-review"
        pb_info.description = "Reviews code"
        pb_info.author = "cmdop"
        pb_info.version = "1.0.0"
        pb_info.model = ""
        pb_info.origin = "builtin"
        pb_info.required_bins = []
        pb_info.required_env = []

        mock_response = MagicMock()
        mock_response.found = True
        mock_response.info = pb_info
        mock_response.content = "# Code Review\nYou review code."
        mock_response.source = "/skills/code-review.md"
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.SkillShow = AsyncMock(return_value=mock_response)
        service._stub = mock_stub

        async def fake_call_async(method, request, timeout=None):
            return await method(request)

        service._call_async = fake_call_async

        detail = await service.show("code-review")
        assert isinstance(detail, SkillDetail)
        assert detail.found is True
        assert detail.info.name == "code-review"
        assert detail.content == "# Code Review\nYou review code."
        assert detail.source == "/skills/code-review.md"

    @pytest.mark.asyncio
    async def test_show_not_found(self):
        """Test showing non-existent skill."""
        transport = MagicMock()
        service = AsyncSkillsService(transport)

        mock_response = MagicMock()
        mock_response.found = False
        mock_response.info = None
        mock_response.content = ""
        mock_response.source = ""
        mock_response.error = "Skill 'nonexistent' not found"

        mock_stub = MagicMock()
        mock_stub.SkillShow = AsyncMock(return_value=mock_response)
        service._stub = mock_stub

        async def fake_call_async(method, request, timeout=None):
            return await method(request)

        service._call_async = fake_call_async

        detail = await service.show("nonexistent")
        assert detail.found is False
        assert detail.info is None
        assert detail.error == "Skill 'nonexistent' not found"

    @pytest.mark.asyncio
    async def test_run(self):
        """Test running a skill."""
        transport = MagicMock()
        service = AsyncSkillsService(transport)

        pb_usage = MagicMock()
        pb_usage.prompt_tokens = 500
        pb_usage.completion_tokens = 200
        pb_usage.total_tokens = 700

        mock_response = MagicMock()
        mock_response.request_id = "req_123"
        mock_response.success = True
        mock_response.text = "Code review complete. Score: 8/10."
        mock_response.error = ""
        mock_response.tool_results = []
        mock_response.usage = pb_usage
        mock_response.duration_ms = 5000
        mock_response.output_json = ""

        mock_stub = MagicMock()
        mock_stub.SkillRun = AsyncMock(return_value=mock_response)
        service._stub = mock_stub

        async def fake_call_async(method, request, timeout=None):
            return await method(request)

        service._call_async = fake_call_async

        result = await service.run("code-review", "Review this PR")
        assert isinstance(result, SkillRunResult)
        assert result.request_id == "req_123"
        assert result.success is True
        assert result.text == "Code review complete. Score: 8/10."
        assert result.usage.total_tokens == 700
        assert result.duration_ms == 5000

    @pytest.mark.asyncio
    async def test_run_with_options(self):
        """Test running a skill with custom options."""
        transport = MagicMock()
        service = AsyncSkillsService(transport)

        pb_usage = MagicMock()
        pb_usage.prompt_tokens = 100
        pb_usage.completion_tokens = 50
        pb_usage.total_tokens = 150

        mock_response = MagicMock()
        mock_response.request_id = "req_456"
        mock_response.success = True
        mock_response.text = "Done"
        mock_response.error = ""
        mock_response.tool_results = []
        mock_response.usage = pb_usage
        mock_response.duration_ms = 2000
        mock_response.output_json = ""

        mock_stub = MagicMock()
        mock_stub.SkillRun = AsyncMock(return_value=mock_response)
        service._stub = mock_stub

        captured_request = None

        async def fake_call_async(method, request, timeout=None):
            nonlocal captured_request
            captured_request = request
            return await method(request)

        service._call_async = fake_call_async

        opts = SkillRunOptions(model="openai/gpt-4o", timeout_seconds=120)
        result = await service.run("summarize", "Summarize this", options=opts)

        assert result.success is True
        assert captured_request.skill_name == "summarize"
        assert captured_request.prompt == "Summarize this"
        assert captured_request.timeout_seconds == 120

    @pytest.mark.asyncio
    async def test_run_with_structured_output(self):
        """Test running a skill with structured output model."""
        from pydantic import BaseModel

        class Review(BaseModel):
            score: int
            summary: str

        transport = MagicMock()
        service = AsyncSkillsService(transport)

        pb_usage = MagicMock()
        pb_usage.prompt_tokens = 100
        pb_usage.completion_tokens = 50
        pb_usage.total_tokens = 150

        mock_response = MagicMock()
        mock_response.request_id = "req_structured"
        mock_response.success = True
        mock_response.text = "Review done"
        mock_response.error = ""
        mock_response.tool_results = []
        mock_response.usage = pb_usage
        mock_response.duration_ms = 3000
        mock_response.output_json = json.dumps({"score": 9, "summary": "Great code"})

        mock_stub = MagicMock()
        mock_stub.SkillRun = AsyncMock(return_value=mock_response)
        service._stub = mock_stub

        captured_request = None

        async def fake_call_async(method, request, timeout=None):
            nonlocal captured_request
            captured_request = request
            return await method(request)

        service._call_async = fake_call_async

        result = await service.run(
            "code-review",
            "Review this PR",
            output_model=Review,
        )
        assert result.success is True
        assert result.data is not None
        assert isinstance(result.data, Review)
        assert result.data.score == 9
        assert result.data.summary == "Great code"
        # output_schema should be populated in request
        assert captured_request.output_schema != ""

    @pytest.mark.asyncio
    async def test_run_failure(self):
        """Test running a skill that fails."""
        transport = MagicMock()
        service = AsyncSkillsService(transport)

        pb_usage = MagicMock()
        pb_usage.prompt_tokens = 0
        pb_usage.completion_tokens = 0
        pb_usage.total_tokens = 0

        mock_response = MagicMock()
        mock_response.request_id = "req_fail"
        mock_response.success = False
        mock_response.text = ""
        mock_response.error = "Skill execution failed"
        mock_response.tool_results = []
        mock_response.usage = pb_usage
        mock_response.duration_ms = 1000
        mock_response.output_json = ""

        mock_stub = MagicMock()
        mock_stub.SkillRun = AsyncMock(return_value=mock_response)
        service._stub = mock_stub

        async def fake_call_async(method, request, timeout=None):
            return await method(request)

        service._call_async = fake_call_async

        result = await service.run("broken-skill", "Do something")
        assert result.success is False
        assert result.error == "Skill execution failed"

    @pytest.mark.asyncio
    async def test_list_empty(self):
        """Test listing when no skills available."""
        transport = MagicMock()
        service = AsyncSkillsService(transport)

        mock_response = MagicMock()
        mock_response.skills = []
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.SkillList = AsyncMock(return_value=mock_response)
        service._stub = mock_stub

        async def fake_call_async(method, request, timeout=None):
            return await method(request)

        service._call_async = fake_call_async

        skills = await service.list()
        assert skills == []

    @pytest.mark.asyncio
    async def test_run_default_session_id(self):
        """Test run uses 'local' as default session ID."""
        transport = MagicMock()
        service = AsyncSkillsService(transport)

        pb_usage = MagicMock()
        pb_usage.prompt_tokens = 0
        pb_usage.completion_tokens = 0
        pb_usage.total_tokens = 0

        mock_response = MagicMock()
        mock_response.request_id = "req_local"
        mock_response.success = True
        mock_response.text = "OK"
        mock_response.error = ""
        mock_response.tool_results = []
        mock_response.usage = pb_usage
        mock_response.duration_ms = 100
        mock_response.output_json = ""

        mock_stub = MagicMock()
        mock_stub.SkillRun = AsyncMock(return_value=mock_response)
        service._stub = mock_stub

        captured_request = None

        async def fake_call_async(method, request, timeout=None):
            nonlocal captured_request
            captured_request = request
            return await method(request)

        service._call_async = fake_call_async

        await service.run("test-skill", "test prompt")
        assert captured_request.session_id == "local"


# ============================================================================
# Client Integration Tests
# ============================================================================


class TestClientSkillsProperty:
    """Test that skills property is accessible on clients."""

    def test_sync_client_has_skills(self):
        """Test CMDOPClient has skills property."""
        from cmdop import CMDOPClient

        assert hasattr(CMDOPClient, "skills")

    def test_async_client_has_skills(self):
        """Test AsyncCMDOPClient has skills property."""
        from cmdop import AsyncCMDOPClient

        assert hasattr(AsyncCMDOPClient, "skills")

    def test_sync_client_lazy_load(self):
        """Test skills service is lazy-loaded."""
        transport = MagicMock()
        from cmdop import CMDOPClient

        client = CMDOPClient(transport)
        assert client._skills is None
        _ = client.skills
        assert client._skills is not None

    def test_async_client_lazy_load(self):
        """Test skills service is lazy-loaded for async."""
        transport = MagicMock()
        from cmdop import AsyncCMDOPClient

        client = AsyncCMDOPClient(transport)
        assert client._skills is None
        _ = client.skills
        assert client._skills is not None


# ============================================================================
# Top-level Export Tests
# ============================================================================


class TestSkillExports:
    """Test that skill models are exported at top level."""

    def test_skill_info_export(self):
        """Test SkillInfo is exported from cmdop."""
        from cmdop import SkillInfo

        assert SkillInfo is not None

    def test_skill_detail_export(self):
        """Test SkillDetail is exported from cmdop."""
        from cmdop import SkillDetail

        assert SkillDetail is not None

    def test_skill_run_options_export(self):
        """Test SkillRunOptions is exported from cmdop."""
        from cmdop import SkillRunOptions

        assert SkillRunOptions is not None

    def test_skill_run_result_export(self):
        """Test SkillRunResult is exported from cmdop."""
        from cmdop import SkillRunResult

        assert SkillRunResult is not None

    def test_services_export(self):
        """Test services are exported from cmdop.services."""
        from cmdop.services import SkillsService, AsyncSkillsService

        assert SkillsService is not None
        assert AsyncSkillsService is not None
