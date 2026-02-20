import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StreamFileType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STREAM_FILE_TYPE_UNSPECIFIED: _ClassVar[StreamFileType]
    STREAM_FILE: _ClassVar[StreamFileType]
    STREAM_DIRECTORY: _ClassVar[StreamFileType]
    STREAM_SYMLINK: _ClassVar[StreamFileType]

class FileIconType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ICON_UNSPECIFIED: _ClassVar[FileIconType]
    ICON_FILE: _ClassVar[FileIconType]
    ICON_CODE: _ClassVar[FileIconType]
    ICON_TEXT: _ClassVar[FileIconType]
    ICON_IMAGE: _ClassVar[FileIconType]
    ICON_VIDEO: _ClassVar[FileIconType]
    ICON_AUDIO: _ClassVar[FileIconType]
    ICON_ARCHIVE: _ClassVar[FileIconType]
    ICON_DATA: _ClassVar[FileIconType]
    ICON_PDF: _ClassVar[FileIconType]
    ICON_FOLDER: _ClassVar[FileIconType]
    ICON_FOLDER_HOME: _ClassVar[FileIconType]
    ICON_FOLDER_DESKTOP: _ClassVar[FileIconType]
    ICON_FOLDER_DOCUMENTS: _ClassVar[FileIconType]
    ICON_FOLDER_DOWNLOADS: _ClassVar[FileIconType]
    ICON_FOLDER_PICTURES: _ClassVar[FileIconType]
    ICON_FOLDER_MUSIC: _ClassVar[FileIconType]
    ICON_FOLDER_VIDEOS: _ClassVar[FileIconType]
    ICON_FOLDER_APPLICATIONS: _ClassVar[FileIconType]
    ICON_FOLDER_LIBRARY: _ClassVar[FileIconType]
    ICON_FOLDER_SYSTEM: _ClassVar[FileIconType]
    ICON_FOLDER_DRIVE: _ClassVar[FileIconType]
    ICON_FOLDER_CLOUD: _ClassVar[FileIconType]
    ICON_FOLDER_TRASH: _ClassVar[FileIconType]
    ICON_FOLDER_HIDDEN: _ClassVar[FileIconType]
    ICON_FOLDER_CODE: _ClassVar[FileIconType]
    ICON_FOLDER_SERVER: _ClassVar[FileIconType]
    ICON_FOLDER_DATABASE: _ClassVar[FileIconType]
    ICON_FOLDER_ARCHIVE: _ClassVar[FileIconType]

class ViewerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VIEWER_UNKNOWN: _ClassVar[ViewerType]
    VIEWER_CODE: _ClassVar[ViewerType]
    VIEWER_TEXT: _ClassVar[ViewerType]
    VIEWER_IMAGE: _ClassVar[ViewerType]
    VIEWER_VIDEO: _ClassVar[ViewerType]
    VIEWER_AUDIO: _ClassVar[ViewerType]
    VIEWER_PDF: _ClassVar[ViewerType]
    VIEWER_MARKDOWN: _ClassVar[ViewerType]
    VIEWER_JSON: _ClassVar[ViewerType]
    VIEWER_YAML: _ClassVar[ViewerType]
    VIEWER_XML: _ClassVar[ViewerType]
    VIEWER_ARCHIVE: _ClassVar[ViewerType]
    VIEWER_HEX: _ClassVar[ViewerType]

class LoadMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOAD_UNSPECIFIED: _ClassVar[LoadMethod]
    LOAD_RPC: _ClassVar[LoadMethod]
    LOAD_HTTP_STREAM: _ClassVar[LoadMethod]
    LOAD_SKIP: _ClassVar[LoadMethod]
    LOAD_HTTP_TRANSCODE: _ClassVar[LoadMethod]
    LOAD_HTTP_HLS: _ClassVar[LoadMethod]

class FileVisibilityMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VISIBILITY_AUTO: _ClassVar[FileVisibilityMode]
    VISIBILITY_USER: _ClassVar[FileVisibilityMode]
    VISIBILITY_ADMIN: _ClassVar[FileVisibilityMode]
    VISIBILITY_ALL: _ClassVar[FileVisibilityMode]
