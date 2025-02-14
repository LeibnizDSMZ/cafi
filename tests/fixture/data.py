from importlib import resources
import subprocess
import pytest
from cafi import data


@pytest.fixture
def load_fix_acr_db() -> bytes:
    with resources.files(data).joinpath("acr_db.json").open("rb") as fhd:
        return fhd.read()


@pytest.fixture
def load_fix_regex_db() -> bytes:
    with resources.files(data).joinpath("regex_db.json").open("rb") as fhd:
        return fhd.read()


@pytest.fixture
def load_fix_catalogue_db() -> bytes:
    with resources.files(data).joinpath("catalogue_db.json").open("rb") as fhd:
        return fhd.read()


def _get_data_from_main_branch(data_name: str, proj: str = "cafi", /) -> bytes:
    sub_proc = subprocess.Popen(  # noqa: S603
        ["git", "show", f"origin/main:src/{proj}/data/{data_name}.json"],  # noqa: S607
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    out, err = sub_proc.communicate()
    if not out or err:
        if proj != "knacr":
            return _get_data_from_main_branch(data_name, "knacr")
        pytest.fail(f"could not read from main {data_name} {err!s}")
    return out.encode("utf-8")


@pytest.fixture
def load_fix_min_main_acr_db() -> bytes:
    return _get_data_from_main_branch("acr_db")


@pytest.fixture
def load_fix_main_regex_db() -> bytes:
    return _get_data_from_main_branch("regex_db")
