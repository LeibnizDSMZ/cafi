from typing import Final, TypeVar
import re

from jsonschema import ValidationError, validate
from knacr.container.acr_db import AcrDb
from knacr.container.fun.acr_db import check_uri_template, create_acr_db
from knacr.errors.custom_exceptions import ValJsonEx

from knacr.schemas.acr_db import ACR_DB, ACR_MIN_DB

_TJ = TypeVar("_TJ")


_ACR: Final[re.Pattern[str]] = re.compile("^[A-Z:]+$")
_ACR_SPL: Final[re.Pattern[str]] = re.compile(":")


def _check_unique(
    uniqueness: set[tuple[str, str, str, str]], acr_db: AcrDb, /
) -> tuple[str, str, str, str]:
    unique_id = (acr_db.code, acr_db.acr, acr_db.name, acr_db.country)
    if unique_id in uniqueness:
        raise ValJsonEx(f"{unique_id} was seen more than once, but should be unique")
    return unique_id


def _check_changed_to_id(all_ids: set[int], acr_db: AcrDb, /) -> None:
    for acr_cha in acr_db.acr_changed_to:
        if acr_cha.id not in all_ids:
            raise ValJsonEx(f"missing 'changed to' acr id {acr_cha.id}")


def _check_missing_link_id(all_ids: set[int], /) -> None:
    for ind in range(1, max(all_ids) + 1):
        if ind not in all_ids:
            raise ValJsonEx(f"missing acr id {ind}")


def _check_acr(acr: str, /) -> None:
    if _ACR.match(acr) is None:
        raise ValJsonEx(f"{acr} does not comply to acronym standards ^[A-Z:]+$")


def _check_acr_in_reg(acr: str, ccno_reg: str, /) -> None:
    for acr_part in _ACR_SPL.split(acr):
        if acr_part not in ccno_reg:
            raise ValJsonEx(f"{acr} mismatches the acronym in regex: {ccno_reg}")


def _check_loops(cur: AcrDb, full: dict[int, AcrDb], ids: set[int], /) -> None:
    for changed in cur.acr_changed_to:
        changed_to = full.get(changed.id, None)
        if changed.id in ids:
            raise ValJsonEx(f"loop detected in {ids} for {cur.acr}")
        if changed_to is None:
            raise ValJsonEx(f"missing changed to id {changed.id} for acronym {cur.acr}")
        ids.add(changed.id)
        _check_loops(changed_to, full, ids)


def _validate_acr_db_dc(to_eval_acr: dict[int, AcrDb], /) -> None:
    all_ids = set(to_eval_acr.keys())
    _check_missing_link_id(all_ids)
    uniqueness: set[tuple[str, str, str, str]] = set()
    for acr_id, acr_db in to_eval_acr.items():
        check_uri_template(acr_db.catalogue)
        uniqueness.add(_check_unique(uniqueness, acr_db))
        _check_changed_to_id(all_ids, acr_db)
        _check_acr(acr_db.acr)
        _check_acr_in_reg(acr_db.acr, acr_db.regex_ccno)
        _check_loops(acr_db, to_eval_acr, {acr_id})


def validate_acr_db_schema(to_eval: _TJ, /) -> None:
    if not isinstance(to_eval, dict):
        raise ValJsonEx(f"expected a dictionary, got {type(to_eval)}")
    try:
        validate(instance=to_eval, schema=ACR_DB)
        acr_db = create_acr_db(to_eval)
        if len(acr_db) > 0:
            _validate_acr_db_dc(acr_db)
    except ValidationError as exc:
        raise ValJsonEx(
            f"Acronym Data is incorrectly formatted! [{exc.message}]"
        ) from exc


def validate_min_acr_db_schema(to_eval: _TJ, /) -> None:
    if not isinstance(to_eval, dict):
        raise ValJsonEx(f"expected a dictionary, got {type(to_eval)}")
    try:
        validate(instance=to_eval, schema=ACR_MIN_DB)
    except ValidationError as exc:
        raise ValJsonEx(
            f"Acronym Data is incorrectly formatted! [{exc.message}]"
        ) from exc
