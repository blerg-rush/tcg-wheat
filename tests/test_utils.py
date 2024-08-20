import time
from unittest.mock import Mock

from tcg_wheat.utils import AsyncThrottler


class TestAsyncThrottler:
    async def test_throttler_default(self):
        mock_fn = Mock()
        throttler = AsyncThrottler()

        start = time.monotonic()
        for _ in range(5):
            async with throttler:
                mock_fn()
        diff = time.monotonic() - start
        assert diff < 1
        assert mock_fn.call_count == 5

        for _ in range(5):
            async with throttler:
                mock_fn()
        diff = time.monotonic() - start
        assert 2 > diff >= 1
        assert mock_fn.call_count == 10

    async def test_throttler_sleeps(self):
        mock_fn = Mock()
        throttler = AsyncThrottler(limit=2, interval=1)

        start = time.monotonic()
        for _ in range(3):
            async with throttler:
                mock_fn()
        diff = time.monotonic() - start
        assert 2 > diff >= 1
        assert mock_fn.call_count == 3

    async def test_throttled_sleeps_multiple_times(self):
        mock_fn = Mock()
        throttler = AsyncThrottler(limit=1, interval=1)

        start = time.monotonic()
        for _ in range(3):
            async with throttler:
                mock_fn()
        diff = time.monotonic() - start
        assert 3 > diff >= 2
        assert mock_fn.call_count == 3
