"""
Tests for CMDOP SDK Extract service and models.
"""

import json
from dataclasses import dataclass
from typing import List, Optional
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from cmdop.models.extract import (
    ExtractErrorCode,
    ExtractMetrics,
    ExtractOptions,
    ExtractResult,
    TokenUsage,
)
from cmdop.services.extract import (
    _model_to_json_schema,
    _parse_error_code,
    _parse_metrics,
    ExtractService,
)


# Sample Pydantic models for testing
class SimpleModel(BaseModel):
    name: str
    count: int


class NestedModel(BaseModel):
    host: str
    port: int
    ssl: bool = False


class ComplexModel(BaseModel):
    items: List[str]
    config: Optional[NestedModel] = None


class TestExtractModels:
    """Test Extract model dataclasses."""

    def test_token_usage(self):
        """Test TokenUsage dataclass."""
        usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
        )
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150

    def test_extract_metrics(self):
        """Test ExtractMetrics dataclass."""
        tokens = TokenUsage(100, 50, 150)
        metrics = ExtractMetrics(
            duration_ms=1000,
            llm_duration_ms=800,
            tool_duration_ms=200,
            llm_calls=2,
            tool_calls=3,
            retries=1,
            tokens=tokens,
        )
        assert metrics.duration_ms == 1000
        assert metrics.llm_duration_ms == 800
        assert metrics.tool_duration_ms == 200
        assert metrics.llm_calls == 2
        assert metrics.tool_calls == 3
        assert metrics.retries == 1
        assert metrics.tokens.total_tokens == 150

    def test_extract_options_defaults(self):
        """Test ExtractOptions default values."""
        opts = ExtractOptions()
        assert opts.model is None
        assert opts.temperature == 0.0
        assert opts.max_tokens == 4096
        assert opts.max_retries == 3
        assert opts.timeout_seconds == 60
        assert opts.working_directory is None
        assert opts.enabled_tools is None

    def test_extract_options_custom(self):
        """Test ExtractOptions with custom values."""
        opts = ExtractOptions(
            model="custom/model",
            temperature=0.5,
            max_tokens=2048,
            max_retries=5,
            timeout_seconds=120,
            working_directory="/tmp/work",
            enabled_tools=["read_file", "list_directory"],
        )
        assert opts.model == "custom/model"
        assert opts.temperature == 0.5
        assert opts.max_tokens == 2048
        assert opts.max_retries == 5
        assert opts.timeout_seconds == 120
        assert opts.working_directory == "/tmp/work"
        assert opts.enabled_tools == ["read_file", "list_directory"]

    def test_extract_result_success(self):
        """Test ExtractResult with success."""
        result = ExtractResult(
            success=True,
            data={"name": "test"},
            reasoning="Found the value",
            error=None,
            error_code=ExtractErrorCode.NONE,
            metrics=ExtractMetrics(
                duration_ms=1000,
                llm_duration_ms=800,
                tool_duration_ms=0,
                llm_calls=1,
                tool_calls=0,
                retries=0,
                tokens=TokenUsage(100, 50, 150),
            ),
        )
        assert result.success is True
        assert result.data == {"name": "test"}
        assert result.reasoning == "Found the value"
        assert result.error is None
        assert result.error_code == ExtractErrorCode.NONE

    def test_extract_result_failure(self):
        """Test ExtractResult with failure."""
        result = ExtractResult(
            success=False,
            data=None,
            reasoning="",
            error="Validation failed",
            error_code=ExtractErrorCode.VALIDATION_FAILED,
            metrics=ExtractMetrics(
                duration_ms=500,
                llm_duration_ms=400,
                tool_duration_ms=0,
                llm_calls=1,
                tool_calls=0,
                retries=2,
                tokens=TokenUsage(100, 50, 150),
            ),
        )
        assert result.success is False
        assert result.data is None
        assert result.error == "Validation failed"
        assert result.error_code == ExtractErrorCode.VALIDATION_FAILED


class TestExtractErrorCode:
    """Test ExtractErrorCode enum."""

    def test_error_codes(self):
        """Test all error code values."""
        assert ExtractErrorCode.NONE == 0
        assert ExtractErrorCode.INVALID_SCHEMA == 1
        assert ExtractErrorCode.EXTRACTION_FAILED == 2
        assert ExtractErrorCode.VALIDATION_FAILED == 3
        assert ExtractErrorCode.TIMEOUT == 4
        assert ExtractErrorCode.LLM_ERROR == 5
        assert ExtractErrorCode.TOOL_ERROR == 6
        assert ExtractErrorCode.CANCELLED == 7
        assert ExtractErrorCode.SCHEMA_TOO_LARGE == 8

    def test_parse_error_code_valid(self):
        """Test _parse_error_code with valid codes."""
        assert _parse_error_code(0) == ExtractErrorCode.NONE
        assert _parse_error_code(1) == ExtractErrorCode.INVALID_SCHEMA
        assert _parse_error_code(5) == ExtractErrorCode.LLM_ERROR

    def test_parse_error_code_invalid(self):
        """Test _parse_error_code with invalid code."""
        result = _parse_error_code(999)
        assert result == ExtractErrorCode.EXTRACTION_FAILED


