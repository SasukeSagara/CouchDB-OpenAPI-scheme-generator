<div align="center">

# 🚀 CouchDB OpenAPI Scheme Generator

**OpenAPI specification generator for CouchDB** - Perfect for developing and debugging applications using CouchDB as a backend

[![GitHub stars](https://img.shields.io/github/stars/SasukeSagara/CouchDB-OpenAPI-scheme-generator?style=for-the-badge&logo=github&color=yellow)](https://github.com/SasukeSagara/CouchDB-OpenAPI-scheme-generator/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/SasukeSagara/CouchDB-OpenAPI-scheme-generator?style=for-the-badge&logo=github&color=blue)](https://github.com/SasukeSagara/CouchDB-OpenAPI-scheme-generator/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/SasukeSagara/CouchDB-OpenAPI-scheme-generator?style=for-the-badge&logo=github&color=green)](https://github.com/SasukeSagara/CouchDB-OpenAPI-scheme-generator/watchers)
[![GitHub issues](https://img.shields.io/github/issues/SasukeSagara/CouchDB-OpenAPI-scheme-generator?style=for-the-badge&logo=github&color=red)](https://github.com/SasukeSagara/CouchDB-OpenAPI-scheme-generator/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/SasukeSagara/CouchDB-OpenAPI-scheme-generator?style=for-the-badge&logo=github&color=orange)](https://github.com/SasukeSagara/CouchDB-OpenAPI-scheme-generator/pulls)

[![License](https://img.shields.io/github/license/SasukeSagara/CouchDB-OpenAPI-scheme-generator?style=for-the-badge&logo=open-source-initiative&color=success)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyPI version](https://img.shields.io/pypi/v/couchdb-openapi-scheme-generator?style=for-the-badge&logo=pypi&logoColor=white&color=blue)](https://pypi.org/project/couchdb-openapi-scheme-generator/)
[![PyPI downloads](https://img.shields.io/pypi/dm/couchdb-openapi-scheme-generator?style=for-the-badge&logo=pypi&logoColor=white&color=green)](https://pypi.org/project/couchdb-openapi-scheme-generator/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0-green?style=for-the-badge&logo=openapi-initiative&logoColor=white)](https://www.openapis.org/)

![GitHub repo size](https://img.shields.io/github/repo-size/SasukeSagara/CouchDB-OpenAPI-scheme-generator?style=for-the-badge&logo=github)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/SasukeSagara/CouchDB-OpenAPI-scheme-generator?style=for-the-badge&logo=github)
![GitHub last commit](https://img.shields.io/github/last-commit/SasukeSagara/CouchDB-OpenAPI-scheme-generator?style=for-the-badge&logo=git&logoColor=white)
![GitHub contributors](https://img.shields.io/github/contributors/SasukeSagara/CouchDB-OpenAPI-scheme-generator?style=for-the-badge&logo=github)

[![Views](https://komarev.com/ghpvc/?username=SasukeSagara&repo=CouchDB-OpenAPI-scheme-generator&style=for-the-badge&color=blueviolet&label=VIEWS)](https://github.com/SasukeSagara/CouchDB-OpenAPI-scheme-generator)
[![Visitor Badge](https://visitor-badge.laobi.icu/badge?page_id=SasukeSagara.CouchDB-OpenAPI-scheme-generator&left_color=green&right_color=blue&left_text=VISITORS)](https://github.com/SasukeSagara/CouchDB-OpenAPI-scheme-generator)

</div>

---

## 📋 Table of Contents

- [🚀 CouchDB OpenAPI Scheme Generator](#-couchdb-openapi-scheme-generator)
  - [📋 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🎯 Description](#-description)
    - [📋 Supported API Endpoints](#-supported-api-endpoints)
  - [📦 Requirements](#-requirements)
  - [🚀 Quick Start](#-quick-start)
    - [Option 1: Using uvx (Recommended - No Installation Required)](#option-1-using-uvx-recommended---no-installation-required)
    - [Option 2: Install from PyPI](#option-2-install-from-pypi)
    - [Option 3: Development Setup](#option-3-development-setup)
  - [💻 Installation](#-installation)
    - [📦 Install from PyPI](#-install-from-pypi)
      - [Using pip](#using-pip)
      - [Using uv](#using-uv)
      - [Using pipx (Isolated Installation)](#using-pipx-isolated-installation)
    - [🚀 Using uvx (No Installation Required)](#-using-uvx-no-installation-required)
    - [🔧 Development Installation](#-development-installation)
  - [📖 Usage](#-usage)
    - [🐳 Starting CouchDB](#-starting-couchdb)
    - [📄 Generating OpenAPI Specification](#-generating-openapi-specification)
      - [Method 1: Using uvx (Recommended)](#method-1-using-uvx-recommended)
      - [Method 2: Using Installed Package](#method-2-using-installed-package)
      - [Method 3: Development Mode](#method-3-development-mode)
      - [📋 Parameters](#-parameters)
      - [📚 Generated Specification](#-generated-specification)
    - [🎮 Running the Application](#-running-the-application)
  - [🏗️ Project Structure](#️-project-structure)
  - [🛠️ Development](#️-development)
    - [Setting Up Development Environment](#setting-up-development-environment)
    - [Code Style](#code-style)
  - [🤝 Contributing](#-contributing)
    - [Contribution Guidelines](#contribution-guidelines)
  - [📝 License](#-license)
  - [⭐ Show Your Support](#-show-your-support)
    - [Made with ❤️ by SasukeSagara](#made-with-️-by-sasukesagara)
      - [⭐ Star this repo if you find it useful! ⭐](#-star-this-repo-if-you-find-it-useful-)

---

## ✨ Features

| Feature | Description | Status |
|---------|-------------|--------|
| 🐳 **Docker Support** | Quick CouchDB deployment with Docker Compose | ✅ Ready |
| 📄 **OpenAPI 3.0** | Modern OpenAPI specification generator | ✅ Ready |
| 🔧 **CLI Tool** | Easy-to-use command-line interface | ✅ Ready |
| 📊 **JSON/YAML** | Support for both JSON and YAML output formats | ✅ Ready |
| 🔐 **Authentication** | Built-in support for CouchDB authentication | ✅ Ready |
| ⚡ **Fast Setup** | Get started in minutes | ✅ Ready |
| 📚 **Comprehensive API Coverage** | Full coverage of CouchDB API endpoints according to official documentation | ✅ Ready |
| 🎯 **Server Endpoints** | Complete server management endpoints (tasks, cluster, nodes, etc.) | ✅ Ready |
| 🗄️ **Database Operations** | Full database management (shards, security, compaction, etc.) | ✅ Ready |
| 📝 **Design Documents** | Complete design document endpoints (views, search, show, list, update) | ✅ Ready |
| 🔀 **Partitioned Databases** | Support for partitioned database operations | ✅ Ready |
| 📋 **Local Documents** | Support for local (non-replicating) documents | ✅ Ready |

---

## 🎯 Description

This project has been updated for more convenient work with CouchDB and includes:

- 🐳 **Updated Docker Compose configuration** for quick CouchDB deployment
- 📄 **Modern OpenAPI specification generator** for CouchDB API
- 🛠️ **Utilities and tools** for interacting with the CouchDB server
- 🚀 **Production-ready** setup with best practices
- 📚 **Comprehensive API coverage** - The OpenAPI specification includes all major CouchDB API endpoints according to the [official CouchDB documentation](https://docs.couchdb.org/en/stable/api/)

### 📋 Supported API Endpoints

The generated OpenAPI specification includes comprehensive coverage of CouchDB API:

- **Server Endpoints** (18+ endpoints): Server information, active tasks, cluster setup, database updates, membership, scheduler, node management, statistics, Prometheus metrics, UUID generation, resharding, and more
- **Database Endpoints** (20+ endpoints): Database operations, design documents, bulk operations, indexes, shards, compaction, security, purging, revision management, and more
- **Document Endpoints**: Full CRUD operations for documents and attachments
- **Design Document Endpoints** (12+ endpoints): Views, search indexes, nouveau indexes, show/list/update functions, URL rewriting, and more
- **Partitioned Database Endpoints** (5 endpoints): Partition information, queries, and views
- **Local Documents Endpoints** (3 endpoints): Local document operations (non-replicating)
- **User Endpoints**: User management in the `_users` database

---

## 📦 Requirements

- 🐍 **Python** 3.11 or higher
- 📦 **Package manager** (optional): `pip`, `uv`, `pipx`, or `uvx`

---

## 🚀 Quick Start

### Option 1: Using uvx (Recommended - No Installation Required)

```bash
# Generate OpenAPI specification directly without installation
uvx couchdb-openapi-scheme-generator
```

That's it! 🎉 Your OpenAPI specification will be generated in `couchdb-openapi.json`

### Option 2: Install from PyPI

```bash
# Install using pip
pip install couchdb-openapi-scheme-generator

# Or using uv
uv pip install couchdb-openapi-scheme-generator

# Or using pipx (for isolated installation)
pipx install couchdb-openapi-scheme-generator

# Then run
couchdb-openapi-scheme-generator
```

### Option 3: Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/SasukeSagara/CouchDB-OpenAPI-scheme-generator.git
cd couchdb-openapi-scheme-generator

# 2. Install dependencies
uv sync

# 3. Run the generator
uv run openapi_generator.py
```

---

## 💻 Installation

### 📦 Install from PyPI

The package is available on [PyPI](https://pypi.org/project/couchdb-openapi-scheme-generator/). You can install it using any Python package manager:

#### Using pip

```bash
pip install couchdb-openapi-scheme-generator
```

#### Using uv

```bash
uv pip install couchdb-openapi-scheme-generator
```

#### Using pipx (Isolated Installation)

```bash
pipx install couchdb-openapi-scheme-generator
```

### 🚀 Using uvx (No Installation Required)

You can use the package directly without installation using `uvx`:

```bash
uvx couchdb-openapi-scheme-generator
```

This will automatically download and run the latest version from PyPI.

### 🔧 Development Installation

If you want to contribute or modify the code:

```bash
# 1. Clone the repository
git clone https://github.com/SasukeSagara/CouchDB-OpenAPI-scheme-generator.git
cd couchdb-openapi-scheme-generator

# 2. Install dependencies using uv
uv sync

# For development dependencies
uv sync --dev
```

---

## 📖 Usage

### 🐳 Starting CouchDB

Start CouchDB using Docker Compose:

```bash
docker-compose up -d
```

CouchDB will be available at `http://localhost:5984`

> ⚠️ **Important:** Change the password in `.env` before using in production!

### 📄 Generating OpenAPI Specification

Generate the OpenAPI specification for CouchDB API using one of the following methods:

#### Method 1: Using uvx (Recommended)

```bash
# Basic usage (local server)
uvx couchdb-openapi-scheme-generator

# With URL and credentials specified
uvx couchdb-openapi-scheme-generator \
  --url http://localhost:5984 \
  --username admin \
  --password your_password

# With custom output file
uvx couchdb-openapi-scheme-generator --output couchdb-api.json

# Generate in YAML format
uvx couchdb-openapi-scheme-generator \
  --format yaml \
  --output couchdb-api.yaml
```

#### Method 2: Using Installed Package

If you installed the package using `pip`, `uv`, or `pipx`:

```bash
# Basic usage
couchdb-openapi-scheme-generator

# With all options
couchdb-openapi-scheme-generator \
  --url http://localhost:5984 \
  --username admin \
  --password your_password \
  --format json \
  --output my-couchdb-api.json
```

#### Method 3: Development Mode

If you cloned the repository and installed dependencies:

```bash
# Using uv run
uv run openapi_generator.py

# Or directly with Python
python openapi_generator.py
```

#### 📋 Parameters

| Parameter | Short | Description | Default |
|-----------|-------|-------------|---------|
| `--url` | `-u` | CouchDB server URL | `http://localhost:5984` |
| `--username` | - | Username for authentication | - |
| `--password` | - | Password for authentication | - |
| `--output` | `-o` | Output file name | `couchdb-openapi.json` |
| `--format` | `-f` | Output format (`json` or `yaml`) | `json` |

#### 📚 Generated Specification

The generated OpenAPI specification includes:

- ✅ **60+ API endpoints** covering all major CouchDB operations
- ✅ **Complete request/response schemas** for all endpoints
- ✅ **Query parameters** and path parameters properly documented
- ✅ **Authentication support** via Basic Auth
- ✅ **Error responses** with appropriate HTTP status codes
- ✅ **Compatible with** Swagger UI, Postman, Insomnia, and other OpenAPI tools

The specification is based on the [official CouchDB API documentation](https://docs.couchdb.org/en/stable/api/) and includes endpoints for:

- Server management and monitoring
- Database operations and administration
- Document CRUD operations
- Design documents and views
- Search and indexing
- Partitioned databases
- Local documents
- User management

### 🎮 Running the Application

After installation, you can run the generator using:

```bash
# If installed via pip/pipx/uv
couchdb-openapi-scheme-generator

# Or using uvx (no installation needed)
uvx couchdb-openapi-scheme-generator

# Or in development mode
uv run openapi_generator.py
```

---

## 🏗️ Project Structure

```text
CouchDB-OpenAPI-scheme-generator/
├── 📁 couchdb-data/          # CouchDB data (Docker volume)
├── 📁 couchdb-etc/           # CouchDB configuration
├── 📄 docker-compose.yml     # Docker Compose configuration
├── 📄 main.py                # Main application file
├── 📄 openapi_generator.py   # OpenAPI specification generator
├── 📄 pyproject.toml         # Python project configuration
├── 📄 uv.lock                # Dependency lock file
├── 📄 .env                   # Environment variables (create this)
├── 📄 .gitignore             # Git ignore rules
├── 📄 LICENSE                # MIT License
└── 📄 README.md              # This file
```

---

## 🛠️ Development

### Setting Up Development Environment

1. **Clone the repository:**

   ```bash
   git clone https://github.com/SasukeSagara/CouchDB-OpenAPI-scheme-generator.git
   cd couchdb-openapi-scheme-generator
   ```

2. **Install development dependencies:**

   ```bash
   uv sync --dev
   ```

3. **Create `.env` file:**

   ```bash
   cp .env.example .env  # If you have an example file
   # Or create manually with:
   # COUCHDB_USER=admin
   # COUCHDB_PASSWORD=your_secure_password
   ```

4. **Start CouchDB:**

   ```bash
   docker-compose up -d
   ```

5. **Run tests (if available):**

   ```bash
   uv run pytest
   ```

### Code Style

This project follows PEP 8 style guidelines. Consider using:

- `black` for code formatting
- `flake8` or `ruff` for linting
- `mypy` for type checking

---

## 🤝 Contributing

Contributions are welcome! 🎉

1. **Fork the repository**
2. **Create your feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Contribution Guidelines

- 📝 Follow the existing code style
- ✅ Add tests for new features
- 📖 Update documentation as needed
- 🐛 Report bugs using GitHub Issues
- 💡 Suggest enhancements using GitHub Discussions

---

## 📝 License

This project is distributed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

---

## ⭐ Show Your Support

If you find this project helpful, please consider:

- ⭐ **Starring** this repository
- 🍴 **Forking** this repository
- 🐛 **Reporting** bugs
- 💡 **Suggesting** new features
- 📖 **Improving** documentation
- 🤝 **Contributing** code

---

<div align="center">

### Made with ❤️ by [SasukeSagara](https://github.com/SasukeSagara)

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/SasukeSagara)
[![Open Source](https://img.shields.io/badge/Open%20Source-Yes-green?style=for-the-badge)](https://opensource.org/)

#### ⭐ Star this repo if you find it useful! ⭐

</div>
