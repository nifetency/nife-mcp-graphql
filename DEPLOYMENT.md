# GraphQL MCP Server - Deployment Guide

## Overview

The GraphQL MCP Server now includes configurable ports for easy Docker deployment and HTTP endpoints for health checks and monitoring.

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GRAPHQL_ENDPOINT` | GraphQL API endpoint URL | - | Yes |
| `API_ACCESS_TOKEN` | API authentication token | - | Yes |
| `MCP_SERVER_PORT` | HTTP server port | 8080 | No |
| `MCP_SERVER_HOST` | HTTP server host | 0.0.0.0 | No |
| `ENABLE_HTTP_ENDPOINT` | Enable HTTP health/metrics endpoints | true | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO | No |
| `QUERY_TIMEOUT` | Query timeout in seconds | 30 | No |
| `SCHEMA_CACHE_TTL` | Schema cache duration in seconds | 3600 | No |

### Setup Configuration

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your values:**
   ```bash
   GRAPHQL_ENDPOINT=https://api.yourdomain.com/graphql
   API_ACCESS_TOKEN=your_token_here
   MCP_SERVER_PORT=8080
   MCP_SERVER_HOST=0.0.0.0
   ENABLE_HTTP_ENDPOINT=true
   ```

## Deployment Options

### Option 1: Docker Compose (Recommended)

**Build and run:**
```bash
docker-compose up --build
```

**Run in detached mode:**
```bash
docker-compose up -d
```

**Stop the server:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f
```

**Custom port mapping:**
```bash
# Edit docker-compose.yml or use environment variables
MCP_SERVER_PORT=9000 docker-compose up
```

### Option 2: Docker (Manual)

**Build the image:**
```bash
docker build -t graphql-mcp-server:latest .
```

**Run the container:**
```bash
docker run -d \
  --name graphql-mcp-server \
  -p 8080:8080 \
  -e GRAPHQL_ENDPOINT="https://api.yourdomain.com/graphql" \
  -e API_ACCESS_TOKEN="your_token_here" \
  -e MCP_SERVER_PORT=8080 \
  -e ENABLE_HTTP_ENDPOINT=true \
  graphql-mcp-server:latest
```

**Run with custom port:**
```bash
docker run -d \
  --name graphql-mcp-server \
  -p 9000:9000 \
  -e GRAPHQL_ENDPOINT="https://api.yourdomain.com/graphql" \
  -e API_ACCESS_TOKEN="your_token_here" \
  -e MCP_SERVER_PORT=9000 \
  graphql-mcp-server:latest
```

**View logs:**
```bash
docker logs -f graphql-mcp-server
```

**Stop and remove:**
```bash
docker stop graphql-mcp-server
docker rm graphql-mcp-server
```

### Option 3: Local Python

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run the server:**
```bash
# Load environment variables
export $(cat .env | xargs)

# Or use python-dotenv (recommended)
python -m graphql_mcp_server
```

**Run with custom port:**
```bash
MCP_SERVER_PORT=9000 python -m graphql_mcp_server
```

## HTTP Endpoints

When `ENABLE_HTTP_ENDPOINT=true`, the server exposes the following endpoints:

### Root Endpoint
```bash
curl http://localhost:8080/
```

**Response:**
```json
{
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
}
```

### Health Check
```bash
curl http://localhost:8080/health
```

**Response:**
```json
{
  "status": "healthy",
  "server": "graphql-mcp-server",
  "version": "1.0.0",
  "schema_loaded": true,
  "tools_count": 25,
  "queries_count": 15,
  "mutations_count": 8,
  "timestamp": "2024-12-11T10:30:00Z"
}
```

### Metrics
```bash
curl http://localhost:8080/metrics
```

**Response:**
```json
{
  "server": "graphql-mcp-server",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "schema_loaded": true,
  "tools_count": 25,
  "queries_count": 15,
  "mutations_count": 8,
  "ready": true,
  "timestamp": "2024-12-11T10:30:00Z"
}
```

### Schema Information
```bash
curl http://localhost:8080/schema
```

### Available Tools
```bash
curl http://localhost:8080/tools
```

## Kubernetes Deployment

### Basic Deployment

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: graphql-mcp-server
  labels:
    app: graphql-mcp-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: graphql-mcp-server
  template:
    metadata:
      labels:
        app: graphql-mcp-server
    spec:
      containers:
      - name: graphql-mcp-server
        image: graphql-mcp-server:latest
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: GRAPHQL_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: graphql-secrets
              key: endpoint
        - name: API_ACCESS_TOKEN
          valueFrom:
            secretKeyRef:
              name: graphql-secrets
              key: token
        - name: MCP_SERVER_PORT
          value: "8080"
        - name: ENABLE_HTTP_ENDPOINT
          value: "true"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
          requests:
            cpu: "500m"
            memory: "256Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: graphql-mcp-server
