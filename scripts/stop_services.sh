#!/bin/bash
# BMADFlow Service Stop Script
# Stops both Docker and local services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== BMADFlow Service Stop ===${NC}"

# Change to project root directory (parent of scripts/)
cd "$(dirname "$0")/.."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

FRONTEND_PORT=${FRONTEND_PORT:-3002}
BACKEND_PORT=${BACKEND_PORT:-8001}

# Stop Docker containers
echo -e "${YELLOW}Stopping Docker containers...${NC}"
if docker-compose ps --services --filter "status=running" 2>/dev/null | grep -q .; then
    docker-compose down
    echo -e "${GREEN}✓ Docker containers stopped${NC}"
else
    echo -e "${YELLOW}  No Docker containers running${NC}"
fi

# Stop local processes via PID files
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}Stopping backend (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID 2>/dev/null || kill -9 $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✓ Backend stopped${NC}"
    fi
    rm .backend.pid
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}Stopping frontend (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID 2>/dev/null || kill -9 $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✓ Frontend stopped${NC}"
    fi
    rm .frontend.pid
fi

# Force kill any remaining processes on ports
echo -e "${YELLOW}Checking for remaining processes on ports...${NC}"

kill_port() {
    local port=$1
    local service=$2
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}  Killing $service on port $port (PIDs: $pids)${NC}"
        kill -9 $pids 2>/dev/null || true
    fi
}

kill_port $FRONTEND_PORT "Frontend"
kill_port $BACKEND_PORT "Backend"

echo ""
echo -e "${GREEN}=== All Services Stopped ===${NC}"
