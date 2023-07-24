import asyncio
import os
import subprocess
import typing as t
from io import BytesIO

from . import embedded_sass_pb2 as sass_pb
from .request_tracker import RequestTracker
from . import varint


class SassException(Exception):
    pass


class DispatchException(SassException):
    pass


class Dispatcher:
    compiler_path: str
    proc: asyncio.subprocess.Process
    tracker: RequestTracker

    def __init__(self, compiler_path: str = 'sass'):
        self.compiler_path = compiler_path
        self.tracker = RequestTracker()

    async def start(self) -> None:
        self.proc = await asyncio.create_subprocess_exec(
            self.compiler_path, '--embedded',
            env={'PATH': os.environ.get('PATH', '')},
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
        asyncio.create_task(self.read_message())

    @classmethod
    async def create(cls, compiler_path: str = 'sass') -> t.Self:
        self = cls(compiler_path)
        await self.start()
        return self

    async def read_message(self) -> None:
        assert self.proc.stdout is not None
        while True:
            message_length = await varint.decode_stream(self.proc.stdout)
            message = BytesIO(await self.proc.stdout.readexactly(message_length))
            compilation_id = varint.decode_stream_s(message)
            self.tracker.resolve(
                compilation_id,
                sass_pb.OutboundMessage.FromString(message.read()))

    async def dispatch(self, message: sass_pb.InboundMessage) -> sass_pb.OutboundMessage:
        assert self.proc.stdin is not None
        if not message.IsInitialized():
            raise DispatchException('Message is not initialized')

        message_type = message.WhichOneof('message')
        assert message_type is not None

        is_version_request = message_type == 'version_request'
        message_id, response_future = await self.tracker.add(version_request=is_version_request)

        buffer = varint.encode(message_id)
        buffer += message.SerializeToString()
        length_buffer = varint.encode(len(buffer))

        self.proc.stdin.write(length_buffer)
        self.proc.stdin.write(buffer)
        await self.proc.stdin.drain()

        return await response_future
