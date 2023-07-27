import asyncio

import pytest

from embedded_sass_python import varint


@pytest.mark.asyncio
async def test_encode() -> None:
    expected = b'\x80\x02'
    actual = varint.encode(256)
    assert expected == actual


def test_decode_bytes() -> None:
    assert varint.decode_bytes(varint.encode(256)) == 256


@pytest.mark.asyncio
async def test_decode_stream() -> None:
    encoded = varint.encode(256)
    stream = asyncio.StreamReader()
    stream.feed_data(encoded)
    stream.feed_eof()
    assert (await varint.decode_stream(stream)) == 256
