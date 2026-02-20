"""
Sync wrapper generator for async services.

Automatically generates sync methods from async methods.
Write only async code, sync is generated at class definition time.

Usage:
    class AsyncAgentService(BaseService):
        async def run(self, prompt: str) -> AgentResult:
            ...

        async def run_stream(self, prompt: str) -> AsyncIterator[AgentStreamEvent]:
            ...

    # Sync service is generated automatically
    AgentService = create_sync_service(AsyncAgentService)

Or use decorator:
    @sync_service
    class AsyncAgentService(BaseService):
        ...
    # Creates AsyncAgentService._sync_class
"""

from __future__ import annotations

import asyncio
import functools
import inspect
from typing import Any, Callable, Iterator, TypeVar, get_type_hints

T = TypeVar("T")


def _run_sync(coro):
    """Run coroutine synchronously."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Already in async context - create new loop in thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)


def _make_sync_method(async_method: Callable) -> Callable:
    """Convert async method to sync method."""

    @functools.wraps(async_method)
    def sync_method(self, *args, **kwargs):
        # Get the async service instance
        async_service = getattr(self, "_async_service", None)
        if async_service is None:
            raise RuntimeError("Sync service not properly initialized")

        # Call async method
        coro = async_method(async_service, *args, **kwargs)
        return _run_sync(coro)

    return sync_method


def _make_sync_generator(async_method: Callable) -> Callable:
    """Convert async generator method to sync generator."""

    @functools.wraps(async_method)
    def sync_generator(self, *args, **kwargs) -> Iterator:
        # Get the async service instance
        async_service = getattr(self, "_async_service", None)
        if async_service is None:
            raise RuntimeError("Sync service not properly initialized")

        # Run async generator synchronously
        async def collect():
            results = []
            async for item in async_method(async_service, *args, **kwargs):
                results.append(item)
            return results

        for item in _run_sync(collect()):
            yield item

    return sync_generator


def _is_async_generator(func: Callable) -> bool:
    """Check if function is async generator."""
    return inspect.isasyncgenfunction(func)


def _is_coroutine_function(func: Callable) -> bool:
    """Check if function is coroutine."""
    return inspect.iscoroutinefunction(func)


def create_sync_service(async_class: type) -> type:
    """
    Create sync service class from async service class.

    Args:
        async_class: Async service class with async methods

    Returns:
        New sync service class wrapping async methods

    Example:
        >>> class AsyncFileService(BaseService):
        ...     async def read(self, path: str) -> bytes:
        ...         response = await self._call_async(...)
        ...         return response.data
        ...
        >>> FileService = create_sync_service(AsyncFileService)
        >>> # FileService.read() is now sync
    """
    # Get class name without "Async" prefix
    sync_name = async_class.__name__
    if sync_name.startswith("Async"):
        sync_name = sync_name[5:]  # Remove "Async" prefix

    # Build sync methods dict
    sync_methods = {}

    # Copy class attributes and convert methods
    for name in dir(async_class):
        if name.startswith("_"):
            continue

        attr = getattr(async_class, name)

        if _is_async_generator(attr):
            # Async generator -> sync generator
            sync_methods[name] = _make_sync_generator(attr)
        elif _is_coroutine_function(attr):
            # Async method -> sync method
            sync_methods[name] = _make_sync_method(attr)

    # Create sync class
    def sync_init(self, transport):
        # Store transport
        self._transport = transport
        # Create async service instance
        self._async_service = async_class(transport)

    # Forward properties
    def make_property_forwarder(prop_name):
        @property
        def forwarder(self):
            return getattr(self._async_service, prop_name)
        return forwarder

    # Collect properties from async class
    sync_properties = {}
    for name in dir(async_class):
        if name.startswith("_"):
            continue
        attr = getattr(async_class, name, None)
        if isinstance(attr, property):
            sync_properties[name] = make_property_forwarder(name)

    # Build class dict
    class_dict = {
        "__init__": sync_init,
        "__doc__": async_class.__doc__,
        "__module__": async_class.__module__,
        **sync_methods,
        **sync_properties,
    }

    # Add forwarding methods for special sync methods
    for name in ["set_session_id", "clear_session"]:
        if hasattr(async_class, name):
            original = getattr(async_class, name)
            if not _is_coroutine_function(original):
                # Already sync - just forward
                def make_forwarder(method_name):
                    def forwarder(self, *args, **kwargs):
                        return getattr(self._async_service, method_name)(*args, **kwargs)
                    return forwarder
                class_dict[name] = make_forwarder(name)

    # Create the class
    sync_class = type(sync_name, (), class_dict)

    return sync_class


def sync_service(async_class: type) -> type:
    """
    Decorator to auto-generate sync class.

    Adds `_sync_class` attribute to async class.

    Example:
        >>> @sync_service
        ... class AsyncAgentService(BaseService):
        ...     async def run(self, prompt: str) -> AgentResult:
        ...         ...
        ...
        >>> AgentService = AsyncAgentService._sync_class
    """
    async_class._sync_class = create_sync_service(async_class)
    return async_class
