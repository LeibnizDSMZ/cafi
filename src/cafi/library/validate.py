from typing import Any, Callable, Final
import re

from pydantic import ValidationError
from cafi.constants.types import ACR_DB_T, CCNO_DB_T

from cafi.container.acr_db import (
    ACR_MIN_CON,
    CCNO_DB_CON,
    CCNO_DB_KEYS,
    AcrCoreReg,
    AcrDbEntry,
    ACR_DB_KEYS,
)
from cafi.container.fun.acr_db import check_uri_template, create_acr_db, create_ccno_db
from cafi.container.fun.format import url_to_str
from cafi.errors.custom_exceptions import ValJsonEx


_ACR: Final[re.Pattern[str]] = re.compile(r"^[A-Z:]+$")
_NON_WORD: Final[re.Pattern[str]] = re.compile(r"[^A-Za-z]+")
_ACR_SPL: Final[re.Pattern[str]] = re.compile(r":")
_CORE_ID: Final[re.Pattern[str]] = re.compile(r"^\d+(\D\d+)*$")
_CL_REGEX: Final[re.Pattern[str]] = re.compile(r"[()\][]")

type _UNIQUE_GEN = tuple[str, str, str, str]
type _UNIQUE_GID = tuple[str, str, str]


def _check_unique_gen(unique: set[_UNIQUE_GEN], acr_db: AcrDbEntry, /) -> _UNIQUE_GEN:
    unique_id = (acr_db.code, acr_db.acr, acr_db.name, acr_db.country)
    if unique_id in unique:
        raise ValJsonEx(f"{unique_id} was seen more than once, but should be unique")
    return unique_id


def _check_unique_gid(
    unique: set[_UNIQUE_GID],
    acr_db: AcrDbEntry,
    gid: Callable[[AcrDbEntry], str],
    gid_type: str,
    /,
) -> _UNIQUE_GID:
    if gid(acr_db):
        return "_", "_", "_"
    unique_id = (acr_db.acr, gid(acr_db), gid_type)
    if unique_id in unique:
        raise ValJsonEx(f"{unique_id} was seen more than once, but should be unique")
    return unique_id


def _check_active(cur_acr_con: AcrDbEntry, /) -> None:
    if not cur_acr_con.active and url_to_str(cur_acr_con.homepage) != "":
        raise ValJsonEx(
            f"{cur_acr_con.acr}: 'inactive' BRC can not have a 'homepage' link"
        )
    if not cur_acr_con.active and len(cur_acr_con.catalogue) != 0:
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
    first, *_ = _ACR_SPL.split(acr)
    first_reg = f"\\^{first}"
    if re.match(first_reg, ccno_reg, re.I) is None:
        raise ValJsonEx(f"regex {ccno_reg} does not start with {first_reg} [{acr}]")
    compact_reg = _NON_WORD.sub("", ccno_reg)
    compact_acr = _ACR_SPL.sub("", acr).strip()
    if re.match(compact_acr, compact_reg, re.I) is None:
        raise ValJsonEx(f"{compact_acr} mismatches the acronym in regex: {compact_reg}")


def _check_regex_start_end(reg_full: list[str], reg_part: list[str], /) -> None:
    for reg in reg_full:
        if reg[0] != r"^" or reg[-1] != r"$":
            raise ValJsonEx(f"invalid full regex {reg}")
    for reg in reg_part:
        if reg[0] == r"^" or reg[-1] == r"$":
            raise ValJsonEx(f"invalid part regex {reg}")


def _check_or_order(regex: str, bid: int, /) -> None:
    if "|" in regex:
        cl_reg = _CL_REGEX.sub("", regex)
        ors = cl_reg.split("|")
        for cnt, or_ch in enumerate(ors):
            for com_ch in ors[cnt + 1 :]:
                if com_ch.startswith(or_ch):
                    raise ValJsonEx(
                        f"regex for collection {bid} has a smaller"
                        f" substring before the longer string {or_ch} - {regex}"
                    )


