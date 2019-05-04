from typing import List, Union

from asonic.connection import ConnectionPool
from asonic.enums import (Actions, Channels, Commands, all_commands,
                          enabled_commands)
from asonic.exceptions import ClientError


def escape(t):
    if t is None:
        return ""
    return '"' + t.replace('"', '\\"').replace('\r\n', ' ') + '"'


class Client:
    def __init__(self, host: str = 'localhost', port: int = 1491, password: str = 'SecretPassword',
                 max_connections: int = 100):
        self.host = host
        self.port = port
        self.password = password
        self.max_connections = max_connections

        self._channel = Channels.UNINITIALIZED.value
        self.pool: Union[ConnectionPool, None] = None

    async def channel(self, channel: str) -> None:
        if self._channel != Channels.UNINITIALIZED.value:
            raise ClientError('Channel cannot be set twice')
        Channels(channel)

        async def mock(*_, **__):
            raise ClientError(f'Command not available in {channel} channel')

        for command in all_commands:
            if command not in enabled_commands[channel]:
                setattr(self, command.lower(), mock)
        self._channel = channel
        self.pool = ConnectionPool(host=self.host, port=self.port, channel=channel,
                                   max_connections=self.max_connections,
                                   password=self.password)

    async def query(self,
                    collection: str,
                    bucket: str,
                    terms: str,
                    limit: int = None,
                    offset: int = None,
                    locale: str = None
                    ) -> List[bytes]:
        """
        query database
        time complexity: O(1) if enough exact word matches or O(N) if not enough exact matches where
        N is the number of alternate words tried, in practice it approaches O(1)
        :param collection: index collection (ie. what you search in, eg. messages, products, etc.)
        :param bucket: index bucket name (ie. user-specific search classifier in the collection if you have any
        :param terms: text for search terms
        :param limit: a positive integer number; set within allowed maximum & minimum limits
        :param offset: a positive integer number; set within allowed maximum & minimum limits
        :param locale: an ISO 639-3 locale code eg. `eng` for English
        (if set, the locale must be a valid ISO 639-3 code; if not set, the locale will be guessed from text)
        """

        response = await self._command(Commands.QUERY, collection, bucket, escape(terms),
                                       limit=limit, offset=offset, locale=locale)
        tokens = response.split()
        if len(tokens) == 3:
            return []
        else:
            return tokens[3:]

    async def suggest(self, collection: str, bucket: str, word: str, limit: int = None) -> List[bytes]:
        """
        auto-completes word
        time complexity: O(1)
        :param collection: index collection (ie. what you search in, eg. messages, products, etc.)
        :param bucket: index bucket name (ie. user-specific search classifier in the collection if you have any
        :param word: text for search term
        :param limit: a positive integer number; set within allowed maximum & minimum limits
        """
        response = await self._command(Commands.SUGGEST, collection, bucket, escape(word), limit=limit)
        tokens = response.split()
        if len(tokens) == 3:
            return []
        else:
            return tokens[3:]

    async def ping(self) -> bytes:
        """
        ping server
        time complexity: O(1)
        """
        return await self._command(Commands.PING)

    async def quit(self) -> bytes:
        """
        stop connection
        time complexity: O(1)
        """
        return await self._command(Commands.QUIT)

    async def help(self, manual: str) -> bytes:
        """
        show help
        time complexity: O(1)
        :param manual: help manual to be shown (available manuals: commands)
        """
        return await self._command(Commands.HELP, manual)

    async def push(self, collection: str, bucket: str, obj: str, text: str, locale: str = None) -> bytes:
        """
        Push search data in the index
        time complexity: O(1)
        :param collection: index collection (ie. what you search in, eg. messages, products, etc.)
        :param bucket: index bucket name (ie. user-specific search classifier in the collection if you have any
        :param obj: object identifier that refers to an entity in an external database, where the searched object
        is stored (eg. you use Sonic to index CRM contacts by name; full CRM contact data is stored in a MySQL database
        in this case the object identifier in Sonic will be the MySQL primary key for the CRM contact)
        :param text: search text to be indexed (can be a single word, or a longer text; within maximum length safety
        limits)
        :param locale: an ISO 639-3 locale code eg. `eng` for English
        (if set, the locale must be a valid ISO 639-3 code; if not set, the locale will be guessed from text)
        """
        return await self._command(Commands.PUSH, collection, bucket, obj, escape(text), locale=locale)

    async def pop(self, collection: str, bucket: str, obj: str, text: str) -> int:
        """
        Pop search data from the index
        time complexity: O(1)
        :param collection: index collection (ie. what you search in, eg. messages, products, etc.)
        :param bucket: index bucket name (ie. user-specific search classifier in the collection if you have any
        :param obj: object identifier that refers to an entity in an external database, where the searched object
        is stored (eg. you use Sonic to index CRM contacts by name; full CRM contact data is stored in a MySQL database
        in this case the object identifier in Sonic will be the MySQL primary key for the CRM contact)
        :param text: search text to be indexed (can be a single word, or a longer text; within maximum length safety
        limits)
        """
        result = await self._command(Commands.POP, collection, bucket, obj, escape(text))
        return int(result[7:])

    async def flushc(self, collection: str) -> int:
        """
        Flush all indexed data from a collection
        time complexity: O(1)
        :param collection: index collection (ie. what you search in, eg. messages, products, etc.)
        """
        return int((await self._command(Commands.FLUSHC, collection))[7:])

    async def flushb(self, collection: str, bucket: str) -> int:
        """
        Flush all indexed data from a bucket in a collection
        time complexity: O(1)
        :param collection: index collection (ie. what you search in, eg. messages, products, etc.)
        :param bucket: index bucket name (ie. user-specific search classifier in the collection if you have any
        """

        return int((await self._command(Commands.FLUSHB, collection, bucket))[7:])

    async def flusho(self, collection: str, bucket: str, obj: str) -> int:
        """
        Flush all indexed data from an object in a bucket in collection
        time complexity: O(1)
        :param collection: index collection (ie. what you search in, eg. messages, products, etc.)
        :param bucket: index bucket name (ie. user-specific search classifier in the collection if you have any
        :param obj: object identifier that refers to an entity in an external database, where the searched object
        is stored (eg. you use Sonic to index CRM contacts by name; full CRM contact data is stored in a MySQL database
        in this case the object identifier in Sonic will be the MySQL primary key for the CRM contact)
        """

        return int((await self._command(Commands.FLUSHO, collection, bucket, obj))[7:])

    async def count(self, collection: str, bucket: str = None, obj: str = None) -> int:
        """
        Count indexed search data
        time complexity: O(1)
        :param collection: index collection (ie. what you search in, eg. messages, products, etc.)
        :param bucket: index bucket name (ie. user-specific search classifier in the collection if you have any
        :param obj: object identifier that refers to an entity in an external database, where the searched object
        is stored (eg. you use Sonic to index CRM contacts by name; full CRM contact data is stored in a MySQL database
        in this case the object identifier in Sonic will be the MySQL primary key for the CRM contact)
        """
        result = await self._command(Commands.COUNT, collection, bucket=bucket, object=obj)
        return int(result[7:])

    async def trigger(self, action: str = None) -> bytes:
        """
        Trigger an action
        time complexity: O(1)
        :param action: action to be triggered (available actions: consolidate)
        """
        Actions(action)
        return await self._command(Commands.TRIGGER, action=action)

    async def info(self) -> dict:
        """
        Get server information
        time complexity: O(1)
        """
        res = await self._command(Commands.INFO)
        return dict(map(lambda x: x.replace('(', ' ').replace(')', '').split(), res[7:].decode().split()))

    async def _command(self, command: Commands, *args, **kwargs) -> bytes:
        if isinstance(command, Commands):
            command = command.value

        if self._channel == Channels.UNINITIALIZED.value:
            raise ClientError('Call .channel before running any command')

        c = await self.pool.get_connection()

        values = []
        for k in kwargs:
            if kwargs[k] is not None:
                if k == 'limit':
                    values.append(f'LIMIT({kwargs[k]})')
                elif k == 'offset':
                    values.append(f'OFFSET({kwargs[k]})')
                elif k == 'locale':
                    values.append(f'LANG({kwargs[k]})')
                else:
                    values.append(kwargs[k])
        await c.write(f'{command} {" ".join(args)} {" ".join(values)}'.strip())

        result = await c.read()
        if command in {Commands.QUERY.value, Commands.SUGGEST.value}:
            result = await c.read()
        await self.pool.release(c)
        if command == Commands.QUIT.value:
            await self.pool.destroy()
        return result
