"""
File operation models for CMDOP SDK.

Models for file listing, reading, writing, and metadata.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class FileType(str, Enum):
    """File system entry type."""

    FILE = "file"
    DIRECTORY = "directory"
    SYMLINK = "symlink"
    UNKNOWN = "unknown"


class FileEntry(BaseModel):
    """File system entry in directory listing."""

    model_config = ConfigDict(extra="forbid")

    name: str
    """File or directory name."""

    path: str
    """Full absolute path."""

    type: FileType
    """Entry type."""

    size: int = 0
    """Size in bytes (0 for directories)."""

    modified_at: datetime | None = None
    """Last modification time."""

    is_hidden: bool = False
    """Whether file is hidden (starts with dot)."""

    permissions: str | None = None
    """Unix permission string (e.g., 'rwxr-xr-x')."""


class FileInfo(BaseModel):
    """Detailed file information."""

    model_config = ConfigDict(extra="forbid")

    path: str
    """Full absolute path."""

    type: FileType
    """Entry type."""

    size: int
    """Size in bytes."""

    created_at: datetime | None = None
    """Creation time."""

    modified_at: datetime | None = None
    """Last modification time."""

    accessed_at: datetime | None = None
    """Last access time."""

    permissions: str | None = None
    """Unix permission string."""

    owner: str | None = None
    """Owner username."""

    group: str | None = None
    """Group name."""

    is_readable: bool = True
    """Whether file is readable."""

    is_writable: bool = True
    """Whether file is writable."""

    is_executable: bool = False
    """Whether file is executable."""

    mime_type: str | None = None
    """MIME type if detected."""


class ListDirectoryRequest(BaseModel):
    """Request to list directory contents."""

    model_config = ConfigDict(extra="forbid")

    path: str
    """Directory path to list."""

    include_hidden: bool = False
    """Include hidden files (starting with dot)."""

    page_size: Annotated[int, Field(ge=1, le=1000)] = 100
    """Number of entries per page."""

    page_token: str | None = None
    """Pagination token."""


class ListDirectoryResponse(BaseModel):
    """Directory listing response."""

    model_config = ConfigDict(extra="forbid")

    path: str
    """Listed directory path."""

    entries: list[FileEntry]
    """Directory entries."""

    next_page_token: str | None = None
    """Token for next page (if more entries)."""

    total_count: int | None = None
    """Total entry count (if known)."""


class ReadFileRequest(BaseModel):
    """Request to read file contents."""

    model_config = ConfigDict(extra="forbid")

    path: str
    """File path to read."""

    offset: Annotated[int, Field(ge=0)] = 0
    """Byte offset to start reading from."""

    limit: Annotated[int, Field(ge=0)] = 0
    """Maximum bytes to read. 0 = entire file."""


class WriteFileRequest(BaseModel):
    """Request to write file contents."""

    model_config = ConfigDict(extra="forbid")

    path: str
    """File path to write."""

    content: bytes
    """Content to write."""

    create_parents: bool = False
    """Create parent directories if needed."""

    overwrite: bool = True
    """Overwrite existing file."""

    permissions: str | None = None
    """Unix permissions to set (e.g., '644')."""
