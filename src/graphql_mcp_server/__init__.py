"""
GraphQL MCP Server - Dynamic tool generation from GraphQL schemas
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Dynamic MCP server for GraphQL APIs"

from graphql_mcp_server.server import GraphQLMCPServer
from graphql_mcp_server.schema_manager import SchemaManager
from graphql_mcp_server.graphql_client import GraphQLClient

__all__ = ["GraphQLMCPServer", "SchemaManager", "GraphQLClient"]
