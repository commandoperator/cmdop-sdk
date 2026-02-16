"""Timing capability."""

import random
import time
import threading
from typing import Callable, TypeVar

from ._base import BaseCapability

T = TypeVar("T")


class TimingCapability(BaseCapability):
    """Timing operations: wait, delays, timeouts.

    Usage:
        session.timing.wait(1000)
        session.timing.random(0.5, 2.0)
        result, ok = session.timing.timeout(lambda: slow_fn(), 30)
    """

    def wait(self, ms: int, jitter: float = 0.1) -> None:
        """Wait milliseconds with jitter (±10% by default)."""
        actual = (ms / 1000) * (1 + random.uniform(-jitter, jitter))
        time.sleep(actual)

    def seconds(self, sec: float, jitter: float = 0.1) -> None:
        """Wait seconds with jitter."""
        self.wait(int(sec * 1000), jitter)

    def random(self, min_sec: float = 0.5, max_sec: float = 1.5) -> None:
        """Wait random time between min and max seconds."""
        time.sleep(min_sec + random.random() * (max_sec - min_sec))

    def timeout(
        self,
        fn: Callable[[], T],
        seconds: float = 60.0,
        on_timeout: Callable[[], None] | None = None,
    ) -> tuple[T | None, bool]:
        """Run function with timeout. Returns (result, success)."""
        result: list[T | None] = [None]
        error: list[Exception | None] = [None]
        done = threading.Event()

        def run():
            try:
                result[0] = fn()
            except Exception as e:
                error[0] = e
            finally:
                done.set()

        threading.Thread(target=run, daemon=True).start()

        if done.wait(timeout=seconds):
            if error[0]:
                raise error[0]
            return result[0], True

        if on_timeout:
            try:
                on_timeout()
            except Exception:
                pass
        return None, False
