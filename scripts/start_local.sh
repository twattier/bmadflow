#!/bin/bash
# BMADFlow Local Startup Script
# Builds and launches frontend and backend services locally (non-Docker)
# Checks for running services and stops them before starting

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== BMADFlow Local Startup ===${NC}"

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
echo "  Postgres: $POSTGRES_PORT (Docker only)"
echo "  pgAdmin:  $PGADMIN_PORT (Docker only)"
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
    echo -e "${YELLOW}⚠ Docker containers are running. Stopping frontend and backend containers...${NC}"
    docker-compose stop frontend backend
    echo -e "${GREEN}✓ Docker frontend and backend stopped (keeping DB and pgAdmin)${NC}"
fi

# Check and kill local processes on ports
echo -e "${YELLOW}Checking for local services on ports...${NC}"

if check_port $FRONTEND_PORT "Frontend"; then
    kill_port $FRONTEND_PORT
fi

if check_port $BACKEND_PORT "Backend"; then
    kill_port $BACKEND_PORT
fi

echo -e "${GREEN}✓ Ports cleared${NC}"
sleep 2  # Wait for ports to be fully released

# Check prerequisites
echo ""
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js $(node --version)${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm $(npm --version)${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $(python3 --version)${NC}"

# Start database in Docker (if not already running)
echo ""
echo -e "${YELLOW}Starting database services (Docker)...${NC}"
docker-compose up -d db pgadmin
sleep 3

if docker-compose exec -T db pg_isready -U $POSTGRES_USER > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database is ready on port $POSTGRES_PORT${NC}"
else
    echo -e "${RED}✗ Database failed to start${NC}"
    exit 1
fi

# Install frontend dependencies
echo ""
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
fi

# Install backend dependencies
echo ""
echo -e "${YELLOW}Setting up backend environment...${NC}"
cd ../backend
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✓ Python virtual environment created${NC}"
fi

source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Run database migrations
echo ""
echo -e "${YELLOW}Running database migrations...${NC}"
alembic upgrade head
echo -e "${GREEN}✓ Database migrations complete${NC}"

# Start backend in background
echo ""
echo -e "${YELLOW}Starting backend server...${NC}"
cd ..
nohup bash -c "cd backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload" > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > .backend.pid
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID, logs: backend.log)${NC}"

# Wait for backend to be ready
echo -e "${YELLOW}Waiting for backend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is responding${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Backend failed to start. Check backend.log${NC}"
        exit 1
    fi
done

# Start frontend in background
echo ""
echo -e "${YELLOW}Starting frontend server...${NC}"
nohup bash -c "cd frontend && npm run dev" > frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > .frontend.pid
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID, logs: frontend.log)${NC}"

# Wait for frontend to be ready
echo -e "${YELLOW}Waiting for frontend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is responding${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Frontend failed to start. Check frontend.log${NC}"
        exit 1
    fi
done

echo ""
echo -e "${GREEN}=== BMADFlow Local Deployment Complete ===${NC}"
echo ""
echo "Access your services:"
echo -e "  Frontend:  ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
echo -e "  Backend:   ${GREEN}http://localhost:$BACKEND_PORT/docs${NC}"
echo -e "  pgAdmin:   ${GREEN}http://localhost:$PGADMIN_PORT${NC}"
echo ""
echo "Process IDs saved to:"
echo "  Backend:  .backend.pid (PID: $BACKEND_PID)"
echo "  Frontend: .frontend.pid (PID: $FRONTEND_PID)"
echo ""
echo "Logs available at:"
echo "  Backend:  backend.log"
echo "  Frontend: frontend.log"
echo ""
echo "To stop services:"
echo "  kill \$(cat .backend.pid) \$(cat .frontend.pid)"
echo "  docker-compose stop db pgadmin"
