# GraphQL MCP Server

A dynamic Model Context Protocol (MCP) server that automatically discovers and generates tools from any GraphQL API schema. This server enables seamless integration between Large Language Models and GraphQL APIs without requiring manual tool definition or hardcoded queries.

## Overview

GraphQL MCP Server is a schema-driven integration tool that automatically introspects GraphQL APIs and exposes their capabilities as MCP tools. This approach eliminates the need for manual tool configuration and ensures that your integration stays synchronized with API changes.

## Key Features

### Automatic Discovery
- Introspects GraphQL schemas and generates MCP tools dynamically
- Automatically adapts to schema changes
- Zero manual configuration for queries and mutations

### Production Ready
- Docker and Docker Compose support
- Kubernetes compatible
- AWS ECS and Google Cloud Run deployment ready
- Built-in health checks and monitoring endpoints

### Flexible Architecture
- Configurable HTTP endpoints for health monitoring
- Custom port configuration
- Schema caching with configurable TTL
- Support for authenticated and public APIs

### Developer Experience
- Self-documenting through schema exploration
- Type-safe query validation
- Multiple field selection modes (auto, all, custom)
- Comprehensive error handling and logging

## Prerequisites

- Python 3.11 or higher
- Docker (optional, recommended for deployment)
- A GraphQL API endpoint
- API access token (if authentication is required)

## Installation

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/graphql-mcp-server.git
cd graphql-mcp-server

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your GraphQL endpoint and credentials

# Run the server
python -m graphql_mcp_server
```

### Docker Deployment

#### Quick Start with Scripts

```bash
# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Linux/Mac
./quickstart.sh

# Windows
quickstart.bat
```

#### Docker Compose

```bash
docker-compose up -d
```

#### Manual Docker Build

```bash
docker build -t graphql-mcp-server .
docker run -it -p 8080:8080 --env-file .env graphql-mcp-server
```

#### Environment Variables Only

```bash
docker run -it -p 8080:8080 \
  -e GRAPHQL_ENDPOINT=https://api.example.com/graphql \
  -e API_ACCESS_TOKEN=your_token_here \
  -e MCP_SERVER_PORT=8080 \
  -e ENABLE_HTTP_ENDPOINT=true \
  graphql-mcp-server:latest
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following configuration:

```env
# Required: GraphQL API endpoint
GRAPHQL_ENDPOINT=https://api.example.com/graphql

# Required: API access token (if authentication is needed)
API_ACCESS_TOKEN=your_access_token_here

# Optional: Logging configuration
LOG_LEVEL=INFO

# Optional: Request timeout in seconds
QUERY_TIMEOUT=30

# Optional: Schema cache duration in seconds
SCHEMA_CACHE_TTL=3600

# Optional: HTTP server configuration
ENABLE_HTTP_ENDPOINT=true
MCP_SERVER_PORT=8080
MCP_SERVER_HOST=0.0.0.0
```

### Configuration Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `GRAPHQL_ENDPOINT` | GraphQL API endpoint URL | None | Yes |
| `API_ACCESS_TOKEN` | Authentication token | None | Conditional |
| `LOG_LEVEL` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) | INFO | No |
| `QUERY_TIMEOUT` | Request timeout in seconds | 30 | No |
| `SCHEMA_CACHE_TTL` | Schema cache duration in seconds | 3600 | No |
| `ENABLE_HTTP_ENDPOINT` | Enable HTTP health/metrics endpoints | true | No |
| `MCP_SERVER_PORT` | HTTP server port | 8080 | No |
| `MCP_SERVER_HOST` | HTTP server host | 0.0.0.0 | No |

## HTTP Endpoints

When `ENABLE_HTTP_ENDPOINT` is enabled, the server exposes the following REST endpoints:

### GET /
Server information and available endpoints

### GET /health
Health check endpoint for monitoring systems
```json
{
  "status": "healthy",
  "timestamp": "2024-03-30T12:00:00Z",
  "schema_loaded": true,
  "tools_count": 42
}
```

