@echo off
REM Quick start script for GraphQL MCP Server (Windows)

echo ================================================
echo GraphQL MCP Server - Quick Start
echo ================================================
echo.

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo [INFO] Creating .env from .env.example...
    copy .env.example .env
    echo [SUCCESS] .env file created
    echo.
    echo [WARNING] Please edit .env file with your configuration:
    echo    - GRAPHQL_ENDPOINT
    echo    - API_ACCESS_TOKEN
    echo.
    echo Then run this script again.
    exit /b 1
)

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed
    echo Please install Docker from: https://docs.docker.com/get-docker/
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed
    echo Please install Docker Compose from: https://docs.docker.com/compose/install/
    exit /b 1
)

echo [SUCCESS] Docker and Docker Compose are installed
echo.

REM Load environment variables
for /f "tokens=*" %%i in ('type .env ^| findstr /v "^#"') do set %%i

REM Validate required variables
if "%GRAPHQL_ENDPOINT%"=="" (
    echo [ERROR] GRAPHQL_ENDPOINT is not set in .env
    exit /b 1
)

if "%API_ACCESS_TOKEN%"=="" (
    echo [ERROR] API_ACCESS_TOKEN is not set in .env
    exit /b 1
)

echo [SUCCESS] Configuration validated
echo.
echo Configuration:
echo   - GraphQL Endpoint: %GRAPHQL_ENDPOINT%
echo   - Server Port: %MCP_SERVER_PORT%
echo   - HTTP Endpoint: %ENABLE_HTTP_ENDPOINT%
echo.

REM Build and start
echo [BUILD] Building Docker image...
docker-compose build

echo.
echo [START] Starting server...
docker-compose up -d

echo.
echo [WAIT] Waiting for server to be ready...
timeout /t 5 /nobreak >nul

REM Get the port
if "%MCP_SERVER_PORT%"=="" set MCP_SERVER_PORT=8080

REM Health check
echo [CHECK] Checking server health...
curl -f http://localhost:%MCP_SERVER_PORT%/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Server is starting but health check failed
    echo This might be normal if the schema is still loading
    echo.
    echo Check logs with: docker-compose logs -f
) else (
    echo [SUCCESS] Server is healthy!
    echo.
    echo ================================================
    echo Server is running!
    echo ================================================
    echo.
    echo Endpoints:
    echo   - Root:    http://localhost:%MCP_SERVER_PORT%/
    echo   - Health:  http://localhost:%MCP_SERVER_PORT%/health
    echo   - Metrics: http://localhost:%MCP_SERVER_PORT%/metrics
    echo   - Schema:  http://localhost:%MCP_SERVER_PORT%/schema
    echo   - Tools:   http://localhost:%MCP_SERVER_PORT%/tools
    echo.
    echo Useful commands:
    echo   - View logs:    docker-compose logs -f
    echo   - Stop server:  docker-compose down
    echo   - Restart:      docker-compose restart
    echo.
)
