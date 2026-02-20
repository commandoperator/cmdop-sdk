"""Synchronous agent service.

Auto-generated from AsyncAgentService using sync wrapper.
"""

from cmdop.services.agent.async_ import AsyncAgentService
from cmdop.services._sync_wrapper import create_sync_service

# Generate sync service from async
AgentService = create_sync_service(AsyncAgentService)

__all__ = ["AgentService"]
