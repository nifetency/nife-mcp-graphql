#!/usr/bin/env python3
"""
Main entry point for GraphQL MCP Server
Supports configuration via CLI args, environment variables, or .env file
Priority: CLI args > Environment variables > .env file > defaults
"""
import asyncio
import argparse
import os
import sys
from dotenv import load_dotenv


def parse_args():
    parser = argparse.ArgumentParser(
        description="GraphQL MCP Server - Dynamic MCP server for any GraphQL API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration priority (highest to lowest):
  1. CLI arguments (--endpoint, --token, etc.)
  2. Environment variables (GRAPHQL_ENDPOINT, API_ACCESS_TOKEN, etc.)
  3. .env file in current working directory
  4. Built-in defaults

Examples:
  # Run with CLI args
  graphql-mcp-server --endpoint https://api.example.com/graphql --token mytoken

  # Run in HTTP mode (Docker/server deployments)
  graphql-mcp-server --endpoint https://api.example.com/graphql --mode http --port 8080

  # Run with env vars
  GRAPHQL_ENDPOINT=https://api.example.com/graphql API_ACCESS_TOKEN=mytoken graphql-mcp-server

  # Claude Desktop config (no CLI args needed — env block handles it)
  See: https://github.com/your-repo#claude-desktop
        """
    )

    parser.add_argument(
        "--endpoint",
        metavar="URL",
        help="GraphQL API endpoint URL (overrides GRAPHQL_ENDPOINT env var)"
    )
    parser.add_argument(
        "--token",
        metavar="TOKEN",
        help="API access token for authentication (overrides API_ACCESS_TOKEN env var)"
    )
    parser.add_argument(
        "--mode",
        choices=["stdio", "http"],
        default=None,
        help="Server mode: 'stdio' for MCP clients (default), 'http' for Docker/server deployments (overrides MCP_MODE env var)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        metavar="PORT",
        help="HTTP server port, only used when --mode=http (default: 8080, overrides MCP_SERVER_PORT env var)"
    )
    parser.add_argument(
        "--host",
        default=None,
        metavar="HOST",
        help="HTTP server host, only used when --mode=http (default: 0.0.0.0, overrides MCP_SERVER_HOST env var)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
        metavar="LEVEL",
        help="Logging level (default: INFO, overrides LOG_LEVEL env var)"
    )
    parser.add_argument(
        "--env-file",
        default=None,
        metavar="PATH",
        help="Path to a custom .env file (default: looks for .env in current directory)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    return parser.parse_args()


async def main():
    args = parse_args()

    # Load .env file first (lowest priority — CLI args and real env vars override it)
    if args.env_file:
        if not os.path.exists(args.env_file):
            print(f"[ERROR] --env-file not found: {args.env_file}", file=sys.stderr)
            sys.exit(1)
        load_dotenv(dotenv_path=args.env_file, override=False)
    else:
        load_dotenv(override=False)  # loads .env from cwd if present, won't override real env vars

    # Apply CLI args into environment (they take highest priority)
    if args.endpoint:
        os.environ["GRAPHQL_ENDPOINT"] = args.endpoint

    if args.token:
        os.environ["API_ACCESS_TOKEN"] = args.token

    if args.mode:
        os.environ["MCP_MODE"] = args.mode

    if args.port is not None:
        os.environ["MCP_SERVER_PORT"] = str(args.port)

    if args.host:
        os.environ["MCP_SERVER_HOST"] = args.host

    if args.log_level:
        os.environ["LOG_LEVEL"] = args.log_level

    # Validate required config
    if not os.environ.get("GRAPHQL_ENDPOINT"):
        print(
            "[ERROR] GraphQL endpoint not configured.\n"
            "\n"
            "Set it using one of these methods:\n"
            "  1. CLI arg:    graphql-mcp-server --endpoint https://api.example.com/graphql\n"
            "  2. Env var:    export GRAPHQL_ENDPOINT=https://api.example.com/graphql\n"
            "  3. .env file:  echo 'GRAPHQL_ENDPOINT=https://api.example.com/graphql' > .env\n"
            "  4. Claude Desktop config: add GRAPHQL_ENDPOINT to the 'env' block\n",
            file=sys.stderr
        )
        sys.exit(1)

    # Now import and run the server (imports after env setup so config is ready)
    from graphql_mcp_server.server import GraphQLMCPServer
    server = GraphQLMCPServer()
    await server.run()


def main_sync():
    """Synchronous entry point for the CLI script registered in pyproject.toml"""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
