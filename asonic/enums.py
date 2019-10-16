from enum import Enum
from itertools import chain

from typing import Set


class Action(Enum):
    CONSOLIDATE = 'consolidate'
    BACKUP = 'backup'
    RESTORE = 'restore'


class Command(Enum):
    QUERY = 'QUERY'
    SUGGEST = 'SUGGEST'
    PING = 'PING'
    QUIT = 'QUIT'
    HELP = 'HELP'
    PUSH = 'PUSH'
    POP = 'POP'
    FLUSHB = 'FLUSHB'
    FLUSHC = 'FLUSHC'
    FLUSHO = 'FLUSHO'
    COUNT = 'COUNT'
    TRIGGER = 'TRIGGER'
    INFO = 'INFO'


class Channel(Enum):
    UNINITIALIZED = 'uninitialized'
    INGEST = 'ingest'
    SEARCH = 'search'
    CONTROL = 'control'


enabled_commands = {
    Channel.UNINITIALIZED: {
        Command.QUIT,
    },
    Channel.SEARCH: {
        Command.QUERY,
        Command.SUGGEST,
        Command.PING,
        Command.HELP,
        Command.QUIT,
    },
    Channel.INGEST: {
        Command.PUSH,
        Command.POP,
        Command.COUNT,
        Command.FLUSHB,
        Command.FLUSHC,
        Command.FLUSHO,
        Command.PING,
        Command.HELP,
        Command.QUIT,
    },
    Channel.CONTROL: {
        Command.TRIGGER,
        Command.PING,
        Command.HELP,
        Command.QUIT,
    }
}

all_commands = set(chain(*enabled_commands.values()))  # type: Set[Command]
