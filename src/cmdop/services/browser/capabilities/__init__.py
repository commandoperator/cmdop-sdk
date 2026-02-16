"""Browser capabilities."""

from .scroll import ScrollCapability
from .input import InputCapability
from .timing import TimingCapability
from .dom import DOMCapability
from .fetch import FetchCapability
from .network import NetworkCapability
from .visual import VisualCapability

__all__ = [
    "ScrollCapability",
    "InputCapability",
    "TimingCapability",
    "DOMCapability",
    "FetchCapability",
    "NetworkCapability",
    "VisualCapability",
]
