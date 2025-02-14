from typing import final


class KnownException(Exception):
    __slots__ = "__message"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.__message = message

    @final
    @property
    def message(self) -> str:
        return self.__message


# FATAL errors


class ValJsonEx(KnownException):
    pass


class ReqURIEx(KnownException):
    pass
