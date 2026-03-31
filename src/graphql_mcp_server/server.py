#!/usr/bin/env python3
"""
Intelligent GraphQL MCP Server - Schema-Driven Implementation
Auto-generates tools from GraphQL schema - Zero hardcoded queries!
"""
import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from aiohttp import web
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Import schema manager and GraphQL client
from graphql_mcp_server.schema_manager import SchemaManager
from graphql_mcp_server.graphql_client import GraphQLClient

class GraphQLMCPServer:
    """
    Intelligent MCP Server with automatic tool generation
    
    Features:
    - Auto-discovers all queries and mutations from GraphQL schema
    - Generates MCP tools dynamically
    - Zero hardcoded queries
    - Always up-to-date with API
    - Self-documenting
    - Optional HTTP endpoint for health checks and metrics
    """
    
    def __init__(self):
        self.schema_manager = SchemaManager()
        self.tools: Dict[str, Dict] = {}
        self.ready = False
        self.port = int(os.environ.get('MCP_SERVER_PORT', 8080))
        self.host = os.environ.get('MCP_SERVER_HOST', '0.0.0.0')
        self.enable_http = os.environ.get('ENABLE_HTTP_ENDPOINT', 'true').lower() == 'true'
        self.app = None
        self.runner = None
        self.mode = os.environ.get("MCP_MODE", "stdio")  
        
    async def initialize(self) -> bool:
        """Initialize server by loading schema and generating tools"""
        logger.info("="*60)
        logger.info("Intelligent GraphQL MCP Server - Initializing")
        logger.info(f"Server Configuration:")
        logger.info(f"  - HTTP Endpoint: {'Enabled' if self.enable_http else 'Disabled'}")
        if self.enable_http:
            logger.info(f"  - Host: {self.host}")
            logger.info(f"  - Port: {self.port}")
        logger.info("="*60)
        
        # Get configuration
        graphql_endpoint = os.environ.get('GRAPHQL_ENDPOINT')
        access_token = os.environ.get('API_ACCESS_TOKEN')
        print(f"✓ GraphQL Endpoint: {graphql_endpoint if graphql_endpoint else 'Not configured'}")
        print(f"✓ Access Token: {"Found" if access_token else 'Not found'}")
        
        if not graphql_endpoint:
            logger.error("✗ GRAPHQL_ENDPOINT not configured")
            return False
        
        if access_token:
            self.schema_manager.access_token = access_token
            logger.info("✓ Access token found")
        else:
            logger.warning("⚠️  No access token - some features may not work")
        
        # Set GraphQL endpoint
        self.schema_manager.graphql_url = graphql_endpoint
        
        # Load schema
        logger.info("Loading GraphQL schema...")
        success = self.schema_manager.load_schema()
        
        if not success:
            logger.error("✗ Failed to load schema")
            return False
        
        # Generate tools
        logger.info("Generating MCP tools from schema...")
        self._generate_tools()
        
        self.ready = True
        logger.info("="*60)
        logger.info(f"✓ Server ready with {len(self.tools)} tools!")
        logger.info("="*60)
        
        return True
    
    def _generate_tools(self):
        """Generate MCP tools dynamically from schema"""
        self.tools = {}
        
        # Generate query tools
        queries = self.schema_manager.get_available_queries()
        for query in queries:
            tool_name = f"query_{query['name']}"
            self.tools[tool_name] = {
                "name": tool_name,
                "description": f"Execute query: {query['name']} - {query['description']}",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "args": {
                            "type": "object",
                            "description": "Query arguments",
                            "default": {}
                        },
                        "fields": {
                            "type": "string",
                            "description": "Field selection mode: 'auto' (scalar only), 'all' (all fields), 'custom' (specify fields)",
                            "enum": ["auto", "all", "custom"],
                            "default": "auto"
                        },
                        "custom_fields": {
                            "type": "array",
                            "description": "Custom field list (required if fields='custom')",
                            "items": {"type": "string"}
                        }
                    },
                    "required": []
                }
            }
        
        # Generate mutation tools
        mutations = self.schema_manager.get_available_mutations()
        for mutation in mutations:
            tool_name = f"mutation_{mutation['name']}"
            self.tools[tool_name] = {
                "name": tool_name,
                "description": f"Execute mutation: {mutation['name']} - {mutation['description']}",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "object",
                            "description": "Mutation input data (required)"
                        },
                        "return_fields": {
                            "type": "array",
                            "description": "Fields to return (auto-detected if not specified)",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["input"]
                }
            }
        
        # Add utility tools
        self._add_utility_tools()
        
        logger.info(f"Generated {len([t for t in self.tools if t.startswith('query_')])} query tools")
        logger.info(f"Generated {len([t for t in self.tools if t.startswith('mutation_')])} mutation tools")
        logger.info(f"Added {len([t for t in self.tools if not t.startswith('query_') and not t.startswith('mutation_')])} utility tools")
    
    def _add_utility_tools(self):
        """Add utility tools for schema exploration"""
        
        self.tools["list_available_queries"] = {
            "name": "list_available_queries",
            "description": "List all available GraphQL queries that can be executed",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Optional search term to filter queries"
                    }
                },
                "required": []
            }
        }
        
        self.tools["list_available_mutations"] = {
            "name": "list_available_mutations",
            "description": "List all available GraphQL mutations that can be executed",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        
        self.tools["get_schema_info"] = {
            "name": "get_schema_info",
            "description": "Get detailed information about the GraphQL schema",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "type_name": {
                        "type": "string",
                        "description": "Optional: Get details about a specific type"
                    }
                },
                "required": []
            }
        }
        
        self.tools["get_query_signature"] = {
            "name": "get_query_signature",
            "description": "Get the signature (arguments and return type) for a query",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query_name": {
                        "type": "string",
                        "description": "Name of the query"
                    }
                },
                "required": ["query_name"]
            }
        }
        
        self.tools["execute_custom_query"] = {
            "name": "execute_custom_query",
            "description": "Execute a custom GraphQL query with full control",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "GraphQL query string (required)"
                    },
                    "variables": {
                        "type": "object",
                        "description": "Query variables",
                        "default": {}
                    }
                },
                "required": ["query"]
            }
        }
        
        self.tools["health_check"] = {
            "name": "health_check",
            "description": "Check server health and schema status",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    
    async def handle_tool_call(self, tool_name: str, arguments: dict) -> dict:
        """Route tool calls to appropriate handlers"""
        
        if not self.ready:
            return {"error": "Server not ready. Schema not loaded."}
        
        try:
            # Query tools
            if tool_name.startswith("query_"):
                query_name = tool_name[6:]  # Remove 'query_' prefix
                return await self._handle_dynamic_query(query_name, arguments)
            
            # Mutation tools
            elif tool_name.startswith("mutation_"):
                mutation_name = tool_name[9:]  # Remove 'mutation_' prefix
                return await self._handle_dynamic_mutation(mutation_name, arguments)
            
            # Utility tools
            elif tool_name == "list_available_queries":
                return self._handle_list_queries(arguments)
            
            elif tool_name == "list_available_mutations":
                return self._handle_list_mutations(arguments)
            
            elif tool_name == "get_schema_info":
                return self._handle_schema_info(arguments)
            
            elif tool_name == "get_query_signature":
                return self._handle_query_signature(arguments)
            
            elif tool_name == "execute_custom_query":
                return await self._handle_custom_query(arguments)
            
            elif tool_name == "health_check":
                return self._handle_health_check(arguments)
            
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Error in handle_tool_call: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def _handle_dynamic_query(self, query_name: str, args: dict) -> dict:
        """Handle dynamically generated query tools"""
        try:
            # Build query dynamically
            query_args = args.get('args', {})
            fields_mode = args.get('fields', 'auto')
            custom_fields = args.get('custom_fields')
            
            query = self.schema_manager.build_query(
                query_name=query_name,
                args=query_args,
                fields=fields_mode,
                custom_fields=custom_fields
            )
            
            logger.info(f"Executing query: {query_name}")
            logger.debug(f"Generated query:\n{query}")
            
            # Execute query
            client = GraphQLClient(
                self.schema_manager.graphql_url,
                self.schema_manager.access_token
            )
            result = client.execute_query(query)
            
            if result is None:
                return {
                    "error": "Query execution returned no result",
                    "query": query
                }
            
            if 'errors' in result:
                return {
                    "error": "Query execution failed",
                    "details": result['errors'],
                    "query": query
                }
            
            return {
                "success": True,
                "data": result.get('data', {}) if result else {},
                "metadata": {
                    "query_name": query_name,
                    "fields_mode": fields_mode,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in dynamic query: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def _handle_dynamic_mutation(self, mutation_name: str, args: dict) -> dict:
        """Handle dynamically generated mutation tools"""
        try:
            input_data = args.get('input')
            if not input_data:
                return {"error": "Input data required"}
            
            return_fields = args.get('return_fields')
            
            # Build mutation dynamically
            mutation = self.schema_manager.build_mutation(
                mutation_name=mutation_name,
                input_data=input_data,
                return_fields=return_fields
            )
            
            logger.info(f"Executing mutation: {mutation_name}")
            logger.debug(f"Generated mutation:\n{mutation}")
            
            # Execute mutation
            client = GraphQLClient(
                self.schema_manager.graphql_url,
                self.schema_manager.access_token
            )
            result = client.execute_query(mutation)
            
            if result is None:
                return {
                    "error": "Mutation execution returned no result",
                    "mutation": mutation
                }
            
            if 'errors' in result:
                return {
                    "error": "Mutation execution failed",
                    "details": result['errors'],
                    "mutation": mutation
                }
            
            return {
                "success": True,
                "data": result.get('data', {}) if result else {},
                "metadata": {
                    "mutation_name": mutation_name,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in dynamic mutation: {e}", exc_info=True)
            return {"error": str(e)}
    
    def _handle_list_queries(self, args: dict) -> dict:
        """List available queries"""
        search = args.get('search')
        
        if search:
            queries = self.schema_manager.search_queries(search)
        else:
            queries = self.schema_manager.get_available_queries()
        
        return {
            "queries": queries,
            "total_count": len(queries),
            "search_term": search if search else None
        }
    
    def _handle_list_mutations(self, args: dict) -> dict:
        """List available mutations"""
        mutations = self.schema_manager.get_available_mutations()
        
        return {
            "mutations": mutations,
            "total_count": len(mutations)
        }
    
    def _handle_schema_info(self, args: dict) -> dict:
        """Get schema information"""
        type_name = args.get('type_name')
        
        if type_name:
            type_info = self.schema_manager.get_type_info(type_name)
            if not type_info:
                return {"error": f"Type '{type_name}' not found"}
            return {"type": type_info}
        
        schema = self.schema_manager.schema or {}
        return {
            "schema_stats": {
                "total_queries": len(self.schema_manager.queries_cache),
                "total_mutations": len(self.schema_manager.mutations_cache),
                "total_types": len(self.schema_manager.types_cache)
            },
            "query_type": schema.get('queryType', {}).get('name'),
            "mutation_type": schema.get('mutationType', {}).get('name')
        }
    
    def _handle_query_signature(self, args: dict) -> dict:
        """Get query signature"""
        query_name = args.get('query_name')
        if not query_name:
            return {"error": "query_name required"}
        
        signature = self.schema_manager.get_query_signature(query_name)
        if not signature:
            return {"error": f"Query '{query_name}' not found"}
        
        return {
            "query_name": query_name,
            "signature": signature
        }
    
    async def _handle_custom_query(self, args: dict) -> dict:
        """Execute custom GraphQL query"""
        try:
            query = args.get('query')
            variables = args.get('variables', {})
            
            if not query:
                return {"error": "Query required"}
            
            logger.info("Executing custom query")
            
            client = GraphQLClient(
                self.schema_manager.graphql_url,
                self.schema_manager.access_token
            )
            result = client.execute_query(query, variables)
            
            if result is None:
                return {
                    "error": "Query execution returned no result"
                }
            
            if 'errors' in result:
                return {
                    "error": "Query execution failed",
                    "details": result['errors']
                }
            
            return {
                "success": True,
                "data": result.get('data', {}) if result else {}
            }
            
        except Exception as e:
            logger.error(f"Error in custom query: {e}", exc_info=True)
            return {"error": str(e)}
    
    def _handle_health_check(self, args: dict) -> dict:
        """Health check"""
        return {
            "status": "healthy" if self.ready else "not_ready",
            "server": "graphql-mcp-server",
            "version": "1.0.0",
            "schema_loaded": self.schema_manager.schema_loaded,
            "tools_count": len(self.tools),
            "queries_count": len(self.schema_manager.queries_cache),
            "mutations_count": len(self.schema_manager.mutations_cache),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def handle_request(self, request: dict) -> Optional[dict]:
        """Handle MCP JSON-RPC requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                # Initialize if not already done
                if not self.ready:
                    await self.initialize()
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "graphql-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "notifications/initialized":
                logger.info("✓ Client initialized successfully")
                return None
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": tool["name"],
                                "description": tool["description"],
                                "inputSchema": tool["inputSchema"]
                            }
                            for tool in self.tools.values()
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_arguments = params.get("arguments", {})
                
                result = await self.handle_tool_call(tool_name, tool_arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            else:
                raise Exception(f"Unknown method: {method}")
                
        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def setup_http_server(self):
        """Setup optional HTTP server for health checks and metrics"""
        if not self.enable_http:
            return
        
        self.app = web.Application()
        
        # Health check endpoint
        async def health_handler(request):
            health_data = self._handle_health_check({})
            return web.json_response(health_data)
        
        # Metrics endpoint
        async def metrics_handler(request):
            metrics = {
                "server": "graphql-mcp-server",
                "version": "1.0.0",
                "uptime_seconds": asyncio.get_event_loop().time() - getattr(self, '_start_time', 0),
                "schema_loaded": self.schema_manager.schema_loaded,
                "tools_count": len(self.tools),
                "queries_count": len(self.schema_manager.queries_cache),
                "mutations_count": len(self.schema_manager.mutations_cache),
                "ready": self.ready,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            return web.json_response(metrics)
        
        # Schema info endpoint
        async def schema_handler(request):
            schema_info = self._handle_schema_info({})
            return web.json_response(schema_info)
        
        # Tools list endpoint
        async def tools_handler(request):
            tools_list = [
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "type": "query" if tool["name"].startswith("query_") else 
                            "mutation" if tool["name"].startswith("mutation_") else "utility"
                }
                for tool in self.tools.values()
            ]
            return web.json_response({
                "tools": tools_list,
                "total_count": len(tools_list)
            })
        
        # Root endpoint
        async def root_handler(request):
            return web.json_response({
                "server": "graphql-mcp-server",
                "version": "1.0.0",
                "status": "running",
                "mode": "stdio",
                "endpoints": {
                    "health": "/health",
                    "metrics": "/metrics",
                    "schema": "/schema",
                    "tools": "/tools"
                }
            })
        
        # Register routes
        self.app.router.add_get('/', root_handler)
        self.app.router.add_get('/health', health_handler)
        self.app.router.add_get('/metrics', metrics_handler)
        self.app.router.add_get('/schema', schema_handler)
        self.app.router.add_get('/tools', tools_handler)
        
        # Start HTTP server
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.host, self.port)
        await site.start()
        
        logger.info("="*60)
        logger.info(f"✓ HTTP Server started on http://{self.host}:{self.port}")
        logger.info(f"  - Health: http://{self.host}:{self.port}/health")
        logger.info(f"  - Metrics: http://{self.host}:{self.port}/metrics")
        logger.info(f"  - Schema: http://{self.host}:{self.port}/schema")
        logger.info(f"  - Tools: http://{self.host}:{self.port}/tools")
        logger.info("="*60)
    
    async def run(self):
        logger.info("Starting GraphQL MCP Server...")

        # Initialize schema
        logger.info("Initializing server and loading schema...")
        await self.initialize()

        self._start_time = asyncio.get_event_loop().time()

        if self.mode == "http":
            logger.info("Running in HTTP mode (Docker/K8s)...")
            await self.setup_http_server()
            await asyncio.Event().wait()  # keep alive

        elif self.mode == "stdio":
            logger.info("Running in MCP stdio mode...")
            await self._run_stdin_loop()

        else:
            raise ValueError(f"Invalid MCP_MODE: {self.mode}")
        logger.info("GraphQL MCP Server stopped")

    async def _run_stdin_loop(self):
        """Listen for JSON-RPC requests on stdin."""
        logger.info("Waiting for MCP client connection via stdin/stdout")
        self._start_time = asyncio.get_event_loop().time()
        
        while True:
            try:
                # Read JSON-RPC request from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    logger.info("No more input, exiting")
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Parse and handle request
                request = json.loads(line)
                response = await self.handle_request(request)
                
                # Send response to stdout
                if response is not None:
                    print(json.dumps(response), flush=True)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
            except KeyboardInterrupt:
                logger.info("Server stopped by user")
                break
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                break

if __name__ == "__main__":
    server = GraphQLMCPServer()
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested.")
