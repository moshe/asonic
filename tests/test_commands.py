import pytest

a = pytest.mark.asyncio
collection = 'collection'

pytestmark = pytest.mark.asyncio


async def test_ping(search, ingest):
    assert await search.ping() == b'PONG'
    assert await ingest.ping() == b'PONG'


async def test_help(search):
    assert await search.help('commands') == b'RESULT commands(QUERY, SUGGEST, PING, HELP, QUIT)'


async def test_empty(search):
    assert await search.query(collection, 'user1', 'test') == []
    assert await search.suggest(collection, 'user1', 'test') == []


async def test_push(search, ingest):
    bucket = 'bucket:1'
    uid = 'uid'
    assert (await ingest.push(collection, bucket, uid, 'The quick brown fox jumps over the lazy dog')) == b'OK'
    assert (await search.suggest(collection, bucket, 't', 1)) == []
    assert (await ingest.count(collection, bucket, uid)) == 6


async def test_query(search, ingest):
    bucket = 'bucket:1'
    uid = 'uid'
    assert (await ingest.push(collection, bucket, uid, 'The quick brown fox jumps over the lazy dog')) == b'OK'
    assert (await search.query(collection, bucket, 'quick', 1, 0)) == [uid.encode()]


async def test_pop(search, ingest):
    bucket = 'bucket:1'
    uid = 'uid'
    assert (await ingest.push(collection, bucket, uid, 'The quick brown fox jumps over the lazy dog')) == b'OK'
    assert (await ingest.pop(collection, bucket, uid, 'quick')) == 1
    assert (await ingest.count(collection, bucket, uid)) == 5
    assert (await search.query(collection, bucket, 'quick')) == []


async def test_limit_offset(search, ingest):
    bucket = 'bucket:1'
    uid = 'uid'
    uid2 = 'uid2'
    assert (await ingest.push(collection, bucket, uid, 'The quick brown fox jumps over the lazy dog')) == b'OK'
    assert (await ingest.push(collection, bucket, uid2,
                              'The quick brown fox jumps over the lazy dog complete')) == b'OK'
    assert (await search.query(collection, bucket, 'fox')) == [uid2.encode(), uid.encode()]
    assert (await search.query(collection, bucket, 'fox', limit=1)) == [uid2.encode()]
    assert (await search.query(collection, bucket, 'fox', limit=1, offset=1)) == [uid.encode()]
