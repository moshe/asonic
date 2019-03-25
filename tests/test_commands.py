import pytest

from asonic import Client
from asonic.enums import Channels

a = pytest.mark.asyncio
collection = 'collection'


@pytest.fixture(autouse=True)
async def clean():
    c = Client(host='127.0.0.1', port=1491)
    await c.channel(Channels.INGEST.value)
    await c.flushc(collection)


@pytest.fixture
async def search():
    c = Client(host='127.0.0.1', port=1491)
    await c.channel(Channels.SEARCH.value)
    return c


@pytest.fixture
async def ingest():
    c = Client(host='127.0.0.1', port=1491)
    await c.channel(Channels.INGEST.value)
    return c


@a
async def test_ping(search, ingest):
    assert await search.ping() == b'PONG'
    assert await ingest.ping() == b'PONG'


@a
async def test_help(search):
    assert await search.help('commands') == b'RESULT commands(QUERY, SUGGEST, PING, HELP, QUIT)'


@a
async def test_empty(search):
    assert await search.query(collection, 'user1', 'test') is None
    assert await search.suggest(collection, 'user1', 'test') is None


@a
async def test_push(search, ingest):
    bucket = 'bucket:1'
    uid = 'uid'
    assert (await ingest.push(collection, bucket, uid, 'The quick brown fox jumps over the lazy dog complete')) == b'OK'
    assert (await search.suggest(collection, bucket, 't', 1)) is None
    assert (await ingest.count(collection, bucket, uid)) == 7
    assert (await search.query(collection, bucket, 'quick', 1, 0)) == uid.encode()
    assert (await ingest.pop(collection, bucket, uid, 'quick')) == 1
    assert (await ingest.count(collection, bucket, uid)) == 6
    assert (await search.query(collection, bucket, 'quick')) is None
