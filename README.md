# GraphQL MCP Server

A dynamic Model Context Protocol (MCP) server that automatically discovers and generates tools from any GraphQL API schema. Zero hardcoding required!

## 🚀 Features

- **Automatic Tool Generation**: Introspects GraphQL schemas and generates MCP tools dynamically
- **Zero Configuration**: Just provide your GraphQL endpoint and token
- **Schema-Driven**: Always up-to-date with your API
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Configurable Ports**: Define custom ports for HTTP endpoints
- **HTTP Health Endpoints**: Built-in health checks, metrics, and monitoring
- **Production Ready**: Kubernetes, AWS ECS, Google Cloud Run compatible
- **Flexible Field Selection**: Auto, all, or custom field selection modes
- **Type-Safe**: Validates queries against the schema
- **Self-Documenting**: Built-in schema exploration tools

## 📋 Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- A GraphQL API endpoint
- API access token (if your API requires authentication)

## 🛠️ Installation

### Option 1: Local Installation

```bash
# Clone or download this folder
cd graphql-mcp-server

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your GraphQL endpoint and token

# Run the server
python -m graphql_mcp_server
```

### Option 2: Docker (Recommended for Deployment)

```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with your GraphQL endpoint and token

# Quick start (Linux/Mac)
./quickstart.sh

# Quick start (Windows)
quickstart.bat

# Or manually with Docker Compose
docker-compose up -d

# Or build and run manually
docker build -t graphql-mcp-server .
docker run -it -p 8080:8080 --env-file .env graphql-mcp-server
```

### Option 3: Docker with Environment Variables

```bash
docker run -it -p 8080:8080 \
  -e GRAPHQL_ENDPOINT=https://api.example.com/graphql \
  -e API_ACCESS_TOKEN=your_token_here \
  -e MCP_SERVER_PORT=8080 \
  -e ENABLE_HTTP_ENDPOINT=true \
  graphql-mcp-server:latest
```

## 🔧 Configuration

Create a `.env` file in the project root:

```env
GRAPHQL_ENDPOINT=https://api.example.com/graphql
API_ACCESS_TOKEN=your_access_token_here
LOG_LEVEL=INFO
QUERY_TIMEOUT=30
SCHEMA_CACHE_TTL=3600
```

## 🌐 HTTP Endpoints

When `ENABLE_HTTP_ENDPOINT=true` (default), the server provides REST endpoints:

- **GET /** - Server info and available endpoints
- **GET /health** - Health check (use for monitoring)
- **GET /metrics** - Server metrics and statistics
- **GET /schema** - GraphQL schema information
- **GET /tools** - List of available MCP tools

Example:
```bash
curl http://localhost:8080/health
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 📖 Usage

### With Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "graphql": {
      "command": "python",
      "args": ["-m", "graphql_mcp_server"],
      "env": {
        "GRAPHQL_ENDPOINT": "https://api.example.com/graphql",
        "API_ACCESS_TOKEN": "your_token"
      }
    }
  }
}
```

Or using Docker:

```json
{
  "mcpServers": {
    "graphql": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "GRAPHQL_ENDPOINT=https://api.example.com/graphql",
        "-e", "API_ACCESS_TOKEN=your_token",
        "graphql-mcp-server:latest"
      ]
    }
  }
}
```

### Available Tools

The server automatically generates the following types of tools:

1. **Query Tools**: `query_<queryName>` - Execute any query from your schema
2. **Mutation Tools**: `mutation_<mutationName>` - Execute any mutation
3. **Utility Tools**:
   - `list_available_queries` - List all queries
   - `list_available_mutations` - List all mutations
   - `get_schema_info` - Get schema information
   - `get_query_signature` - Get query details
   - `execute_custom_query` - Run custom GraphQL queries
   - `health_check` - Check server health

### Example Queries

```
# List available queries
"Show me all available queries"

# Execute a specific query
"Run the getUsers query with limit 10"

# Custom query with field selection
"Query getApps with custom fields: id, name, status"

# Execute a mutation
"Create a new app with name 'MyApp' and region 'us-west'"

# Get schema information
"What fields are available on the App type?"
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              Claude Desktop / CLI               │
└───────────────────┬─────────────────────────────┘
                    │ MCP Protocol (stdio)
┌───────────────────▼─────────────────────────────┐
│           GraphQL MCP Server                    │
│  ┌─────────────────────────────────────────┐   │
│  │      Schema Manager                     │   │
│  │  • Introspects GraphQL schema           │   │
│  │  • Caches types, queries, mutations     │   │
│  │  • Generates tool definitions           │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │      GraphQL Client                     │   │
│  │  • Executes queries and mutations       │   │
│  │  • Handles authentication               │   │
│  │  • Error handling and retries           │   │
│  └─────────────────────────────────────────┘   │
└───────────────────┬─────────────────────────────┘
                    │ HTTPS
┌───────────────────▼─────────────────────────────┐
│           Your GraphQL API                      │
└─────────────────────────────────────────────────┘
```

##  Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

##  License

This project is licensed under the MIT License.

##  Acknowledgments

- Built on the [Model Context Protocol](https://modelcontextprotocol.io/)
- Inspired by the need for dynamic, schema-driven API integration

##  Troubleshooting

### Schema Not Loading
Check endpoint URL, access token, and network connectivity

### Docker Container Exits Immediately
Verify environment variables are set correctly

### Tool Calls Failing
Check API authentication and permissions

### No Tools Generated
Verify schema loaded successfully, check logs

## 📧 Support

- Open an issue on GitHub
- Check documentation

---


