# CouchDB OpenAPI scheme generator

OpenAPI specification generator for CouchDB, suitable for developing and debugging applications using CouchDB as a backend.

## Description

This project has been updated for more convenient work with CouchDB and includes:

- Updated Docker Compose configuration for quick CouchDB deployment
- Modern OpenAPI specification generator for CouchDB API
- Utilities and tools for interacting with the CouchDB server

## Requirements

- Python 3.11 or higher
- Docker and Docker Compose
- [uv](https://github.com/astral-sh/uv) (Python package manager)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/SasukeSagara/CouchDB-OpenAPI-scheme-generator.git
    cd couchdb-openapi-scheme-generator
    ```

2. Install dependencies using uv:

    ```bash
    uv sync
    ```

## Usage

### Starting CouchDB

Start CouchDB using Docker Compose:

```bash
docker-compose up -d
```

CouchDB will be available at `http://localhost:5984`

⚠️ **Important:** Change the password in `.env` before using in production!

### Generating OpenAPI specification

Use `openapi_generator.py` to generate the OpenAPI specification for CouchDB API:

```bash
# Basic usage (local server)
uv run openapi_generator.py

# With URL and credentials specified
uv run openapi_generator.py --url http://localhost:5984 --username admin --password your_password

# With output file specified
uv run openapi_generator.py --output couchdb-api.json

# Generate in YAML format
uv run openapi_generator.py --format yaml --output couchdb-api.yaml
```

**Parameters:**

- `--url, -u`: CouchDB server URL (default: `http://localhost:5984`)
- `--username`: Username for authentication
- `--password`: Password for authentication
- `--output, -o`: Output file name (default: `couchdb-openapi.json`)
- `--format, -f`: Output format - `json` or `yaml` (default: `json`)

### Running the main application

```bash
uv run genopenapi_generatorerator.py
```

## Project Structure

```bash
CouchDB-OpenAPI-scheme-generator/
├── couchdb-data/          # CouchDB data (Docker volume)
├── couchdb-etc/           # CouchDB configuration
├── docker-compose.yml     # Docker Compose configuration
├── main.py                # Main application file
├── openapi_generator.py   # OpenAPI specification generator
├── pyproject.toml         # Python project configuration
├── uv.lock                # Dependency lock file
└── README.md              # This file
```

## Development

### Installing development dependencies

```bash
uv sync --dev
```

## License

This project is distributed under the MIT license. See the [LICENSE](LICENSE) file for details.
