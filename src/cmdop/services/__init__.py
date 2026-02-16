"""
CMDOP Service Layer.

Services provide domain-specific operations on top of gRPC stubs.
Each service wraps a specific domain (terminal, files, extract, etc.) and
converts between Pydantic models and protobuf messages.
"""

from cmdop.services.agent import AgentService, AsyncAgentService
from cmdop.services.base import BaseService
from cmdop.services.browser import AsyncBrowserService, BrowserService
from cmdop.services.download import AsyncDownloadService, DownloadService
from cmdop.services.extract import AsyncExtractService, ExtractService
from cmdop.services.files import AsyncFilesService, FilesService
from cmdop.services.terminal import AsyncTerminalService, TerminalService

__all__ = [
    "BaseService",
    "TerminalService",
    "AsyncTerminalService",
    "FilesService",
    "AsyncFilesService",
    "ExtractService",
    "AsyncExtractService",
    "AgentService",
    "AsyncAgentService",
    "BrowserService",
    "AsyncBrowserService",
    "DownloadService",
    "AsyncDownloadService",
]
