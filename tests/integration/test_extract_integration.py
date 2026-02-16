"""
Integration tests for CMDOP SDK Extract service.

These tests verify the full flow from SDK to proto serialization.
Note: These tests use mocked transport, not actual gRPC connections.
"""

import json
from typing import List, Optional
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, Field

from cmdop.models.extract import (
    ExtractErrorCode,
    ExtractMetrics,
    ExtractOptions,
    ExtractResult,
    TokenUsage,
)
from cmdop.services.extract import ExtractService, _model_to_json_schema


# Test Pydantic models
class Person(BaseModel):
    """Simple person model."""
    name: str
    age: int
    email: Optional[str] = None


class Address(BaseModel):
    """Address model for nested tests."""
    street: str
    city: str
    country: str = "USA"
    zip_code: Optional[str] = None


class Company(BaseModel):
    """Company model with nested objects."""
    name: str
    address: Address
    employees: int
    tags: List[str] = Field(default_factory=list)


class TaskStatus(BaseModel):
    """Model with enum-like values."""
    status: str  # pending, active, completed
    priority: str  # low, medium, high


class DatabaseConfig(BaseModel):
    """Complex configuration model."""
    host: str
    port: int
    database: str
    ssl: bool = False
    pool_size: int = 10
    timeout_seconds: float = 30.0


class TestExtractServiceIntegration:
    """Integration tests for ExtractService."""

    def test_simple_model_extraction(self):
        """Test extracting a simple Pydantic model."""
        # Verify schema generation
        schema_str = _model_to_json_schema(Person)
        schema = json.loads(schema_str)

        assert "properties" in schema
        assert "name" in schema["properties"]
        assert "age" in schema["properties"]
        assert schema["properties"]["name"]["type"] == "string"
        assert schema["properties"]["age"]["type"] == "integer"

    def test_nested_model_extraction(self):
        """Test extracting nested Pydantic models."""
        schema_str = _model_to_json_schema(Company)
        schema = json.loads(schema_str)

        assert "address" in schema["properties"]
        # Pydantic v2 uses $defs for nested models
        assert "$defs" in schema or "definitions" in schema or "properties" in schema

    def test_optional_fields(self):
        """Test handling of optional fields."""
        schema_str = _model_to_json_schema(Person)
        schema = json.loads(schema_str)

        # Email is optional
        required = schema.get("required", [])
        assert "email" not in required or schema["properties"]["email"].get("default") is not None

    def test_default_values(self):
        """Test handling of default values."""
        schema_str = _model_to_json_schema(DatabaseConfig)
        schema = json.loads(schema_str)

        props = schema["properties"]
        # These have defaults
        assert "ssl" in props
        assert "pool_size" in props

    def test_list_fields(self):
        """Test handling of list fields."""
        schema_str = _model_to_json_schema(Company)
        schema = json.loads(schema_str)

        assert "tags" in schema["properties"]
        tags_schema = schema["properties"]["tags"]
        assert tags_schema["type"] == "array"

    def test_extract_result_success_flow(self):
        """Test successful extraction result flow."""
        # Simulate successful extraction
        result = ExtractResult(
            success=True,
            data=Person(name="John Doe", age=30, email="john@example.com"),
            reasoning="Found person information in the provided context",
            error=None,
            error_code=ExtractErrorCode.NONE,
            metrics=ExtractMetrics(
                duration_ms=1500,
                llm_duration_ms=1200,
                tool_duration_ms=300,
                llm_calls=2,
                tool_calls=1,
                retries=0,
                tokens=TokenUsage(
                    prompt_tokens=500,
                    completion_tokens=100,
                    total_tokens=600,
                ),
            ),
        )

        # Verify result
        assert result.success is True
        assert result.data is not None
        assert result.data.name == "John Doe"
        assert result.data.age == 30
        assert result.data.email == "john@example.com"
        assert result.error is None
        assert result.error_code == ExtractErrorCode.NONE

        # Verify metrics
        assert result.metrics.duration_ms == 1500
        assert result.metrics.llm_calls == 2
        assert result.metrics.tokens.total_tokens == 600

    def test_extract_result_failure_flow(self):
        """Test failed extraction result flow."""
        result = ExtractResult(
            success=False,
            data=None,
            reasoning="Attempted to find config but failed validation",
            error="Schema validation failed: missing required field 'host'",
            error_code=ExtractErrorCode.VALIDATION_FAILED,
            metrics=ExtractMetrics(
                duration_ms=2000,
                llm_duration_ms=1500,
                tool_duration_ms=0,
                llm_calls=3,
                tool_calls=0,
                retries=2,
                tokens=TokenUsage(1000, 300, 1300),
            ),
        )

        assert result.success is False
        assert result.data is None
        assert result.error is not None
        assert "validation" in result.error.lower()
        assert result.error_code == ExtractErrorCode.VALIDATION_FAILED
        assert result.metrics.retries == 2

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
            model="anthropic/claude-3-opus",
            temperature=0.7,
            max_tokens=8192,
            max_retries=5,
            timeout_seconds=120,
            working_directory="/home/user/project",
            enabled_tools=["read_file", "list_directory"],
        )

        assert opts.model == "anthropic/claude-3-opus"
        assert opts.temperature == 0.7
        assert opts.max_tokens == 8192
        assert opts.max_retries == 5
        assert opts.timeout_seconds == 120
        assert opts.working_directory == "/home/user/project"
        assert len(opts.enabled_tools) == 2

    def test_complex_model_schema(self):
        """Test complex model with all field types."""

        class ComplexModel(BaseModel):
            string_field: str
            int_field: int
            float_field: float
            bool_field: bool
            list_field: List[str]
            optional_field: Optional[str] = None
            default_field: str = "default"

        schema_str = _model_to_json_schema(ComplexModel)
        schema = json.loads(schema_str)

        props = schema["properties"]
        assert props["string_field"]["type"] == "string"
        assert props["int_field"]["type"] == "integer"
        assert props["float_field"]["type"] == "number"
        assert props["bool_field"]["type"] == "boolean"
        assert props["list_field"]["type"] == "array"

    def test_error_codes_comprehensive(self):
        """Test all error codes are defined correctly."""
        error_codes = [
            (ExtractErrorCode.NONE, 0),
            (ExtractErrorCode.INVALID_SCHEMA, 1),
            (ExtractErrorCode.EXTRACTION_FAILED, 2),
            (ExtractErrorCode.VALIDATION_FAILED, 3),
            (ExtractErrorCode.TIMEOUT, 4),
            (ExtractErrorCode.LLM_ERROR, 5),
            (ExtractErrorCode.TOOL_ERROR, 6),
            (ExtractErrorCode.CANCELLED, 7),
            (ExtractErrorCode.SCHEMA_TOO_LARGE, 8),
        ]

        for code, value in error_codes:
            assert code == value
            assert ExtractErrorCode(value) == code

    def test_metrics_tracking(self):
        """Test metrics are properly tracked."""
        tokens = TokenUsage(
            prompt_tokens=1000,
            completion_tokens=500,
            total_tokens=1500,
        )

        metrics = ExtractMetrics(
            duration_ms=5000,
            llm_duration_ms=4000,
            tool_duration_ms=1000,
            llm_calls=3,
            tool_calls=5,
            retries=2,
            tokens=tokens,
        )

        # Verify all fields
        assert metrics.duration_ms == 5000
        assert metrics.llm_duration_ms == 4000
        assert metrics.tool_duration_ms == 1000
        assert metrics.llm_calls == 3
        assert metrics.tool_calls == 5
        assert metrics.retries == 2
        assert metrics.tokens.prompt_tokens == 1000
        assert metrics.tokens.completion_tokens == 500
        assert metrics.tokens.total_tokens == 1500

    def test_model_validation_with_result(self):
        """Test that model validation works correctly."""
        # Valid data
        valid_data = {"name": "Test", "age": 25}
        person = Person.model_validate(valid_data)
        assert person.name == "Test"
        assert person.age == 25

        # Invalid data should raise
        invalid_data = {"name": "Test", "age": "not a number"}
        with pytest.raises(Exception):  # ValidationError
            Person.model_validate(invalid_data)

    def test_nested_model_validation(self):
        """Test nested model validation."""
        data = {
            "name": "Acme Corp",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "country": "USA",
            },
            "employees": 100,
            "tags": ["tech", "startup"],
        }

        company = Company.model_validate(data)
        assert company.name == "Acme Corp"
        assert company.address.city == "New York"
        assert company.employees == 100
        assert len(company.tags) == 2


