from dataclasses import dataclass
from enum import Enum
import re
from typing import Annotated, Final, final
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    HttpUrl,
    AfterValidator,
    PlainSerializer,
    TypeAdapter,
)
from uuid import UUID

type _UrlStr = Annotated[HttpUrl, PlainSerializer(lambda val: str(val), return_type=str)]
type _UuidStr = Annotated[UUID, PlainSerializer(lambda val: str(val), return_type=str)]


def _is_regex(val: str) -> str:
    try:
        re.compile(val)
    except re.error as err:
        raise ValueError("Regex has a wrong format") from err
    return val


# TODO define more types
class AcrChaT(str, Enum):
    unk = "unknown"
    syn = "synonym"
    dep = "transfer"


@final
class AcrChaCon(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: Annotated[int, Field(gt=0)]
    type: AcrChaT


@final
class AcrCoreReg(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", validate_default=False)

    full: Annotated[str, Field(min_length=2), AfterValidator(_is_regex)]
    core: Annotated[str, Field(min_length=2), AfterValidator(_is_regex)] = ""
    pre: Annotated[str, Field(min_length=1), AfterValidator(_is_regex)] = ""
    suf: Annotated[str, Field(min_length=1), AfterValidator(_is_regex)] = ""


@final
class AcrDbEntry(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", validate_default=False)

    acr: Annotated[str, Field(min_length=2, pattern=r"^[A-Z:]+$")]
    code: Annotated[str, Field(min_length=2, pattern=r"^[A-Z:]+$")]
    name: Annotated[str, Field(min_length=2)]
    country: Annotated[str, Field(pattern=r"^[A-Z]{2}$")]
    active: bool
    regex_ccno: Annotated[str, Field(min_length=4), AfterValidator(_is_regex)]
    regex_id: AcrCoreReg
    ror: Annotated[str, Field(min_length=1)] = ""
    # gbif: _UuidStr | None = None
    gbif: Annotated[str, Field(min_length=36, pattern=r"^([IC]:)?[a-zA-Z0-9-]+$")] = ""
    deprecated: bool = False
    homepage: _UrlStr | None = None
    catalogue: list[_UrlStr] = Field(default_factory=list)
    acr_changed_to: list[AcrChaCon] = Field(default_factory=list)
    acr_synonym: list[Annotated[str, Field(min_length=2, pattern=r"^[A-Z:]+$")]] = Field(
        default_factory=list
    )


ACR_DB_KEYS: Final = TypeAdapter(list[Annotated[str, Field(pattern="^[1-9][0-9]*$")]])


@final
class AcrDbMinEntry(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    acr: Annotated[str, Field(min_length=2, pattern=r"^[A-Z:]+$")]
    deprecated: bool = False


ACR_MIN_CON = TypeAdapter(list[AcrDbMinEntry])
CCNO_DB_CON: Final = TypeAdapter(list[list[Annotated[str, Field(min_length=3)]]])
CCNO_DB_KEYS: Final = TypeAdapter(list[Annotated[str, Field(pattern="^[1-9][0-9]*$")]])


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CatArgs:
    acr: str
    id: str
    pre: str
    core: str
    suf: str
