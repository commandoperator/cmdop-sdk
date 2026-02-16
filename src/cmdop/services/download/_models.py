"""
Models for download service.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class TransferStats(BaseModel):
    """Statistics from a transfer operation."""

    bytes_transferred: int = 0
    chunks_count: int = 0
    retries_count: int = 0


class DownloadMetrics(BaseModel):
    """Metrics for a download operation."""

    # Timing (seconds)
    total_time: float = 0.0
    curl_time: float = 0.0
    transfer_time: float = 0.0

    # Sizes (bytes)
    remote_size: int = 0
    transferred_size: int = 0
    local_size: int = 0

    # Transfer details
    chunks_count: int = 0
    parts_count: int = 0
    retries_count: int = 0

    @property
    def transfer_speed_mbps(self) -> float:
        """Transfer speed in MB/s."""
        if self.transfer_time <= 0:
            return 0.0
        return (self.transferred_size / 1024 / 1024) / self.transfer_time

    @property
    def total_speed_mbps(self) -> float:
        """Total speed including curl download in MB/s."""
        if self.total_time <= 0:
            return 0.0
        return (self.transferred_size / 1024 / 1024) / self.total_time

    def summary(self) -> str:
        """Human-readable summary."""
        size_mb = self.transferred_size / 1024 / 1024
        lines = [
            f"Size: {size_mb:.1f} MB ({self.transferred_size:,} bytes)",
            f"Total: {self.total_time:.1f}s @ {self.total_speed_mbps:.1f} MB/s",
        ]
        if self.curl_time > 0:
            lines.append(f"  └─ Curl: {self.curl_time:.1f}s")
        if self.transfer_time > 0:
            lines.append(
                f"  └─ Transfer: {self.transfer_time:.1f}s @ {self.transfer_speed_mbps:.1f} MB/s"
            )
        if self.parts_count > 1:
            lines.append(f"Parts: {self.parts_count}")
        if self.chunks_count > 0:
            lines.append(f"Chunks: {self.chunks_count}")
        if self.retries_count > 0:
            lines.append(f"Retries: {self.retries_count}")
        return "\n".join(lines)


class DownloadResult(BaseModel):
    """Result of a download operation."""

    model_config = {"arbitrary_types_allowed": True}

    success: bool
    local_path: Path | None = None
    size: int = 0
    error: str | None = None
    metrics: DownloadMetrics = Field(default_factory=DownloadMetrics)

    def __repr__(self) -> str:
        if self.success:
            m = self.metrics
            size_mb = self.size / 1024 / 1024
            return (
                f"DownloadResult(ok, {size_mb:.1f}MB, "
                f"{m.total_time:.1f}s, {m.total_speed_mbps:.1f}MB/s)"
            )
        return f"DownloadResult(failed: {self.error})"

    def __str__(self) -> str:
        if self.success:
            return self.metrics.summary()
        return f"Failed: {self.error}"
