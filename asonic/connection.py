import asyncio
from logging import getLogger

from typing import Set, Optional

from asonic.enums import Channel
from asonic.exceptions import ServerError, ConnectionClosed


class Connection:
    def __init__(self, host: str, port: int, channel: Channel, password: str):
        self.host = host
        self.port = port
        self.channel = channel
        self.password = password
        self.reader = None  # type: Optional[asyncio.StreamReader]
        self.writer = None  # type: Optional[asyncio.StreamWriter]
        self.logger = getLogger('connection')

    async def connect(self) -> None:
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        result = await self.read()
        assert result.startswith(b'CONNECTED')

        await self.write(f'START {self.channel.value} {self.password}')
        await self.read()

    async def write(self, msg: str) -> None:
        assert self.writer is not None, 'connect'
        self.logger.debug('>%s', msg)
        self.writer.write(((msg + '\r\n').encode()))
        await self.writer.drain()

    async def read(self) -> bytes:
        assert self.reader is not None
        line = (await self.reader.readline()).strip()
        self.logger.debug('<%s', line)
        if line.startswith(b'ERR '):
            raise ServerError(line[4:])
        return line


class ConnectionPool:
    def __init__(self, host: str, port: int, channel: Channel, password: str, max_connections: int = 100):
        self.closed = False
        self._created_connections = 0
        self._available_connections = asyncio.Queue()  # type: asyncio.Queue[Connection]
        self._in_use_connections = set()  # type: Set[Connection]
        self.max_connections = max_connections
        self.host = host
        self.port = port
        self.password = password
        self.channel = channel

    async def get_connection(self) -> Connection:
        if self.closed is True:
            raise ConnectionClosed('Connection pool is closed')
        try:
            connection = self._available_connections.get_nowait()
        except asyncio.QueueEmpty:
            connection = await self.make_connection()
        self._in_use_connections.add(connection)
        return connection

    async def make_connection(self) -> Connection:
        if self._created_connections >= self.max_connections:
            return await self._available_connections.get()
        self._created_connections += 1
        c = Connection(self.host, self.port, self.channel, self.password)
        await c.connect()
        return c

    async def release(self, connection: Connection) -> None:
        self._in_use_connections.remove(connection)
        await self._available_connections.put(connection)

    async def destroy(self):
        self.closed = True
