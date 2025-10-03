#!/bin/bash
# Docker Deployment Script for BMAD Flow
# Runs all services in Docker containers
# Uses .env for all configuration

set -e

echo "🐳 BMAD Flow - Docker Deployment"
echo "================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Load .env to get port configuration
if [ -f ".env" ]; then
    echo "Loading configuration from .env..."
    set -a
    source .env
    set +a
    echo -e "${GREEN}✓${NC} Configuration loaded"
else
    echo -e "${RED}Error: .env file not found${NC}"
    exit 1
fi

wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=60
    local attempt=1

    echo -n "Waiting for $service_name..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
        ((attempt++))
    done
    echo -e " ${RED}✗${NC}"
    return 1
}

echo ""
echo "Step 1: Prerequisites"
echo "---------------------"
command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker required${NC}"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}Docker Compose required${NC}"; exit 1; }
docker info > /dev/null 2>&1 || { echo -e "${RED}Docker daemon not running${NC}"; exit 1; }
echo -e "${GREEN}✓${NC} All prerequisites met"

echo ""
echo "Step 2: Cleanup"
echo "---------------"
cd infrastructure
docker-compose down 2>/dev/null || true
docker-compose rm -f 2>/dev/null || true

echo ""
echo "Step 3: Building Images"
echo "-----------------------"
docker-compose build backend
docker-compose build frontend

echo ""
echo "Step 4: Starting Services"
echo "-------------------------"
docker-compose up -d
cd ..

echo ""
echo "Step 5: Health Checks"
echo "---------------------"
wait_for_service "http://localhost:${POSTGRES_PORT}" "PostgreSQL" || { docker-compose -f infrastructure/docker-compose.yml logs postgres; exit 1; }
wait_for_service "http://localhost:${BACKEND_PORT}/api/health" "Backend" || { docker logs bmad-flow-backend --tail 50; exit 1; }
wait_for_service "http://localhost:${FRONTEND_PORT}" "Frontend" || { docker logs bmad-flow-frontend --tail 50; exit 1; }

echo ""
echo "Step 6: Connection Tests"
echo "------------------------"

echo -n "Database connection..."
docker exec bmad-flow-postgres pg_isready -U ${POSTGRES_USER} > /dev/null 2>&1 && echo -e " ${GREEN}✓${NC}" || echo -e " ${RED}✗${NC}"

echo -n "Backend health..."
HEALTH=$(curl -s http://localhost:${BACKEND_PORT}/api/health | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "error")
[ "$HEALTH" = "healthy" ] && echo -e " ${GREEN}✓${NC}" || echo -e " ${YELLOW}⚠${NC} ($HEALTH)"

echo -n "Frontend -> Backend proxy..."
PROXY=$(docker exec bmad-flow-frontend wget -q -O- http://backend:8000/api/health 2>&1 | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "error")
[ "$PROXY" = "healthy" ] && echo -e " ${GREEN}✓${NC}" || echo -e " ${RED}✗${NC}"

echo -n "Epics endpoint..."
EPICS=$(curl -s "http://localhost:${BACKEND_PORT}/api/epics?project_id=7e4d469f-dd82-42ab-93a1-bc240e175c29" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
[ "$EPICS" -gt "0" ] && echo -e " ${GREEN}✓${NC} ($EPICS epics)" || echo -e " ${YELLOW}⚠${NC} (empty)"

echo ""
echo "Step 7: Container Status"
echo "------------------------"
docker ps --filter "name=bmad-flow" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✓ Docker Deployment Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Services:"
echo "  Frontend:  http://localhost:${FRONTEND_PORT}"
echo "  Backend:   http://localhost:${BACKEND_PORT}"
echo "  API Docs:  http://localhost:${BACKEND_PORT}/docs"
echo "  Database:  127.0.0.1:${POSTGRES_PORT}"
echo "  PgAdmin:   http://localhost:${PGADMIN_PORT} (${PGADMIN_EMAIL} / ${PGADMIN_PASSWORD})"
echo ""
echo "Management:"
echo "  Logs:    docker logs bmad-flow-backend -f"
echo "  Stop:    cd infrastructure && docker-compose down"
echo "  Restart: cd infrastructure && docker-compose restart <service>"
echo ""
