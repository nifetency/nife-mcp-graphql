#!/bin/bash
# Quick start script for GraphQL MCP Server

set -e

echo "================================================"
echo "GraphQL MCP Server - Quick Start"
echo "================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  Please edit .env file with your configuration:"
    echo "   - GRAPHQL_ENDPOINT"
    echo "   - API_ACCESS_TOKEN"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Validate required variables
if [ -z "$GRAPHQL_ENDPOINT" ]; then
    echo "❌ GRAPHQL_ENDPOINT is not set in .env"
    exit 1
fi

if [ -z "$API_ACCESS_TOKEN" ]; then
    echo "❌ API_ACCESS_TOKEN is not set in .env"
    exit 1
fi

echo "✅ Configuration validated"
echo ""
echo "Configuration:"
echo "  - GraphQL Endpoint: $GRAPHQL_ENDPOINT"
echo "  - Server Port: ${MCP_SERVER_PORT:-8080}"
echo "  - HTTP Endpoint: ${ENABLE_HTTP_ENDPOINT:-true}"
echo ""

# Build and start
echo "🔨 Building Docker image..."
docker-compose build

echo ""
echo "🚀 Starting server..."
docker-compose up -d

echo ""
echo "⏳ Waiting for server to be ready..."
sleep 5

# Get the port
PORT=${MCP_SERVER_PORT:-8080}

# Health check
echo "🏥 Checking server health..."
if curl -f http://localhost:$PORT/health &> /dev/null; then
    echo "✅ Server is healthy!"
    echo ""
    echo "================================================"
    echo "Server is running!"
    echo "================================================"
    echo ""
    echo "Endpoints:"
    echo "  - Root:    http://localhost:$PORT/"
    echo "  - Health:  http://localhost:$PORT/health"
    echo "  - Metrics: http://localhost:$PORT/metrics"
    echo "  - Schema:  http://localhost:$PORT/schema"
    echo "  - Tools:   http://localhost:$PORT/tools"
    echo ""
    echo "Useful commands:"
    echo "  - View logs:    docker-compose logs -f"
    echo "  - Stop server:  docker-compose down"
    echo "  - Restart:      docker-compose restart"
    echo ""
else
    echo "⚠️  Server is starting but health check failed"
    echo "This might be normal if the schema is still loading"
    echo ""
    echo "Check logs with: docker-compose logs -f"
fi
