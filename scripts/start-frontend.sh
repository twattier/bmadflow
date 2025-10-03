#!/bin/bash
cd "$(dirname "$0")/../apps/web"
exec npx vite --host 0.0.0.0 --port "${1:-5173}"
