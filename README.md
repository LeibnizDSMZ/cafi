# Collection acronyms for identification - cafi

[![release: 0.9.10](https://img.shields.io/badge/rel-0.9.10-blue.svg?style=flat-square)](https://github.com/LeibnizDSMZ/cafi)
[![MIT LICENSE](https://img.shields.io/badge/License-MIT-brightgreen.svg?style=flat-square)](https://choosealicense.com/licenses/mit/)
[![DATA LICENSE - CC BY 4.0](https://img.shields.io/badge/Data%20License-CC%20BY%204.0-brightgreen.svg?style=flat-square)](http://creativecommons.org/licenses/by/4.0/)
[![Documentation Status](https://img.shields.io/badge/docs-GitHub-blue.svg?style=flat-square)](https://LeibnizDSMZ.github.io/cafi/)

[![main](https://github.com/LeibnizDSMZ/cafi/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/LeibnizDSMZ/cafi/actions/workflows/main.yml)

[![DOI](https://zenodo.org/badge/638857356.svg)](https://doi.org/10.5281/zenodo.14872268)

---

**cafi** is a centralized registry for assigning unique identifiers to acronyms, enabling efficient management and cross-software identification of all acronyms consistently.

## Key Features

* **Efficient organization**: Store and manage unique IDs in a single location for easy access and maintenance.
* **Data license compliance**: All data is licensed under Creative Commons Attribution 4.0 International License, ensuring proper attribution and sharing.

---

## Installation - Development

### Prerequisites

- **GNU/Linux**
- **Docker (optional)**
- **Docker Compose (optional)**
- **Dev Container CLI (optional)**

### Steps

1. Clone the repository:
   ```sh
   git clone https://github.com/LeibnizDSMZ/cafi.git
   cd cafi
   ```

#### Docker

2. If using Docker, start the development container manually or use VSCode:
   ```sh
   devcontainer up --workspace-folder .
   devcontainer exec --workspace-folder . bash
   ```

3. Create and activate a virtual environment (inside docker the container):
   ```sh
   make dev
   make runAct
   ```

#### Local

2. Create and activate a virtual environment:
   ```sh
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install the dependencies:
   ```sh
   pip install .
   pip install -r configs/dev/requirements.dev.txt
   pip install -r configs/dev/requirements.test.txt
   pip install -r configs/dev/requirements.docs.txt
   ```


## Contributors

- Isabel Schober
- Artur Lissin
- Julius Witte
- Helko Lüken

---

## License

All source code is licensed under the MIT License (see LICENSE). The acronym data inside the data folder (src/cafi/data) is licensed under the [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/) (see LICENSE-CC-BY).