STREAM_FILE_TYPE_UNSPECIFIED: StreamFileType
STREAM_FILE: StreamFileType
STREAM_DIRECTORY: StreamFileType
STREAM_SYMLINK: StreamFileType
ICON_UNSPECIFIED: FileIconType
ICON_FILE: FileIconType
ICON_CODE: FileIconType
ICON_TEXT: FileIconType
ICON_IMAGE: FileIconType
ICON_VIDEO: FileIconType
ICON_AUDIO: FileIconType
ICON_ARCHIVE: FileIconType
ICON_DATA: FileIconType
ICON_PDF: FileIconType
ICON_FOLDER: FileIconType
ICON_FOLDER_HOME: FileIconType
ICON_FOLDER_DESKTOP: FileIconType
ICON_FOLDER_DOCUMENTS: FileIconType
ICON_FOLDER_DOWNLOADS: FileIconType
ICON_FOLDER_PICTURES: FileIconType
ICON_FOLDER_MUSIC: FileIconType
ICON_FOLDER_VIDEOS: FileIconType
ICON_FOLDER_APPLICATIONS: FileIconType
ICON_FOLDER_LIBRARY: FileIconType
ICON_FOLDER_SYSTEM: FileIconType
ICON_FOLDER_DRIVE: FileIconType
ICON_FOLDER_CLOUD: FileIconType
ICON_FOLDER_TRASH: FileIconType
ICON_FOLDER_HIDDEN: FileIconType
ICON_FOLDER_CODE: FileIconType
ICON_FOLDER_SERVER: FileIconType
ICON_FOLDER_DATABASE: FileIconType
ICON_FOLDER_ARCHIVE: FileIconType
VIEWER_UNKNOWN: ViewerType
VIEWER_CODE: ViewerType
VIEWER_TEXT: ViewerType
VIEWER_IMAGE: ViewerType
VIEWER_VIDEO: ViewerType
VIEWER_AUDIO: ViewerType
VIEWER_PDF: ViewerType
VIEWER_MARKDOWN: ViewerType
VIEWER_JSON: ViewerType
VIEWER_YAML: ViewerType
VIEWER_XML: ViewerType
VIEWER_ARCHIVE: ViewerType
VIEWER_HEX: ViewerType
LOAD_UNSPECIFIED: LoadMethod
LOAD_RPC: LoadMethod
LOAD_HTTP_STREAM: LoadMethod
LOAD_SKIP: LoadMethod
LOAD_HTTP_TRANSCODE: LoadMethod
LOAD_HTTP_HLS: LoadMethod
VISIBILITY_AUTO: FileVisibilityMode
VISIBILITY_USER: FileVisibilityMode
VISIBILITY_ADMIN: FileVisibilityMode
VISIBILITY_ALL: FileVisibilityMode

