# GraphQL MCP Server

![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![MCP](https://img.shields.io/badge/MCP-compatible-purple)

A dynamic Model Context Protocol (MCP) server that automatically discovers and generates tools from any GraphQL API schema. This server enables seamless integration between Large Language Models and GraphQL APIs using either MCP (stdio) or HTTP deployment modes.

---

## Overview

GraphQL MCP Server is a schema-driven integration tool that automatically introspects GraphQL APIs and exposes their capabilities as MCP tools. This approach eliminates the need for manual tool configuration and ensures that your integration stays synchronized with API changes.

---

## Operating Modes

The server supports two execution modes depending on your use case:

### 🔹 MCP Mode (`stdio`)
- Used for Claude Desktop, Cursor, and MCP clients
- Communicates via stdin/stdout
- No HTTP server started
- Default mode

```
MCP_MODE=stdio
ENABLE_HTTP_ENDPOINT=false
```

---

### 🔹 HTTP Mode (`http`)
- Used for Docker, Kubernetes, or standalone deployments
- Starts HTTP server with health + metrics endpoints
- Runs indefinitely

```
MCP_MODE=http
ENABLE_HTTP_ENDPOINT=true
```

---

## Key Features

### Automatic Discovery
- Introspects GraphQL schemas and generates MCP tools dynamically
- Automatically adapts to schema changes
- Zero manual configuration for queries and mutations

### Production Ready
- Docker and Docker Compose support
- Kubernetes compatible
- AWS ECS and Google Cloud Run ready
- Built-in health checks and monitoring endpoints

### Flexible Architecture
- Dual-mode support (MCP + HTTP)
- Configurable ports and host
- Schema caching with TTL
- Supports authenticated and public APIs

### Developer Experience
- Self-documenting schema exploration
- Type-safe query validation
- Multiple field selection modes (auto, all, custom)
- Strong logging and error handling

---

## Prerequisites

- Python 3.11+
- Docker (optional)
- GraphQL endpoint
- API token (if required)

---

## Installation

### Local Development

```
git clone https://github.com/nifetency/nife-mcp-graphql
cd graphql-mcp-server

pip install -r requirements.txt

cp .env.example .env
# Edit .env

python -m graphql_mcp_server
```

---

### Docker

```
docker build -t graphql-mcp-server .
docker run -it -p 8080:8080 --env-file .env graphql-mcp-server
```

---

### Docker (direct env)

```
docker run -it -p 8080:8080 \
  -e GRAPHQL_ENDPOINT=https://api.example.com/graphql \
  -e API_ACCESS_TOKEN=your_token \
  -e MCP_MODE=http \
  -e ENABLE_HTTP_ENDPOINT=true \
  graphql-mcp-server
```

---

## Configuration

### Environment Variables

```
GRAPHQL_ENDPOINT=https://api.example.com/graphql
API_ACCESS_TOKEN=your_token_here

MCP_MODE=stdio

LOG_LEVEL=INFO
QUERY_TIMEOUT=30
SCHEMA_CACHE_TTL=3600

ENABLE_HTTP_ENDPOINT=true
MCP_SERVER_PORT=8080
MCP_SERVER_HOST=0.0.0.0
```

---

## Integration

### Claude Desktop (Repo-based)

```
{
  "mcpServers": {
    "graphql": {
      "command": "python",
      "args": ["-m", "graphql_mcp_server"],
      "cwd": "/absolute/path/to/graphql-mcp-server",
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

---

## Troubleshooting

### Port already in use

```
OSError: address already in use
```

Fix:
- Change port
- Stop existing process
- Use MCP_MODE=stdio

---

### Docker exits immediately

Fix:
```
MCP_MODE=http
ENABLE_HTTP_ENDPOINT=true
```

---

## License

MIT
