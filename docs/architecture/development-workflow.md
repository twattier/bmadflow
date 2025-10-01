# Development Workflow

## Prerequisites

```bash
node --version  # 20.x+
python --version  # 3.11+
docker --version  # 24.0+
```

## Initial Setup

```bash
git clone https://github.com/your-org/bmadflow.git
cd bmadflow
cp .env.example .env

npm install  # Install all workspace packages

cd apps/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# Note: OLLAMA runs on external server, configure OLLAMA_BASE_URL in .env
# Verify OLLAMA server has required model (llama3:8b or mistral:7b)

cd ../..
docker compose up -d
```

## Development Commands

```bash
# Start all services
docker compose up

# Frontend only (hot reload)
npm run dev --workspace=apps/web

# Backend only (hot reload)
cd apps/api && uvicorn src.main:app --reload

# Run tests
npm run test  # Frontend
cd apps/api && pytest  # Backend

# Lint/format
npm run lint
cd apps/api && black src/ && ruff check src/

# Database migrations
cd apps/api && alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Environment Variables

```bash
# Frontend (.env.local)
VITE_API_BASE_URL=http://localhost:8000/api

# Backend (.env)
DATABASE_URL=postgresql+asyncpg://bmadflow:password@localhost:5432/bmadflow
REDIS_URL=redis://localhost:6379/0
OLLAMA_BASE_URL=http://your-ollama-server:11434  # Point to your existing OLLAMA server
OLLAMA_MODEL=llama3:8b  # Model available on your OLLAMA server
OLLAMA_TIMEOUT=30  # Timeout in seconds
GITHUB_TOKEN=  # Optional
SECRET_KEY=change-in-production
```

---
