#!/usr/bin/env python3
"""
CouchDB Swagger/OpenAPI Generator

Python версия CLI инструмента digitalnodecom/couchdb-swagger для генерации
OpenAPI/Swagger спецификации на основе CouchDB REST API.

Модуль предоставляет класс CouchDBSwaggerGenerator для программной генерации
OpenAPI спецификаций и функцию main() для использования из командной строки.

Пример использования:
    >>> generator = CouchDBSwaggerGenerator(
    ...     base_url="http://localhost:5984",
    ...     username="admin",
    ...     password="password"
    ... )
    >>> spec = generator.generate_openapi_spec()
    >>> generator.save_spec("couchdb-api.json", spec)

Пример использования из командной строки:
    $ python openapi_generator.py --url http://localhost:5984 --output api.json
    $ python openapi_generator.py --url http://localhost:5984 -u admin -p password -f yaml
"""

import argparse
import json
import sys

import requests


class CouchDBSwaggerGenerator:
    """
    Генератор OpenAPI/Swagger спецификации для CouchDB API.

    Этот класс предоставляет функциональность для подключения к CouchDB серверу
    и генерации OpenAPI спецификации на основе доступных эндпоинтов и схем данных.
    Поддерживает базовую HTTP аутентификацию и автоматически определяет версию
    CouchDB сервера для включения в спецификацию.

    Attributes:
        base_url (str): Базовый URL CouchDB сервера без завершающего слеша.
            Используется для всех HTTP запросов к серверу.
        auth (tuple[str, str] | None): Кортеж (username, password) для базовой
            HTTP аутентификации. Устанавливается в None, если учетные данные
            не предоставлены.

    Example:
        >>> # Создание генератора без аутентификации
        >>> generator = CouchDBSwaggerGenerator()
        >>>
        >>> # Создание генератора с аутентификацией
        >>> generator = CouchDBSwaggerGenerator(
        ...     base_url="http://couchdb.example.com:5984",
        ...     username="admin",
        ...     password="secret"
        ... )
        >>>
        >>> # Генерация и сохранение спецификации
        >>> spec = generator.generate_openapi_spec(version="3.0.0")
        >>> generator.save_spec("couchdb-openapi.json", spec)

    Note:
        При инициализации URL автоматически очищается от завершающего слеша
        для обеспечения консистентности при формировании путей запросов.
    """

    def __init__(self, base_url="http://localhost:5984", username=None, password=None):
        """
        Инициализирует генератор OpenAPI спецификации для CouchDB.

        Создает новый экземпляр генератора с указанными параметрами подключения.
        Если предоставлены username и password, настраивается базовая HTTP
        аутентификация для всех последующих запросов.

        Args:
            base_url (str, optional): Базовый URL CouchDB сервера.
                Должен включать протокол (http:// или https://) и порт при необходимости.
                По умолчанию: "http://localhost:5984".
                Примеры: "http://localhost:5984", "https://couchdb.example.com:5984"
            username (str | None, optional): Имя пользователя для базовой HTTP
                аутентификации. Если указан, должен быть указан и password.
                По умолчанию: None (без аутентификации).
            password (str | None, optional): Пароль для базовой HTTP аутентификации.
                Если указан, должен быть указан и username.
                По умолчанию: None (без аутентификации).

        Note:
            - URL автоматически очищается от завершающего слеша
            - Если указан только username или только password, аутентификация
              не будет настроена (auth будет None)
            - Для защищенных серверов обязательно указывайте оба параметра
              аутентификации

        Example:
            >>> # Локальный сервер без аутентификации
            >>> gen1 = CouchDBSwaggerGenerator()
            >>>
            >>> # Удаленный сервер с аутентификацией
            >>> gen2 = CouchDBSwaggerGenerator(
            ...     base_url="https://couchdb.example.com:5984",
            ...     username="admin",
            ...     password="secure_password"
            ... )
        """
        self.base_url = base_url.rstrip("/")
        self.auth = (username, password) if username and password else None

    def get_server_info(self):
        """
        Получает информацию о CouchDB сервере.

        Выполняет GET запрос к корневому эндпоинту CouchDB (/) для получения
        информации о версии, функциях и других метаданных сервера. Эта информация
        используется для генерации OpenAPI спецификации с корректной версией
        CouchDB в метаданных API.

        Returns:
            dict: Словарь с информацией о сервере в формате JSON. Типичная структура:
                {
                    "couchdb": "Welcome",
                    "version": "3.3.0",
                    "git_sha": "abc123...",
                    "uuid": "12345678-1234-1234-1234-123456789abc",
                    "features": ["access-ready", "partitioned", "pluggable-storage-engines"],
                    "vendor": {
                        "name": "The Apache Software Foundation",
                        "version": "3.3.0"
                    }
                }

        Raises:
            SystemExit: Выход из программы с кодом 1 при ошибке подключения,
                отсутствии сервера, проблемах с сетью или неверных учетных данных.
                Сообщение об ошибке выводится в stderr.

        Note:
            - Метод использует базовую HTTP аутентификацию, если она была настроена
              при инициализации класса
            - При ошибке подключения программа завершается немедленно
            - Для успешного выполнения требуется доступность CouchDB сервера
              по указанному base_url

        Example:
            >>> generator = CouchDBSwaggerGenerator()
            >>> info = generator.get_server_info()
            >>> print(info["version"])
            '3.3.0'
            >>> print(info["features"])
            ['access-ready', 'partitioned', 'pluggable-storage-engines']
        """
        try:
            response = requests.get(self.base_url, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error connecting to CouchDB: {e}", file=sys.stderr)
            sys.exit(1)

    def generate_openapi_spec(self, version="3.0.0"):
        """
        Генерирует полную OpenAPI спецификацию для CouchDB API.

        Создает полную OpenAPI спецификацию версии 3.0.0, включающую информацию
        о сервере, все доступные пути (endpoints), схемы данных и настройки
        безопасности. Версия CouchDB определяется автоматически путем запроса
        к серверу и включается в метаданные спецификации.

        Args:
            version (str, optional): Версия OpenAPI спецификации.
                Поддерживаются версии OpenAPI 3.x. По умолчанию: "3.0.0".
                Рекомендуется использовать "3.0.0" или "3.1.0" для совместимости
                с большинством инструментов.

        Returns:
            dict: Полная OpenAPI спецификация в формате словаря, соответствующая
                стандарту OpenAPI 3.0. Структура включает:
                - openapi (str): Версия спецификации OpenAPI
                - info (dict): Метаданные API:
                    - title: "CouchDB API"
                    - description: Описание с версией CouchDB
                    - version: Версия CouchDB сервера
                    - contact: Контактная информация Apache CouchDB
                - servers (list): Список серверов с базовым URL
                - paths (dict): Все доступные эндпоинты с методами HTTP
                - components (dict): Компоненты спецификации:
                    - schemas: Схемы данных для объектов CouchDB
                    - securitySchemes: Схемы безопасности (basicAuth)
                - security (list): Настройки безопасности по умолчанию

        Note:
            - Метод выполняет запрос к серверу через get_server_info() для
              получения версии CouchDB
            - При ошибке подключения к серверу программа завершается
            - Спецификация совместима с инструментами типа Swagger UI,
              Postman, Insomnia и другими OpenAPI-совместимыми клиентами

        Example:
            >>> generator = CouchDBSwaggerGenerator()
            >>> spec = generator.generate_openapi_spec()
            >>> print(spec["info"]["version"])
            '3.3.0'
            >>> print(spec["openapi"])
            '3.0.0'
            >>> print(list(spec["paths"].keys()))
            ['/', '/_all_dbs', '/{db}', '/{db}/_all_docs', '/_users', '/_users/{user_id}']
        """
        server_info = self.get_server_info()
        couchdb_version = server_info.get("version", "unknown")

        openapi_spec = {
            "openapi": version,
            "info": {
                "title": "CouchDB API",
                "description": f"CouchDB {couchdb_version} REST API",
                "version": couchdb_version,
                "contact": {
                    "name": "Apache CouchDB",
                    "url": "https://couchdb.apache.org/",
                },
            },
            "servers": [{"url": self.base_url, "description": "CouchDB Server"}],
            "paths": self.generate_paths(),
            "components": {
                "schemas": self.generate_schemas(),
                "securitySchemes": {"basicAuth": {"type": "http", "scheme": "basic"}},
            },
            "security": [{"basicAuth": []}],
        }

        return openapi_spec

    def generate_paths(self):
        """
        Генерирует определения путей (paths) для основных эндпоинтов CouchDB.

        Создает OpenAPI определения для основных REST API эндпоинтов CouchDB.
        Каждый путь включает описание методов HTTP, параметров, запросов,
        ответов и кодов состояния. Определения соответствуют стандарту OpenAPI 3.0.

        Поддерживаемые эндпоинты:
        - GET /: Информация о сервере CouchDB
        - GET /_all_dbs: Список всех баз данных в экземпляре
        - PUT /{db}: Создание новой базы данных
        - GET /{db}: Получение информации о базе данных
        - DELETE /{db}: Удаление базы данных
        - GET /{db}/_all_docs: Получение всех документов из базы данных
        - GET /_users: Информация о системной базе данных пользователей
        - GET /_users/{user_id}: Получение документа пользователя
        - PUT /_users/{user_id}: Создание или обновление пользователя
        - GET /{db}/{docid}: Получение документа
        - PUT /{db}/{docid}: Создание или обновление документа
        - DELETE /{db}/{docid}: Удаление документа
        - HEAD /{db}/{docid}: Проверка существования документа
        - POST /{db}/_find: Поиск документов с использованием Mango Query
        - GET /{db}/_changes: Получение потока изменений базы данных
        - POST /{db}/_bulk_docs: Массовые операции с документами
        - GET /{db}/_design/{ddoc}: Получение design документа
        - PUT /{db}/_design/{ddoc}: Создание или обновление design документа
        - DELETE /{db}/_design/{ddoc}: Удаление design документа
        - GET /{db}/_design/{ddoc}/_view/{view}: Запрос представления (view)
        - POST /{db}/_design/{ddoc}/_view/{view}: Запрос представления через POST
        - GET /{db}/{docid}/{attachment}: Получение вложения
        - PUT /{db}/{docid}/{attachment}: Добавление или обновление вложения
        - DELETE /{db}/{docid}/{attachment}: Удаление вложения
        - POST /_replicate: Репликация базы данных

        Returns:
            dict: Словарь с определениями путей в формате OpenAPI 3.0, где:
                - Ключ (str): Путь эндпоинта (например, "/", "/_all_dbs", "/{db}")
                - Значение (dict): Объект с методами HTTP (get, put, delete) и их
                  описаниями, включающими:
                    - summary: Краткое описание операции
                    - description: Подробное описание операции
                    - parameters: Список параметров пути/запроса
                    - requestBody: Тело запроса (для PUT методов)
                    - responses: Коды ответов и их описания
                    - content: Схемы данных для ответов

        Note:
            - Пути с параметрами используют синтаксис OpenAPI: {param_name}
            - Все определения включают стандартные коды ответов HTTP
            - Схемы ответов ссылаются на компоненты в generate_schemas()
            - Метод не выполняет запросы к серверу, только формирует структуру

        Example:
            >>> generator = CouchDBSwaggerGenerator()
            >>> paths = generator.generate_paths()
            >>> "/" in paths
            True
            >>> "{db}" in paths["/{db}"]["get"]["parameters"][0]["name"]
            True
            >>> paths["/"]["get"]["summary"]
            'Get server information'
        """
        paths = {
            "/": {
                "get": {
                    "summary": "Get server information",
                    "description": "Accesses the root of a CouchDB instance",
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ServerInfo"
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/_all_dbs": {
                "get": {
                    "summary": "List all databases",
                    "description": "Returns a list of all the databases in the CouchDB instance",
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/{db}": {
                "put": {
                    "summary": "Create database",
                    "description": "Creates a new database",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "201": {"description": "Database created successfully"},
                        "400": {"description": "Invalid database name"},
                    },
                },
                "get": {
                    "summary": "Get database information",
                    "description": "Gets information about the specified database",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/DatabaseInfo"
                                    }
                                }
                            },
                        }
                    },
                },
                "delete": {
                    "summary": "Delete database",
                    "description": "Deletes the specified database",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "Database deleted successfully"}
                    },
                },
            },
            "/{db}/_all_docs": {
                "get": {
                    "summary": "Get all documents",
                    "description": "Returns all documents in the database",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/AllDocsResponse"
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/_users": {
                "get": {
                    "summary": "Get users database info",
                    "description": "Accesses the internal users database",
                    "responses": {
                        "200": {"description": "Request completed successfully"}
                    },
                }
            },
            "/_users/{user_id}": {
                "get": {
                    "summary": "Get user document",
                    "description": "Gets a user document from the users database",
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "Request completed successfully"}
                    },
                },
                "put": {
                    "summary": "Create/update user",
                    "description": "Creates or updates a user document",
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/UserDocument"}
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "User created/updated successfully"}
                    },
                },
            },
            "/{db}/{docid}": {
                "get": {
                    "summary": "Get document",
                    "description": "Gets a document from the specified database",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "docid",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "rev",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                            "description": "Document revision",
                        },
                        {
                            "name": "revs",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "boolean"},
                            "description": "Include revision history",
                        },
                        {
                            "name": "revs_info",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "boolean"},
                            "description": "Include revision info",
                        },
                        {
                            "name": "attachments",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "boolean"},
                            "description": "Include attachments",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Document"}
                                }
                            },
                        },
                        "404": {"description": "Document not found"},
                    },
                },
                "put": {
                    "summary": "Create/update document",
                    "description": "Creates or updates a document in the specified database",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "docid",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Document"}
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Document created/updated successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/DocumentResponse"
                                    }
                                }
                            },
                        },
                        "400": {"description": "Invalid request"},
                        "409": {"description": "Document conflict"},
                    },
                },
                "delete": {
                    "summary": "Delete document",
                    "description": "Deletes a document from the specified database",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "docid",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "rev",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Document revision",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Document deleted successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/DocumentResponse"
                                    }
                                }
                            },
                        },
                        "404": {"description": "Document not found"},
                        "409": {"description": "Document conflict"},
                    },
                },
                "head": {
                    "summary": "Check document existence",
                    "description": "Checks if a document exists in the specified database",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "docid",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {
                        "200": {"description": "Document exists"},
                        "404": {"description": "Document not found"},
                    },
                },
            },
            "/{db}/_find": {
                "post": {
                    "summary": "Query documents using Mango",
                    "description": "Query documents using the Mango query syntax",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MangoQuery"}
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/MangoResponse"
                                    }
                                }
                            },
                        },
                        "400": {"description": "Invalid query"},
                    },
                }
            },
            "/{db}/_changes": {
                "get": {
                    "summary": "Get database changes",
                    "description": "Returns a list of changes made to documents in the database",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "feed",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": [
                                    "normal",
                                    "longpoll",
                                    "continuous",
                                    "eventsource",
                                ],
                            },
                            "description": "Type of feed",
                        },
                        {
                            "name": "since",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                            "description": "Start from this sequence number",
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer"},
                            "description": "Maximum number of results",
                        },
                        {
                            "name": "include_docs",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "boolean"},
                            "description": "Include document bodies",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ChangesResponse"
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_bulk_docs": {
                "post": {
                    "summary": "Bulk document operations",
                    "description": "Performs bulk document operations (create, update, delete)",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/BulkDocsRequest"
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Bulk operations completed",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/DocumentResponse"
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_design/{ddoc}": {
                "get": {
                    "summary": "Get design document",
                    "description": "Gets a design document from the specified database",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "ddoc",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/DesignDocument"
                                    }
                                }
                            },
                        },
                        "404": {"description": "Design document not found"},
                    },
                },
                "put": {
                    "summary": "Create/update design document",
                    "description": "Creates or updates a design document in the specified database",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "ddoc",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/DesignDocument"
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Design document created/updated successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/DocumentResponse"
                                    }
                                }
                            },
                        }
                    },
                },
                "delete": {
                    "summary": "Delete design document",
                    "description": "Deletes a design document from the specified database",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "ddoc",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "rev",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Document revision",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Design document deleted successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/DocumentResponse"
                                    }
                                }
                            },
                        }
                    },
                },
            },
            "/{db}/_design/{ddoc}/_view/{view}": {
                "get": {
                    "summary": "Query a view",
                    "description": "Queries a view from a design document",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "ddoc",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "view",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "key",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                            "description": "Key to query",
                        },
                        {
                            "name": "startkey",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                            "description": "Start key",
                        },
                        {
                            "name": "endkey",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                            "description": "End key",
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer"},
                            "description": "Maximum number of results",
                        },
                        {
                            "name": "include_docs",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "boolean"},
                            "description": "Include document bodies",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ViewResponse"
                                    }
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Query a view with POST",
                    "description": "Queries a view from a design document using POST method",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "ddoc",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "view",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ViewQuery"}
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ViewResponse"
                                    }
                                }
                            },
                        }
                    },
                },
            },
            "/{db}/{docid}/{attachment}": {
                "get": {
                    "summary": "Get attachment",
                    "description": "Gets an attachment from a document",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "docid",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "attachment",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "rev",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                            "description": "Document revision",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/octet-stream": {
                                    "schema": {"type": "string", "format": "binary"}
                                }
                            },
                        },
                        "404": {"description": "Attachment not found"},
                    },
                },
                "put": {
                    "summary": "Add/update attachment",
                    "description": "Adds or updates an attachment to a document",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "docid",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "attachment",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "rev",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Document revision",
                        },
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/octet-stream": {
                                "schema": {"type": "string", "format": "binary"}
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Attachment added/updated successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/DocumentResponse"
                                    }
                                }
                            },
                        }
                    },
                },
                "delete": {
                    "summary": "Delete attachment",
                    "description": "Deletes an attachment from a document",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "docid",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "attachment",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "rev",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Document revision",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Attachment deleted successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/DocumentResponse"
                                    }
                                }
                            },
                        }
                    },
                },
            },
            "/_replicate": {
                "post": {
                    "summary": "Replicate database",
                    "description": "Replicates a database from source to target",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ReplicationRequest"
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Replication started",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ReplicationResponse"
                                    }
                                }
                            },
                        }
                    },
                }
            },
        }

        return paths

    def generate_schemas(self):
        """
        Генерирует схемы данных (schemas) для объектов CouchDB.

        Создает OpenAPI JSON Schema определения для основных типов данных,
        используемых в CouchDB API. Схемы определяют структуру, типы полей,
        обязательные поля и ограничения для объектов, возвращаемых API.

        Генерируемые схемы:
        - ServerInfo: Информация о сервере CouchDB, включая версию, UUID,
          функции и информацию о поставщике
        - DatabaseInfo: Метаданные базы данных: имя, количество документов,
          размеры, последовательности обновлений
        - AllDocsResponse: Ответ на запрос _all_docs с массивом документов,
          общим количеством строк и смещением
        - UserDocument: Документ пользователя в системной базе _users с
          обязательными полями name, password, type, roles
        - Document: Базовый документ CouchDB с полями _id, _rev, _deleted,
          _attachments и поддержкой дополнительных свойств
        - DocumentResponse: Ответ на операции создания/обновления/удаления
          документа с полями ok, id, rev
        - MangoQuery: Запрос Mango Query с селектором, лимитом, сортировкой
          и другими параметрами
        - MangoResponse: Ответ на Mango Query с массивом документов и закладкой
        - ChangesResponse: Ответ на запрос изменений с массивом результатов
          и последней последовательностью
        - BulkDocsRequest: Запрос массовых операций с массивом документов
        - DesignDocument: Design документ с представлениями, фильтрами,
          списками и другими функциями
        - ViewQuery: Параметры запроса представления (view) с ключами,
          лимитами и другими опциями
        - ViewResponse: Ответ на запрос представления с массивом строк
          и метаданными
        - ReplicationRequest: Запрос репликации с источником, целью и параметрами
        - ReplicationResponse: Ответ на запрос репликации с историей сессий

        Returns:
            dict: Словарь схем данных в формате OpenAPI JSON Schema, где:
                - Ключ (str): Название схемы (например, "ServerInfo", "DatabaseInfo")
                - Значение (dict): Определение схемы JSON Schema, включающее:
                    - type: Тип объекта ("object", "array", "string", etc.)
                    - properties: Словарь свойств объекта с их типами
                    - required: Список обязательных полей (для UserDocument)
                    - items: Определение элементов массива (для массивов)

        Note:
            - Схемы соответствуют стандарту JSON Schema Draft 7
            - Схемы используются в paths через $ref ссылки
            - Все свойства имеют описания типов, но не все имеют ограничения
            - UserDocument, MangoQuery, BulkDocsRequest, DesignDocument,
              ReplicationRequest - схемы с обязательными полями
            - Document поддерживает дополнительные свойства (additionalProperties: True)

        Example:
            >>> generator = CouchDBSwaggerGenerator()
            >>> schemas = generator.generate_schemas()
            >>> "ServerInfo" in schemas
            True
            >>> schemas["ServerInfo"]["type"]
            'object'
            >>> "version" in schemas["ServerInfo"]["properties"]
            True
            >>> schemas["UserDocument"]["required"]
            ['name', 'password', 'type', 'roles']
            >>> "Document" in schemas
            True
            >>> "MangoQuery" in schemas
            True
            >>> schemas["Document"]["additionalProperties"]
            True
        """
        schemas = {
            "ServerInfo": {
                "type": "object",
                "properties": {
                    "couchdb": {"type": "string"},
                    "version": {"type": "string"},
                    "git_sha": {"type": "string"},
                    "uuid": {"type": "string"},
                    "features": {"type": "array", "items": {"type": "string"}},
                    "vendor": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "version": {"type": "string"},
                        },
                    },
                },
            },
            "DatabaseInfo": {
                "type": "object",
                "properties": {
                    "db_name": {"type": "string"},
                    "doc_count": {"type": "integer"},
                    "doc_del_count": {"type": "integer"},
                    "update_seq": {"type": "integer"},
                    "purge_seq": {"type": "integer"},
                    "compact_running": {"type": "boolean"},
                    "disk_size": {"type": "integer"},
                    "data_size": {"type": "integer"},
                    "instance_start_time": {"type": "string"},
                    "disk_format_version": {"type": "integer"},
                },
            },
            "AllDocsResponse": {
                "type": "object",
                "properties": {
                    "total_rows": {"type": "integer"},
                    "offset": {"type": "integer"},
                    "rows": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "key": {"type": "string"},
                                "value": {"type": "object"},
                                "doc": {"type": "object"},
                            },
                        },
                    },
                },
            },
            "UserDocument": {
                "type": "object",
                "required": ["name", "password", "type", "roles"],
                "properties": {
                    "_id": {"type": "string"},
                    "_rev": {"type": "string"},
                    "name": {"type": "string"},
                    "password": {"type": "string"},
                    "type": {"type": "string", "enum": ["user"]},
                    "roles": {"type": "array", "items": {"type": "string"}},
                },
            },
            "Document": {
                "type": "object",
                "properties": {
                    "_id": {"type": "string"},
                    "_rev": {"type": "string"},
                    "_deleted": {"type": "boolean"},
                    "_attachments": {"type": "object"},
                    "_revisions": {"type": "object"},
                    "_revs_info": {"type": "array"},
                },
                "additionalProperties": True,
            },
            "DocumentResponse": {
                "type": "object",
                "properties": {
                    "ok": {"type": "boolean"},
                    "id": {"type": "string"},
                    "rev": {"type": "string"},
                },
            },
            "MangoQuery": {
                "type": "object",
                "required": ["selector"],
                "properties": {
                    "selector": {
                        "type": "object",
                        "description": "JSON object describing criteria used to select documents",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results returned",
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Skip the first 'n' results",
                    },
                    "sort": {
                        "type": "array",
                        "description": "Array of field name direction pairs",
                        "items": {"type": "object"},
                    },
                    "fields": {
                        "type": "array",
                        "description": "Array of field names to return",
                        "items": {"type": "string"},
                    },
                    "use_index": {
                        "type": "array",
                        "description": "Index to use for query",
                        "items": {"type": "string"},
                    },
                },
            },
            "MangoResponse": {
                "type": "object",
                "properties": {
                    "docs": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Document"},
                    },
                    "bookmark": {"type": "string"},
                    "warning": {"type": "string"},
                },
            },
            "ChangesResponse": {
                "type": "object",
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "seq": {"type": "string"},
                                "id": {"type": "string"},
                                "changes": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "rev": {"type": "string"},
                                        },
                                    },
                                },
                                "deleted": {"type": "boolean"},
                                "doc": {"$ref": "#/components/schemas/Document"},
                            },
                        },
                    },
                    "last_seq": {"type": "string"},
                    "pending": {"type": "integer"},
                },
            },
            "BulkDocsRequest": {
                "type": "object",
                "required": ["docs"],
                "properties": {
                    "docs": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Document"},
                    },
                    "new_edits": {"type": "boolean", "default": True},
                },
            },
            "DesignDocument": {
                "type": "object",
                "required": ["_id", "views"],
                "properties": {
                    "_id": {"type": "string"},
                    "_rev": {"type": "string"},
                    "language": {"type": "string", "default": "javascript"},
                    "views": {
                        "type": "object",
                        "description": "Map of view names to view definitions",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "map": {"type": "string"},
                                "reduce": {"type": "string"},
                            },
                        },
                    },
                    "filters": {"type": "object"},
                    "lists": {"type": "object"},
                    "shows": {"type": "object"},
                    "updates": {"type": "object"},
                    "validate_doc_update": {"type": "string"},
                    "autoupdate": {"type": "boolean"},
                },
            },
            "ViewQuery": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Key to query"},
                    "keys": {
                        "type": "array",
                        "description": "Array of keys to query",
                        "items": {"type": "string"},
                    },
                    "startkey": {"type": "string", "description": "Start key"},
                    "endkey": {"type": "string", "description": "End key"},
                    "startkey_docid": {"type": "string"},
                    "endkey_docid": {"type": "string"},
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Skip the first 'n' results",
                    },
                    "descending": {"type": "boolean", "default": False},
                    "include_docs": {"type": "boolean", "default": False},
                    "inclusive_end": {"type": "boolean", "default": True},
                    "reduce": {"type": "boolean", "default": True},
                    "group": {"type": "boolean", "default": False},
                    "group_level": {"type": "integer"},
                },
            },
            "ViewResponse": {
                "type": "object",
                "properties": {
                    "total_rows": {"type": "integer"},
                    "offset": {"type": "integer"},
                    "rows": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "key": {"type": "string"},
                                "value": {"type": "object"},
                                "doc": {"$ref": "#/components/schemas/Document"},
                            },
                        },
                    },
                },
            },
            "ReplicationRequest": {
                "type": "object",
                "required": ["source", "target"],
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source database URL or name",
                    },
                    "target": {
                        "type": "string",
                        "description": "Target database URL or name",
                    },
                    "create_target": {"type": "boolean", "default": False},
                    "continuous": {"type": "boolean", "default": False},
                    "doc_ids": {
                        "type": "array",
                        "description": "Array of document IDs to replicate",
                        "items": {"type": "string"},
                    },
                    "filter": {"type": "string"},
                    "query_params": {"type": "object"},
                },
            },
            "ReplicationResponse": {
                "type": "object",
                "properties": {
                    "ok": {"type": "boolean"},
                    "session_id": {"type": "string"},
                    "source_last_seq": {"type": "integer"},
                    "history": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"},
                                "start_time": {"type": "string"},
                                "end_time": {"type": "string"},
                                "start_last_seq": {"type": "integer"},
                                "end_last_seq": {"type": "integer"},
                                "recorded_seq": {"type": "integer"},
                                "missing_checked": {"type": "integer"},
                                "missing_found": {"type": "integer"},
                                "docs_read": {"type": "integer"},
                                "docs_written": {"type": "integer"},
                                "doc_write_failures": {"type": "integer"},
                            },
                        },
                    },
                },
            },
        }

        return schemas

    def save_spec(self, filename, spec):
        """
        Сохраняет OpenAPI спецификацию в файл в формате JSON.

        Записывает OpenAPI спецификацию в файл с форматированием (отступы 2 пробела)
        и поддержкой Unicode символов. Файл создается в режиме записи с UTF-8
        кодировкой. При успешном сохранении выводится сообщение в stdout.

        Args:
            filename (str): Путь к файлу для сохранения спецификации.
                Может быть относительным или абсолютным путем.
                Рекомендуется использовать расширение .json.
                Примеры: "couchdb-api.json", "/path/to/api.json"
            spec (dict): OpenAPI спецификация в формате словаря Python.
                Должна соответствовать структуре, возвращаемой generate_openapi_spec().

        Raises:
            SystemExit: Выход из программы с кодом 1 при ошибке записи файла.
                Возможные причины:
                - Недостаточно прав для записи в указанную директорию
                - Диск переполнен
                - Некорректный путь к файлу
                - Файл открыт в другой программе
                Сообщение об ошибке выводится в stderr.

        Note:
            - Файл перезаписывается, если уже существует
            - JSON форматируется с отступами для читаемости
            - Unicode символы сохраняются как есть (ensure_ascii=False)
            - При успешном сохранении выводится сообщение в stdout

        Example:
            >>> generator = CouchDBSwaggerGenerator()
            >>> spec = generator.generate_openapi_spec()
            >>> generator.save_spec("couchdb-api.json", spec)
            OpenAPI spec saved to: couchdb-api.json
            >>>
            >>> # Сохранение в другую директорию
            >>> generator.save_spec("/tmp/couchdb-openapi.json", spec)
            OpenAPI spec saved to: /tmp/couchdb-openapi.json
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(spec, f, indent=2, ensure_ascii=False)
            print(f"OpenAPI spec saved to: {filename}")
        except IOError as e:
            print(f"Error saving file: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """
    Главная функция для запуска генератора OpenAPI спецификации из командной строки.

    Парсит аргументы командной строки, создает экземпляр генератора,
    подключается к CouchDB серверу, генерирует OpenAPI спецификацию и сохраняет
    её в файл в указанном формате (JSON или YAML). При выборе формата YAML
    требуется установленная библиотека PyYAML, иначе выполняется откат к JSON.

    Поддерживаемые аргументы командной строки:
        --url (str): URL CouchDB сервера.
            По умолчанию: "http://localhost:5984"
            Примеры: "http://localhost:5984", "https://couchdb.example.com:5984"

        --username, -u (str): Имя пользователя для базовой HTTP аутентификации.
            Опционально. Если указан, должен быть указан и --password.

        --password, -p (str): Пароль для базовой HTTP аутентификации.
            Опционально. Если указан, должен быть указан и --username.

        --output, -o (str): Имя выходного файла для сохранения спецификации.
            По умолчанию: "couchdb-openapi.json"
            При выборе формата YAML расширение .json автоматически заменяется на .yaml

        --format, -f (str): Формат выходного файла.
            Доступные значения: "json", "yaml"
            По умолчанию: "json"
            Для YAML требуется установленная библиотека PyYAML

    Returns:
        None: Функция не возвращает значение. Результат работы - сохраненный файл
            со спецификацией. Сообщения о прогрессе и ошибках выводятся в stdout/stderr.

    Raises:
        SystemExit: Выход из программы при:
            - Ошибке подключения к CouchDB серверу
            - Ошибке записи файла
            - Некорректных аргументах командной строки

    Note:
        - При ошибке подключения к серверу программа завершается с кодом 1
        - Если PyYAML не установлен и выбран формат YAML, выполняется откат к JSON
        - Сообщения о прогрессе выводятся в stdout
        - Сообщения об ошибках выводятся в stderr

    Example:
        Использование из командной строки:

        # Базовое использование с локальным сервером
        $ python openapi_generator.py

        # Указание URL сервера
        $ python openapi_generator.py --url http://couchdb.example.com:5984

        # С аутентификацией
        $ python openapi_generator.py -u admin -p password

        # Сохранение в YAML формате
        $ python openapi_generator.py --format yaml -o couchdb-api.yaml

        # Полный пример с всеми параметрами
        $ python openapi_generator.py \\
            --url https://couchdb.example.com:5984 \\
            --username admin \\
            --password secret \\
            --output my-couchdb-api.json \\
            --format json
    """
    parser = argparse.ArgumentParser(description="Generate OpenAPI spec for CouchDB")
    parser.add_argument(
        "--url",
        default="http://localhost:5984",
        help="CouchDB server URL (default: http://localhost:5984)",
    )
    parser.add_argument("--username", "-u", help="CouchDB username")
    parser.add_argument("--password", "-p", help="CouchDB password")
    parser.add_argument(
        "--output",
        "-o",
        default="couchdb-openapi.json",
        help="Output filename (default: couchdb-openapi.json)",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "yaml"],
        default="json",
        help="Output format (default: json)",
    )

    args = parser.parse_args()

    # Create generator
    generator = CouchDBSwaggerGenerator(
        base_url=args.url, username=args.username, password=args.password
    )

    # Generate OpenAPI spec
    print("Generating OpenAPI specification for CouchDB...")
    openapi_spec = generator.generate_openapi_spec()

    # Save based on format
    if args.format == "yaml":
        try:
            import yaml

            filename = args.output.replace(".json", ".yaml")
            with open(filename, "w", encoding="utf-8") as f:
                yaml.dump(openapi_spec, f, default_flow_style=False, allow_unicode=True)
            print(f"OpenAPI spec saved to: {filename}")
        except ImportError:
            print("PyYAML not installed. Falling back to JSON format.")
            generator.save_spec(args.output, openapi_spec)
    else:
        generator.save_spec(args.output, openapi_spec)


if __name__ == "__main__":
    main()
