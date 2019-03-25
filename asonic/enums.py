from enum import Enum


class Actions(Enum):
    CONSOLIDATE = 'consolidate'


class Commands(Enum):
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


class Channels(Enum):
    UNINITIALIZED = 'uninitialized'
    INGEST = 'ingest'
    SEARCH = 'search'
    CONTROL = 'control'


enabled_commands = {
    Channels.UNINITIALIZED.value: {
        Commands.QUIT.value,
    },
    Channels.SEARCH.value: {
        Commands.QUERY.value,
        Commands.SUGGEST.value,
        Commands.PING.value,
        Commands.HELP.value,
        Commands.QUIT.value,
    },
    Channels.INGEST.value: {
        Commands.PUSH.value,
        Commands.POP.value,
        Commands.COUNT.value,
        Commands.FLUSHB.value,
        Commands.FLUSHC.value,
        Commands.FLUSHO.value,
        Commands.PING.value,
        Commands.HELP.value,
        Commands.QUIT.value,
    },
    Channels.CONTROL.value: {
        Commands.TRIGGER.value,
        Commands.PING.value,
        Commands.HELP.value,
        Commands.QUIT.value,
    }
}

all_commands = set(sum([list(x) for x in enabled_commands.values()], list()))
