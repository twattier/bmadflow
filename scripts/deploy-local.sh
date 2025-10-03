#!/bin/bash
# Local Deployment Script for BMAD Flow
# Runs frontend/backend locally, database in Docker
# Auto-detects and stops Docker frontend/backend if running

set -e

# Get absolute path to project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 BMAD Flow - Local Deployment"
echo "================================"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Load .env
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    exit 1
fi

set -a
source .env
set +a

export DATABASE_URL=$(echo "$DATABASE_URL" | sed "s/@postgres:5432/@127.0.0.1:${POSTGRES_PORT}/")
export VITE_API_URL="http://localhost:${BACKEND_PORT}"

echo -e "${GREEN}✓${NC} Configuration loaded from .env"

echo ""
echo "Step 1: Stop Docker Frontend/Backend"
echo "-------------------------------------"
if docker ps --format '{{.Names}}' | grep -qE 'bmad-flow-(frontend|backend)'; then
    echo "Stopping Docker frontend/backend containers..."
    docker stop bmad-flow-frontend bmad-flow-backend 2>/dev/null || true
    docker rm bmad-flow-frontend bmad-flow-backend 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Docker containers stopped (postgres/pgadmin still running)"
else
    echo "No Docker frontend/backend containers running"
fi

wait_for_postgres() {
    echo -n "Waiting for PostgreSQL..."
    for i in {1..30}; do
        if docker exec bmad-flow-postgres pg_isready -U ${POSTGRES_USER} >/dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
    done
    echo -e " ${RED}✗${NC}"
    return 1
}

echo ""
echo "Step 2: Database (Docker)"
echo "-------------------------"
cd infrastructure
docker-compose up -d postgres
cd ..
wait_for_postgres || exit 1

echo ""
echo "Step 3: Backend (Local)"
echo "-----------------------"
if lsof -ti:${BACKEND_PORT} >/dev/null 2>&1; then
    echo "Stopping existing backend on port ${BACKEND_PORT}..."
    lsof -ti:${BACKEND_PORT} | xargs -r kill -9 2>/dev/null
    sleep 2
fi

pip install -q -r apps/api/requirements.txt
"$PROJECT_ROOT/scripts/start-backend.sh" ${BACKEND_PORT} &
BACKEND_PID=$!
sleep 3

echo -n "Waiting for backend..."
BACKEND_READY=false
for i in {1..30}; do
    if curl -s http://localhost:${BACKEND_PORT}/api/health >/dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        BACKEND_READY=true
        break
    fi
    echo -n "."
    sleep 1
done

if [ "$BACKEND_READY" = false ]; then
    echo -e " ${RED}✗${NC}"
    echo -e "${RED}Error: Backend failed to start${NC}"
    echo "Check logs: tail -f /tmp/bmad-backend.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "Step 4: Frontend (Local)"
echo "------------------------"
if lsof -ti:${FRONTEND_PORT} >/dev/null 2>&1; then
    echo "Stopping existing frontend on port ${FRONTEND_PORT}..."
    lsof -ti:${FRONTEND_PORT} | xargs -r kill -9 2>/dev/null
    sleep 2
fi

npm install --prefix apps/web
"$PROJECT_ROOT/scripts/start-frontend.sh" ${FRONTEND_PORT} &
FRONTEND_PID=$!
sleep 8

echo -n "Waiting for frontend..."
FRONTEND_READY=false
for i in {1..60}; do
    if curl -s http://localhost:${FRONTEND_PORT} >/dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        FRONTEND_READY=true
        break
    fi
    echo -n "."
    sleep 1
done

if [ "$FRONTEND_READY" = false ]; then
    echo -e " ${RED}✗${NC}"
    echo -e "${RED}Error: Frontend failed to start${NC}"
    echo "Check logs: tail -f /tmp/bmad-frontend.log"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo ""
echo "Services:"
echo "  Frontend:  http://localhost:${FRONTEND_PORT}"
echo "  Backend:   http://localhost:${BACKEND_PORT}"
echo "  Database:  127.0.0.1:${POSTGRES_PORT} (Docker)"
echo "  PgAdmin:   http://localhost:${PGADMIN_PORT} (Docker)"
echo ""
echo "PIDs: Backend=${BACKEND_PID}, Frontend=${FRONTEND_PID}"
echo ""
echo "⚠️  IMPORTANT: Keep this terminal open!"
echo "   Closing this terminal will stop the frontend/backend services."
echo ""
echo "To stop: Press Ctrl+C or run: kill ${BACKEND_PID} ${FRONTEND_PID}"
echo "To stop database: cd infrastructure && docker-compose down"
echo ""
echo "Waiting for Ctrl+C..."
wait
