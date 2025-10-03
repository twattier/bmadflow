#!/bin/bash
cd "$(dirname "$0")/../apps/api"
exec python3 -m uvicorn src.main:app --reload --host 0.0.0.0 --port "${1:-8003}"
