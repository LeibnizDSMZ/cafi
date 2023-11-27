import json
from unittest.mock import MagicMock, patch
import pytest
from knacr.constants.versions import CURRENT_VER, LATEST_VER, STABLE_VER

from knacr.errors.custom_exceptions import ValJsonEx, ReqURIEx
from knacr.library.loader import (
    load_acr_db,
    load_min_acr_db,
    load_regex_db,
    load_catalogue_db,
    parse_acr_db,
)

pytest_plugins = ("tests.fixture.data",)


class TestLoader:
    @patch("knacr.library.loader.requests")
    def test_load_acr_db_success(self, req: MagicMock, load_fix_acr_db: bytes) -> None:
        resp = MagicMock()
        resp.ok = True
        resp.json.return_value = json.loads(load_fix_acr_db)
        req.get.return_value = resp
        try:
            load_acr_db(LATEST_VER)
        except (ValJsonEx, ReqURIEx) as val_ex:
            pytest.fail(f"acr data malformed - {val_ex.message}")

    @patch("knacr.library.loader.requests")
    def test_load_acr_db_fail(self, req: MagicMock) -> None:
        resp = MagicMock()
        resp.ok = False
        req.get.return_value = resp
        with pytest.raises(ReqURIEx):
            load_acr_db("never_tag")

    @patch("knacr.library.loader.requests")
    def test_load_acr_db_current_success(self, req: MagicMock) -> None:
        resp = MagicMock()
        resp.ok = False
        req.get.return_value = resp
        try:
            load_acr_db(CURRENT_VER)
        except (ValJsonEx, ReqURIEx) as val_ex:
            pytest.fail(f"acr data malformed - {val_ex.message}")

    @patch("knacr.library.loader.requests")
    def test_load_min_acr_db_fail(self, req: MagicMock) -> None:
        resp = MagicMock()
        resp.ok = False
        req.get.return_value = resp
        with pytest.raises(ReqURIEx):
            load_min_acr_db("never_tag")

    @patch("knacr.library.loader.requests")
    def test_load_min_acr_db_success(
        self, req: MagicMock, load_fix_acr_db: bytes
    ) -> None:
        resp = MagicMock()
        resp.ok = True
        resp.json.return_value = json.loads(load_fix_acr_db)
        req.get.return_value = resp
        try:
            load_min_acr_db(STABLE_VER)
        except (ValJsonEx, ReqURIEx) as val_ex:
            pytest.fail(f"acr data malformed - {val_ex.message}")

    @patch("knacr.library.loader.requests")
    def test_load_regex_db_fail(self, req: MagicMock) -> None:
        resp = MagicMock()
        resp.ok = False
        req.get.return_value = resp
        with pytest.raises(ReqURIEx):
            load_regex_db({}, "never_tag")

    @patch("knacr.library.loader.requests")
    def test_load_regex_db_success(
        self, req: MagicMock, load_fix_regex_db: bytes, load_fix_acr_db: bytes
    ) -> None:
        resp = MagicMock()
        resp.ok = True
        resp.json.return_value = json.loads(load_fix_regex_db)
        req.get.return_value = resp
        acr_db = parse_acr_db(json.loads(load_fix_acr_db))
        try:
            load_regex_db(acr_db, STABLE_VER)
        except (ValJsonEx, ReqURIEx) as val_ex:
            pytest.fail(f"regex data malformed - {val_ex.message}")

    @patch("knacr.library.loader.requests")
    def test_load_catalogue_db_fail(self, req: MagicMock) -> None:
        resp = MagicMock()
        resp.ok = False
        req.get.return_value = resp
        with pytest.raises(ReqURIEx):
            load_catalogue_db({}, "never_tag")

    @patch("knacr.library.loader.requests")
    def test_load_catalogue_db_success(
        self, req: MagicMock, load_fix_catalogue_db: bytes, load_fix_acr_db: bytes
    ) -> None:
        resp = MagicMock()
        resp.ok = True
        resp.json.return_value = json.loads(load_fix_catalogue_db)
        req.get.return_value = resp
        acr_db = parse_acr_db(json.loads(load_fix_acr_db))
        try:
            load_catalogue_db(acr_db, STABLE_VER)
        except (ValJsonEx, ReqURIEx) as val_ex:
            pytest.fail(f"regex data malformed - {val_ex.message}")
