# asonic - async python client for the sonic search backend
Asonic implements all [Sonic](https://github.com/valeriansaliou/sonic) APIs  
Bugfixes and api changes are welcome

## Install
`pip install asonic`

## API Docs
[here](https://asonic.readthedocs.io/en/latest/asonic.html#module-asonic.client)

## Usage
### Search channel
```python
import asyncio

from asonic import Client
from asonic.enums import Channel


async def main():
  c = await Client.create(
    host="127.0.0.1",
    port=1491,
    password="SecretPassword",
    channel=Channel.SEARCH,
    max_connections=100
  )
  assert (await c.query('collection', 'bucket', 'quick')) == [b'user_id']
  assert (await c.suggest('collection', 'bucket', 'br', 1)) == [b'brown']

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

### Ingest channel

```python
import asyncio

from asonic import Client
from asonic.enums import Channel


async def main():
  c = await Client.create(
    host="127.0.0.1",
    port=1491,
    password="SecretPassword",
    channel=Channel.INGEST,
    max_connections=100
  )
  await c.push('collection', 'bucket', 'user_id', 'The quick brown fox jumps over the lazy dog')
  # Return b'OK'
  await c.pop('collection', 'bucket', 'user_id', 'The')
  # Return 1

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```


### Control channel

```python
import asyncio

from asonic import Client
from asonic.enums import Channel, Action


async def main():
  c = await Client.create(
    host="127.0.0.1",
    port=1491,
    password="SecretPassword",
    channel=Channel.CONTROL,
  )
  await c.trigger(Action.CONSOLIDATE)
  # Return b'OK'

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```
