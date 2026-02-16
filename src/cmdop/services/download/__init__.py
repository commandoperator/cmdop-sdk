"""
Download service for CMDOP SDK.

Provides file download from URLs on remote server with chunked transfer.
Uses terminal for curl execution and files API for chunked reading.

Handles cloud relay limits (~30MB per session) by:
- Splitting large files on remote server
- Downloading each part with fresh connection
- Automatic retry with exponential backoff
"""

"""
Download service for CMDOP SDK.

Provides file download from URLs on remote server with chunked transfer.

Features:
- Chunked file transfer via files.read(offset, length)
- Cloud relay limits handling (split/reconnect for files >10MB)
- Automatic retry with exponential backoff
- Detailed metrics (timing, speed, chunks, retries)
"""

from cmdop.services.download._aio import AsyncDownloadService
from cmdop.services.download._models import DownloadMetrics, DownloadResult, TransferStats
from cmdop.services.download._sync import DownloadService

__all__ = [
    "DownloadMetrics",
    "DownloadResult",
    "TransferStats",
    "DownloadService",
    "AsyncDownloadService",
]
