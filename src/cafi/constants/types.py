from cafi.container.acr_db import AcrDbEntry


type ACR_DB_T = dict[int, AcrDbEntry]
type ACR_MIN_DB_T = dict[int, tuple[str, bool]]
type CCNO_DB_T = dict[int, list[str]]