### GET /metrics
Server metrics and statistics
```json
{
  "uptime_seconds": 3600,
  "queries_executed": 150,
  "mutations_executed": 25,
  "errors_count": 2,
  "cache_hits": 120,
  "cache_misses": 30
}
```

### GET /schema
GraphQL schema information including queries, mutations, and types

### GET /tools
List of all available MCP tools

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Integration

### Claude Desktop

Add the following configuration to your Claude Desktop config file (`claude_desktop_config.json`):

#### Using Python

```json
{
  "mcpServers": {
    "graphql": {
      "command": "python",
      "args": ["-m", "graphql_mcp_server"],
      "env": {
        "GRAPHQL_ENDPOINT": "https://api.example.com/graphql",
        "API_ACCESS_TOKEN": "your_token_here"
      }
    }
  }
}
```

#### Using Docker

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
        "-e", "API_ACCESS_TOKEN=your_token_here",
        "graphql-mcp-server:latest"
      ]
    }
  }
}
```

### Other MCP Clients

The server implements the standard MCP protocol over stdio, making it compatible with any MCP-compliant client. Refer to your client's documentation for specific integration instructions.

## Available Tools

The server automatically generates tools based on your GraphQL schema:

### Query Tools
- `query_<queryName>`: Execute any query defined in your schema
- Dynamic parameter validation based on schema
- Automatic field selection with customization options

### Mutation Tools
- `mutation_<mutationName>`: Execute any mutation defined in your schema
- Input validation against schema types
- Return field selection support

### Utility Tools

#### list_available_queries
Lists all queries available in the GraphQL schema with descriptions and parameters.

#### list_available_mutations
Lists all mutations available in the GraphQL schema with descriptions and parameters.

#### get_schema_info
Retrieves detailed information about types, fields, and relationships in the schema.

#### get_query_signature
Returns the signature and documentation for a specific query, including required parameters and return types.

#### execute_custom_query
Executes arbitrary GraphQL queries with full control over query structure and field selection.

#### health_check
Checks the server health status, schema load state, and connectivity to the GraphQL API.

## Usage Examples

### Listing Available Operations

```
User: "Show me all available queries"
Server: Returns a list of all queries with descriptions
```

### Executing Queries

```
User: "Execute the getUsers query with a limit of 10"
Server: Runs the query and returns results
```

### Custom Field Selection

```
User: "Query getApps but only return id, name, and status fields"
Server: Executes query with specified field selection
```

### Mutations

```
User: "Create a new application named 'MyApp' in the us-west region"
Server: Executes the appropriate mutation with provided parameters
```

### Schema Exploration

```
User: "What fields are available on the Application type?"
Server: Returns all fields, their types, and descriptions
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│         MCP Client (Claude Desktop, etc.)       │
└───────────────────┬─────────────────────────────┘
                    │ MCP Protocol (stdio)
┌───────────────────▼─────────────────────────────┐
│           GraphQL MCP Server                    │
│  ┌─────────────────────────────────────────┐   │
│  │      Schema Manager                     │   │
│  │  - Introspects GraphQL schema           │   │
│  │  - Caches types, queries, mutations     │   │
│  │  - Generates tool definitions           │   │
│  │  - Validates queries against schema     │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │      GraphQL Client                     │   │
│  │  - Executes queries and mutations       │   │
│  │  - Handles authentication               │   │
│  │  - Error handling and retries           │   │
│  │  - Request/response logging             │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │      HTTP Server (Optional)             │   │
│  │  - Health check endpoints               │   │
│  │  - Metrics and monitoring               │   │
│  │  - Schema inspection API                │   │
│  └─────────────────────────────────────────┘   │
└───────────────────┬─────────────────────────────┘
                    │ HTTPS
