"""Base capability class."""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..session import BrowserSession


class BaseCapability:
    """Base class for all capabilities.

    Capabilities group related browser operations and delegate
    actual execution to the session.
    """

    __slots__ = ("_s",)

    def __init__(self, session: "BrowserSession") -> None:
        self._s = session

    def _js(self, script: str) -> str:
        """Execute JS via session."""
        return self._s.execute_script(script)

    def _call(self, method: str, *args: Any, **kwargs: Any) -> Any:
        """Call service method via session."""
        return self._s._call_service(method, *args, **kwargs)
