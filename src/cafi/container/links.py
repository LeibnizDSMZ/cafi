from dataclasses import dataclass, field
from enum import Enum
from typing import final


class LinkLevel(Enum):
    cat = "catalogue"
    home = "homepage"
    emp = "no link found"


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CatalogueLink:
    level: LinkLevel
    catalogue: list[str] = field(default_factory=list)
    homepage: str = ""
