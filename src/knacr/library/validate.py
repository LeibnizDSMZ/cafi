from typing import Final, TypeAlias, TypeVar
import re

from jsonschema import ValidationError, validate
from knacr.constants.types import ACR_DB_T, REG_DB_T

from knacr.container.acr_db import AcrCoreReg, AcrDbEntry
from knacr.container.fun.acr_db import check_uri_template, create_acr_db, create_regex_db
from knacr.errors.custom_exceptions import ValJsonEx
from knacr.schemas.acr_db import ACR_DB, ACR_MIN_DB, REGEX_DB


_TJ = TypeVar("_TJ")


_ACR: Final[re.Pattern[str]] = re.compile("^[A-Z:]+$")
_ACR_SPL: Final[re.Pattern[str]] = re.compile(":")
_UNIQUE_GEN: TypeAlias = tuple[str, str, str, str]
_UNIQUE_ROR: TypeAlias = tuple[str, str]


def _check_unique_gen(unique: set[_UNIQUE_GEN], acr_db: AcrDbEntry, /) -> _UNIQUE_GEN:
    unique_id = (acr_db.code, acr_db.acr, acr_db.name, acr_db.country)
    if unique_id in unique:
        raise ValJsonEx(f"{unique_id} was seen more than once, but should be unique")
    return unique_id


def _check_unique_ror(unique: set[_UNIQUE_ROR], acr_db: AcrDbEntry, /) -> _UNIQUE_ROR:
    if acr_db.ror == "":
        return "_", "_"
    unique_id = (acr_db.acr, acr_db.ror)
    if unique_id in unique:
        raise ValJsonEx(f"{unique_id} was seen more than once, but should be unique")
    return unique_id


def _check_active(cur_acr_con: AcrDbEntry, /) -> None:
    if not cur_acr_con.active and cur_acr_con.homepage != "":
        raise ValJsonEx(
            f"{cur_acr_con.acr}: 'inactive' BRC can not have a 'homepage' link"
        )
    if not cur_acr_con.active and cur_acr_con.catalogue != "":
        raise ValJsonEx(
            f"{cur_acr_con.acr}: 'inactive' BRC can not have a 'catalogue' link"
        )
    if cur_acr_con.active and len(cur_acr_con.acr_changed_to) > 0:
        raise ValJsonEx(
            f"{cur_acr_con.acr}: 'active' BRC can not have a 'changed to' field"
        )


def _check_deprecated(cur_acr_con: AcrDbEntry, /) -> None:
    if cur_acr_con.deprecated and len(cur_acr_con.acr_synonym) > 0:
        raise ValJsonEx(
            f"{cur_acr_con.acr}: 'deprecated' can not have a 'synonyms' field"
        )
    if cur_acr_con.deprecated and len(cur_acr_con.acr_changed_to) > 0:
        raise ValJsonEx(
            f"{cur_acr_con.acr}: 'deprecated' can not have a 'changed to' field"
        )
    if cur_acr_con.deprecated and cur_acr_con.active:
        raise ValJsonEx(
            f"{cur_acr_con.acr}: 'deprecated' can not have an 'active' status"
        )


def _check_changed_to_id(cur_acr_con: AcrDbEntry, acr_db: ACR_DB_T, /) -> None:
    changed_to_ids = set()
    for acr_cha in cur_acr_con.acr_changed_to:
        next_acr_con = acr_db.get(acr_cha.id, None)
        if next_acr_con is None:
            raise ValJsonEx(f"missing 'changed to' acr id {acr_cha.id}")
        if acr_cha.id in changed_to_ids:
            raise ValJsonEx(f"found duplicate acr id {acr_cha.id} in 'changed to'")
        changed_to_ids.add(acr_cha.id)
        if next_acr_con.deprecated:
            raise ValJsonEx(
                f"{cur_acr_con.acr}: acr can not change into "
                + f"a deprecated acr {acr_cha.id}"
            )


def _check_db_composition(cur_acr_con: AcrDbEntry, acr_db: ACR_DB_T, /) -> None:
    _check_changed_to_id(cur_acr_con, acr_db)
    _check_deprecated(cur_acr_con)
    _check_active(cur_acr_con)


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


def _check_regex_start_end(reg_full: list[str], reg_part: list[str], /) -> None:
    for reg in reg_full:
        if reg[0] != r"^" or reg[-1] != r"$":
            raise ValJsonEx(f"invalid full regex {reg}")
    for reg in reg_part:
        if reg[0] == r"^" or reg[-1] == r"$":
            raise ValJsonEx(f"invalid part regex {reg}")


def _check_list_uniqueness(typ: str, con: list[str], /) -> None:
    if len(set(con)) != len(con):
        raise ValJsonEx(f"duplicates in {typ} - {con} found")


def _check_pre_suf(typ: str, pr_su: str, pr_su_con: list[str], /) -> None:
    if pr_su != "" and len(pr_su_con) == 0:
        raise ValJsonEx(f"{typ} defines {pr_su} but given list is empty")
    for ps_el in pr_su_con:
        if ps_el not in pr_su:
            raise ValJsonEx(f"given list for {typ} has unknown element {ps_el}")


