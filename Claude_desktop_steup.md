{
  "mcpServers": {
    "graphql": {
      "command": "python",
      "args": ["-m", "graphql_mcp_server"],
      "cwd": "<PATH_TO_REPO_ROOT>",
      "env": {
        "MCP_MODE": "stdio",
        "GRAPHQL_ENDPOINT": "",
        "API_ACCESS_TOKEN": "",
        "ENABLE_HTTP_ENDPOINT": "false"
      }
    }
  }
}