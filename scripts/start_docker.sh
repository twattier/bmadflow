#!/bin/bash
# BMADFlow Docker Startup Script
# Builds and deploys frontend and backend in Docker containers
# Checks for running services and stops them before starting

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== BMADFlow Docker Startup ===${NC}"

# Change to project root directory (parent of scripts/)
cd "$(dirname "$0")/.."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✓ Loaded .env configuration${NC}"
else
    echo -e "${RED}✗ .env file not found. Copy .env.example to .env${NC}"
    exit 1
fi

# Ports from .env
FRONTEND_PORT=${FRONTEND_PORT:-3002}
BACKEND_PORT=${BACKEND_PORT:-8001}
POSTGRES_PORT=${POSTGRES_PORT:-5434}
PGADMIN_PORT=${PGADMIN_PORT:-5050}

echo -e "${YELLOW}Configured ports:${NC}"
echo "  Frontend: $FRONTEND_PORT"
echo "  Backend:  $BACKEND_PORT"
echo "  Postgres: $POSTGRES_PORT"
echo "  pgAdmin:  $PGADMIN_PORT"
echo ""

# Function to check if port is in use
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 || ss -ltn | grep -q ":$port " 2>/dev/null; then
        echo -e "${YELLOW}⚠ Port $port ($service) is in use${NC}"
        return 0
    else
        return 1
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}  Killing processes on port $port: $pids${NC}"
        kill -9 $pids 2>/dev/null || true
        sleep 1
    fi
}

# Check for running Docker containers
echo -e "${YELLOW}Checking for running Docker containers...${NC}"
if docker-compose ps --services --filter "status=running" 2>/dev/null | grep -q .; then
    echo -e "${YELLOW}⚠ Docker containers are running. Stopping them...${NC}"
    docker-compose down
    echo -e "${GREEN}✓ Docker containers stopped${NC}"
fi

# Check for local services on ports
echo -e "${YELLOW}Checking for local services on ports...${NC}"
CONFLICTS=0

if check_port $FRONTEND_PORT "Frontend"; then
    kill_port $FRONTEND_PORT
    CONFLICTS=1
fi

if check_port $BACKEND_PORT "Backend"; then
    kill_port $BACKEND_PORT
    CONFLICTS=1
fi

if check_port $POSTGRES_PORT "PostgreSQL"; then
    kill_port $POSTGRES_PORT
    CONFLICTS=1
fi

if check_port $PGADMIN_PORT "pgAdmin"; then
    kill_port $PGADMIN_PORT
    CONFLICTS=1
fi

if [ $CONFLICTS -eq 1 ]; then
    echo -e "${GREEN}✓ Cleared conflicting services${NC}"
    sleep 2  # Wait for ports to be fully released
fi

# Build and start Docker containers
echo ""
echo -e "${GREEN}Building and starting Docker containers...${NC}"
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be healthy
echo ""
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 5

# Check service health
echo ""
echo -e "${GREEN}=== Service Status ===${NC}"
docker-compose ps

# Verify services are responding
echo ""
echo -e "${YELLOW}Verifying services...${NC}"

# Check backend health
if curl -s http://localhost:$BACKEND_PORT/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is responding on port $BACKEND_PORT${NC}"
else
    echo -e "${RED}✗ Backend is not responding on port $BACKEND_PORT${NC}"
fi

# Check frontend
if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is responding on port $FRONTEND_PORT${NC}"
else
    echo -e "${RED}✗ Frontend is not responding on port $FRONTEND_PORT${NC}"
fi

# Check database
if docker-compose exec -T db pg_isready -U $POSTGRES_USER > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database is ready${NC}"
else
    echo -e "${RED}✗ Database is not ready${NC}"
fi

echo ""
echo -e "${GREEN}=== BMADFlow Docker Deployment Complete ===${NC}"
echo ""
echo "Access your services:"
echo -e "  Frontend:  ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
echo -e "  Backend:   ${GREEN}http://localhost:$BACKEND_PORT/docs${NC}"
echo -e "  pgAdmin:   ${GREEN}http://localhost:$PGADMIN_PORT${NC}"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop:      docker-compose down"
