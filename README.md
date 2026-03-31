# GraphQL MCP Server

![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![MCP](https://img.shields.io/badge/MCP-compatible-purple)

A dynamic Model Context Protocol (MCP) server that automatically discovers and generates tools from any GraphQL API schema. Point it at any GraphQL endpoint and it instantly exposes every query and mutation as an MCP tool — zero manual configuration.

---

## Installation

```bash
pip install graphql-mcp-server
```

---

## Configuration

There are **four ways** to configure the server. They are applied in priority order — higher entries win:

| Priority | Method | Best for |
|----------|--------|----------|
| 1  | CLI arguments | One-off runs, testing |
| 2 | Environment variables | Docker, CI/CD, shell scripts |
| 3 | `.env` file | Local development |
| 4  | Defaults | Nothing required by default |

### Method 1 — CLI Arguments

```bash
graphql-mcp-server --endpoint https://api.example.com/graphql --token mytoken
```

All available flags:

```
--endpoint URL       GraphQL API endpoint (required if not set via env)
--token TOKEN        API access token for authentication
--mode stdio|http    Server mode (default: stdio)
--port PORT          HTTP port, only used in http mode (default: 8080)
--host HOST          HTTP host, only used in http mode (default: 0.0.0.0)
--log-level LEVEL    Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
--env-file PATH      Path to a custom .env file
--version            Show version and exit
```

### Method 2 — Environment Variables

```bash
export GRAPHQL_ENDPOINT=https://api.example.com/graphql
export API_ACCESS_TOKEN=your_token_here
export MCP_MODE=stdio

graphql-mcp-server
```

### Method 3 — `.env` File

Create a `.env` file in your working directory:

```env
GRAPHQL_ENDPOINT=https://api.example.com/graphql
API_ACCESS_TOKEN=your_token_here
MCP_MODE=stdio
LOG_LEVEL=INFO
```

Then just run:

```bash
graphql-mcp-server
```

### Method 4 — Claude Desktop Config (most common for MCP use)

No `.env` file needed. Pass everything via the `env` block in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "graphql": {
      "command": "graphql-mcp-server",
      "env": {
        "GRAPHQL_ENDPOINT": "https://api.example.com/graphql",
        "API_ACCESS_TOKEN": "your_token_here",
        "MCP_MODE": "stdio",
        "ENABLE_HTTP_ENDPOINT": "false"
      }
    }
  }
}
```

Claude Desktop injects the `env` block values directly into the process — this is the standard MCP pattern.

---

## Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GRAPHQL_ENDPOINT` |  Yes | — | GraphQL API URL |
| `API_ACCESS_TOKEN` | No | — | Bearer token for auth |
| `MCP_MODE` | No | `stdio` | `stdio` or `http` |
| `ENABLE_HTTP_ENDPOINT` | No | `true` | Enable HTTP health/metrics endpoints |
| `MCP_SERVER_PORT` | No | `8080` | HTTP server port |
| `MCP_SERVER_HOST` | No | `0.0.0.0` | HTTP server host |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |
| `QUERY_TIMEOUT` | No | `30` | Request timeout in seconds |
| `SCHEMA_CACHE_TTL` | No | `3600` | Schema cache TTL in seconds |

---

## Operating Modes

### MCP Mode (`stdio`) — for Claude Desktop, Cursor, MCP clients

```bash
graphql-mcp-server --endpoint https://api.example.com/graphql --mode stdio
```

Communicates via stdin/stdout. No HTTP server is started. This is the default.

### HTTP Mode — for Docker, Kubernetes, server deployments

```bash
graphql-mcp-server --endpoint https://api.example.com/graphql --mode http --port 8080
```

Starts an HTTP server with health and metrics endpoints:
- `GET /health` — health check
- `GET /metrics` — server metrics
- `GET /schema` — schema summary
- `GET /tools` — all generated tools

---

## Docker

```bash
docker build -t graphql-mcp-server .

docker run -p 8080:8080 \
  -e GRAPHQL_ENDPOINT=https://api.example.com/graphql \
  -e API_ACCESS_TOKEN=your_token \
  -e MCP_MODE=http \
  graphql-mcp-server
```

Or with Docker Compose:

```bash
cp .env.example .env   # fill in your values
docker-compose up
```

---

## Key Features

- **Zero config queries** — auto-introspects any GraphQL schema and generates MCP tools
- **Dual mode** — stdio for MCP clients, HTTP for server deployments
- **Flexible config** — CLI args, env vars, .env file, or Claude Desktop env block
- **Production ready** — Docker, Kubernetes, AWS ECS, Google Cloud Run compatible
- **Self-documenting** — `list_available_queries`, `get_schema_info`, `get_query_signature` tools built in

---

## Troubleshooting

**`[ERROR] GraphQL endpoint not configured`**

Set `GRAPHQL_ENDPOINT` via any method above. The most common fix:
```bash
graphql-mcp-server --endpoint https://your-api.com/graphql
```

**Port already in use**

Change the port:
```bash
graphql-mcp-server --mode http --port 9090
```

**Docker container exits immediately**

Make sure you're using HTTP mode:
```bash
docker run -e MCP_MODE=http -e GRAPHQL_ENDPOINT=... graphql-mcp-server
```

---




