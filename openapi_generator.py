#!/usr/bin/env python3
"""
CouchDB Swagger/OpenAPI Generator

Python version of the CLI tool digitalnodecom/couchdb-swagger for generating
OpenAPI/Swagger specifications based on CouchDB REST API.

The module provides the CouchDBSwaggerGenerator class for programmatic generation
of OpenAPI specifications and the main() function for command-line usage.

Usage example:
    >>> generator = CouchDBSwaggerGenerator(
    ...     base_url="http://localhost:5984",
    ...     username="admin",
    ...     password="password"
    ... )
    >>> spec = generator.generate_openapi_spec()
    >>> generator.save_spec("couchdb-api.json", spec)

Command-line usage example:
    $ python openapi_generator.py --url http://localhost:5984 --output api.json
    $ python openapi_generator.py --url http://localhost:5984 -u admin -p password -f yaml
"""

import argparse
import json
import sys

import requests


class CouchDBSwaggerGenerator:
    """
    OpenAPI/Swagger specification generator for CouchDB API.

    This class provides functionality to connect to a CouchDB server
    and generate OpenAPI specifications based on available endpoints and data schemas.
    Supports basic HTTP authentication and automatically detects the CouchDB server
    version for inclusion in the specification.

    Attributes:
        base_url (str): Base URL of the CouchDB server without trailing slash.
            Used for all HTTP requests to the server.
        auth (tuple[str, str] | None): Tuple (username, password) for basic
            HTTP authentication. Set to None if credentials are not provided.

    Example:
        >>> # Create generator without authentication
        >>> generator = CouchDBSwaggerGenerator()
        >>>
        >>> # Create generator with authentication
        >>> generator = CouchDBSwaggerGenerator(
        ...     base_url="http://couchdb.example.com:5984",
        ...     username="admin",
        ...     password="secret"
        ... )
        >>>
        >>> # Generate and save specification
        >>> spec = generator.generate_openapi_spec(version="3.0.0")
        >>> generator.save_spec("couchdb-openapi.json", spec)

    Note:
        During initialization, the URL is automatically cleaned of trailing slash
        to ensure consistency when forming request paths.
    """

    def __init__(self, base_url="http://localhost:5984", username=None, password=None):
        """
        Initialize the OpenAPI specification generator for CouchDB.

        Creates a new generator instance with the specified connection parameters.
        If username and password are provided, basic HTTP authentication is configured
        for all subsequent requests.

        Args:
            base_url (str, optional): Base URL of the CouchDB server.
                Must include protocol (http:// or https://) and port if necessary.
                Default: "http://localhost:5984".
                Examples: "http://localhost:5984", "https://couchdb.example.com:5984"
            username (str | None, optional): Username for basic HTTP authentication.
                If specified, password must also be specified.
                Default: None (no authentication).
            password (str | None, optional): Password for basic HTTP authentication.
                If specified, username must also be specified.
                Default: None (no authentication).

        Note:
            - URL is automatically cleaned of trailing slash
            - If only username or only password is specified, authentication
              will not be configured (auth will be None)
            - For secured servers, both authentication parameters must be specified

        Example:
            >>> # Local server without authentication
            >>> gen1 = CouchDBSwaggerGenerator()
            >>>
            >>> # Remote server with authentication
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
        Get information about the CouchDB server.

        Performs a GET request to the root CouchDB endpoint (/) to retrieve
        information about version, features, and other server metadata. This information
        is used to generate the OpenAPI specification with the correct CouchDB
        version in the API metadata.

        The method first attempts to connect without authentication, as most
        CouchDB endpoints (including server info) are publicly accessible.
        If authentication is required (401 error) and credentials are provided,
        the request is retried with authentication.

        Returns:
            dict | None: Dictionary with server information in JSON format, or None
                if the server is not accessible. Typical structure:
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

        Note:
            - Method first attempts connection without authentication
            - If 401 error occurs and credentials are available, retries with authentication
            - Returns None if server is not accessible (allows schema generation to continue)
            - For successful execution, CouchDB server should be accessible
              at the specified base_url, but schema generation can proceed without it

        Example:
            >>> generator = CouchDBSwaggerGenerator()
            >>> info = generator.get_server_info()
            >>> if info:
            ...     print(info["version"])
            '3.3.0'
        """
        # First, try without authentication (most CouchDB endpoints are public)
        try:
            response = requests.get(self.base_url, auth=None)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            # If we got 401 and have credentials, try with authentication
            if e.response.status_code == 401 and self.auth is not None:
                try:
                    response = requests.get(self.base_url, auth=self.auth)
                    response.raise_for_status()
                    return response.json()
                except requests.RequestException:
                    # If authenticated request also fails, return None
                    # Schema generation can continue without server info
                    return None
            # For other HTTP errors or if no credentials available, return None
            return None
        except requests.RequestException:
            # For connection errors, return None instead of exiting
            # Schema generation can continue without server info
            return None

    def generate_openapi_spec(self, version="3.0.0"):
        """
        Generate a complete OpenAPI specification for CouchDB API.

        Creates a complete OpenAPI specification version 3.0.0, including server
        information, all available paths (endpoints), data schemas, and security
        settings. The CouchDB version is automatically determined by querying
        the server and included in the specification metadata.

        Args:
            version (str, optional): OpenAPI specification version.
                OpenAPI 3.x versions are supported. Default: "3.0.0".
                It is recommended to use "3.0.0" or "3.1.0" for compatibility
                with most tools.

        Returns:
            dict: Complete OpenAPI specification in dictionary format, conforming
                to OpenAPI 3.0 standard. Structure includes:
                - openapi (str): OpenAPI specification version
                - info (dict): API metadata:
                    - title: "CouchDB API"
                    - description: Description with CouchDB version
                    - version: CouchDB server version
                    - contact: Apache CouchDB contact information
                - servers (list): List of servers with base URL
                - paths (dict): All available endpoints with HTTP methods
                - components (dict): Specification components:
                    - schemas: Data schemas for CouchDB objects
                    - securitySchemes: Security schemes (basicAuth)
                - security (list): Default security settings

        Note:
            - Method attempts to query the server via get_server_info() to
              get the CouchDB version, but can proceed without it if the server
              is not accessible (version will be set to "unknown")
            - Schema generation does not require server access - most endpoints
              and schemas are statically defined
            - Specification is compatible with tools like Swagger UI,
              Postman, Insomnia, and other OpenAPI-compatible clients

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
        if server_info:
            couchdb_version = server_info.get("version", "unknown")
        else:
            couchdb_version = "unknown"
            print(
                "Warning: Could not connect to CouchDB server. "
                "Generating schema without server version information.",
                file=sys.stderr,
            )

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
        Generate path definitions for main CouchDB endpoints.

        Creates OpenAPI definitions for main CouchDB REST API endpoints.
        Each path includes HTTP method descriptions, parameters, requests,
        responses, and status codes. Definitions conform to OpenAPI 3.0 standard.

        Supported endpoints:
        Server endpoints:
        - GET /: CouchDB server information
        - GET /_all_dbs: List all databases in the instance
        - GET /_active_tasks: List active tasks
        - POST /_dbs_info: Get information about multiple databases
        - GET /_cluster_setup: Get cluster setup status
        - POST /_cluster_setup: Configure cluster
        - GET /_db_updates: List database updates
        - GET /_membership: Get cluster membership
        - GET /_scheduler/jobs: List replication jobs
        - GET /_scheduler/docs: List replication document jobs
        - GET /_node/{node-name}: Get node information
        - GET /_node/{node-name}/_stats: Get node statistics
        - GET /_node/{node-name}/_prometheus: Get Prometheus metrics
        - GET /_node/{node-name}/_smoosh/status: Get smoosh status
        - GET /_node/{node-name}/_system: Get system information
        - POST /_node/{node-name}/_restart: Restart node
        - GET /_node/{node-name}/_versions: Get node versions
        - POST /_search_analyze: Analyze search text
        - POST /_nouveau_analyze: Analyze nouveau text
        - GET /_up: Check server status
        - GET /_uuids: Generate UUIDs
        - GET /_reshard: Get resharding status
        - POST /_reshard: Start resharding
        - POST /_replicate: Replicate database

        Database endpoints:
        - PUT /{db}: Create a new database
        - GET /{db}: Get database information
        - DELETE /{db}: Delete database
        - GET /{db}/_all_docs: Get all documents from the database
        - GET /{db}/_design_docs: Get all design documents
        - POST /{db}/_bulk_get: Bulk get documents
        - GET /{db}/_index: List indexes
        - POST /{db}/_index: Create index
        - DELETE /{db}/_index: Delete index
        - POST /{db}/_explain: Explain query
        - GET /{db}/_shards: Get database shards
        - GET /{db}/_shards/{docid}: Get document shards
        - POST /{db}/_sync_shards: Sync database shards
        - POST /{db}/_compact: Compact database
        - POST /{db}/_compact/{ddoc}: Compact design document
        - POST /{db}/_ensure_full_commit: Ensure full commit
        - POST /{db}/_view_cleanup: Cleanup view indexes
        - POST /{db}/_search_cleanup: Cleanup search indexes
        - POST /{db}/_nouveau_cleanup: Cleanup nouveau indexes
        - GET /{db}/_security: Get database security
        - PUT /{db}/_security: Set database security
        - POST /{db}/_purge: Purge documents
        - GET /{db}/_purged_infos: Get purged information
        - GET /{db}/_purged_infos_limit: Get purged information limit
        - PUT /{db}/_purged_infos_limit: Set purged information limit
        - POST /{db}/_missing_revs: Get missing revisions
        - POST /{db}/_revs_diff: Get revision differences
        - GET /{db}/_revs_limit: Get revision limit
        - PUT /{db}/_revs_limit: Set revision limit
        - GET /{db}/_changes: Get database changes stream
        - POST /{db}/_bulk_docs: Bulk document operations
        - POST /{db}/_find: Query documents using Mango Query

        Document endpoints:
        - GET /{db}/{docid}: Get document
        - PUT /{db}/{docid}: Create or update document
        - DELETE /{db}/{docid}: Delete document
        - HEAD /{db}/{docid}: Check document existence
        - GET /{db}/{docid}/{attachment}: Get attachment
        - PUT /{db}/{docid}/{attachment}: Add or update attachment
        - DELETE /{db}/{docid}/{attachment}: Delete attachment

        Design Document endpoints:
        - GET /{db}/_design/{ddoc}: Get design document
        - PUT /{db}/_design/{ddoc}: Create or update design document
        - DELETE /{db}/_design/{ddoc}: Delete design document
        - GET /{db}/_design/{ddoc}/_info: Get design document information
        - GET /{db}/_design/{ddoc}/_view/{view}: Query a view
        - POST /{db}/_design/{ddoc}/_view/{view}: Query a view via POST
        - GET /{db}/_design/{ddoc}/_search/{index}: Query search index
        - POST /{db}/_design/{ddoc}/_search/{index}: Query search index with POST
        - GET /{db}/_design/{ddoc}/_search_info/{index}: Get search index information
        - GET /{db}/_design/{ddoc}/_nouveau/{index}: Query nouveau index
        - POST /{db}/_design/{ddoc}/_nouveau/{index}: Query nouveau index with POST
        - GET /{db}/_design/{ddoc}/_nouveau_info/{index}: Get nouveau index information
        - GET /{db}/_design/{ddoc}/_show/{func}: Execute show function
        - GET /{db}/_design/{ddoc}/_show/{func}/{docid}: Execute show function for document
        - GET /{db}/_design/{ddoc}/_list/{func}/{view}: Execute list function
        - GET /{db}/_design/{ddoc}/_list/{func}/{other-ddoc}/{view}: Execute list function from another design document
        - POST /{db}/_design/{ddoc}/_update/{func}: Execute update function
        - PUT /{db}/_design/{ddoc}/_update/{func}/{docid}: Execute update function for document
        - GET /{db}/_design/{ddoc}/_rewrite/{path}: Rewrite URL

        Partitioned Database endpoints:
        - GET /{db}/_partition/{partition_id}: Get partition information
        - GET /{db}/_partition/{partition_id}/_all_docs: Get all documents in partition
        - GET /{db}/_partition/{partition_id}/_design/{ddoc}/_view/{view}: Query a view in partition
        - POST /{db}/_partition/{partition_id}/_find: Query documents in partition using Mango
        - POST /{db}/_partition/{partition_id}/_explain: Explain query in partition

        Local Documents endpoints:
        - GET /{db}/_local_docs: Get all local documents
        - POST /{db}/_local_docs/queries: Query local documents
        - GET /{db}/_local/{docid}: Get local document
        - PUT /{db}/_local/{docid}: Create or update local document
        - DELETE /{db}/_local/{docid}: Delete local document

        User endpoints:
        - GET /_users: Information about the system users database
        - GET /_users/{user_id}: Get user document
        - PUT /_users/{user_id}: Create or update user

        Returns:
            dict: Dictionary with path definitions in OpenAPI 3.0 format, where:
                - Key (str): Endpoint path (e.g., "/", "/_all_dbs", "/{db}")
                - Value (dict): Object with HTTP methods (get, put, delete) and their
                  descriptions, including:
                    - summary: Brief operation description
                    - description: Detailed operation description
                    - parameters: List of path/query parameters
                    - requestBody: Request body (for PUT methods)
                    - responses: Response codes and their descriptions
                    - content: Data schemas for responses

        Note:
            - Paths with parameters use OpenAPI syntax: {param_name}
            - All definitions include standard HTTP response codes
            - Response schemas reference components in generate_schemas()
            - Method does not perform server requests, only forms the structure

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
            "/_active_tasks": {
                "get": {
                    "summary": "List active tasks",
                    "description": "Returns a list of active tasks, including the task type, name, status and progress",
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"type": "object"},
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/_dbs_info": {
                "post": {
                    "summary": "Get information about multiple databases",
                    "description": "Returns information about a list of specified databases",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "keys": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"type": "object"},
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/_cluster_setup": {
                "get": {
                    "summary": "Get cluster setup status",
                    "description": "Returns the status of the node or cluster, per the cluster setup wizard",
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Configure cluster",
                    "description": "Configure a node as a single node, as part of a cluster, or finalize a cluster",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
            },
            "/_db_updates": {
                "get": {
                    "summary": "List database updates",
                    "description": "Returns a list of all database events in the CouchDB instance",
                    "parameters": [
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
                            "name": "timeout",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer"},
                            "description": "Number of seconds to wait for a change before the response closes",
                        },
                        {
                            "name": "heartbeat",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer"},
                            "description": "Period in milliseconds after which an empty line is sent in the results",
                        },
                        {
                            "name": "since",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                            "description": "Start from this update sequence",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/_membership": {
                "get": {
                    "summary": "Get cluster membership",
                    "description": "Displays the nodes that are part of the cluster as cluster_nodes",
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/_scheduler/jobs": {
                "get": {
                    "summary": "List replication jobs",
                    "description": "Returns information about replication jobs",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer"},
                            "description": "Maximum number of results",
                        },
                        {
                            "name": "skip",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer"},
                            "description": "Skip this number of results before returning",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/_scheduler/docs": {
                "get": {
                    "summary": "List replication document jobs",
                    "description": "Returns information about replication document jobs",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer"},
                            "description": "Maximum number of results",
                        },
                        {
                            "name": "skip",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer"},
                            "description": "Skip this number of results before returning",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/_node/{node-name}": {
                "get": {
                    "summary": "Get node information",
                    "description": "Returns information about the specified node",
                    "parameters": [
                        {
                            "name": "node-name",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/_node/{node-name}/_stats": {
                "get": {
                    "summary": "Get node statistics",
                    "description": "Returns statistics for the running server",
                    "parameters": [
                        {
                            "name": "node-name",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/_node/{node-name}/_prometheus": {
                "get": {
                    "summary": "Get Prometheus metrics",
                    "description": "Returns metrics in Prometheus format",
                    "parameters": [
                        {
                            "name": "node-name",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "text/plain": {
                                    "schema": {"type": "string"},
                                }
                            },
                        }
                    },
                }
            },
            "/_node/{node-name}/_smoosh/status": {
                "get": {
                    "summary": "Get smoosh status",
                    "description": "Returns status of the smoosh compaction daemon",
                    "parameters": [
                        {
                            "name": "node-name",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/_node/{node-name}/_system": {
                "get": {
                    "summary": "Get system information",
                    "description": "Returns system information for the node",
                    "parameters": [
                        {
                            "name": "node-name",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/_node/{node-name}/_restart": {
                "post": {
                    "summary": "Restart node",
                    "description": "Restarts the node",
                    "parameters": [
                        {
                            "name": "node-name",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/_node/{node-name}/_versions": {
                "get": {
                    "summary": "Get node versions",
                    "description": "Returns version information for the node",
                    "parameters": [
                        {
                            "name": "node-name",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/_search_analyze": {
                "post": {
                    "summary": "Analyze search text",
                    "description": "Tests analysis of search text",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/_nouveau_analyze": {
                "post": {
                    "summary": "Analyze nouveau text",
                    "description": "Tests analysis of nouveau text",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/_up": {
                "get": {
                    "summary": "Check server status",
                    "description": "Confirms that the server is up, running, and ready to accept requests",
                    "responses": {
                        "200": {
                            "description": "Server is up and running",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/_uuids": {
                "get": {
                    "summary": "Generate UUIDs",
                    "description": "Requests one or more Universally Unique Identifiers (UUIDs) from the CouchDB instance",
                    "parameters": [
                        {
                            "name": "count",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer"},
                            "description": "Number of UUIDs to generate",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "uuids": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                            }
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/_reshard": {
                "get": {
                    "summary": "Get resharding status",
                    "description": "Returns status of resharding jobs",
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Start resharding",
                    "description": "Starts resharding jobs",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
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
            "/{db}/_design_docs": {
                "get": {
                    "summary": "Get all design documents",
                    "description": "Returns all design documents in the database",
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
            "/{db}/_bulk_get": {
                "post": {
                    "summary": "Bulk get documents",
                    "description": "Returns multiple documents in a single request",
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
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_index": {
                "get": {
                    "summary": "List indexes",
                    "description": "Returns a list of all indexes in the database",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Create index",
                    "description": "Creates a new index",
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
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
                "delete": {
                    "summary": "Delete index",
                    "description": "Deletes an index",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "ddoc",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Design document name",
                        },
                        {
                            "name": "name",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Index name",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
            },
            "/{db}/_explain": {
                "post": {
                    "summary": "Explain query",
                    "description": "Shows which index is being used by the query",
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
                                "schema": {"$ref": "#/components/schemas/MangoQuery"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_shards": {
                "get": {
                    "summary": "Get database shards",
                    "description": "Returns information about the shards in a database",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_shards/{docid}": {
                "get": {
                    "summary": "Get document shards",
                    "description": "Returns information about the shards where a document is stored",
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
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_sync_shards": {
                "post": {
                    "summary": "Sync database shards",
                    "description": "Synchronizes database shards",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_compact": {
                "post": {
                    "summary": "Compact database",
                    "description": "Starts compaction of the specified database",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "202": {
                            "description": "Compaction request has been accepted",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_compact/{ddoc}": {
                "post": {
                    "summary": "Compact design document",
                    "description": "Starts compaction of the view indexes associated with the specified design document",
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
                        "202": {
                            "description": "Compaction request has been accepted",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_ensure_full_commit": {
                "post": {
                    "summary": "Ensure full commit",
                    "description": "Ensures that all changes to the database are committed to disk",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_view_cleanup": {
                "post": {
                    "summary": "Cleanup view indexes",
                    "description": "Removes view index files that are no longer required",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "202": {
                            "description": "Cleanup request has been accepted",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_search_cleanup": {
                "post": {
                    "summary": "Cleanup search indexes",
                    "description": "Removes search index files that are no longer required",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "202": {
                            "description": "Cleanup request has been accepted",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_nouveau_cleanup": {
                "post": {
                    "summary": "Cleanup nouveau indexes",
                    "description": "Removes nouveau index files that are no longer required",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "202": {
                            "description": "Cleanup request has been accepted",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_security": {
                "get": {
                    "summary": "Get database security",
                    "description": "Returns the current security object from the specified database",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
                "put": {
                    "summary": "Set database security",
                    "description": "Sets the security object for the given database",
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
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
            },
            "/{db}/_purge": {
                "post": {
                    "summary": "Purge documents",
                    "description": "Purges documents from the database",
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
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_purged_infos": {
                "get": {
                    "summary": "Get purged information",
                    "description": "Returns information about purged documents",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_purged_infos_limit": {
                "get": {
                    "summary": "Get purged information limit",
                    "description": "Returns the limit of purged information",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
                "put": {
                    "summary": "Set purged information limit",
                    "description": "Sets the limit of purged information",
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
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
            },
            "/{db}/_missing_revs": {
                "post": {
                    "summary": "Get missing revisions",
                    "description": "Returns the document revisions that do not exist in the database",
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
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_revs_diff": {
                "post": {
                    "summary": "Get revision differences",
                    "description": (
                        "Given a set of document/revision IDs, returns the subset "
                        "of those that do not correspond to revisions stored in the database"
                    ),
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
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_revs_limit": {
                "get": {
                    "summary": "Get revision limit",
                    "description": "Returns the limit of document revisions",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
                "put": {
                    "summary": "Set revision limit",
                    "description": "Sets the limit of document revisions",
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
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
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
            "/{db}/_design/{ddoc}/_info": {
                "get": {
                    "summary": "Get design document information",
                    "description": "Returns information about a design document",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_design/{ddoc}/_search/{index}": {
                "get": {
                    "summary": "Query search index",
                    "description": "Queries a search index from a design document",
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
                            "name": "index",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "q",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                            "description": "Query string",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Query search index with POST",
                    "description": "Queries a search index from a design document using POST method",
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
                            "name": "index",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
            },
            "/{db}/_design/{ddoc}/_search_info/{index}": {
                "get": {
                    "summary": "Get search index information",
                    "description": "Returns information about a search index",
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
                            "name": "index",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_design/{ddoc}/_nouveau/{index}": {
                "get": {
                    "summary": "Query nouveau index",
                    "description": "Queries a nouveau index from a design document",
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
                            "name": "index",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Query nouveau index with POST",
                    "description": "Queries a nouveau index from a design document using POST method",
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
                            "name": "index",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                },
            },
            "/{db}/_design/{ddoc}/_nouveau_info/{index}": {
                "get": {
                    "summary": "Get nouveau index information",
                    "description": "Returns information about a nouveau index",
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
                            "name": "index",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_design/{ddoc}/_show/{func}": {
                "get": {
                    "summary": "Execute show function",
                    "description": "Executes a show function from a design document",
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
                            "name": "func",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "text/html": {
                                    "schema": {"type": "string"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_design/{ddoc}/_show/{func}/{docid}": {
                "get": {
                    "summary": "Execute show function for document",
                    "description": "Executes a show function from a design document for a specific document",
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
                            "name": "func",
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
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "text/html": {
                                    "schema": {"type": "string"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_design/{ddoc}/_list/{func}/{view}": {
                "get": {
                    "summary": "Execute list function",
                    "description": "Executes a list function from a design document",
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
                            "name": "func",
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
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "text/html": {
                                    "schema": {"type": "string"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_design/{ddoc}/_list/{func}/{other-ddoc}/{view}": {
                "get": {
                    "summary": "Execute list function from another design document",
                    "description": "Executes a list function from a design document using a view from another design document",
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
                            "name": "func",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "other-ddoc",
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
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "text/html": {
                                    "schema": {"type": "string"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_design/{ddoc}/_update/{func}": {
                "post": {
                    "summary": "Execute update function",
                    "description": "Executes an update function from a design document",
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
                            "name": "func",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_design/{ddoc}/_update/{func}/{docid}": {
                "put": {
                    "summary": "Execute update function for document",
                    "description": "Executes an update function from a design document for a specific document",
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
                            "name": "func",
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
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_design/{ddoc}/_rewrite/{path}": {
                "get": {
                    "summary": "Rewrite URL",
                    "description": "Rewrites a URL using rewrite rules from a design document",
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
                            "name": "path",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
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
            "/{db}/_partition/{partition_id}": {
                "get": {
                    "summary": "Get partition information",
                    "description": "Returns information about a partition",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "partition_id",
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
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_partition/{partition_id}/_all_docs": {
                "get": {
                    "summary": "Get all documents in partition",
                    "description": "Returns all documents in the partition",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "partition_id",
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
                                        "$ref": "#/components/schemas/AllDocsResponse"
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_partition/{partition_id}/_design/{ddoc}/_view/{view}": {
                "get": {
                    "summary": "Query a view in partition",
                    "description": "Queries a view from a design document in a partition",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "partition_id",
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
                }
            },
            "/{db}/_partition/{partition_id}/_find": {
                "post": {
                    "summary": "Query documents in partition using Mango",
                    "description": "Query documents in a partition using the Mango query syntax",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "partition_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MangoQuery"},
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
                        }
                    },
                }
            },
            "/{db}/_partition/{partition_id}/_explain": {
                "post": {
                    "summary": "Explain query in partition",
                    "description": "Shows which index is being used by the query in a partition",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "partition_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MangoQuery"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_local_docs": {
                "get": {
                    "summary": "Get all local documents",
                    "description": "Returns all local documents in the database",
                    "parameters": [
                        {
                            "name": "db",
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
                                        "$ref": "#/components/schemas/AllDocsResponse"
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_local_docs/queries": {
                "post": {
                    "summary": "Query local documents",
                    "description": "Queries local documents using multiple queries",
                    "parameters": [
                        {
                            "name": "db",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                }
                            },
                        }
                    },
                }
            },
            "/{db}/_local/{docid}": {
                "get": {
                    "summary": "Get local document",
                    "description": "Gets a local document from the specified database",
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
                        "200": {
                            "description": "Request completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Document"},
                                }
                            },
                        },
                        "404": {"description": "Document not found"},
                    },
                },
                "put": {
                    "summary": "Create/update local document",
                    "description": "Creates or updates a local document in the specified database",
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
                                "schema": {"$ref": "#/components/schemas/Document"},
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
                    },
                },
                "delete": {
                    "summary": "Delete local document",
                    "description": "Deletes a local document from the specified database",
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
        Generate data schemas for CouchDB objects.

        Creates OpenAPI JSON Schema definitions for main data types
        used in CouchDB API. Schemas define structure, field types,
        required fields, and constraints for objects returned by the API.

        Generated schemas:
        - ServerInfo: CouchDB server information, including version, UUID,
          features, and vendor information
        - DatabaseInfo: Database metadata: name, document count,
          sizes, update sequences
        - AllDocsResponse: Response to _all_docs request with array of documents,
          total row count, and offset
        - UserDocument: User document in system _users database with
          required fields name, password, type, roles
        - Document: Base CouchDB document with fields _id, _rev, _deleted,
          _attachments, and support for additional properties
        - DocumentResponse: Response to document create/update/delete operations
          with fields ok, id, rev
        - MangoQuery: Mango Query request with selector, limit, sort
          and other parameters
        - MangoResponse: Response to Mango Query with array of documents and bookmark
        - ChangesResponse: Response to changes request with array of results
          and last sequence
        - BulkDocsRequest: Bulk operations request with array of documents
        - DesignDocument: Design document with views, filters,
          lists, and other functions
        - ViewQuery: View query parameters with keys,
          limits, and other options
        - ViewResponse: Response to view query with array of rows
          and metadata
        - ReplicationRequest: Replication request with source, target, and parameters
        - ReplicationResponse: Response to replication request with session history

        Returns:
            dict: Dictionary of data schemas in OpenAPI JSON Schema format, where:
                - Key (str): Schema name (e.g., "ServerInfo", "DatabaseInfo")
                - Value (dict): JSON Schema definition, including:
                    - type: Object type ("object", "array", "string", etc.)
                    - properties: Dictionary of object properties with their types
                    - required: List of required fields (for UserDocument)
                    - items: Array element definition (for arrays)

        Note:
            - Schemas conform to JSON Schema Draft 7 standard
            - Schemas are used in paths via $ref references
            - All properties have type descriptions, but not all have constraints
            - UserDocument, MangoQuery, BulkDocsRequest, DesignDocument,
              ReplicationRequest - schemas with required fields
            - Document supports additional properties (additionalProperties: True)

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
        Save OpenAPI specification to a file in JSON format.

        Writes OpenAPI specification to a file with formatting (2-space indentation)
        and Unicode character support. File is created in write mode with UTF-8
        encoding. On successful save, a message is printed to stdout.

        Args:
            filename (str): Path to file for saving the specification.
                Can be relative or absolute path.
                It is recommended to use .json extension.
                Examples: "couchdb-api.json", "/path/to/api.json"
            spec (dict): OpenAPI specification in Python dictionary format.
                Must match the structure returned by generate_openapi_spec().

        Raises:
            SystemExit: Exit the program with code 1 on file write error.
                Possible causes:
                - Insufficient permissions to write to the specified directory
                - Disk full
                - Invalid file path
                - File is open in another program
                Error message is printed to stderr.

        Note:
            - File is overwritten if it already exists
            - JSON is formatted with indentation for readability
            - Unicode characters are saved as-is (ensure_ascii=False)
            - On successful save, a message is printed to stdout

        Example:
            >>> generator = CouchDBSwaggerGenerator()
            >>> spec = generator.generate_openapi_spec()
            >>> generator.save_spec("couchdb-api.json", spec)
            OpenAPI spec saved to: couchdb-api.json
            >>>
            >>> # Save to a different directory
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
    Main function for running the OpenAPI specification generator from command line.

    Parses command-line arguments, creates a generator instance,
    connects to CouchDB server, generates OpenAPI specification, and saves
    it to a file in the specified format (JSON or YAML). When YAML format is selected,
    PyYAML library must be installed, otherwise falls back to JSON.

    Supported command-line arguments:
        --url (str): CouchDB server URL.
            Default: "http://localhost:5984"
            Examples: "http://localhost:5984", "https://couchdb.example.com:5984"

        --username, -u (str): Username for basic HTTP authentication.
            Optional. If specified, --password must also be specified.

        --password, -p (str): Password for basic HTTP authentication.
            Optional. If specified, --username must also be specified.

        --output, -o (str): Output filename for saving the specification.
            Default: "couchdb-openapi.json"
            When YAML format is selected, .json extension is automatically replaced with .yaml

        --format, -f (str): Output file format.
            Available values: "json", "yaml"
            Default: "json"
            PyYAML library is required for YAML format

    Returns:
        None: Function does not return a value. Result of work is a saved file
            with the specification. Progress and error messages are printed to stdout/stderr.

    Raises:
        SystemExit: Exit the program on:
            - CouchDB server connection error
            - File write error
            - Invalid command-line arguments

    Note:
        - On server connection error, program exits with code 1
        - If PyYAML is not installed and YAML format is selected, falls back to JSON
        - Progress messages are printed to stdout
        - Error messages are printed to stderr

    Example:
        Command-line usage:

        # Basic usage with local server
        $ python openapi_generator.py

        # Specify server URL
        $ python openapi_generator.py --url http://couchdb.example.com:5984

        # With authentication
        $ python openapi_generator.py -u admin -p password

        # Save in YAML format
        $ python openapi_generator.py --format yaml -o couchdb-api.yaml

        # Full example with all parameters
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
