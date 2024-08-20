import asyncio
import signal
import time
from collections.abc import Awaitable, Iterable
from typing import Any


class AsyncThrottler:
    """
    Limits the wrapped function to a set number of executions per interval.

    Args:
        limit: The number of executions to allow before throttling
        interval: The number of seconds to wait if the limit is reached
    """

    def __init__(self, limit: int = 5, interval: int = 1):
        self.interval = interval
        self.limit = limit
        self.throttled_start_times: list[float] = []

    async def __aenter__(self):
        await self.acquire()

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.release()

    async def acquire(self) -> None:
        if len(self.throttled_start_times) >= self.limit:
            allowed_start_time = self.throttled_start_times.pop(0)
            if allowed_start_time >= time.monotonic():
                await asyncio.sleep(allowed_start_time - time.monotonic())

    async def release(self) -> None:
        self.throttled_start_times.append(time.monotonic() + self.interval)


def run(coro: Awaitable[Any], signals: Iterable[signal.Signals] = (signal.SIGINT, signal.SIGTERM)) -> None:
    """
    Run a coroutine in a synchronous context.

    Args:
        coro: A coroutine.
        signals: Cancel the coroutine on these signals.

    This function approximates the behaviour of `asyncio.run()` in Python 3.11+.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    main = asyncio.ensure_future(coro)
    for sig in signals:
        loop.add_signal_handler(sig, main.cancel)
    try:
        loop.run_until_complete(main)
    finally:
        loop.close()
