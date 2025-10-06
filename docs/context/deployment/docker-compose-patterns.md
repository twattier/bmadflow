# Docker Compose Patterns for Full-Stack Applications

## Overview

This document provides Docker Compose best practices and patterns for orchestrating multi-service applications, specifically focusing on full-stack deployments with React (frontend), FastAPI (backend), and PostgreSQL (database) services.

## Table of Contents

1. [Multi-Service Orchestration](#multi-service-orchestration)
2. [Environment Variable Configuration](#environment-variable-configuration)
3. [Volume Persistence Patterns](#volume-persistence-patterns)
4. [Health Checks and Service Dependencies](#health-checks-and-service-dependencies)
5. [Development vs Production Configurations](#development-vs-production-configurations)
6. [Complete Examples](#complete-examples)

---

## 1. Multi-Service Orchestration

### Basic Multi-Service Architecture

A typical full-stack application consists of three core services:

```yaml
services:
  frontend:
    build:
      context: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db

  db:
    image: postgres:16
    ports:
      - "5432:5432"
```

### Service Communication

Services communicate using service names as hostnames within the Docker network:

```yaml
services:
  backend:
    environment:
      - DATABASE_HOST=db  # Service name as hostname
      - DATABASE_PORT=5432
```

### Networks

Define custom networks for service isolation:

```yaml
services:
  frontend:
    networks:
      - app-network
  backend:
    networks:
      - app-network
  db:
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

---

## 2. Environment Variable Configuration

### Using .env Files

Docker Compose automatically loads variables from `.env` files in the project root:

**.env**
```bash
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=appdb
POSTGRES_PORT=5432

# Backend Configuration
BACKEND_PORT=8000
API_DEBUG=false

# Frontend Configuration
FRONTEND_PORT=3000
REACT_APP_API_URL=http://localhost:8000
```

### Multiple Environment Files

Specify multiple environment files with priority:

```yaml
services:
  backend:
    env_file:
      - path: ./default.env
        required: true
      - path: ./override.env
        required: false
```

### Environment Variable Methods

**1. Direct Declaration**
```yaml
services:
  backend:
    environment:
      - NODE_ENV=production
      - DEBUG=true
```

**2. Variable Interpolation from .env**
```yaml
services:
  backend:
    environment:
      - POSTGRES_HOST=db
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
```

**3. Using env_file**
```yaml
services:
  backend:
    env_file:
      - .env
```

### Environment Variable Interpolation Patterns

**Default Values**
```yaml
services:
  backend:
    environment:
      - DEBUG=${DEBUG:-false}
      - PORT=${PORT:-8000}
```

**Mandatory Variables**
```yaml
services:
  backend:
    environment:
      - API_KEY=${API_KEY:?API_KEY environment variable not set}
```

### Compose-Specific Environment Variables

```bash
# Specify compose file(s)
export COMPOSE_FILE=docker-compose.yml

# Set project name
export COMPOSE_PROJECT_NAME=my_project

# Activate profiles
export COMPOSE_PROFILES=frontend,debug

# Control parallelism
export COMPOSE_PARALLEL_LIMIT=1

# Multiple environment files
export COMPOSE_ENV_FILES=.env.base,.env.local
```

---

## 3. Volume Persistence Patterns

### Database Volume Persistence

**Named Volumes (Recommended for Production)**
```yaml
services:
  db:
    image: postgres:16
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
    # Optional: specify driver options
    driver: local
```

**Bind Mounts (Development)**
```yaml
services:
  db:
    image: postgres:16
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
```

### Application Data Volumes

**Frontend Build Artifacts**
```yaml
services:
  frontend:
    build:
      context: ./frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules  # Prevent overwriting
```

**Backend Code (Development)**
```yaml
services:
  backend:
    build:
      context: ./backend
    volumes:
      - ./backend:/app
      - /app/__pycache__  # Exclude cache
```

### Read-Only Volumes

```yaml
services:
  web:
    volumes:
      - app-storage:/var/www/storage:ro  # Read-only

  app:
    volumes:
      - app-storage:/var/www/storage  # Read-write
```

### Dynamic Volume Naming

```yaml
services:
  db:
    volumes:
      - ${DATABASE_VOLUME_NAME:-postgres-data}:/var/lib/postgresql/data

volumes:
  postgres-data:
```

### Pre-seeded Database Volumes

```yaml
services:
  db:
    build:
      context: ./db
      dockerfile: Dockerfile
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

**Dockerfile for Pre-seeded DB**
```dockerfile
FROM postgres:16

# Copy initialization scripts
COPY ./init.sql /docker-entrypoint-initdb.d/

# Set environment variables
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=mysecretpassword
ENV POSTGRES_DB=appdb
```

---

## 4. Health Checks and Service Dependencies

### PostgreSQL Health Check

```yaml
services:
  db:
    image: postgres:16
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### Alternative PostgreSQL Health Check

```yaml
services:
  db:
    image: postgres:16
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### FastAPI/Backend Health Check

```yaml
services:
  backend:
    build:
      context: ./backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Service Dependencies with Health Checks

**Basic Dependency**
```yaml
services:
  backend:
    depends_on:
      - db
```

**Health-Based Dependency (Recommended)**
```yaml
services:
  backend:
    depends_on:
      db:
        condition: service_healthy

  db:
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### Complete Dependency Chain

```yaml
services:
  frontend:
    depends_on:
      backend:
        condition: service_healthy

  backend:
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### Redis Health Check

```yaml
services:
  redis:
    image: redis:alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3
```

---

## 5. Development vs Production Configurations

### Development Configuration (compose.dev.yaml)

```yaml
services:
  frontend:
    build:
      context: ./frontend
      target: development
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - REACT_APP_API_URL=http://localhost:8000
    command: npm start

  backend:
    build:
      context: ./backend
      target: development
    volumes:
      - ./backend:/app
      - /app/__pycache__
    ports:
      - "8000:8000"
      - "5678:5678"  # Debug port
    environment:
      - FASTAPI_ENV=development
      - DEBUG=true
      - RELOAD=true
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:16
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=dev_password
      - POSTGRES_DB=dev_db
    volumes:
      - postgres-dev-data:/var/lib/postgresql/data

volumes:
  postgres-dev-data:
```

### Production Configuration (compose.prod.yaml)

```yaml
services:
  frontend:
    build:
      context: ./frontend
      target: production
    restart: unless-stopped
    ports:
      - "80:80"
    environment:
      - NODE_ENV=production

  backend:
    build:
      context: ./backend
      target: production
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - FASTAPI_ENV=production
      - DEBUG=false
      - WORKERS=4
    secrets:
      - db-password

  db:
    image: postgres:16
    restart: unless-stopped
    secrets:
      - db-password
    volumes:
      - postgres-prod-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=prod_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD_FILE=/run/secrets/db-password
    expose:
      - 5432
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres-prod-data:

secrets:
  db-password:
    file: ./secrets/db_password.txt
```

### Base Configuration (compose.yaml)

```yaml
services:
  frontend:
    build:
      context: ./frontend
    ports:
      - "3000:3000"

  backend:
    build:
      context: ./backend
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### Running Different Configurations

**Development**
```bash
docker compose -f compose.yaml -f compose.dev.yaml up
```

**Production**
```bash
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

### Using Profiles

```yaml
services:
  frontend:
    profiles: ["frontend", "full"]
    build: ./frontend

  backend:
    profiles: ["backend", "full"]
    build: ./backend

  db:
    profiles: ["full"]
    image: postgres:16
```

**Activate Profiles**
```bash
# Start only frontend
docker compose --profile frontend up

# Start frontend and backend
docker compose --profile frontend --profile backend up

# Start everything
docker compose --profile full up
```

---

## 6. Complete Examples

### Example 1: React + FastAPI + PostgreSQL (Development)

**compose.yaml**
```yaml
version: "3.8"

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: react-frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    networks:
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: fastapi-backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy
    networks:
      - app-network

  db:
    image: postgres:16
    container_name: postgres-db
    restart: always
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres-data:
```

**.env**
```bash
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=appdb

# FastAPI Configuration
FASTAPI_DEBUG=true
API_PORT=8000

# React Configuration
REACT_APP_API_URL=http://localhost:8000
```

**backend/Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**backend/requirements.txt**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic==2.5.3
```

**frontend/Dockerfile**
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

### Example 2: Production Setup with Secrets

**compose.prod.yaml**
```yaml
version: "3.8"

services:
  frontend:
    build:
      context: ./frontend
      target: production
    container_name: react-frontend-prod
    restart: unless-stopped
    ports:
      - "80:80"
    networks:
      - app-network-prod

  backend:
    build:
      context: ./backend
      target: production
    container_name: fastapi-backend-prod
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD_FILE=/run/secrets/db-password
      - POSTGRES_DB=prod_db
    secrets:
      - db-password
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - app-network-prod

  db:
    image: postgres:16
    container_name: postgres-db-prod
    restart: unless-stopped
    user: postgres
    secrets:
      - db-password
    volumes:
      - postgres-prod-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=prod_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD_FILE=/run/secrets/db-password
    expose:
      - 5432
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network-prod

networks:
  app-network-prod:
    external: false

volumes:
  postgres-prod-data:

secrets:
  db-password:
    file: ./secrets/db_password.txt
```

### Example 3: Multi-Stage Development/Production

**compose.yaml**
```yaml
version: "3.8"

services:
  frontend:
    build:
      context: ./frontend
      target: ${BUILD_TARGET:-development}
    ports:
      - "${FRONTEND_PORT:-3000}:3000"
    environment:
      - NODE_ENV=${NODE_ENV:-development}
    volumes:
      - ./frontend:/app
      - /app/node_modules

  backend:
    build:
      context: ./backend
      target: ${BUILD_TARGET:-development}
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    environment:
      - POSTGRES_HOST=db
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres-data:
```

**Multi-stage Dockerfile (backend)**
```dockerfile
# Development stage
FROM python:3.11-slim AS development

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM python:3.11-slim AS production

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## Best Practices Summary

### 1. Environment Management
- Use `.env` files for environment-specific variables
- Never commit sensitive data (passwords, API keys) to version control
- Use Docker secrets for production credentials
- Leverage variable interpolation with default values

### 2. Service Dependencies
- Always use health checks with `depends_on`
- Implement proper health check endpoints in your applications
- Use `condition: service_healthy` for critical dependencies

### 3. Volume Strategy
- Use named volumes for database persistence
- Use bind mounts only for development
- Exclude unnecessary directories (node_modules, __pycache__)
- Use read-only volumes where appropriate

### 4. Multi-Environment Setup
- Maintain a base `compose.yaml` with common configuration
- Create environment-specific override files
- Use build targets for multi-stage Dockerfiles
- Leverage profiles for optional services

### 5. Networking
- Create custom networks for service isolation
- Use service names for inter-service communication
- Expose ports appropriately based on environment

### 6. Production Considerations
- Use `restart: unless-stopped` for critical services
- Implement comprehensive health checks
- Use secrets for sensitive data
- Limit exposed ports (use `expose` instead of `ports`)
- Set resource limits when needed

---

## Useful Commands

### Development
```bash
# Start all services
docker compose up

# Start with rebuild
docker compose up --build

# Start in detached mode
docker compose up -d

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend

# Execute commands in running containers
docker compose exec backend python manage.py migrate
docker compose exec db psql -U postgres

# Run one-off commands
docker compose run --rm backend python manage.py createsuperuser
```

### Production
```bash
# Deploy with production config
docker compose -f compose.yaml -f compose.prod.yaml up -d

# Pull latest images
docker compose pull

# Scale services
docker compose up -d --scale backend=3

# View resource usage
docker compose stats
```

### Maintenance
```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# Remove orphaned containers
docker compose down --remove-orphans

# View running containers
docker compose ps

# Validate compose file
docker compose config

# Dry run (test without executing)
docker compose --dry-run up
```

---

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Compose File Reference](https://docs.docker.com/compose/compose-file/)
- [Best Practices for Writing Dockerfiles](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Secrets](https://docs.docker.com/engine/swarm/secrets/)
