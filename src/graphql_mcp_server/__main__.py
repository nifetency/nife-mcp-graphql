#!/usr/bin/env python3
"""
Main entry point for GraphQL MCP Server
"""
import asyncio
from graphql_mcp_server.server import GraphQLMCPServer

async def main():
    server = GraphQLMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
