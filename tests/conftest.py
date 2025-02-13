from os import getenv

import pytest_asyncio

from asonic import Client
from asonic.enums import Channel

collection = 'collection'


@pytest_asyncio.fixture
async def clean():
    c = Client(host=getenv('SONIC_HOST', 'localhost'), port=1491)
    await c.channel(Channel.INGEST)
    await c.flushc(collection)


@pytest_asyncio.fixture
async def search() -> Client:
    c = Client(host=getenv('SONIC_HOST', 'localhost'), port=1491)
    await c.channel(Channel.SEARCH)
    return c


@pytest_asyncio.fixture
async def ingest():
    c = Client(host=getenv('SONIC_HOST', 'localhost'), port=1491)
    await c.channel(Channel.INGEST)
    return c


@pytest_asyncio.fixture
async def control():
    c = Client(host=getenv('SONIC_HOST', 'localhost'), port=1491)
    await c.channel(Channel.CONTROL)
    return c
