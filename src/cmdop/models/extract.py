"""
Extract models for CMDOP SDK.

Provides data classes for structured data extraction results.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any, TypeVar, Generic

T = TypeVar("T")


class ExtractErrorCode(IntEnum):
    """Error codes for extraction operations."""

    NONE = 0
    INVALID_SCHEMA = 1
    EXTRACTION_FAILED = 2
    VALIDATION_FAILED = 3
    TIMEOUT = 4
    LLM_ERROR = 5
    TOOL_ERROR = 6
    CANCELLED = 7
    SCHEMA_TOO_LARGE = 8


@dataclass
class TokenUsage:
    """Token usage statistics."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class ExtractMetrics:
    """Extraction execution metrics."""

    duration_ms: int
    llm_duration_ms: int
    tool_duration_ms: int
    llm_calls: int
    tool_calls: int
    retries: int
    tokens: TokenUsage


@dataclass
class ExtractResult(Generic[T]):
    """
    Result of a structured extraction operation.

    Generic type T represents the extracted data model type.
    """

    success: bool
    """Whether extraction succeeded."""

    data: T | None
    """Extracted data (if success=True)."""

    reasoning: str
    """Agent's explanation of how data was extracted."""

    error: str | None
    """Error message (if success=False)."""

    error_code: ExtractErrorCode
    """Error code for programmatic handling."""

    metrics: ExtractMetrics
    """Execution statistics."""


@dataclass
class ExtractOptions:
    """Options for extraction requests."""

    model: str | None = None
    """LLM model to use (None = default)."""

    temperature: float = 0.0
    """Temperature for LLM (0.0 = deterministic)."""

    max_tokens: int = 4096
    """Max tokens for LLM response."""

    max_retries: int = 3
    """Max retries on validation failure."""

    timeout_seconds: int = 60
    """Total timeout for extraction."""

    working_directory: str | None = None
    """Working directory for tool execution."""

    enabled_tools: list[str] | None = None
    """List of enabled tools (None = all)."""
