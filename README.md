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
  - [📦 Requirements](#-requirements)
  - [🚀 Quick Start](#-quick-start)
  - [💻 Installation](#-installation)
    - [Step 1: Clone the repository](#step-1-clone-the-repository)
    - [Step 2: Install dependencies](#step-2-install-dependencies)
  - [📖 Usage](#-usage)
    - [🐳 Starting CouchDB](#-starting-couchdb)
    - [📄 Generating OpenAPI Specification](#-generating-openapi-specification)
      - [Basic Usage](#basic-usage)
      - [Advanced Usage](#advanced-usage)
      - [📋 Parameters](#-parameters)
    - [🎮 Running the Main Application](#-running-the-main-application)
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

---

## 🎯 Description

This project has been updated for more convenient work with CouchDB and includes:

- 🐳 **Updated Docker Compose configuration** for quick CouchDB deployment
- 📄 **Modern OpenAPI specification generator** for CouchDB API
- 🛠️ **Utilities and tools** for interacting with the CouchDB server
- 🚀 **Production-ready** setup with best practices

---

## 📦 Requirements

- 🐍 **Python** 3.11 or higher
- 🐳 **Docker** and Docker Compose
- 📦 **[uv](https://github.com/astral-sh/uv)** (Python package manager)

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/SasukeSagara/CouchDB-OpenAPI-scheme-generator.git
cd couchdb-openapi-scheme-generator

# 2. Install dependencies
uv sync

# 3. Start CouchDB
docker-compose up -d

# 4. Generate OpenAPI specification
uv run openapi_generator.py
```

That's it! 🎉 Your OpenAPI specification will be generated in `couchdb-openapi.json`

---

## 💻 Installation

### Step 1: Clone the repository

```bash
git clone https://github.com/SasukeSagara/CouchDB-OpenAPI-scheme-generator.git
cd couchdb-openapi-scheme-generator
```

### Step 2: Install dependencies

Install dependencies using `uv`:

```bash
uv sync
```

For development dependencies:

```bash
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

Use `openapi_generator.py` to generate the OpenAPI specification for CouchDB API:

#### Basic Usage

```bash
# Basic usage (local server)
uv run openapi_generator.py
```

#### Advanced Usage

```bash
# With URL and credentials specified
uv run openapi_generator.py \
  --url http://localhost:5984 \
  --username admin \
  --password your_password

# With custom output file
uv run openapi_generator.py --output couchdb-api.json

# Generate in YAML format
uv run openapi_generator.py \
  --format yaml \
  --output couchdb-api.yaml

# Full example with all options
uv run openapi_generator.py \
  --url http://localhost:5984 \
  --username admin \
  --password your_password \
  --format json \
  --output my-couchdb-api.json
```

#### 📋 Parameters

| Parameter | Short | Description | Default |
|-----------|-------|-------------|---------|
| `--url` | `-u` | CouchDB server URL | `http://localhost:5984` |
| `--username` | - | Username for authentication | - |
| `--password` | - | Password for authentication | - |
| `--output` | `-o` | Output file name | `couchdb-openapi.json` |
| `--format` | `-f` | Output format (`json` or `yaml`) | `json` |

### 🎮 Running the Main Application

```bash
uv run genopenapi_generatorerator.py
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
