"""
Extract service for CMDOP SDK.

Provides structured data extraction using LLM with JSON Schema validation.
Supports both sync and async patterns with Pydantic model support.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, TypeVar, Type, get_type_hints

from cmdop.models.extract import (
    ExtractErrorCode,
    ExtractMetrics,
    ExtractOptions,
    ExtractResult,
    TokenUsage,
)
from cmdop.services.base import BaseService

if TYPE_CHECKING:
    from pydantic import BaseModel

    from cmdop.transport.base import BaseTransport

T = TypeVar("T", bound="BaseModel")


def _model_to_json_schema(model_class: Type[T]) -> str:
    """Convert Pydantic model to JSON Schema string."""
    try:
        schema = model_class.model_json_schema()
        return json.dumps(schema)
    except AttributeError:
        # Pydantic v1 fallback
        schema = model_class.schema()
        return json.dumps(schema)


def _parse_metrics(pb_metrics: Any) -> ExtractMetrics:
    """Convert protobuf metrics to dataclass."""
    tokens = TokenUsage(
        prompt_tokens=pb_metrics.tokens.prompt_tokens if pb_metrics.tokens else 0,
        completion_tokens=pb_metrics.tokens.completion_tokens if pb_metrics.tokens else 0,
        total_tokens=pb_metrics.tokens.total_tokens if pb_metrics.tokens else 0,
    )
    return ExtractMetrics(
        duration_ms=pb_metrics.duration_ms,
        llm_duration_ms=pb_metrics.llm_duration_ms,
        tool_duration_ms=pb_metrics.tool_duration_ms,
        llm_calls=pb_metrics.llm_calls,
        tool_calls=pb_metrics.tool_calls,
        retries=pb_metrics.retries,
        tokens=tokens,
    )


def _parse_error_code(code: int) -> ExtractErrorCode:
    """Convert protobuf error code to enum."""
    try:
        return ExtractErrorCode(code)
    except ValueError:
        return ExtractErrorCode.EXTRACTION_FAILED


class ExtractService(BaseService):
    """
    Synchronous extract service.

    Provides structured data extraction with Pydantic model support.

    Example:
        >>> from pydantic import BaseModel
        >>> class Config(BaseModel):
        ...     host: str
        ...     port: int
        >>>
        >>> result = client.extract.run(
        ...     Config,
        ...     "Find the database config in ~/.config/app.yaml"
        ... )
        >>> if result.success:
        ...     print(result.data.host)  # Type-safe access
    """

    def __init__(self, transport: BaseTransport) -> None:
        super().__init__(transport)
        self._stub: Any = None

    @property
    def _get_stub(self) -> Any:
        """Lazy-load gRPC stub."""
        if self._stub is None:
            from cmdop._generated.service_pb2_grpc import (
                TerminalStreamingServiceStub,
            )

            self._stub = TerminalStreamingServiceStub(self._channel)
        return self._stub

    def run(
        self,
        model: Type[T],
        prompt: str,
        options: ExtractOptions | None = None,
    ) -> ExtractResult[T]:
        """
        Extract structured data into a Pydantic model.

        Args:
            model: Pydantic model class to fill
            prompt: Extraction instruction
            options: Optional extraction options

        Returns:
            ExtractResult with typed data

        Example:
            >>> class DatabaseConfig(BaseModel):
            ...     host: str
            ...     port: int
            ...     name: str
            >>>
            >>> result = client.extract.run(
            ...     DatabaseConfig,
            ...     "Find the database settings in the config file"
            ... )
            >>> if result.success:
            ...     print(f"Database: {result.data.name}")
        """
        from cmdop._generated.rpc_messages.extract_pb2 import (
            ExtractRequest,
            ExtractOptions as PbExtractOptions,
        )

        # Convert model to JSON Schema
        json_schema = _model_to_json_schema(model)

        # Build request
        request = ExtractRequest(
            prompt=prompt,
            json_schema=json_schema,
        )

        # Add options if provided
        if options:
            pb_options = PbExtractOptions(
                model=options.model or "",
                temperature=options.temperature,
                max_tokens=options.max_tokens,
                max_retries=options.max_retries,
                timeout_seconds=options.timeout_seconds,
                working_directory=options.working_directory or "",
            )
            if options.enabled_tools:
                pb_options.enabled_tools.extend(options.enabled_tools)
            request.options.CopyFrom(pb_options)

        # Execute RPC
        response = self._call_sync(
            self._get_stub.Extract,
            request,
            timeout=options.timeout_seconds if options else 60,
        )

        # Parse response
        return self._parse_response(response, model)

    def _parse_response(
        self,
        response: Any,
        model: Type[T],
    ) -> ExtractResult[T]:
        """Parse protobuf response into ExtractResult."""
        metrics = _parse_metrics(response.metrics) if response.metrics else ExtractMetrics(
            duration_ms=0,
            llm_duration_ms=0,
            tool_duration_ms=0,
            llm_calls=0,
            tool_calls=0,
            retries=0,
            tokens=TokenUsage(0, 0, 0),
        )

        if not response.success:
            return ExtractResult(
                success=False,
                data=None,
                reasoning=response.reasoning or "",
                error=response.error,
                error_code=_parse_error_code(response.error_code),
                metrics=metrics,
            )

        # Parse result JSON into model
        try:
            data_dict = json.loads(response.result_json)
            data = model.model_validate(data_dict)
        except json.JSONDecodeError as e:
            return ExtractResult(
                success=False,
                data=None,
                reasoning=response.reasoning or "",
                error=f"Invalid JSON in result: {e}",
                error_code=ExtractErrorCode.VALIDATION_FAILED,
                metrics=metrics,
            )
        except Exception as e:
            return ExtractResult(
                success=False,
                data=None,
                reasoning=response.reasoning or "",
                error=f"Failed to validate result: {e}",
                error_code=ExtractErrorCode.VALIDATION_FAILED,
                metrics=metrics,
            )

        return ExtractResult(
            success=True,
            data=data,
            reasoning=response.reasoning or "",
            error=None,
            error_code=ExtractErrorCode.NONE,
            metrics=metrics,
        )


class AsyncExtractService(BaseService):
    """
    Asynchronous extract service.

    Provides async structured data extraction with Pydantic model support.
    """

    def __init__(self, transport: BaseTransport) -> None:
        super().__init__(transport)
        self._stub: Any = None

    @property
    def _get_stub(self) -> Any:
        """Lazy-load async gRPC stub."""
        if self._stub is None:
            from cmdop._generated.service_pb2_grpc import (
                TerminalStreamingServiceStub,
            )

            self._stub = TerminalStreamingServiceStub(self._async_channel)
        return self._stub

    async def run(
        self,
        model: Type[T],
        prompt: str,
        options: ExtractOptions | None = None,
    ) -> ExtractResult[T]:
        """
        Extract structured data into a Pydantic model (async).

        Args:
            model: Pydantic model class to fill
            prompt: Extraction instruction
            options: Optional extraction options

        Returns:
            ExtractResult with typed data
        """
        from cmdop._generated.rpc_messages.extract_pb2 import (
            ExtractRequest,
            ExtractOptions as PbExtractOptions,
        )

        # Convert model to JSON Schema
        json_schema = _model_to_json_schema(model)

        # Build request
        request = ExtractRequest(
            prompt=prompt,
            json_schema=json_schema,
        )

        # Add options if provided
        if options:
            pb_options = PbExtractOptions(
                model=options.model or "",
                temperature=options.temperature,
                max_tokens=options.max_tokens,
                max_retries=options.max_retries,
                timeout_seconds=options.timeout_seconds,
                working_directory=options.working_directory or "",
            )
            if options.enabled_tools:
                pb_options.enabled_tools.extend(options.enabled_tools)
            request.options.CopyFrom(pb_options)

        # Execute RPC
        response = await self._call_async(
            self._get_stub.Extract,
            request,
            timeout=options.timeout_seconds if options else 60,
        )

        # Parse response
        return self._parse_response(response, model)

    def _parse_response(
        self,
        response: Any,
        model: Type[T],
    ) -> ExtractResult[T]:
        """Parse protobuf response into ExtractResult."""
        metrics = _parse_metrics(response.metrics) if response.metrics else ExtractMetrics(
            duration_ms=0,
            llm_duration_ms=0,
            tool_duration_ms=0,
            llm_calls=0,
            tool_calls=0,
            retries=0,
            tokens=TokenUsage(0, 0, 0),
        )

        if not response.success:
            return ExtractResult(
                success=False,
                data=None,
                reasoning=response.reasoning or "",
                error=response.error,
                error_code=_parse_error_code(response.error_code),
                metrics=metrics,
            )

        # Parse result JSON into model
        try:
            data_dict = json.loads(response.result_json)
            data = model.model_validate(data_dict)
        except json.JSONDecodeError as e:
            return ExtractResult(
                success=False,
                data=None,
                reasoning=response.reasoning or "",
                error=f"Invalid JSON in result: {e}",
                error_code=ExtractErrorCode.VALIDATION_FAILED,
                metrics=metrics,
            )
        except Exception as e:
            return ExtractResult(
                success=False,
                data=None,
                reasoning=response.reasoning or "",
                error=f"Failed to validate result: {e}",
                error_code=ExtractErrorCode.VALIDATION_FAILED,
                metrics=metrics,
            )

        return ExtractResult(
            success=True,
            data=data,
            reasoning=response.reasoning or "",
            error=None,
            error_code=ExtractErrorCode.NONE,
            metrics=metrics,
        )
