# Manual Testing Guide - Story 3.2: Detail View

## Prerequisites

1. **Database**: PostgreSQL running on port configured in `.env` (default: 5434)
2. **Test Data**: Document ID `f068fbff-0f4e-466d-bd53-9e13412a9308` already inserted

## Starting the Development Servers

Both servers read port configuration from `.env` file.

### Terminal 1: Start Backend API

```bash
cd /home/wsluser/dev/bmad-test/bmad-flow/apps/api
./start.sh
```

This will:
- Read `BACKEND_PORT` from root `.env` (default: 8003)
- Read `DATABASE_URL` from `apps/api/.env`
- Start FastAPI with hot-reload on configured port

### Terminal 2: Start Frontend

```bash
cd /home/wsluser/dev/bmad-test/bmad-flow/apps/web
npm run dev
```

This will:
- Read `FRONTEND_PORT` from root `.env` (default: 5173)
- Proxy `/api` requests to `http://localhost:${BACKEND_PORT}`
- Start Vite dev server with hot-reload

## Test URLs

### 1. Detail View with Test Document
**URL**: http://localhost:5173/detail/f068fbff-0f4e-466d-bd53-9e13412a9308

**Expected Result**: Document content renders with:
- ✅ Markdown formatting (headers, lists, tables)
- ✅ Syntax highlighting for 8 code languages
- ✅ Copy-to-clipboard buttons on code blocks
- ✅ Proper typography and spacing
- ✅ Responsive layout (max-width 1280px)
- ✅ XSS protection (malicious scripts blocked)

### 2. Loading State
**URL**: http://localhost:5173/detail/f068fbff-0f4e-466d-bd53-9e13412a9308

**Test**: Throttle network in DevTools to "Slow 3G"

**Expected Result**: Loading skeleton appears while fetching

### 3. Error State
**URL**: http://localhost:5173/detail/00000000-0000-0000-0000-000000000000

**Expected Result**: Red error card with "Failed to load document" message

## Story 3.2 Acceptance Criteria Checklist

- [ ] **AC1**: Document fetched from GET /api/documents/{id}
- [ ] **AC2**: GitHub Flavored Markdown rendered correctly
- [ ] **AC3**: Syntax highlighting works for TypeScript, Python, JavaScript, YAML, JSON, Bash, SQL, Markdown
- [ ] **AC4**: Copy-to-clipboard functionality on all code blocks
- [ ] **AC5**: Proper typography (max-width 1280px, 90% on tablet, 100% on mobile)
- [ ] **AC6**: XSS sanitization blocks malicious scripts
- [ ] **AC7**: Performance <2 seconds for 5000+ word document
- [ ] **AC8**: Responsive design works on desktop/tablet/mobile
- [ ] **AC9**: Loading skeleton displays during fetch

## Test Document Content

The test document (`f068fbff-0f4e-466d-bd53-9e13412a9308`) includes:

1. **Headers**: H1, H2, H3 with proper styling
2. **Code Blocks**: All 8 supported languages with syntax highlighting
3. **Lists**: Ordered and unordered lists
4. **Tables**: GitHub Flavored Markdown table
5. **Links**: Internal and external links
6. **XSS Test**: Malicious script tags (should be sanitized)
7. **Blockquotes**: Styled blockquotes
8. **Inline Code**: Styled inline code elements

## Configuration Notes

### Port Configuration (.env)
```bash
FRONTEND_PORT=5173  # Vite dev server
BACKEND_PORT=8003   # FastAPI server
POSTGRES_PORT=5434  # PostgreSQL host port
```

### Changing Ports
If you need to use different ports:
1. Update `.env` file in project root
2. Restart both servers
3. Both frontend and backend will automatically use new ports

### CORS Configuration
Backend CORS is configured to accept requests from `http://localhost:${FRONTEND_PORT}` based on `.env`.
