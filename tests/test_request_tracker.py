import asyncio
import functools
from typing import Awaitable, Callable, TypeVar

import pytest

from esass.request_tracker import RequestTracker


@pytest.fixture
def request_tracker() -> RequestTracker:
    return RequestTracker()


T = TypeVar('T')


def async_wrap(cb: Callable[[], T]) -> Awaitable[T]:
    @functools.wraps(cb)
    async def wrapped():
        return cb()

    return wrapped


@pytest.mark.asyncio
async def test_add(request_tracker: RequestTracker) -> None:
    index, future = await request_tracker.add()
    assert request_tracker._messages[index] == future


@pytest.mark.asyncio
async def test_ready(request_tracker: RequestTracker) -> None:
    index, future = await request_tracker.add()
    future.set_result(None)
    assert request_tracker.ready(index)


@pytest.mark.asyncio
async def test_ready_nonexistant_id(request_tracker: RequestTracker) -> None:
    with pytest.raises(KeyError):
        request_tracker.ready(-1)


@pytest.mark.asyncio
async def test_pop(request_tracker: RequestTracker):
    index, future = await request_tracker.add()
    expected = object()
    future.set_result(expected)
    actual = request_tracker.pop(index)
    assert expected is actual


@pytest.mark.asyncio
async def test_pop_with_bad_id(request_tracker: RequestTracker) -> None:
    index, _ = await request_tracker.add()
    request_tracker._messages[index] = None

    with pytest.raises(KeyError):
        request_tracker.pop(index)


@pytest.mark.asyncio
async def test_pop_not_ready(request_tracker: RequestTracker) -> None:
    index, _ = await request_tracker.add()

    with pytest.raises(ValueError):
        request_tracker.pop(index)


@pytest.mark.asyncio
async def test_wait(request_tracker: RequestTracker) -> None:
    index, future = await request_tracker.add()
    expected = object()
    coro = async_wrap(lambda: future.set_result(expected))
    asyncio.create_task(coro())
    actual = await request_tracker.wait(index)
    assert actual is expected
