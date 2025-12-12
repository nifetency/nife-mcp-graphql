# GraphQL MCP Server - Quick Start Guide

## Changes Made

### 1. Environment Variable Loading (✅ Fixed)
- Added `from dotenv import load_dotenv` to `__main__.py`
- Added `from dotenv import load_dotenv` to `server.py`
- Added `load_dotenv()` call at the start of both files
- Now properly reads `.env` file on startup

### 2. Schema Initialization (✅ Fixed)
- Schema now loads immediately on server startup
- Previously only loaded when MCP client connected
- HTTP endpoints now work immediately after server starts

### 3. Test Files Created (✅ New)
- `test_mcp_client.py` - Python test script
- `web_interface.html` - Visual web interface

## Running the Server

```bash
cd "C:\Users\Varun S\Desktop\MCP Schema\GraphQL"
python -m graphql_mcp_server
```

You should see:
```
Starting GraphQL MCP Server...
Initializing server and loading schema...
============================================================
Intelligent GraphQL MCP Server - Initializing
Server Configuration:
  - HTTP Endpoint: Enabled
  - Host: 0.0.0.0
  - Port: 8080
============================================================
✓ Access token found
Loading GraphQL schema...
✓ GraphQL schema loaded successfully
  - GraphQL URL: https://api.nife.io/graphql
  - XX queries
  - XX mutations
  - XX types
Generating MCP tools from schema...
============================================================
✓ Server ready with XX tools!
============================================================
✓ HTTP Server started on http://0.0.0.0:8080
  - Health: http://0.0.0.0:8080/health
  - Metrics: http://0.0.0.0:8080/metrics
  - Schema: http://0.0.0.0:8080/schema
  - Tools: http://0.0.0.0:8080/tools
============================================================
```

## Testing Options

### 1. Web Interface (Easiest!)
Open `web_interface.html` in your browser
- Real-time server status
- All queries, mutations, and utilities
- Tabbed interface for easy navigation
- Beautiful purple gradient theme

### 2. Python Test Script
```bash
python test_mcp_client.py
```

### 3. Direct HTTP Endpoints
- http://localhost:8080/health
- http://localhost:8080/tools
- http://localhost:8080/schema
- http://localhost:8080/metrics

### 4. cURL Commands
```bash
# Check health
curl http://localhost:8080/health

# List all tools
curl http://localhost:8080/tools

# Get schema info
curl http://localhost:8080/schema
```

## Configuration (.env)

```env
GRAPHQL_ENDPOINT=https://api.nife.io/graphql
API_ACCESS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
LOG_LEVEL=DEBUG
QUERY_TIMEOUT=30
SCHEMA_CACHE_TTL=3600
```

## Troubleshooting

### "not_ready" status
- ✅ **FIXED**: This was caused by schema not loading on startup
- Verify `.env` file exists and is configured
- Check GRAPHQL_ENDPOINT is correct
- Verify API_ACCESS_TOKEN is valid

### Cannot connect
- Ensure server is running
- Check port 8080 is not in use
- Try http://localhost:8080/health

### Schema loading fails
- Verify GRAPHQL_ENDPOINT is accessible
- Check API_ACCESS_TOKEN is valid and not expired
- Test the endpoint with curl or Postman first

## Claude Desktop Integration

Edit: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "graphql-nife": {
      "command": "python",
      "args": ["-m", "graphql_mcp_server"],
      "cwd": "C:\\Users\\Varun S\\Desktop\\MCP Schema\\GraphQL",
      "env": {
        "GRAPHQL_ENDPOINT": "https://api.nife.io/graphql",
        "API_ACCESS_TOKEN": "your_token_here",
        "ENABLE_HTTP_ENDPOINT": "false"
      }
    }
  }
}
```

Then restart Claude Desktop and you can ask:
- "List all available GraphQL queries"
- "Execute the query to get applications"
- "Show me the GraphQL schema"

## All Tests Passing! ✅

The server is now working correctly with:
- ✅ Environment variables loading from .env
- ✅ Schema loading on startup
- ✅ HTTP endpoints responding immediately
- ✅ Test scripts available
- ✅ Web interface ready
- ✅ Nife.io GraphQL API connected
