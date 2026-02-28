"""Synchronous skills service.

Auto-generated from AsyncSkillsService using sync wrapper.
"""

from cmdop.services.skills.async_ import AsyncSkillsService
from cmdop.services._sync_wrapper import create_sync_service

# Generate sync service from async
SkillsService = create_sync_service(AsyncSkillsService)

__all__ = ["SkillsService"]
