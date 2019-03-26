# asonic - async python client for the sonic search backend
Asonic implements all [Sonic](https://github.com/valeriansaliou/sonic) APIs  
This is a very early stage of the package, bugfixes and api changes are welcome

## Install
`pip install asonic`

## API Docs
[here](https://asonic.readthedocs.io/en/latest/asonic.html#module-asonic.client)

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
