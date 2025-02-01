from collections.abc import Iterable
from importlib import resources
import json
from typing import Any, Callable
import warnings

import requests
from knacr.constants.types import ACR_DB_T, ACR_MIN_DB_T, CCNO_DB_T
from knacr.constants.versions import CURRENT_VER
from knacr.container.fun.acr_db import create_acr_min_db
from knacr.errors.custom_exceptions import ReqURIEx, ValJsonEx
from knacr.errors.custom_warnings import LoadWarn
from knacr.library.validate import (
    validate_acr_db,
    validate_catalogue_db,
    validate_min_acr_db_schema,
    validate_regex_db,
)
from knacr import data


def _load_data_from_file(db_name: str, /) -> bytes:
    with resources.files(data).joinpath(f"{db_name}.json").open("rb") as fhd:
        return fhd.read()


def _load_data[
    T: (ACR_DB_T, ACR_MIN_DB_T, CCNO_DB_T)
](version: str, db_name: str, create: Callable[[Any], T], /) -> T:
    knacr = "https://raw.githubusercontent.com/LeibnizDSMZ/knAcr"
    req = f"{knacr}/{version}/src/knacr/data/{db_name}.json"
    if version == CURRENT_VER:
        print("[KnAcr] loading from local file")
        return create(json.loads(_load_data_from_file(db_name)))
    print("[KnAcr] downloading from github collection")
    if (res := requests.get(req, timeout=60)).ok:
        con = res.json()
        return create(con)
    else:
        raise ReqURIEx(f"Could not get {req}")


def _catch_expected_err[
    **P, T: (ACR_DB_T, ACR_MIN_DB_T, CCNO_DB_T)
](loader: Callable[P, T]) -> Callable[P, T]:
    def load_f(*args: P.args, **kwargs: P.kwargs) -> T:
        version = CURRENT_VER
        if len(args) > 0 and isinstance(args, Iterable):
            v_2: list[Any]
            v_1, *v_2 = args
            if isinstance(v_1, str):
                version = v_1
            elif len(v_2) > 0 and isinstance(v_2[0], str):
                version = v_2[0]
        try:
            return loader(*args, **kwargs)
        except (ReqURIEx, ValJsonEx):
            warnings.warn(f"Could not load version: {version}", LoadWarn, stacklevel=2)
        return loader(
            *tuple(CURRENT_VER if isinstance(arg, str) else arg for arg in args),  # type: ignore
            **kwargs,
        )

    return load_f


@_catch_expected_err
def load_acr_db(version: str = CURRENT_VER, /) -> ACR_DB_T:
    return _load_data(version, "acr_db", parse_acr_db)


@_catch_expected_err
def load_min_acr_db(version: str = CURRENT_VER, /) -> ACR_MIN_DB_T:
    return _load_data(version, "acr_db", parse_min_acr_db)


@_catch_expected_err
def load_regex_db(acr_db: ACR_DB_T, version: str = CURRENT_VER, /) -> CCNO_DB_T:
    return _load_data(
        version, "regex_db", lambda reg_db: parse_regex_db(reg_db, acr_db, True)
    )


@_catch_expected_err
def load_catalogue_db(acr_db: ACR_DB_T, version: str = CURRENT_VER, /) -> CCNO_DB_T:
    return _load_data(
        version, "catalogue_db", lambda reg_db: parse_catalogue_db(reg_db, acr_db)
    )


def _dict_guard(database: Any, /) -> dict[str, Any]:
    if not isinstance(database, dict):
        raise ValJsonEx("JSON is not a dictionary")
    for key in database.keys():
        if not isinstance(key, str):
            raise ValJsonEx("JSON first level keys are not strings")
    return database


def parse_acr_db(acr_db: Any) -> ACR_DB_T:
    return validate_acr_db(_dict_guard(acr_db))


def parse_min_acr_db(acr_db: Any) -> ACR_MIN_DB_T:
    dict_db = _dict_guard(acr_db)
    validate_min_acr_db_schema(dict_db)
    return create_acr_min_db(dict_db)


def parse_regex_db(regex_db: Any, acr_db: ACR_DB_T, equal_sized: bool, /) -> CCNO_DB_T:
    return validate_regex_db(_dict_guard(regex_db), acr_db, equal_sized)


def parse_catalogue_db(regex_db: Any, acr_db: ACR_DB_T, /) -> CCNO_DB_T:
    return validate_catalogue_db(_dict_guard(regex_db), acr_db)
