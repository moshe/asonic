class BaseSonicException(Exception):
    pass


class ClientError(BaseSonicException):
    pass


class ConnectionClosed(ClientError):
    pass


class ServerError(BaseSonicException):
    pass
