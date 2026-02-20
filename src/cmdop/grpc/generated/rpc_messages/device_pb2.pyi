from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RegisterDeviceTokenRequest(_message.Message):
    __slots__ = ("device_id", "token", "platform", "machine_id", "apns_environment", "app_version")
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    APNS_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    APP_VERSION_FIELD_NUMBER: _ClassVar[int]
    device_id: str
    token: str
    platform: str
    machine_id: str
    apns_environment: str
    app_version: str
    def __init__(self, device_id: _Optional[str] = ..., token: _Optional[str] = ..., platform: _Optional[str] = ..., machine_id: _Optional[str] = ..., apns_environment: _Optional[str] = ..., app_version: _Optional[str] = ...) -> None: ...

class RegisterDeviceTokenResponse(_message.Message):
    __slots__ = ("success", "error", "token_id")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TOKEN_ID_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    token_id: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., token_id: _Optional[str] = ...) -> None: ...

class UnregisterDeviceTokenRequest(_message.Message):
    __slots__ = ("device_id", "token")
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    device_id: str
    token: str
    def __init__(self, device_id: _Optional[str] = ..., token: _Optional[str] = ...) -> None: ...

class UnregisterDeviceTokenResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...