┌───────────────────▼─────────────────────────────┐
│           Your GraphQL API                      │
└─────────────────────────────────────────────────┘
```

## Development

### Project Structure

```
graphql-mcp-server/
├── src/
│   └── graphql_mcp_server/
│       ├── __init__.py
│       ├── __main__.py          # Entry point
│       ├── server.py             # MCP server implementation
│       ├── schema_manager.py     # Schema introspection and caching
│       └── graphql_client.py     # GraphQL API client
├── .env.example                  # Environment configuration template
├── .gitignore
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                    # Docker build instructions
├── LICENSE                       # MIT License
├── README.md                     # This file
├── requirements.txt              # Python dependencies
└── quickstart.sh/bat            # Quick start scripts
```

### Running Tests

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests (when available)
python -m pytest tests/
```

### Building Docker Image

```bash
docker build -t graphql-mcp-server:latest .
```

## Troubleshooting

### Schema Loading Fails

**Symptoms**: Server starts but reports "Failed to load schema"

**Common Causes**:
- Incorrect GraphQL endpoint URL (ensure path is complete, e.g., `/graphql`)
- Invalid or expired access token
- Network connectivity issues
- API requires different authentication method

**Solutions**:
1. Verify endpoint URL is correct and includes full path
2. Check access token validity
3. Test endpoint with curl or Postman
4. Review server logs for detailed error messages

### Docker Container Exits Immediately

**Symptoms**: Container starts and immediately stops

**Common Causes**:
- Missing or incorrect environment variables
- Port conflicts
- Insufficient permissions

**Solutions**:
1. Verify all required environment variables are set
2. Check if port 8080 is available
3. Review Docker logs: `docker logs <container_id>`

### Tools Not Generated

**Symptoms**: Server starts but no tools are available

**Common Causes**:
- Schema introspection returned empty results
- GraphQL API has introspection disabled
- Authentication issues preventing schema access

**Solutions**:
1. Check if schema loaded successfully in logs
2. Verify API supports introspection
3. Test API access with provided credentials

### Query Execution Failures

**Symptoms**: Queries fail despite successful schema loading

**Common Causes**:
- Insufficient API permissions
- Query syntax errors
- Required arguments missing
- Rate limiting

**Solutions**:
1. Verify API token has necessary permissions
2. Check query parameters match schema requirements
3. Review error messages in response
4. Implement rate limiting if needed

## Performance Considerations

### Schema Caching
The server caches the GraphQL schema to minimize introspection queries. Adjust `SCHEMA_CACHE_TTL` based on how frequently your schema changes.

### Connection Pooling
For high-throughput scenarios, consider implementing connection pooling in the GraphQL client.

### Resource Limits
When deploying in containerized environments, allocate appropriate memory and CPU based on expected load.

## Security Best Practices

1. **Token Management**: Store API tokens securely using environment variables or secret management systems
2. **Network Security**: Use HTTPS for all GraphQL endpoints
3. **Access Control**: Implement appropriate access controls in your deployment environment
4. **Logging**: Review logs regularly for unauthorized access attempts
5. **Updates**: Keep dependencies updated to patch security vulnerabilities

## Contributing

Contributions are welcome and appreciated. To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR
- Provide clear commit messages

## Roadmap

- [ ] Add support for GraphQL subscriptions
- [ ] Implement request caching and optimization
- [ ] Add support for batch queries
- [ ] Provide comprehensive test coverage
- [ ] Add monitoring and observability features
- [ ] Support for GraphQL federation
- [ ] CLI tool for standalone usage

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on the [Model Context Protocol](https://modelcontextprotocol.io/) specification
- Inspired by the need for dynamic, schema-driven API integration
- Thanks to the open-source community for tools and libraries used in this project

## Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/yourusername/graphql-mcp-server/issues)
- **Discussions**: Join community discussions on [GitHub Discussions](https://github.com/yourusername/graphql-mcp-server/discussions)
- **Documentation**: Additional documentation available in the [docs](docs/) directory

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

---

**Note**: Replace `yourusername` with your actual GitHub username before publishing.