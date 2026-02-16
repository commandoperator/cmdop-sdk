"""
CMDOP SDK Generated Protobuf/gRPC Types.

Generated using grpcio for full metadata/timeout support.

Usage:
    from cmdop._generated import (
        # gRPC stubs
        TerminalStreamingServiceStub,
        FileServiceStub,
    )

    from cmdop._generated.rpc_messages.session_pb2 import (
        CreateSessionRequest,
        CreateSessionResponse,
    )
"""

# Re-export main service stubs
from .service_pb2_grpc import (
    TerminalStreamingServiceStub,
)

__all__ = [
    "TerminalStreamingServiceStub",
]
