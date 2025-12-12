# Docker Build and Push Guide

This guide helps you build the Docker image and push it to a container registry.

## Building the Docker Image

### Local Build

```bash
# Build with default tag
docker build -t graphql-mcp-server:latest .

# Build with custom tag
docker build -t graphql-mcp-server:v1.0.0 .

# Build with multiple tags
docker build -t graphql-mcp-server:latest -t graphql-mcp-server:v1.0.0 .
```

### Multi-platform Build

For deploying to different architectures (ARM, x86):

```bash
# Create a builder
docker buildx create --name multiplatform --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t graphql-mcp-server:latest \
  --push \
  .
```

## Pushing to Container Registries

### Docker Hub

```bash
# Login
docker login

# Tag image
docker tag graphql-mcp-server:latest yourusername/graphql-mcp-server:latest
docker tag graphql-mcp-server:latest yourusername/graphql-mcp-server:v1.0.0

# Push
docker push yourusername/graphql-mcp-server:latest
docker push yourusername/graphql-mcp-server:v1.0.0
```

### GitHub Container Registry (ghcr.io)

```bash
# Login (use Personal Access Token with packages:write permission)
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag image
docker tag graphql-mcp-server:latest ghcr.io/yourusername/graphql-mcp-server:latest
docker tag graphql-mcp-server:latest ghcr.io/yourusername/graphql-mcp-server:v1.0.0

# Push
docker push ghcr.io/yourusername/graphql-mcp-server:latest
docker push ghcr.io/yourusername/graphql-mcp-server:v1.0.0
```

### AWS Elastic Container Registry (ECR)

```bash
# Login (requires AWS CLI)
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com

# Create repository (first time only)
aws ecr create-repository \
  --repository-name graphql-mcp-server \
  --region us-east-1

# Tag image
docker tag graphql-mcp-server:latest \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/graphql-mcp-server:latest

# Push
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/graphql-mcp-server:latest
```

### Google Container Registry (GCR)

```bash
# Login (requires gcloud CLI)
gcloud auth configure-docker

# Tag image
docker tag graphql-mcp-server:latest \
  gcr.io/your-project-id/graphql-mcp-server:latest

# Push
docker push gcr.io/your-project-id/graphql-mcp-server:latest
```

### Azure Container Registry (ACR)

```bash
# Login (requires Azure CLI)
az acr login --name myregistry

# Tag image
docker tag graphql-mcp-server:latest \
  myregistry.azurecr.io/graphql-mcp-server:latest

# Push
docker push myregistry.azurecr.io/graphql-mcp-server:latest
```

## Automated Build with CI/CD

### GitHub Actions

Create `.github/workflows/docker-build.yml`:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - name: Checkout
      uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}

    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        platforms: linux/amd64,linux/arm64
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
variables:
  DOCKER_IMAGE: $CI_REGISTRY_IMAGE
  DOCKER_TAG: $CI_COMMIT_REF_SLUG

stages:
  - build
  - push

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $DOCKER_IMAGE:$DOCKER_TAG .
    - docker push $DOCKER_IMAGE:$DOCKER_TAG
  only:
    - main
    - tags
```

## Testing the Image

### Local Testing

```bash
# Run with test environment
docker run -it --rm \
  -e GRAPHQL_ENDPOINT=https://api.example.com/graphql \
  -e API_ACCESS_TOKEN=test_token \
  -e MCP_SERVER_PORT=8080 \
  -p 8080:8080 \
  graphql-mcp-server:latest

# Test health endpoint
curl http://localhost:8080/health
```

### Docker Compose Testing

```yaml
version: '3.8'
services:
  graphql-mcp-server:
    image: graphql-mcp-server:latest
    ports:
      - "8080:8080"
    environment:
      - GRAPHQL_ENDPOINT=https://api.example.com/graphql
      - API_ACCESS_TOKEN=test_token
      - MCP_SERVER_PORT=8080
      - ENABLE_HTTP_ENDPOINT=true
