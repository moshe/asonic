# asonic - async python client for the sonic search backend

## Install
`pip install asonic`

## Usage
### Search channel
```python
import asyncio

from asonic import Client
from asonic.enums import Channels


async def main():
  c = Client(host='127.0.0.1', port=1491)
  await c.channel(Channels.SEARCH.value)  # or simply search
  await c.query('collection', 'bucket', 'quick') == 'user_id'
  await c.suggest('collection', 'bucket', 'br', 1)) == 'brown'

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

### Ingest channel

```python
import asyncio

from asonic import Client
from asonic.enums import Channels


async def main():
  c = Client(host='127.0.0.1', port=1491)
  await c.channel(Channels.INGEST.value)  # or simply ingest
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
from asonic.enums import Channels, Actions


async def main():
  c = Client(host='127.0.0.1', port=1491)
  await c.channel(Channels.CONTROL.value)  # or simply control
  await c.trigger(Actions.CONSOLIDATE) # or simply consolidate
  # Return b'OK'
  await ingest.pop('collection', 'bucket', 'user_id', 'The')
  # Return 1

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```
