# BMADFlow Quick Start Guide

## Database Setup and Seeding

### 1. Start PostgreSQL Database

```bash
docker-compose up -d db
```

### 2. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 3. Seed Initial Data & Sync Documentation

```bash
# From backend directory - this will seed AND automatically sync docs
python3 scripts/seed_database.py seed_data.yaml

# Optional: Skip auto-sync if you just want to test database structure
python3 scripts/seed_database.py seed_data.yaml --no-sync
```

This will:
1. Create **Project**: BMADFlow
2. Create **ProjectDoc**: Project Documentation (https://github.com/twattier/bmadflow.git, docs folder)
3. **Automatically sync all documentation from GitHub** (downloads ~40+ files)

Expected output:
```
✓ Created project BMADFlow (ID: xxx)
✓ Created project doc Project Documentation (ID: yyy)

📥 Starting documentation sync...
  ✓ Sync completed: 42 files synced in 8.5s

✅ All operations completed!
```

### 4. Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Verify Data (Optional)

Check that documentation was synced:

```bash
# Get sync status
curl http://localhost:8000/api/project-docs/{project_doc_id}/sync-status

# Expected response:
# {"status": "completed", "message": "Sync completed successfully. 42 files synced.", ...}
```

### 6. Access API Documentation

Open http://localhost:8000/docs for interactive API documentation.

## Custom Seed Data

Edit `backend/seed_data.yaml` to add your own projects:

```yaml
project:
    name: Your Project Name
    description: Your project description
    project_docs:
        - name: Documentation Name
          description: Description of this doc source
          github_url: https://github.com/user/repo.git
          github_folder_path: docs  # Optional
        - name: Another Doc Source
          github_url: https://github.com/user/another-repo.git
```

## Available Endpoints

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Project Docs
- `GET /api/projects/{project_id}/docs` - List project docs
- `POST /api/projects/{project_id}/docs` - Create project doc
- `GET /api/project-docs/{id}` - Get project doc details
- `PUT /api/project-docs/{id}` - Update project doc
- `DELETE /api/project-docs/{id}` - Delete project doc
- **`POST /api/project-docs/{id}/sync`** - Trigger GitHub sync
- **`GET /api/project-docs/{id}/sync-status`** - Check sync status

### Health
- `GET /api/health` - Health check

## Environment Variables

Create `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://bmadflow:bmadflow@localhost:5432/bmadflow
GITHUB_TOKEN=your_github_token_here  # Optional, for higher rate limits
```

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running: `docker-compose ps`
- Check connection string in `.env`

### Seed Script Error
- Verify YAML syntax: `python3 -c "import yaml; yaml.safe_load(open('seed_data.yaml'))"`
- Check database is accessible: `psql $DATABASE_URL -c "SELECT 1"`

### Sync Fails
- Check GitHub token: `echo $GITHUB_TOKEN`
- Verify repository URL is accessible
- Check API logs: `tail -f backend/logs/app.log`
