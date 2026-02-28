"""
Skill models for CMDOP SDK.

Provides models for skill listing, inspection, and execution.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from cmdop.models.agent import AgentToolResult, AgentUsage

T = TypeVar("T")


class SkillInfo(BaseModel):
    """Information about an available skill."""

    model_config = ConfigDict(extra="forbid")

    name: str
    """Skill name (e.g., 'code-review')."""

    description: str = ""
    """Human-readable description."""

    author: str = ""
    """Skill author."""

    version: str = ""
    """Skill version."""

    model: str = ""
    """Default LLM model for this skill."""

    origin: str = ""
    """Origin: 'builtin', 'global', or 'workspace'."""

    required_bins: list[str] = Field(default_factory=list)
    """Required binaries on the machine."""

    required_env: list[str] = Field(default_factory=list)
    """Required environment variables."""


class SkillDetail(BaseModel):
    """Detailed skill information from SkillShow."""

    model_config = ConfigDict(extra="forbid")

    found: bool
    """Whether the skill was found."""

    info: SkillInfo | None = None
    """Skill metadata (if found)."""

    content: str = ""
    """System prompt markdown content."""

    source: str = ""
    """File path on the machine."""

    error: str = ""
    """Error message if not found."""


class SkillRunOptions(BaseModel):
    """Options for skill execution."""

    model_config = ConfigDict(extra="forbid")

    model: str | None = None
    """LLM model to use (e.g., 'openai/gpt-4o')."""

    timeout_seconds: int = Field(default=300, ge=10, le=600)
    """Timeout in seconds."""

    def to_options_map(self) -> dict[str, str]:
        """Convert to proto options map."""
        opts: dict[str, str] = {}
        if self.model:
            opts["model"] = self.model
        opts["timeout_seconds"] = str(self.timeout_seconds)
        return opts


class SkillRunResult(BaseModel, Generic[T]):
    """Result of skill execution.

    When using structured output (output_model parameter), the result
    will have the `data` field populated with the parsed Pydantic model.

    Example:
        >>> class Review(BaseModel):
        ...     score: int
        ...     summary: str
        >>>
        >>> result = await client.skills.run(
        ...     "code-review", "Review this PR",
        ...     output_model=Review,
        ... )
        >>> print(result.data.score)
    """

    model_config = ConfigDict(extra="forbid")

    request_id: str
    """Request ID for correlation."""

    success: bool
    """Whether the skill execution succeeded."""

    text: str = ""
    """Skill's text response."""

    error: str = ""
    """Error message if failed."""

    tool_results: list[AgentToolResult] = Field(default_factory=list)
    """Results from tool executions."""

    usage: AgentUsage = Field(default_factory=AgentUsage)
    """Token usage statistics."""

    duration_ms: int = Field(default=0, ge=0)
    """Total execution duration in milliseconds."""

    data: T | None = None
    """Structured output data (if output_model was provided)."""

    output_json: str = ""
    """Raw JSON string of structured output."""

    @property
    def duration_seconds(self) -> float:
        """Duration in seconds."""
        return self.duration_ms / 1000.0
