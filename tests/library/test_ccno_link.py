import json

from cafi.container.acr_db import CatArgs
from cafi.container.links import LinkLevel
from cafi.library.catalogue import create_catalogue_link, create_ccno_links
from cafi.library.loader import parse_acr_db


pytest_plugins = ("tests.fixture.data", "tests.fixture.links")


class TestCcnoLink:
    def test_link_homepage(
        self, load_fix_acr_db: bytes, ccno_dsmz_1: tuple[int, CatArgs]
    ) -> None:
        cat_id, cat_args = ccno_dsmz_1
        acr_db = parse_acr_db(json.loads(load_fix_acr_db)).get(cat_id, None)
        dsmz_link = "https://www.dsmz.de/"
        assert acr_db is not None
        assert dsmz_link == create_ccno_links(acr_db, cat_args).homepage

    def test_link_catalogue(
        self, load_fix_acr_db: bytes, ccno_dsmz_1: tuple[int, CatArgs]
    ) -> None:
        cat_id, cat_args = ccno_dsmz_1
        acr_db = parse_acr_db(json.loads(load_fix_acr_db)).get(cat_id, None)
        dsmz_link = "https://www.dsmz.de/collection/catalogue/details/culture/DSM-1"
        assert acr_db is not None
        assert dsmz_link in create_ccno_links(acr_db, cat_args).catalogue

    def test_link_lvl_empty(
        self, load_fix_acr_db: bytes, ccno_iam_1: tuple[int, CatArgs]
    ) -> None:
        cat_id, cat_args = ccno_iam_1
        acr_db = parse_acr_db(json.loads(load_fix_acr_db)).get(cat_id, None)
        assert acr_db is not None
        assert LinkLevel.emp == create_ccno_links(acr_db, cat_args).level

    def test_link_lvl_catalogue(
        self, load_fix_acr_db: bytes, ccno_dsmz_1: tuple[int, CatArgs]
    ) -> None:
        cat_id, cat_args = ccno_dsmz_1
        acr_db = parse_acr_db(json.loads(load_fix_acr_db)).get(cat_id, None)
        assert acr_db is not None
        assert LinkLevel.cat == create_ccno_links(acr_db, cat_args).level

    def test_link_lvl_homepage(
        self, load_fix_acr_db: bytes, ccno_nrrl_1: tuple[int, CatArgs]
    ) -> None:
        cat_id, cat_args = ccno_nrrl_1
        acr_db = parse_acr_db(json.loads(load_fix_acr_db)).get(cat_id, None)
        assert acr_db is not None
        assert LinkLevel.home == create_ccno_links(acr_db, cat_args).level

    def test_link_simple_catalogue(
        self, load_fix_acr_db: bytes, ccno_nrrl_1: tuple[int, CatArgs]
    ) -> None:
        cat_id, cat_args = ccno_nrrl_1
        acr_db = parse_acr_db(json.loads(load_fix_acr_db)).get(cat_id, None)
        assert acr_db is not None
        assert len(list(create_catalogue_link(acr_db, cat_args))) == 0

    def test_link_simple_catalogue_zero_core(
        self, load_fix_acr_db: bytes, ccno_msu_418: tuple[int, CatArgs]
    ) -> None:
        cat_id, cat_args = ccno_msu_418
        acr_db = parse_acr_db(json.loads(load_fix_acr_db)).get(cat_id, None)
        assert acr_db is not None
        cat = "https://www.tbrcnetwork.org/microb_detail.php?code=MSCU_0418"
        print(set(create_catalogue_link(acr_db, cat_args)))
        assert cat in set(create_catalogue_link(acr_db, cat_args))

    def test_link_simple_catalogue_split_core(
        self, load_fix_acr_db: bytes, ccno_lmg_1_1: tuple[int, CatArgs]
    ) -> None:
        cat_id, cat_args = ccno_lmg_1_1
        acr_db = parse_acr_db(json.loads(load_fix_acr_db)).get(cat_id, None)
        assert acr_db is not None
        cat = "https://bccm.belspo.be/page/lmg-catalogue-display/fields/name/LMG 1t1"
        assert cat in set(create_catalogue_link(acr_db, cat_args))