class TestModelToJsonSchema:
    """Test Pydantic to JSON Schema conversion."""

    def test_simple_model(self):
        """Test conversion of simple model."""
        schema_str = _model_to_json_schema(SimpleModel)
        schema = json.loads(schema_str)

        assert schema["type"] == "object"
        assert "properties" in schema
        assert "name" in schema["properties"]
        assert "count" in schema["properties"]
        assert schema["properties"]["name"]["type"] == "string"
        assert schema["properties"]["count"]["type"] == "integer"

    def test_nested_model(self):
        """Test conversion of model with default values."""
        schema_str = _model_to_json_schema(NestedModel)
        schema = json.loads(schema_str)

        assert "host" in schema["properties"]
        assert "port" in schema["properties"]
        assert "ssl" in schema["properties"]

    def test_complex_model(self):
        """Test conversion of model with lists and optional fields."""
        schema_str = _model_to_json_schema(ComplexModel)
        schema = json.loads(schema_str)

        assert "items" in schema["properties"]
        assert "config" in schema["properties"]


class TestParseMetrics:
    """Test _parse_metrics function."""

    def test_parse_full_metrics(self):
        """Test parsing complete metrics."""
        mock_metrics = MagicMock()
        mock_metrics.duration_ms = 1000
        mock_metrics.llm_duration_ms = 800
        mock_metrics.tool_duration_ms = 200
        mock_metrics.llm_calls = 2
        mock_metrics.tool_calls = 3
        mock_metrics.retries = 1
        mock_metrics.tokens = MagicMock()
        mock_metrics.tokens.prompt_tokens = 100
        mock_metrics.tokens.completion_tokens = 50
        mock_metrics.tokens.total_tokens = 150

        result = _parse_metrics(mock_metrics)

        assert result.duration_ms == 1000
        assert result.llm_duration_ms == 800
        assert result.tool_duration_ms == 200
        assert result.llm_calls == 2
        assert result.tool_calls == 3
        assert result.retries == 1
        assert result.tokens.prompt_tokens == 100
        assert result.tokens.completion_tokens == 50
        assert result.tokens.total_tokens == 150

    def test_parse_metrics_no_tokens(self):
        """Test parsing metrics with no token info."""
        mock_metrics = MagicMock()
        mock_metrics.duration_ms = 500
        mock_metrics.llm_duration_ms = 400
        mock_metrics.tool_duration_ms = 0
        mock_metrics.llm_calls = 1
        mock_metrics.tool_calls = 0
        mock_metrics.retries = 0
        mock_metrics.tokens = None

        result = _parse_metrics(mock_metrics)

        assert result.duration_ms == 500
        assert result.tokens.prompt_tokens == 0
        assert result.tokens.completion_tokens == 0
        assert result.tokens.total_tokens == 0


class TestExtractResultGeneric:
    """Test ExtractResult generic typing."""

    def test_typed_result(self):
        """Test ExtractResult with typed data."""
        model_instance = SimpleModel(name="test", count=42)
        result: ExtractResult[SimpleModel] = ExtractResult(
            success=True,
            data=model_instance,
            reasoning="Found the data",
            error=None,
            error_code=ExtractErrorCode.NONE,
            metrics=ExtractMetrics(
                duration_ms=100,
                llm_duration_ms=80,
                tool_duration_ms=0,
                llm_calls=1,
                tool_calls=0,
                retries=0,
                tokens=TokenUsage(50, 25, 75),
            ),
        )

        assert result.success is True
        assert result.data is not None
        assert result.data.name == "test"
        assert result.data.count == 42

    def test_none_data_on_failure(self):
        """Test ExtractResult data is None on failure."""
        result: ExtractResult[SimpleModel] = ExtractResult(
            success=False,
            data=None,
            reasoning="",
            error="LLM error",
            error_code=ExtractErrorCode.LLM_ERROR,
            metrics=ExtractMetrics(
                duration_ms=100,
                llm_duration_ms=0,
                tool_duration_ms=0,
                llm_calls=0,
                tool_calls=0,
                retries=0,
                tokens=TokenUsage(0, 0, 0),
            ),
        )

        assert result.success is False
        assert result.data is None
        assert result.error == "LLM error"
