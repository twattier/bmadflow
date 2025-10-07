# Database Seeding Scripts

## seed_database.py

Seeds the database with projects and project docs from a YAML configuration file, then **automatically syncs the documentation from GitHub**.

**Features:**
- ✅ **Idempotent**: Safe to run multiple times - won't create duplicate projects or docs
- ✅ **Authenticated GitHub API**: Uses GITHUB_TOKEN from .env for 5000 requests/hour
- ✅ **Clear option**: Fresh start by deleting all existing data
- ✅ **Skip sync option**: Faster seeding when you only need database structure

### Usage

```bash
# From backend directory - seeds AND syncs documentation automatically
python3 scripts/seed_database.py seed_data.yaml

# Safe to run multiple times (idempotent - no duplicates)
python3 scripts/seed_database.py seed_data.yaml

# Clear all existing data before seeding (fresh start)
python3 scripts/seed_database.py seed_data.yaml --clear

# Seed only, skip sync (for testing or when GitHub is unreachable)
python3 scripts/seed_database.py seed_data.yaml --no-sync

# Combine flags
python3 scripts/seed_database.py seed_data.yaml --clear --no-sync

# Show help
python3 scripts/seed_database.py --help
```

### Options

- `--no-sync` - Skip automatic documentation sync after seeding. Useful for testing database structure without making GitHub API calls.
- `--clear` - Clear all existing data (projects, project_docs, documents) before seeding. Use for a fresh start.

### YAML Format

```yaml
project:
    name: Project Name
    description: Optional project description
    project_docs:
        - name: Documentation Name
          description: Optional doc description
          github_url: https://github.com/user/repo.git
          github_folder_path: docs  # Optional, defaults to root
        - name: Another Doc Source
          github_url: https://github.com/user/another-repo.git
```

### Example

See `../seed_data.yaml` for a complete example with the BMADFlow project.

### Prerequisites

1. PostgreSQL database running (via `docker-compose up -d db`)
2. Database migrations applied (`alembic upgrade head`)
3. Environment variables configured (`.env` file with `DATABASE_URL`)

### What it does

1. Creates a Project with the specified name and description
2. Creates one or more ProjectDoc entries linked to the project
3. **Automatically syncs documentation from GitHub** for each ProjectDoc:
   - Fetches repository file tree
   - Downloads all supported files (.md, .yaml, .json, .csv, .txt)
   - Stores content in documents table
   - Updates sync timestamps
4. Shows detailed progress and statistics for each sync

### Output Example

```
2025-10-07 10:15:00 - INFO - Creating project: BMADFlow
2025-10-07 10:15:00 - INFO - ✓ Created project BMADFlow (ID: xxx)
2025-10-07 10:15:00 - INFO - ✓ Created project doc Project Documentation (ID: yyy)

📥 Starting documentation sync...

  Syncing: Project Documentation
  Repository: https://github.com/twattier/bmadflow.git
  Folder: docs
  ✓ Sync completed: 42 files synced in 8.5s

✅ All operations completed!
```

### Manual Sync

If you used `--no-sync`, you can trigger sync manually:

```bash
# Get the project_doc_id from the script output, then:
curl -X POST http://localhost:8000/api/project-docs/{project_doc_id}/sync

# Check sync status:
curl http://localhost:8000/api/project-docs/{project_doc_id}/sync-status
```

### Error Handling

The script will:
- Validate YAML format before processing
- Check for required fields (name, github_url)
- Roll back all changes if any error occurs
- Log detailed error messages for debugging
