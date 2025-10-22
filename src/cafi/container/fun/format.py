import re
from typing import Protocol
from urllib.parse import unquote_plus


class _URLlike(Protocol):
    def unicode_string(self) -> str: ...


def url_to_str(url: _URLlike | None, /) -> str:
    if url is None:
        return ""
    return unquote_plus(url.unicode_string())


def is_regex(val: str) -> str:
    try:
        re.compile(val)
    except re.error as err:
        raise ValueError("Regex has a wrong format") from err
    return val
