#!/usr/bin/env python3
"""
GraphQL Client for GraphQL MCP Server
Handles GraphQL queries with error handling
"""
import logging
import requests
import time
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class GraphQLClient:
    """GraphQL client with error handling and retries"""
    
    def __init__(
        self, 
        endpoint: str,
        access_token: Optional[str] = None
    ):
        self.endpoint = endpoint
        self.access_token = access_token
    
    def execute_query(
        self, 
        query: str, 
        variables: Optional[Dict] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Execute a GraphQL query
        
        Args:
            query: GraphQL query string
            variables: Query variables (optional)
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with 'data' and/or 'errors'
        """
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'graphql-mcp-server/1.0.0'
        }
        
        # Add authorization header if token is provided
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        payload = {'query': query}
        
        if variables:
            payload['variables'] = variables
        
        start_time = time.time()
        
        try:
            logger.info(f"Executing GraphQL query: {query[:100]}...")
            
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"GraphQL query completed in {elapsed_time:.2f}s")
            
            response.raise_for_status()
            result = response.json()
            
            # Log errors if they exist
            if 'errors' in result:
                logger.error(f"GraphQL errors: {result['errors']}")
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"GraphQL query timeout after {timeout}s")
            return {
                'errors': [{
                    'message': f'Request timeout after {timeout} seconds'
                }]
            }
            
        except requests.exceptions.ConnectionError:
            logger.error("Connection error to GraphQL API")
            return {
                'errors': [{
                    'message': 'Connection error to GraphQL API'
                }]
            }
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            return {
                'errors': [{
                    'message': f'HTTP error: {str(e)}'
                }]
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {
                'errors': [{
                    'message': f'Request failed: {str(e)}'
                }]
            }
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return {
                'errors': [{
                    'message': f'Unexpected error: {str(e)}'
                }]
            }
    
    def execute_introspection_query(self) -> Dict[str, Any]:
        """
        Execute GraphQL introspection query
        
        Returns:
            Dictionary with schema information
        """
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                queryType { name }
                mutationType { name }
                types {
                    kind
                    name
                    description
                    fields(includeDeprecated: true) {
                        name
                        description
                        type {
                            kind
                            name
                            ofType {
                                kind
                                name
                                ofType {
                                    kind
                                    name
                                    ofType {
                                        kind
                                        name
                                    }
                                }
                            }
                        }
                        args {
                            name
                            description
                            type {
                                kind
                                name
                                ofType {
                                    kind
                                    name
                                    ofType {
                                        kind
                                        name
                                    }
                                }
                            }
                            defaultValue
                        }
                        isDeprecated
                        deprecationReason
                    }
                    inputFields {
                        name
                        description
                        type {
                            kind
                            name
                            ofType {
                                kind
                                name
                                ofType {
                                    kind
                                    name
                                }
                            }
                        }
                        defaultValue
                    }
                    interfaces {
                        name
                    }
                    possibleTypes {
                        name
                    }
                    enumValues(includeDeprecated: true) {
                        name
                        description
                        isDeprecated
                        deprecationReason
                    }
                }
            }
        }
        """
        
        return self.execute_query(introspection_query, timeout=60)