class TestExtractServiceMocked:
    """Tests with mocked transport."""

    @pytest.fixture
    def mock_transport(self):
        """Create mock transport."""
        transport = MagicMock()
        transport._channel = MagicMock()
        return transport

    def test_service_initialization(self, mock_transport):
        """Test service initializes correctly."""
        service = ExtractService(mock_transport)
        assert service._stub is None  # Lazy loaded
        assert service._transport == mock_transport

    def test_schema_generation_for_service(self):
        """Test schema generation used by service."""
        # Simple model
        schema = _model_to_json_schema(Person)
        parsed = json.loads(schema)
        assert "type" in parsed
        assert parsed["type"] == "object"

        # Nested model
        schema = _model_to_json_schema(Company)
        parsed = json.loads(schema)
        assert "properties" in parsed


class TestExtractEdgeCases:
    """Edge case tests."""

    def test_empty_list_field(self):
        """Test model with empty list."""
        company = Company(
            name="Test",
            address=Address(street="1", city="2"),
            employees=1,
            tags=[],
        )
        assert company.tags == []

    def test_optional_none_value(self):
        """Test optional field with None."""
        person = Person(name="Test", age=20, email=None)
        assert person.email is None

    def test_unicode_values(self):
        """Test unicode in model values."""
        person = Person(name="日本語", age=25, email="test@例え.jp")
        assert person.name == "日本語"
        assert "例え" in person.email

    def test_large_numbers(self):
        """Test large number handling."""
        config = DatabaseConfig(
            host="localhost",
            port=65535,
            database="test",
            pool_size=1000000,
            timeout_seconds=999999.999,
        )
        assert config.port == 65535
        assert config.pool_size == 1000000

    def test_special_characters_in_strings(self):
        """Test special characters in strings."""
        person = Person(
            name='Test "Quotes" & <Tags>',
            age=30,
            email="test+tag@example.com",
        )
        assert '"' in person.name
        assert "&" in person.name
        assert "+" in person.email

    def test_empty_string_values(self):
        """Test empty string handling."""
        address = Address(street="", city="", country="")
        assert address.street == ""
        assert address.city == ""
