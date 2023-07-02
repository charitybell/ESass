import asyncio

from . import embedded_sass_pb2 as sass_pb
from .dispatcher import Dispatcher


async def main() -> None:
    dispatch = await Dispatcher.create()
    m = sass_pb.InboundMessage()
    m.version_request.id = 0
    await dispatch.dispatch(m)
    print(await dispatch.outbound_queue.get())

asyncio.run(main())
