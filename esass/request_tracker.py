from asyncio import get_running_loop, Future

from .embedded_sass_pb2 import OutboundMessage


class RequestTracker:
    _messages: list[None | Future[OutboundMessage]]

    def __init__(self) -> None:
        self._messages = [None]

    def __next_compilation_id(self) -> int:
        # skip the first element since id 0 is reserved for VersionRequest
        for index, value in enumerate(self._messages[1:]):
            if not value:
                return index + 1

        self._messages.append(None)

        return len(self._messages) - 1

    async def add(self, *, version_request: bool = False) -> tuple[int, Future[OutboundMessage]]:
        loop = get_running_loop()
        future = loop.create_future()
        if version_request:
            compilation_id = 0
        else:
            compilation_id = self.__next_compilation_id()
        self._messages[compilation_id] = future
        return (compilation_id, future)

    def ready(self, index: int) -> bool:
        message = self._messages[index]

        if message:
            return message.done()

        raise KeyError(f"Request index {index} doesn't exist")

    def pop(self, index: int) -> OutboundMessage:
        if self.ready(index):
            message = self._messages[index]
            assert message is not None
            self._messages[index] = None
            return message.result()

        raise ValueError("Request index {index} isn't ready yet")

    async def wait(self, index: int) -> OutboundMessage:
        message = self._messages[index]
        assert message is not None
        self._messages[index] = None
        return await message

    def resolve(self, index: int, message: OutboundMessage) -> None:
        future = self._messages[index]
        assert future is not None
        future.set_result(message)
        self._messages[index] = None