def _check_regex(r_ccno: str, r_id: AcrCoreReg, /) -> None:
    _check_list_uniqueness("prefix", r_id.pre)
    _check_list_uniqueness("suffix", r_id.suf)
    _check_regex_start_end([r_ccno, r_id.full], [r_id.core, *r_id.pre, *r_id.suf])
    if len(r_id.full) <= 2:
        raise ValJsonEx(f"regex for id must be longer than 2 {r_id.full}")
    if r_id.full[1:] not in r_ccno:
        raise ValJsonEx(
            f"regex for ccno must contain regex for id: {r_id.full} -> {r_ccno}"
        )
    if (
        pre_suf := re.compile(rf"^(.*){re.escape(r_id.core)}(.*)$").match(r_id.full)
    ) is not None:
        pre, suf = pre_suf.groups()
        _check_pre_suf("prefix", pre[1:], r_id.pre)
        _check_pre_suf("suffix", suf[0:-2], r_id.suf)
    else:
        raise ValJsonEx(
            f"regex for id must contain regex for core: {r_id.core} -> {r_id.full}"
        )


def _check_loops(cur: AcrDbEntry, full: ACR_DB_T, ids: set[int], /) -> None:
    for changed in cur.acr_changed_to:
        changed_to = full.get(changed.id, None)
        if changed.id in ids:
            raise ValJsonEx(f"loop detected in {ids} for {cur.acr}")
        if changed_to is None:
            raise ValJsonEx(f"missing changed to id {changed.id} for acronym {cur.acr}")
        ids.add(changed.id)
        _check_loops(changed_to, full, ids)


def _check_ids_overlap(reg_db: set[int], acr_db: set[int], equal_sized: bool, /) -> None:
    if equal_sized and len(reg_db) != len(acr_db):
        raise ValJsonEx("regex db and acronym db have different sizes")
    if len(mis_ids := reg_db - acr_db) != 0:
        raise ValJsonEx(f"acronym db missing the following ids: {mis_ids!s}")


def _check_malformed_list(reg_db: REG_DB_T, /) -> None:
    for reg_id, reg_con in reg_db.items():
        filtered = list(filter(lambda ccno: ccno != "", reg_con))
        if len(filtered) == 0:
            raise ValJsonEx(f"{reg_id} does not have any valid examples")
        if len(filtered) != len(set(filtered)):
            raise ValJsonEx(f"{reg_id} does have duplicate examples")


def _apply_regex(acr_id: int, acr_con: AcrDbEntry, ccnos: list[str], /) -> None:
    reg_ccno = re.compile(acr_con.regex_ccno)
    reg_ccno_id = re.compile(acr_con.regex_id.full[1:])
    for ccno in ccnos:
        if reg_ccno.match(ccno) is None:
            raise ValJsonEx(
                f"CCNo {ccno} does not match the default ccno regex - ID {acr_id}"
            )
        if reg_ccno_id.search(ccno) is None:
            raise ValJsonEx(
                f"CCNo {ccno} does not match the default ccno id regex - ID {acr_id}"
            )


def _validate_acr_db_dc(acr_db: ACR_DB_T, /) -> None:
    all_ids = set(acr_db.keys())
    _check_missing_link_id(all_ids)
    unique_gen: set[tuple[str, str, str, str]] = set()
    unique_ror: set[tuple[str, str]] = set()
    for acr_id, acr_con in acr_db.items():
        check_uri_template(acr_con.catalogue)
        unique_gen.add(_check_unique_gen(unique_gen, acr_con))
        unique_ror.add(_check_unique_ror(unique_ror, acr_con))
        _check_db_composition(acr_con, acr_db)
        _check_acr(acr_con.acr)
        _check_regex(acr_con.regex_ccno, acr_con.regex_id)
        _check_acr_in_reg(acr_con.acr, acr_con.regex_ccno)
        _check_loops(acr_con, acr_db, {acr_id})


def _validate_regex_dc(reg_db: REG_DB_T, acr_db: ACR_DB_T, equal_sized: bool, /) -> None:
    all_reg_ids = set(reg_db.keys())
    _check_missing_link_id(all_reg_ids)
    _check_malformed_list(reg_db)
    _check_ids_overlap(all_reg_ids, set(acr_db.keys()), equal_sized)
    for acr_id, acr_con in acr_db.items():
        if acr_id in reg_db:
            _apply_regex(acr_id, acr_con, reg_db[acr_id])


def validate_acr_db(to_eval: _TJ, /) -> ACR_DB_T:
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
    else:
        return acr_db


def validate_min_acr_db_schema(to_eval: _TJ, /) -> None:
    if not isinstance(to_eval, dict):
        raise ValJsonEx(f"expected a dictionary, got {type(to_eval)}")
    try:
        validate(instance=to_eval, schema=ACR_MIN_DB)
    except ValidationError as exc:
        raise ValJsonEx(
            f"Acronym Data is incorrectly formatted! [{exc.message}]"
        ) from exc


def validate_regex_db(to_eval: _TJ, acr_db: ACR_DB_T, equal_sized: bool, /) -> REG_DB_T:
    if not isinstance(to_eval, dict):
        raise ValJsonEx(f"expected a dictionary, got {type(to_eval)}")
    try:
        validate(instance=to_eval, schema=REGEX_DB)
        regex_db = create_regex_db(to_eval)
        _validate_regex_dc(regex_db, acr_db, equal_sized)
    except ValidationError as exc:
        raise ValJsonEx(f"Regex Data is incorrectly formatted! [{exc.message}]") from exc
    else:
        return regex_db
