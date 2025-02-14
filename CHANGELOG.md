## v0.8.0 (2025-02-14)

### Feat

- rename project to cafi
- add CIRM-BRFM catalogue

### Fix

- correct args check to iterable

## v0.7.0 (2025-01-17)

### Feat

- add ITM- CCNo structure
- add more valid suffix to ccap
- add T catalogue link to CAIM
- add core id verification
- update caim links
- move to regex in pre and suf
- migrate to pydantic
- remove ptcc homepage due to timeout
- readd caim and remove fgsc
- disable kccm and caim websites
- add domain checks for catalogues
- update links and add multiple catalogue links support

### Fix

- fix unpack error
- change init to init_py
- change main_run entrypoint to acr_db
- correct main call with default variables
- correct url for ncim homepage
- add prefix suffix regex or order checks
- update caim catalogue ccno
- add missing core regex and remove redundant one
- correct suffix prefix regex
- change CDBB link protocol
- update collection links
- update UKHSA links

### Refactor

- update pyproject.toml structure for dependencies
- improve lefthook
- add comments to dev types
- change author mail
- update license
- use protocol for url_to_str
- move to url instead of http_url
- add optional spaces after prefix
- add optional spaces before suffix
- change ncim homepage
- move to new generics and type structure
- improve readme badges
- add missing __init__.py
- move functions from container module

## v0.6.1 (2024-01-25)

### Fix

- modify UKHSA

### Refactor

- remove link from ror

## v0.6.0 (2023-12-01)

### Feat

- add new examples to uk health security agency
- update UKHSA web links
- change two BRCs homepages
- add library name to print
- add exclude level to ccno links
- add incompatibility failsafe
- add catalogue example db
- update acronyms to 101
- add gbif uuid support

### Fix

- correct SAG catalogue link
- correct catalogue links
- add zeros to NBRC

### Refactor

- move versions to constants folder

## v0.5.1 (2023-11-22)

### Fix

- correct data path for the main branch

## v0.5.0 (2023-11-22)

### Feat

- update db to 97 collections
- check whether duplicates exist in the test examples
- add test data for regex checks
- check acronym db composition
- ignore deprecated ror uniqueness
- update to 90 acronyms
- load current db version locally
- add current version and use it in the loader
- update ror data in acr db
- add ror to schema
- add ror to db
- add function to fill core ids with leading zeroes
- add detailed link creation function

### Fix

- reduce minlength for id full to 3
- remove sym link to data

### Refactor

- update project github uri

## v0.4.1 (2023-08-17)

### Fix

- remove red. print and check for none group

## v0.4.0 (2023-07-30)

### Feat

- add core id separation

### Refactor

- prepare for bump

## v0.3.1 (2023-07-28)

### Fix

- remove load_min_acr_db function call from module

## v0.3.0 (2023-07-23)

### Feat

- add new regex_id structure
- check whether regex_id is in regex_ccno
- add deprecated status to acr

### Refactor

- change acr_syn to acr_synonym and improve code structure

## v0.2.1 (2023-07-18)

## v0.2.0 (2023-07-16)

### Feat

- add country def and new culture collections
- add CFBP and VKM cultures

### Fix

- Improve f-string

## v0.1.0 (2023-05-24)

## v0.1.0-rc2 (2023-05-24)

### Feat

- Check for missing 'changed to' ids
- Add uniqueness check
- Mock request for loader
- First release

### Fix

- Add missing required fields
- Change the data license to CC-BY

### Refactor

- Load data only in sdist
- Change project structure
