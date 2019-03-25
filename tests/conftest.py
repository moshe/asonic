from os import getenv

import pytest

from asonic import Client
from asonic.enums import Channels

collection = 'collection'


@pytest.fixture(autouse=True)
async def clean():
    c = Client(host=getenv('SONIC_HOST', 'localhost'), port=1491)
    await c.channel(Channels.INGEST.value)
    await c.flushc(collection)


@pytest.fixture
async def search() -> Client:
    c = Client(host=getenv('SONIC_HOST', 'localhost'), port=1491)
    await c.channel(Channels.SEARCH.value)
    return c


@pytest.fixture
async def ingest():
    c = Client(host=getenv('SONIC_HOST', 'localhost'), port=1491)
    await c.channel(Channels.INGEST.value)
    return c
