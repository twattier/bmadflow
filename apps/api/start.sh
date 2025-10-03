#!/bin/bash

# Load environment variables from root .env
if [ -f "../../.env" ]; then
    export $(cat ../../.env | grep -v '^#' | xargs)
fi

# Use BACKEND_PORT from .env, default to 8003 if not set
PORT=${BACKEND_PORT:-8003}

# Use DATABASE_URL from apps/api/.env if it exists
if [ -f ".env" ]; then
    export $(cat .env | grep DATABASE_URL | xargs)
fi

echo "Starting FastAPI server on port $PORT..."
uvicorn src.main:app --host 0.0.0.0 --port $PORT --reload