class MediaMetadata(_message.Message):
    __slots__ = ("duration_seconds", "bitrate_kbps", "sample_rate_hz", "audio_channels", "audio_codec", "width", "height", "frame_rate", "video_codec", "title", "artist", "album", "album_artist", "genre", "year", "track_number", "disc_number", "comment", "composer", "cover_art", "cover_art_mime_type", "container_format", "has_video", "has_audio", "needs_transcode", "transcode_reason")
    DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    BITRATE_KBPS_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_HZ_FIELD_NUMBER: _ClassVar[int]
    AUDIO_CHANNELS_FIELD_NUMBER: _ClassVar[int]
    AUDIO_CODEC_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FRAME_RATE_FIELD_NUMBER: _ClassVar[int]
    VIDEO_CODEC_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    ARTIST_FIELD_NUMBER: _ClassVar[int]
    ALBUM_FIELD_NUMBER: _ClassVar[int]
    ALBUM_ARTIST_FIELD_NUMBER: _ClassVar[int]
    GENRE_FIELD_NUMBER: _ClassVar[int]
    YEAR_FIELD_NUMBER: _ClassVar[int]
    TRACK_NUMBER_FIELD_NUMBER: _ClassVar[int]
    DISC_NUMBER_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    COMPOSER_FIELD_NUMBER: _ClassVar[int]
    COVER_ART_FIELD_NUMBER: _ClassVar[int]
    COVER_ART_MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_FORMAT_FIELD_NUMBER: _ClassVar[int]
    HAS_VIDEO_FIELD_NUMBER: _ClassVar[int]
    HAS_AUDIO_FIELD_NUMBER: _ClassVar[int]
    NEEDS_TRANSCODE_FIELD_NUMBER: _ClassVar[int]
    TRANSCODE_REASON_FIELD_NUMBER: _ClassVar[int]
    duration_seconds: int
    bitrate_kbps: int
    sample_rate_hz: int
    audio_channels: int
    audio_codec: str
    width: int
    height: int
    frame_rate: float
    video_codec: str
    title: str
    artist: str
    album: str
    album_artist: str
    genre: str
    year: int
    track_number: int
    disc_number: int
    comment: str
    composer: str
    cover_art: bytes
    cover_art_mime_type: str
    container_format: str
    has_video: bool
    has_audio: bool
    needs_transcode: bool
    transcode_reason: str
    def __init__(self, duration_seconds: _Optional[int] = ..., bitrate_kbps: _Optional[int] = ..., sample_rate_hz: _Optional[int] = ..., audio_channels: _Optional[int] = ..., audio_codec: _Optional[str] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., frame_rate: _Optional[float] = ..., video_codec: _Optional[str] = ..., title: _Optional[str] = ..., artist: _Optional[str] = ..., album: _Optional[str] = ..., album_artist: _Optional[str] = ..., genre: _Optional[str] = ..., year: _Optional[int] = ..., track_number: _Optional[int] = ..., disc_number: _Optional[int] = ..., comment: _Optional[str] = ..., composer: _Optional[str] = ..., cover_art: _Optional[bytes] = ..., cover_art_mime_type: _Optional[str] = ..., container_format: _Optional[str] = ..., has_video: bool = ..., has_audio: bool = ..., needs_transcode: bool = ..., transcode_reason: _Optional[str] = ...) -> None: ...

class StreamFileEntry(_message.Message):
    __slots__ = ("name", "path", "type", "size", "permissions", "owner", "modified_at", "is_hidden", "is_readable", "is_writable", "mime_type", "symlink_target", "icon_type", "is_system", "viewer_type", "load_method", "media_metadata")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_AT_FIELD_NUMBER: _ClassVar[int]
    IS_HIDDEN_FIELD_NUMBER: _ClassVar[int]
    IS_READABLE_FIELD_NUMBER: _ClassVar[int]
    IS_WRITABLE_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    SYMLINK_TARGET_FIELD_NUMBER: _ClassVar[int]
    ICON_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    VIEWER_TYPE_FIELD_NUMBER: _ClassVar[int]
    LOAD_METHOD_FIELD_NUMBER: _ClassVar[int]
    MEDIA_METADATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    path: str
    type: StreamFileType
    size: int
    permissions: str
    owner: str
    modified_at: _timestamp_pb2.Timestamp
    is_hidden: bool
    is_readable: bool
    is_writable: bool
    mime_type: str
    symlink_target: str
    icon_type: FileIconType
    is_system: bool
    viewer_type: ViewerType
    load_method: LoadMethod
    media_metadata: MediaMetadata
    def __init__(self, name: _Optional[str] = ..., path: _Optional[str] = ..., type: _Optional[_Union[StreamFileType, str]] = ..., size: _Optional[int] = ..., permissions: _Optional[str] = ..., owner: _Optional[str] = ..., modified_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., is_hidden: bool = ..., is_readable: bool = ..., is_writable: bool = ..., mime_type: _Optional[str] = ..., symlink_target: _Optional[str] = ..., icon_type: _Optional[_Union[FileIconType, str]] = ..., is_system: bool = ..., viewer_type: _Optional[_Union[ViewerType, str]] = ..., load_method: _Optional[_Union[LoadMethod, str]] = ..., media_metadata: _Optional[_Union[MediaMetadata, _Mapping]] = ...) -> None: ...
