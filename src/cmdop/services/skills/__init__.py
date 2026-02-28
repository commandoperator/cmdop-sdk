"""Skills service for CMDOP SDK.

Provides skill listing, inspection, and execution via gRPC.
"""

from cmdop.services.skills.sync import SkillsService
from cmdop.services.skills.async_ import AsyncSkillsService
from cmdop.services.skills.base import (
    parse_skill_info,
    parse_skill_detail,
    parse_skill_run_result,
)

__all__ = [
    "SkillsService",
    "AsyncSkillsService",
    "parse_skill_info",
    "parse_skill_detail",
    "parse_skill_run_result",
]
