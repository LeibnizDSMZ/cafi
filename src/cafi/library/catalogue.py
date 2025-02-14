from collections.abc import Iterable
from cafi.container.acr_db import AcrDbEntry, CatArgs
from cafi.container.fun.acr_db import replace_param_value
from cafi.container.links import CatalogueLink, LinkLevel

from cafi.container.fun.acr_db import url_to_str


def create_catalogue_link(acr_db: AcrDbEntry, args: CatArgs, /) -> Iterable[str]:
    for cat in acr_db.catalogue:
        yield replace_param_value(url_to_str(cat), args)


def _create_link_level(cat_link: list[str], hom_link: str, /) -> LinkLevel:
    match (cat_link, hom_link):
        case ([], ""):
            level = LinkLevel.emp
        case ([], _):
            level = LinkLevel.home
        case _:
            level = LinkLevel.cat
    return level


def create_ccno_links(
    acr_db: AcrDbEntry, args: CatArgs, exclude: tuple[LinkLevel, ...] = (), /
) -> CatalogueLink:
    if not acr_db.active or acr_db.deprecated:
        return CatalogueLink(level=LinkLevel.emp)
    cat_link, hom_link = [], ""
    if LinkLevel.cat not in exclude:
        cat_link = [
            replace_param_value(url_to_str(cat), args) for cat in acr_db.catalogue
        ]
    if LinkLevel.home not in exclude:
        hom_link = url_to_str(acr_db.homepage)
    return CatalogueLink(
        level=_create_link_level(cat_link, hom_link),
        catalogue=cat_link,
        homepage=hom_link,
    )