def _check_regex(r_ccno: str, r_id: AcrCoreReg, bid: int, /) -> None:
    _check_regex_start_end([r_ccno, r_id.full], [r_id.core, *r_id.pre, *r_id.suf])
    if len(r_id.full) <= 2:
        raise ValJsonEx(f"regex for id must be longer than 2 {r_id.full}")
    if r_id.full[1:] not in r_ccno:
        raise ValJsonEx(
            f"regex for ccno must contain regex for id: {r_id.full} -> {r_ccno}"
        )
    pre_suf = re.compile(rf"^(.*){re.escape(r_id.core)}(.*)$").match(r_id.full[1:-1])
    if pre_suf is None or len(pre_suf.groups()) < 2:
        raise ValJsonEx(
            f"regex for id must contain regex for core: {r_id.core} -> {r_id.full}"
        )
    pre, *_, suf = pre_suf.groups()
    for typ, fps, rps in [("prefix", pre, r_id.pre), ("suffix", suf, r_id.suf)]:
        if not isinstance(fps, str) or rps not in fps or (rps == "" and fps != ""):
            raise ValJsonEx(f"{typ} defines a different {rps} regex than the full id")
    _check_or_order(r_id.suf, bid)
    _check_or_order(r_id.pre, bid)


def _check_loops(cur: AcrDbEntry, full: ACR_DB_T, ids: set[int], /) -> None:
    for changed in cur.acr_changed_to:
        changed_to = full.get(changed.id, None)
        if changed.id in ids:
            raise ValJsonEx(f"loop detected in {ids} for {cur.acr}")
        if changed_to is None:
            raise ValJsonEx(f"missing changed to id {changed.id} for acronym {cur.acr}")
        ids.add(changed.id)
        _check_loops(changed_to, full, ids)


def _check_ids_overlap(ccno_db: set[int], acr_db: set[int], equal_sized: bool, /) -> None:
    if len(mis_ids := ccno_db - acr_db) != 0:
        raise ValJsonEx(f"ccno db missing the following ids: {mis_ids!s}")
    if equal_sized and len(ccno_db) != len(acr_db):
        mis_ids = acr_db - ccno_db
        raise ValJsonEx(f"ccno db and acronym db have different sizes: {mis_ids}")


def _check_malformed_list(reg_db: CCNO_DB_T, /) -> None:
    for reg_id, reg_con in reg_db.items():
        filtered = list(filter(lambda ccno: ccno != "", reg_con))
        if len(filtered) == 0:
            raise ValJsonEx(f"{reg_id} does not have any valid examples")
        if len(filtered) != len(set(filtered)):
            raise ValJsonEx(f"{reg_id} does have duplicate examples")


def _apply_regex(acr_id: int, acr_con: AcrDbEntry, ccnos: list[str], /) -> None:
    reg_ccno = re.compile(acr_con.regex_ccno)
    reg_ccno_id = re.compile(acr_con.regex_id.full[1:])
    reg_core_id = re.compile(rf"^.*?({acr_con.regex_id.core}).*$")
    for ccno in ccnos:
        core_id_m = reg_core_id.match(ccno)
        if core_id_m is None:
            raise ValJsonEx(f"CCNo {ccno} contains a invalid core id - {acr_id}")
        core_id, *_ = core_id_m.groups()
        if not isinstance(core_id, str) or _CORE_ID.match(core_id) is None:
            raise ValJsonEx(
                f"CCNo {ccno} contains a invalid core id [{core_id}] - {acr_id}"
            )
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
    uni_gen: set[tuple[str, str, str, str]] = set()
    uni_gid: set[tuple[str, str, str]] = set()
    for acr_id, acr_con in acr_db.items():
        check_uri_template(acr_con.catalogue)
        uni_gen.add(_check_unique_gen(uni_gen, acr_con))
        uni_gid.add(_check_unique_gid(uni_gid, acr_con, lambda db: db.ror, "ror"))
        uni_gid.add(_check_unique_gid(uni_gid, acr_con, lambda db: db.gbif, "gbif"))
        _check_db_composition(acr_con, acr_db)
        _check_acr(acr_con.acr)
        _check_regex(acr_con.regex_ccno, acr_con.regex_id, acr_id)
        _check_acr_in_reg(acr_con.acr, acr_con.regex_ccno)
        _check_loops(acr_con, acr_db, {acr_id})


