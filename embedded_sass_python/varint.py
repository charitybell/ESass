"""Varint encoder/decoder

varints are a common encoding for variable length integer data, used in
libraries such as sqlite, protobuf, v8, and more.

Here's a quick and dirty module to help avoid reimplementing the same thing
over and over again.

this code has been adapted from <https://github.com/fmoo/python-varint/>. It's licensed under the
MIT license:

The MIT License (MIT)

Copyright (c) 2016 Peter Ruibal

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import typing as t
from io import BytesIO

_BYTE_HEAD = 0b10000000
_BYTE_TAIL = 0b01111111


def _byte(b: int) -> bytes:
    return bytes((b, ))


def encode(number: int) -> bytes:
    """Pack `number` into varint bytes"""
    buf = b''
    while True:
        towrite = number & _BYTE_TAIL
        number >>= 7
        if number:
            buf += _byte(towrite | _BYTE_HEAD)
        else:
            buf += _byte(towrite)
            break
    return buf


async def decode_stream(stream: asyncio.StreamReader) -> int:
    """Read a varint from `stream`"""
    shift = 0
    result = 0
    while True:
        i = await _read_one(stream)
        result, shift, done = _decode_stream_helper(i, result, shift)

        if done:
            return result


def decode_stream_s(stream: t.IO[bytes]) -> int:
    shift = 0
    result = 0
    while True:
        i = _read_one_s(stream)
        result, shift, done = _decode_stream_helper(i, result, shift)
        if done:
            return result


def _decode_stream_helper(i: int, result: int, shift: int) -> tuple[int, int, int]:
    result |= (i & _BYTE_TAIL) << shift
    shift += 7
    done = not (i & _BYTE_HEAD)

    return result, shift, done


def decode_bytes(buf: bytes) -> int:
    """Read a varint from from `buf` bytes"""
    return decode_stream_s(BytesIO(buf))


def _read_one_helper(c: bytes) -> int:
    if c == b'':
        raise EOFError("Unexpected EOF while reading bytes")
    return ord(c)


def _read_one_s(stream: t.IO[bytes]) -> int:
    """Read a byte from the file (as an integer)

    raises EOFError if the stream ends while reading bytes.
    """
    c = stream.read(1)
    return _read_one_helper(c)


async def _read_one(stream: asyncio.StreamReader) -> int:
    """Read a byte from the file (as an integer)

    raises EOFError if the stream ends while reading bytes.
    """
    c = await stream.read(1)
    return _read_one_helper(c)
