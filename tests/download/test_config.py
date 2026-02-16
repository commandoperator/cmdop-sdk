"""Tests for download config."""

import pytest

from cmdop.services.download._config import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_DOWNLOAD_TIMEOUT,
    DEFAULT_POLL_INTERVAL,
    LARGE_FILE_THRESHOLD,
    MAX_PARALLEL_PARTS,
    SPLIT_PART_SIZE_MB,
)


class TestDownloadConfig:
    """Tests for download configuration constants."""

    def test_chunk_size(self):
        assert DEFAULT_CHUNK_SIZE == 1024 * 1024  # 1MB

    def test_download_timeout(self):
        assert DEFAULT_DOWNLOAD_TIMEOUT == 600  # 10 minutes

    def test_poll_interval(self):
        assert DEFAULT_POLL_INTERVAL == 1.0  # 1 second

    def test_large_file_threshold(self):
        assert LARGE_FILE_THRESHOLD == 10 * 1024 * 1024  # 10MB

    def test_split_part_size(self):
        assert SPLIT_PART_SIZE_MB == 5  # 5MB parts

    def test_max_parallel_parts(self):
        assert MAX_PARALLEL_PARTS == 4  # 4 parallel downloads
