"""
Configuration constants for download service.
"""

# Chunk size for file transfer
DEFAULT_CHUNK_SIZE = 1024 * 1024  # 1MB

# Timeout for download completion
DEFAULT_DOWNLOAD_TIMEOUT = 600  # 10 minutes

# Poll interval for file size checks
DEFAULT_POLL_INTERVAL = 1.0  # seconds

# Files larger than this threshold use split transfer
LARGE_FILE_THRESHOLD = 10 * 1024 * 1024  # 10MB

# Part size for splitting large files (to stay under relay limits)
SPLIT_PART_SIZE_MB = 5  # 5MB

# Max parallel downloads for split parts
MAX_PARALLEL_PARTS = 4
