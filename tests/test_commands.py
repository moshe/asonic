from contextlib import nullcontext as does_not_raise
import math
import pytest
import sys
from uuid import uuid4

from asonic import Client
from asonic.client import BUFFER
from asonic.enums import Action, Channel
from asonic.exceptions import ClientError, ConnectionClosed

collection = 'collection'

pytestmark = pytest.mark.asyncio

async def test_client_init():
    with does_not_raise():
        _client = await Client.create(host="localhost", port=1491, password="SecretPassword")
    with pytest.raises(ConnectionClosed):
        _client = await Client.create(host="localhost", port=1491, password="invalid")

async def test_ping(search, ingest):
    assert await search.ping() == b'PONG'
    assert await ingest.ping() == b'PONG'


async def test_help(search):
    assert await search.help('commands') == b'RESULT commands(QUERY, SUGGEST, LIST, PING, HELP, QUIT)'


async def test_empty(search):
    assert await search.query(collection, 'user1', 'test') == []
    assert await search.suggest(collection, 'user1', 'test') == []


async def test_suggest(search, ingest, control):
    bucket = str(uuid4())
    uid = str(uuid4())
    assert (await ingest.push(collection, bucket, uid, 'RESULT commands(QUERY, SUGGEST, LIST, PING, HELP, QUIT)')) == b'OK'
    assert (await control.trigger(Action.CONSOLIDATE)) == b'OK'
    assert (await search.suggest(collection, bucket, 'comm')) == [b'commands']
    assert (await search.suggest(collection, bucket, 'Q')) == [b'query', b'quit']
    assert (await ingest.count(collection, bucket, uid)) == 8


async def test_info(control):
    print((await control.info()))
    assert 'command_latency_best' in (await control.info())


async def test_query(search, ingest):
    bucket = str(uuid4())
    uid = str(uuid4())
    assert (await ingest.push(collection, bucket, uid, 'The quick brown fox jumps over the lazy dog')) == b'OK'
    assert (await search.query(collection, bucket, 'quick', 1, 0)) == [uid.encode()]

async def test_list(search, ingest, control):
    bucket = str(uuid4())
    uid = str(uuid4())
    await ingest.push(collection, bucket, uid, 'The quick brown fox jumps over the lazy dog')
    await ingest.push(collection, bucket, uid, 'brown fox jumps')
    await ingest.push(collection, bucket, uid, 'lazy dog jumps')
    await control.trigger(action=Action.CONSOLIDATE)
    assert set(await search.list(collection, bucket)) == {b'quick', b'brown', b'fox', b'jumps', b'lazy', b'dog'}

async def test_flushb(search, ingest):
    bucket = str(uuid4())
    uid = str(uuid4())
    assert (await ingest.push(collection, bucket, uid, 'The quick brown fox jumps over the lazy dog')) == b'OK'
    assert (await search.query(collection, bucket, 'quick')) == [uid.encode()]
    assert (await ingest.flushb(collection, bucket)) == 1
    assert (await search.query(collection, bucket, 'quick')) == []


async def test_flushc(search, ingest):
    bucket = str(uuid4())
    uid = str(uuid4())
    assert (await ingest.push(collection, bucket, uid, 'The quick brown fox jumps over the lazy dog')) == b'OK'
    assert (await search.query(collection, bucket, 'quick')) == [uid.encode()]
    assert (await ingest.flushc(collection)) == 1
    assert (await search.query(collection, bucket, 'quick')) == []


async def test_flusho(search, ingest):
    bucket = str(uuid4())
    uid = str(uuid4())
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
    bucket = str(uuid4())
    uid = str(uuid4())
    assert (await ingest.push(collection, bucket, uid, 'The quick brown fox jumps over the lazy dog')) == b'OK'
    assert (await ingest.pop(collection, bucket, uid, 'quick')) == 1
    assert (await ingest.count(collection, bucket, uid)) == 5
    assert (await search.query(collection, bucket, 'quick')) == []


async def test_ingest(search, ingest):
    bucket = str(uuid4())
    uid = str(uuid4())
    assert (await ingest.push(collection, bucket, uid, 'żółć')) == b'OK'
    assert (await search.query(collection, bucket, 'żółć', limit=1)) == [uid.encode()]
    long_string = " ".join(str(uuid4()) for _ in range(10000))
    total_size = sys.getsizeof(long_string)
    expected_chunks = math.ceil(total_size/BUFFER)
    chunks = list(ingest._chunk_generator(long_string, BUFFER))
    assert expected_chunks == len(chunks)
    for chunk in chunks:
        assert sys.getsizeof(chunk) <= BUFFER
    assert (await ingest.push(collection, bucket, uid, long_string)) == b'OK'

async def test_limit_offset(search, ingest):
    bucket = str(uuid4())
    uid = str(uuid4())
    uid2 = str(uuid4())
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
