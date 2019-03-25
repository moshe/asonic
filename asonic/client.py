import asyncio

from typing import Union

from asonic.connection import ConnectionPool
from asonic.enums import Commands, Channels, all_commands, enabled_commands, Actions
from asonic.exceptions import ClientError


class Client:
    def __init__(self, host: str, port: int, password: str = 'SecretPassword', max_connections: int = 100):
        self.host = host
        self.port = port
        self.password = password
        self.max_connections = max_connections

        self._channel = Channels.UNINITIALIZED.value
        self.pool: ConnectionPool = None

    async def channel(self, channel: str) -> None:
        if self._channel != Channels.UNINITIALIZED.value:
            raise ClientError('Channel cannot be set twice')
        Channels(channel)

        async def mock(*_, **__):
            raise RuntimeError(f'Command not available in {channel} channel')

        for command in all_commands:
            if command not in enabled_commands[channel]:
                setattr(self, command.lower(), mock)
        self._channel = channel
        self.pool = ConnectionPool(host=self.host, port=self.port, channel=channel,
                                   max_connections=self.max_connections)

    async def query(self, collection: str, bucket: str, terms: str, limit: int = None, offset: int = None) \
            -> Union[None, str]:
        """
        TODO: Check multiple returns, offset and limit
        TODO: Terms shold be list
        query database
        time complexity: O(1) if enough exact word matches or O(N) if not enough exact matches where
        N is the number of alternate words tried, in practice it approaches O(1)
        :param collection: index collection (ie. what you search in, eg. messages, products, etc.);
        :param bucket: index bucket name (ie. user-specific search classifier in the collection if you have any
        :param terms: text for search terms
        :param limit: a positive integer number; set within allowed maximum & minimum limits
        :param offset:  a positive integer number; set within allowed maximum & minimum limits
        """

        response = await self._command(Commands.QUERY, collection, bucket, f'"{terms}"', limit=limit, offset=offset)
        tokens = response.split()
        if len(tokens) == 3:
            return None
        else:
            return tokens[3]

    async def suggest(self, collection: str, bucket: str, word: str, limit: int = None) -> Union[None, str]:
        """
        TODO: Escape word
        auto-completes word
        time complexity: O(1)
        :param collection: index collection (ie. what you search in, eg. messages, products, etc.);
        :param bucket: index bucket name (ie. user-specific search classifier in the collection if you have any
        :param word: text for search term
        :param limit: a positive integer number; set within allowed maximum & minimum limits
        """
        response = await self._command(Commands.SUGGEST, collection, bucket, f'"{word}"', limit=limit)
        tokens = response.split()
        print(tokens)
        if len(tokens) == 3:
            return None
        else:
            return tokens[3]

    async def ping(self) -> str:
        """
        ping server
        time complexity: O(1)
        """
        return await self._command(Commands.PING)

    async def quit(self) -> str:
        """
        stop connection
        time complexity: O(1)
        """
        return await self._command(Commands.QUIT)

    async def help(self, manual: str) -> str:
        """
        show help
        time complexity: O(1)
        :param manual: help manual to be shown (available manuals: commands)
        """
        return await self._command(Commands.HELP, manual)

    async def push(self, collection: str, bucket: str, obj: str, text: str) -> str:
        """
        Push search data in the index
        time complexity: O(1)
        :param collection: index collection (ie. what you search in, eg. messages, products, etc.);
        :param bucket: index bucket name (ie. user-specific search classifier in the collection if you have any
        :param obj: object identifier that refers to an entity in an external database, where the searched object
        is stored (eg. you use Sonic to index CRM contacts by name; full CRM contact data is stored in a MySQL database;
        in this case the object identifier in Sonic will be the MySQL primary key for the CRM contact);
        :param text: search text to be indexed (can be a single word, or a longer text; within maximum length safety
        limits);
        """
        return await self._command(Commands.PUSH, collection, bucket, obj, f'"{text}"')

    async def pop(self, collection: str, bucket: str, obj: str, text: str) -> int:
        """
        Pop search data from the index
        time complexity: O(1)
        :param collection: index collection (ie. what you search in, eg. messages, products, etc.);
        :param bucket: index bucket name (ie. user-specific search classifier in the collection if you have any
        :param obj: object identifier that refers to an entity in an external database, where the searched object
        is stored (eg. you use Sonic to index CRM contacts by name; full CRM contact data is stored in a MySQL database;
        in this case the object identifier in Sonic will be the MySQL primary key for the CRM contact);
        :param text: search text to be indexed (can be a single word, or a longer text; within maximum length safety
        limits);
        """
        result = await self._command(Commands.POP, collection, bucket, obj, f'"{text}"')
        return int(result[7:])

    async def flushc(self, collection: str) -> str:
        """
        Flush all indexed data from a collection
         time complexity: O(1)
        :param collection: index collection (ie. what you search in, eg. messages, products, etc.);
        """
        return await self._command(Commands.FLUSHC, collection)

    async def flushb(self, collection: str, bucket: str) -> str:
        """
        Flush all indexed data from a bucket in a collection
         time complexity: O(1)
        :param collection: index collection (ie. what you search in, eg. messages, products, etc.);
        :param bucket: index bucket name (ie. user-specific search classifier in the collection if you have any
        """

        return await self._command(Commands.FLUSHB, collection, bucket)

    async def flusho(self, collection: str, bucket: str, obj: str) -> str:
        """
        Flush all indexed data from an object in a bucket in collection
         time complexity: O(1)
        :param collection: index collection (ie. what you search in, eg. messages, products, etc.);
        :param bucket: index bucket name (ie. user-specific search classifier in the collection if you have any
        :param obj: object identifier that refers to an entity in an external database, where the searched object
        is stored (eg. you use Sonic to index CRM contacts by name; full CRM contact data is stored in a MySQL database;
        in this case the object identifier in Sonic will be the MySQL primary key for the CRM contact);
        """

        return await self._command(Commands.FLUSHO, collection, bucket, obj)

    async def count(self, collection: str, bucket: str = None, obj: str = None) -> int:
        """
        Count indexed search data
        time complexity: O(1)
        :param collection: index collection (ie. what you search in, eg. messages, products, etc.);
        :param bucket: index bucket name (ie. user-specific search classifier in the collection if you have any
        :param obj: object identifier that refers to an entity in an external database, where the searched object
        is stored (eg. you use Sonic to index CRM contacts by name; full CRM contact data is stored in a MySQL database;
        in this case the object identifier in Sonic will be the MySQL primary key for the CRM contact);
        """
        result = await self._command(Commands.COUNT, collection, bucket=bucket, object=obj)
        return int(result[7:])

    async def trigger(self, action: str = None) -> str:
        """
        Trigger an action
        time complexity: O(1)
        :param action: action to be triggered (available actions: consolidate);
        """
        Actions(action)
        return await self._command(Commands.TRIGGER, action=action)

    async def _command(self, command, *args, **kwargs) -> str:
        if isinstance(command, Commands):
            command = command.value

        if self._channel is None:
            raise RuntimeError('Call .channel before running any command')

        c = await self.pool.get_connection()

        values = []
        for k in kwargs:
            if kwargs[k] is not None:
                if k == 'limit':
                    values.append(f'LIMIT({kwargs[k]})')
                elif k == 'offset':
                    values.append(f'OFFSET({kwargs[k]})')
                else:
                    values.append(kwargs[k])
        print(f'{command} {" ".join(args)} {" ".join(values)}'.strip())
        await c.write(f'{command} {" ".join(args)} {" ".join(values)}'.strip())

        result = await c.read()
        if command in {Commands.QUERY.value, Commands.SUGGEST.value}:
            result = await c.read()
        await self.pool.release(c)
        return result


async def main():
    ci = Client(host='127.0.0.1', port=1491)
    await ci.channel(Channels.INGEST.value)
    print(await ci.ping())
    # jobs = []
    # for job in range(200_000):
    #     if job % 1000 == 0:
    #         print(job)
    #     jobs.append(ci.push('messages', f'user:0dcde3a{job % 1000}', f'conversation:{job}', 'moshe zada haya po'))
    #     # await ci.push('messages', f'user:0dcde3a{job % 1000}', f'conversation:{job}', 'moshe zada haya po')
    # await asyncio.gather(*jobs)
    # c = Client(host='127.0.0.1', port=1491)
    # await c.channel('search')
    # await c.ping()
    # await c.quit()
    # await c.channel('search')
    # await c.help('commands')
    # await c.query('messages', 'user:0dcde3a6', 'zada')
    # await c.suggest('messages', 'user:0dcde3a6', 'mosh')
    #
    # await ci.pop('messages', 'user:0dcde3a6', 'conversation:71f3d63b', 'zada')
    # await c.query('messages', 'user:0dcde3a6', 'zada')
    #
    # assert (await ci.count('messages')) == 1


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
