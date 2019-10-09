import pytest

from asonic import Client
from asonic.enums import Actions, Channel
from asonic.exceptions import ClientError, ConnectionClosed

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


async def test_suggest(search, ingest, control):
    bucket = 'bucket:1'
    uid = 'uid'
    assert (await ingest.push(collection, bucket, uid, 'RESULT commands(QUERY, SUGGEST, PING, HELP, QUIT)')) == b'OK'
    assert (await control.trigger(Actions.CONSOLIDATE.value)) == b'OK'
    assert (await search.suggest(collection, bucket, 'comm')) == [b'commands']
    assert (await search.suggest(collection, bucket, 'Q')) == [b'query', b'quit']
    assert (await ingest.count(collection, bucket, uid)) == 5


async def test_info(control):
    print((await control.info()))
    assert 'command_latency_best' in (await control.info())


async def test_query(search, ingest):
    bucket = 'bucket:1'
    uid = 'uid'
    assert (await ingest.push(collection, bucket, uid, 'The quick brown fox jumps over the lazy dog')) == b'OK'
    assert (await search.query(collection, bucket, 'quick', 1, 0)) == [uid.encode()]


async def test_flushb(search, ingest):
    bucket = 'bucket:1'
    uid = 'uid'
    assert (await ingest.push(collection, bucket, uid, 'The quick brown fox jumps over the lazy dog')) == b'OK'
    assert (await search.query(collection, bucket, 'quick')) == [uid.encode()]
    assert (await ingest.flushb(collection, bucket)) == 1
    assert (await search.query(collection, bucket, 'quick')) == []


async def test_flushc(search, ingest):
    bucket = 'bucket:1'
    uid = 'uid'
    assert (await ingest.push(collection, bucket, uid, 'The quick brown fox jumps over the lazy dog')) == b'OK'
    assert (await search.query(collection, bucket, 'quick')) == [uid.encode()]
    assert (await ingest.flushc(collection)) == 1
    assert (await search.query(collection, bucket, 'quick')) == []


async def test_flusho(search, ingest):
    bucket = 'bucket:1'
    uid = 'uid'
    assert (await ingest.push(collection, bucket, uid, 'The quick brown fox jumps over the lazy dog')) == b'OK'
    assert (await search.query(collection, bucket, 'quick')) == [uid.encode()]
    assert (await ingest.flusho(collection, bucket, uid)) == 6
    assert (await search.query(collection, bucket, 'quick')) == []


async def test_quit(search):
    assert (await search.quit()) == b'ENDED quit'
    try:
        assert (await search.ping()) == b''
    except ConnectionClosed:
        pass
    else:
        raise AssertionError('Should raise exception after calling quit')


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


async def test_mixed_commands(search):
    try:
        await search.push()
    except ClientError:
        pass
    else:
        raise AssertionError('Should raise exception when calling push on a search channel')


async def test_channel_twice(search):
    try:
        await search.channel(Channel.CONTROL)
    except ClientError:
        pass
    else:
        raise AssertionError('Should raise exception when calling channel on initialized connection')


async def test_command_before_channel():
    a = Client()
    try:
        await a.ping()
    except ClientError:
        pass
    else:
        raise AssertionError('Should raise exception when not calling channel')