spec:
  selector:
    app: graphql-mcp-server
  ports:
  - port: 80
    targetPort: 8080
    name: http
  type: LoadBalancer
---
apiVersion: v1
kind: Secret
metadata:
  name: graphql-secrets
type: Opaque
stringData:
  endpoint: "https://api.yourdomain.com/graphql"
  token: "your_token_here"
```

**Deploy:**
```bash
kubectl apply -f deployment.yaml
```

**Check status:**
```bash
kubectl get pods -l app=graphql-mcp-server
kubectl logs -f deployment/graphql-mcp-server
```

**Access the service:**
```bash
kubectl port-forward service/graphql-mcp-server 8080:80
curl http://localhost:8080/health
```

## Cloud Deployment

### AWS ECS

1. **Push image to ECR:**
```bash
aws ecr create-repository --repository-name graphql-mcp-server
docker tag graphql-mcp-server:latest <account-id>.dkr.ecr.<region>.amazonaws.com/graphql-mcp-server:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/graphql-mcp-server:latest
```

2. **Create task definition with port 8080 exposed**

3. **Deploy to ECS service**

### Google Cloud Run

```bash
# Build and push to GCR
docker tag graphql-mcp-server:latest gcr.io/<project-id>/graphql-mcp-server:latest
docker push gcr.io/<project-id>/graphql-mcp-server:latest

# Deploy to Cloud Run
gcloud run deploy graphql-mcp-server \
  --image gcr.io/<project-id>/graphql-mcp-server:latest \
  --port 8080 \
  --set-env-vars GRAPHQL_ENDPOINT=https://api.yourdomain.com/graphql \
  --set-env-vars API_ACCESS_TOKEN=your_token_here \
  --set-env-vars MCP_SERVER_PORT=8080 \
  --allow-unauthenticated
```

### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name graphql-mcp-server \
  --image graphql-mcp-server:latest \
  --ports 8080 \
  --dns-name-label graphql-mcp \
  --environment-variables \
    GRAPHQL_ENDPOINT=https://api.yourdomain.com/graphql \
    API_ACCESS_TOKEN=your_token_here \
    MCP_SERVER_PORT=8080
```

## Monitoring & Debugging

### Health Check Monitoring

Set up automated health checks:
```bash
# Using curl in a cron job
*/5 * * * * curl -f http://localhost:8080/health || alert-script.sh

# Using Docker healthcheck
docker inspect --format='{{.State.Health.Status}}' graphql-mcp-server
```

### Prometheus Metrics (Future Enhancement)

The `/metrics` endpoint can be extended to support Prometheus format for advanced monitoring.

### Log Aggregation

**View logs in real-time:**
```bash
# Docker Compose
docker-compose logs -f --tail=100

# Docker
docker logs -f graphql-mcp-server

# Kubernetes
kubectl logs -f deployment/graphql-mcp-server
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8080

# Use a different port
MCP_SERVER_PORT=9000 docker-compose up
```

### Container Won't Start
```bash
# Check logs
docker logs graphql-mcp-server

# Common issues:
# - Missing GRAPHQL_ENDPOINT
# - Invalid API_ACCESS_TOKEN
# - Port conflicts
```

### HTTP Endpoints Not Working
```bash
# Verify ENABLE_HTTP_ENDPOINT is true
docker exec graphql-mcp-server env | grep ENABLE_HTTP_ENDPOINT

# Check if port is exposed
docker port graphql-mcp-server

# Test connection
curl -v http://localhost:8080/health
```

## Security Best Practices

1. **Never commit `.env` file to version control**
2. **Use secrets management:**
   - Kubernetes Secrets
   - AWS Secrets Manager
   - Azure Key Vault
   - Google Secret Manager

3. **Limit port exposure:**
   ```yaml
   # Only expose to localhost
   ports:
     - "127.0.0.1:8080:8080"
   ```

4. **Use TLS/SSL in production:**
   - Add reverse proxy (nginx, traefik)
   - Configure SSL certificates

5. **Set resource limits in production**

## Performance Tuning

### Docker Resource Limits
```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 1G
    reservations:
      cpus: '1.0'
      memory: 512M
```

### Schema Cache Configuration
```bash
# Increase cache TTL for stable schemas
SCHEMA_CACHE_TTL=7200  # 2 hours
```

### Query Timeout
```bash
# Adjust for slow queries
QUERY_TIMEOUT=60  # 60 seconds
```

## Support & Contributing

For issues, questions, or contributions:
- Open an issue on GitHub
- Submit pull requests
- Check the main README.md for more information

## License

See LICENSE file for details.
