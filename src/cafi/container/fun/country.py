from importlib import resources

from cafi import data


def load_active_countries() -> set[str]:
    with resources.files(data).joinpath("country_codes.txt").open("r") as fhd:
        return {ccs for cc in fhd.readlines() if len(ccs := cc.strip()) == 2}