def _validate_regex_dc(reg_db: CCNO_DB_T, acr_db: ACR_DB_T, equal_sized: bool, /) -> None:
    all_reg_ids = set(reg_db.keys())
    _check_missing_link_id(all_reg_ids)
    _check_malformed_list(reg_db)
    _check_ids_overlap(all_reg_ids, set(acr_db.keys()), equal_sized)
    for acr_id, acr_con in acr_db.items():
        if acr_id in reg_db:
            _apply_regex(acr_id, acr_con, reg_db[acr_id])


def _validate_catalogue_dc(cat_db: CCNO_DB_T, acr_db: ACR_DB_T, /) -> None:
    all_cat_ids = set(cat_db.keys())
    all_acr_ids = set(cid for cid, adb in acr_db.items() if len(adb.catalogue) != 0)
    _check_malformed_list(cat_db)
    _check_ids_overlap(all_cat_ids, all_acr_ids, True)
    for acr_id, acr_con in acr_db.items():
        if acr_id in cat_db:
            _apply_regex(acr_id, acr_con, cat_db[acr_id])


def validate_acr_db(to_eval: dict[str, Any], /) -> ACR_DB_T:
    msg = "Acronym database is incorrectly formatted!"
    try:
        ACR_DB_KEYS.validate_python(list(to_eval.keys()))
        acr_db = create_acr_db(to_eval)
    except ValidationError as exc:
        raise ValJsonEx(f"{msg} [{exc!s}]") from exc
    if len(acr_db) > 0:
        _validate_acr_db_dc(acr_db)
    return acr_db


def validate_min_acr_db_schema(to_eval: dict[str, Any], /) -> None:
    msg = "Acronym min database is incorrectly formatted!"
    try:
        ACR_DB_KEYS.validate_python(list(to_eval.keys()))
        ACR_MIN_CON.validate_python(list(to_eval.values()))
    except ValidationError as exc:
        raise ValJsonEx(f"{msg} [{exc!s}]") from exc


def _validate_ccno_db_struct(msg: str, to_eval: dict[str, Any], /) -> None:
    try:
        CCNO_DB_KEYS.validate_python(list(to_eval.keys()))
        CCNO_DB_CON.validate_python(list(to_eval.values()))
    except ValidationError as exc:
        raise ValJsonEx(f"{msg} [{exc!s}]") from exc


def validate_regex_db(
    to_eval: dict[str, Any], acr_db: ACR_DB_T, equal_sized: bool, /
) -> CCNO_DB_T:
    msg = "Regex data is incorrectly formatted!"
    _validate_ccno_db_struct(msg, to_eval)
    regex_db = create_ccno_db(to_eval)
    _validate_regex_dc(regex_db, acr_db, equal_sized)
    return regex_db


def validate_catalogue_db(to_eval: dict[str, Any], acr_db: ACR_DB_T, /) -> CCNO_DB_T:
    """
    Validates and creates a catalogue database from input data.

    Args:
        to_eval (dict[str, Any]): The input dictionary containing raw catalogue data.
        acr_db (ACR_DB_T): Acronym database used for validation purposes.

    Returns:
        CCNO_DB_T: The validated catalogue database.

    Raises:
        Exception: If the validation process fails, an exception is raised with
            a message indicating incorrect formatting.
    """
    msg = "Catalogue data is incorrectly formatted!"
    _validate_ccno_db_struct(msg, to_eval)
    catalogue = create_ccno_db(to_eval)
    _validate_catalogue_dc(catalogue, acr_db)
    return catalogue
