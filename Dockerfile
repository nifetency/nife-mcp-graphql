# GraphQL MCP Server Dockerfile
FROM python:3.11-slim

LABEL maintainer="your-email@example.com"
LABEL description="GraphQL MCP Server - Dynamic tool generation from GraphQL schemas"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Set Python path
ENV PYTHONPATH=/app

# Environment variables with defaults
ENV GRAPHQL_ENDPOINT=""
ENV API_ACCESS_TOKEN=""
ENV LOG_LEVEL="INFO"
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# Run the server
CMD ["python", "-m", "graphql_mcp_server"]
