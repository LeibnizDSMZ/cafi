from typing import Self, final
from cafi.container.fun.country import load_active_countries


@final
class CountryCodes:
    __slots__ = ("__codes",)
    __instance: Self | None = None

    def __init__(self) -> None:
        self.__codes = load_active_countries()
        super().__init__()

    def __new__(cls, *_args: str) -> Self:
        if cls.__instance is not None:
            return cls.__instance
        cls.__instance = super().__new__(cls)
        return cls.__instance

    def is_code(self, code: str) -> str:
        if code not in self.__codes:
            raise ValueError(f"Code: {code} is not an known active code")
        return code
