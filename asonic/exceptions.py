class BaseSonicException(Exception):
    pass


class ClientError(BaseSonicException):
    pass


class ServerError(BaseSonicException):
    pass
