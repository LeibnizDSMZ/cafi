import json
import pytest

from cafi.errors.custom_exceptions import ValJsonEx
from cafi.library.loader import parse_acr_db, parse_min_acr_db, parse_regex_db


pytest_plugins = ("tests.fixture.data",)


class TestAcrDb:
    def test_acr_db(self, load_fix_acr_db: bytes) -> None:
        try:
            parse_acr_db(json.loads(load_fix_acr_db))
        except ValJsonEx as val_ex:
            pytest.fail(f"acr data malformed - {val_ex.message}")

    def test_acr_db_stability(
        self, load_fix_acr_db: bytes, load_fix_min_main_acr_db: bytes
    ) -> None:
        main_db = parse_min_acr_db(json.loads(load_fix_min_main_acr_db))
        new_db = parse_acr_db(json.loads(load_fix_acr_db))
        for acr_id, (acr, dep) in main_db.items():
            acr_db = new_db.get(acr_id, None)
            if acr_db is None:
                pytest.fail(f"missing main id in the new database - {acr_id}")
            elif acr != acr_db.acr:
                pytest.fail(f"acr changed for id {acr_id} - {acr} -> {acr_db.acr}")
            elif dep and not acr_db.deprecated:
                pytest.fail(f"acr [{acr_id}] can not be re-validated")

    def test_regex_stability(
        self,
        load_fix_acr_db: bytes,
        load_fix_main_regex_db: bytes,
        load_fix_regex_db: bytes,
    ) -> None:
        acr_db = parse_acr_db(json.loads(load_fix_acr_db))
        main_reg = parse_regex_db(json.loads(load_fix_main_regex_db), acr_db, False)
        cur_reg = parse_regex_db(json.loads(load_fix_regex_db), acr_db, True)
        for acr_id in main_reg.keys():
            if cur_reg.get(acr_id, None) is None:
                pytest.fail(f"missing main id in the new database - {acr_id}")
