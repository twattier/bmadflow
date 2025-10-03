# Quick Start Guide - Story 3.2 Testing

## Required: Open Two Terminal Windows

### Terminal 1: Backend API (Port 8003)

```bash
cd /home/wsluser/dev/bmad-test/bmad-flow/apps/api
./start.sh
```

**Expected Output:**
```
Starting FastAPI server on port 8003...
INFO:     Uvicorn running on http://0.0.0.0:8003 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Terminal 2: Frontend Dev Server (Port 5173)

```bash
cd /home/wsluser/dev/bmad-test/bmad-flow/apps/web
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://xxx.xxx.xxx.xxx:5173/
  ➜  press h + enter to show help
```

## Test the Detail View

Once both servers are running, open in your browser:

**http://localhost:5173/detail/f068fbff-0f4e-466d-bd53-9e13412a9308**

## Verify Configuration

Backend reads from `.env`:
- ✅ `BACKEND_PORT=8003`
- ✅ `FRONTEND_PORT=5173`
- ✅ `DATABASE_URL` from `apps/api/.env`

Frontend proxies to backend:
- ✅ `/api/*` → `http://localhost:8003/api/*`

## Troubleshooting

### Error: "ERR_CONNECTION_REFUSED"
- Make sure **both** servers are running in separate terminals
- Check that backend shows "Application startup complete"
- Check that frontend shows "ready in xxx ms"

### Error: Backend won't start
- Verify PostgreSQL is running: `docker ps | grep postgres`
- Check database connection in `apps/api/.env`

### Error: Port already in use
- Check what's using the port: `lsof -i :8003` or `lsof -i :5173`
- Kill the process: `kill -9 <PID>`
- Or change ports in `.env` file