```

```bash
docker-compose up
```

## Image Optimization

### Multi-stage Build (Already Implemented)

The Dockerfile already uses a slim Python base image. For further optimization:

```dockerfile
# Example: Even smaller image using alpine
FROM python:3.11-alpine

RUN apk add --no-cache gcc musl-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
CMD ["python", "-m", "graphql_mcp_server"]
```

### Reducing Image Size

```bash
# View image size
docker images graphql-mcp-server

# Analyze image layers
docker history graphql-mcp-server:latest

# Use dive tool for detailed analysis
dive graphql-mcp-server:latest
```

## Security Scanning

### Scan with Docker Scout

```bash
# Enable Docker Scout
docker scout enroll

# Scan image
docker scout cves graphql-mcp-server:latest

# Get recommendations
docker scout recommendations graphql-mcp-server:latest
```

### Scan with Trivy

```bash
# Install trivy
brew install trivy  # macOS
# or download from https://github.com/aquasecurity/trivy

# Scan image
trivy image graphql-mcp-server:latest

# Scan with severity filter
trivy image --severity HIGH,CRITICAL graphql-mcp-server:latest
```

## Version Tagging Strategy

### Semantic Versioning

```bash
# Major.Minor.Patch
docker tag graphql-mcp-server:latest graphql-mcp-server:1.0.0
docker tag graphql-mcp-server:latest graphql-mcp-server:1.0
docker tag graphql-mcp-server:latest graphql-mcp-server:1

# Push all tags
docker push graphql-mcp-server:1.0.0
docker push graphql-mcp-server:1.0
docker push graphql-mcp-server:1
docker push graphql-mcp-server:latest
```

### Date-based Versioning

```bash
# YYYY-MM-DD format
docker tag graphql-mcp-server:latest graphql-mcp-server:2024-12-11
docker push graphql-mcp-server:2024-12-11
```

### Git Commit-based

```bash
# Use git commit SHA
GIT_SHA=$(git rev-parse --short HEAD)
docker tag graphql-mcp-server:latest graphql-mcp-server:$GIT_SHA
docker push graphql-mcp-server:$GIT_SHA
```

## Cleanup

### Remove Old Images

```bash
# Remove untagged images
docker image prune

# Remove all unused images
docker image prune -a

# Remove specific versions
docker rmi graphql-mcp-server:v0.9.0
```

### Registry Cleanup

```bash
# Docker Hub - use web interface or API

# ECR - Delete old images
aws ecr batch-delete-image \
  --repository-name graphql-mcp-server \
  --image-ids imageTag=old-tag

# GCR - Delete old images
gcloud container images delete \
  gcr.io/project-id/graphql-mcp-server:old-tag
```

## Best Practices

1. **Always tag with version numbers** - Don't rely only on `latest`
2. **Use semantic versioning** - Makes it clear what changed
3. **Scan for vulnerabilities** - Before pushing to production
4. **Test locally first** - Before pushing to registry
5. **Document changes** - Update CHANGELOG.md
6. **Keep images small** - Use multi-stage builds
7. **Use .dockerignore** - Exclude unnecessary files
8. **Sign images** - For production deployments
9. **Automate with CI/CD** - Consistent builds
10. **Monitor image size** - Keep an eye on growth

## Troubleshooting

### Build Fails

```bash
# Clear build cache
docker builder prune -a

# Build without cache
docker build --no-cache -t graphql-mcp-server:latest .
```

### Push Fails

```bash
# Check login status
docker info | grep Username

# Re-login
docker logout
docker login

# Check network
ping registry.hub.docker.com
```

### Large Image Size

```bash
# Check what's taking space
docker history graphql-mcp-server:latest --no-trunc

# Use dive to analyze
dive graphql-mcp-server:latest
```

## References

- [Docker Build Documentation](https://docs.docker.com/engine/reference/commandline/build/)
- [Docker Buildx](https://docs.docker.com/buildx/working-with-buildx/)
- [Container Registry Documentation](https://docs.docker.com/registry/)
- [Best Practices for Writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
