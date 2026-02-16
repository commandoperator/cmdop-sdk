"""Tests for download models."""

from pathlib import Path

import pytest

from cmdop.services.download import DownloadMetrics, DownloadResult, TransferStats


class TestTransferStats:
    """Tests for TransferStats model."""

    def test_default_values(self):
        stats = TransferStats()
        assert stats.bytes_transferred == 0
        assert stats.chunks_count == 0
        assert stats.retries_count == 0

    def test_with_values(self):
        stats = TransferStats(
            bytes_transferred=1024 * 1024,
            chunks_count=10,
            retries_count=2,
        )
        assert stats.bytes_transferred == 1024 * 1024
        assert stats.chunks_count == 10
        assert stats.retries_count == 2


class TestDownloadMetrics:
    """Tests for DownloadMetrics model."""

    def test_default_values(self):
        m = DownloadMetrics()
        assert m.total_time == 0.0
        assert m.curl_time == 0.0
        assert m.transfer_time == 0.0
        assert m.remote_size == 0
        assert m.transferred_size == 0
        assert m.local_size == 0
        assert m.chunks_count == 0
        assert m.parts_count == 0
        assert m.retries_count == 0

    def test_transfer_speed_zero_time(self):
        m = DownloadMetrics(transferred_size=1024 * 1024)
        assert m.transfer_speed_mbps == 0.0

    def test_transfer_speed_calculation(self):
        m = DownloadMetrics(
            transferred_size=10 * 1024 * 1024,  # 10 MB
            transfer_time=10.0,  # 10 seconds
        )
        assert m.transfer_speed_mbps == 1.0

    def test_total_speed_zero_time(self):
        m = DownloadMetrics(transferred_size=1024 * 1024)
        assert m.total_speed_mbps == 0.0

    def test_total_speed_calculation(self):
        m = DownloadMetrics(
            transferred_size=50 * 1024 * 1024,  # 50 MB
            total_time=100.0,  # 100 seconds
        )
        assert m.total_speed_mbps == 0.5

    def test_summary_basic(self):
        m = DownloadMetrics(
            total_time=10.0,
            transferred_size=10 * 1024 * 1024,
        )
        summary = m.summary()
        assert "10.0 MB" in summary
        assert "10.0s" in summary

    def test_summary_with_curl_time(self):
        m = DownloadMetrics(
            total_time=15.0,
            curl_time=5.0,
            transfer_time=10.0,
            transferred_size=10 * 1024 * 1024,
        )
        summary = m.summary()
        assert "Curl: 5.0s" in summary
        assert "Transfer: 10.0s" in summary

    def test_summary_with_parts(self):
        m = DownloadMetrics(
            total_time=100.0,
            transferred_size=50 * 1024 * 1024,
            parts_count=10,
            chunks_count=50,
        )
        summary = m.summary()
        assert "Parts: 10" in summary
        assert "Chunks: 50" in summary

    def test_summary_with_retries(self):
        m = DownloadMetrics(
            total_time=10.0,
            transferred_size=1024 * 1024,
            retries_count=3,
        )
        summary = m.summary()
        assert "Retries: 3" in summary

    def test_summary_no_retries_when_zero(self):
        m = DownloadMetrics(
            total_time=10.0,
            transferred_size=1024 * 1024,
            retries_count=0,
        )
        summary = m.summary()
        assert "Retries" not in summary


class TestDownloadResult:
    """Tests for DownloadResult model."""

    def test_success_result(self):
        r = DownloadResult(
            success=True,
            local_path=Path("/tmp/file.zip"),
            size=1024 * 1024,
        )
        assert r.success is True
        assert r.local_path == Path("/tmp/file.zip")
        assert r.size == 1024 * 1024
        assert r.error is None
        assert isinstance(r.metrics, DownloadMetrics)

    def test_failed_result(self):
        r = DownloadResult(
            success=False,
            error="Connection timeout",
        )
        assert r.success is False
        assert r.error == "Connection timeout"
        assert r.local_path is None
        assert r.size == 0

    def test_repr_success(self):
        r = DownloadResult(
            success=True,
            size=10 * 1024 * 1024,
            metrics=DownloadMetrics(
                total_time=10.0,
                transferred_size=10 * 1024 * 1024,
            ),
        )
        repr_str = repr(r)
        assert "ok" in repr_str
        assert "10.0MB" in repr_str
        assert "10.0s" in repr_str

    def test_repr_failed(self):
        r = DownloadResult(success=False, error="Network error")
        repr_str = repr(r)
        assert "failed" in repr_str
        assert "Network error" in repr_str

    def test_str_success(self):
        r = DownloadResult(
            success=True,
            size=10 * 1024 * 1024,
            metrics=DownloadMetrics(
                total_time=10.0,
                curl_time=2.0,
                transfer_time=8.0,
                transferred_size=10 * 1024 * 1024,
            ),
        )
        str_output = str(r)
        assert "10.0 MB" in str_output
        assert "Curl:" in str_output
        assert "Transfer:" in str_output

    def test_str_failed(self):
        r = DownloadResult(success=False, error="File not found")
        str_output = str(r)
        assert "Failed" in str_output
        assert "File not found" in str_output

    def test_with_custom_metrics(self):
        m = DownloadMetrics(
            total_time=245.3,
            curl_time=12.1,
            transfer_time=233.2,
            parts_count=28,
            chunks_count=140,
        )
        r = DownloadResult(success=True, size=145_981_234, metrics=m)
        assert r.metrics.parts_count == 28
        assert r.metrics.chunks_count == 140
