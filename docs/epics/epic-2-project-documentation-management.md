# Epic 2: Project & Documentation Management

## Epic Goal

Enable users to create Projects and configure ProjectDocs linked to GitHub repositories, sync documentation files to local storage with status tracking, and view sync history. This epic establishes the core data model and GitHub integration.

## Stories

### Story 2.1: Create Project Database Schema and API

**As a** user,
**I want** to create and manage Projects,
**so that** I can organize my BMAD documentation by initiative.

**Acceptance Criteria:**
1. Alembic migration creates `projects` table with fields: id (UUID), name (string), description (text), created_at, updated_at
2. SQLAlchemy model defined for Project with proper relationships
3. REST API endpoints implemented:
   - `POST /api/projects` - Create project (validates name required)
   - `GET /api/projects` - List all projects
   - `GET /api/projects/{id}` - Get project by ID
   - `PUT /api/projects/{id}` - Update project
   - `DELETE /api/projects/{id}` - Delete project (cascade deletes related ProjectDocs)
4. OpenAPI documentation generated for all endpoints
5. Unit tests for Project model and API endpoints (pytest)
6. Integration tests verify database operations

---

### Story 2.2: Create ProjectDoc Database Schema and API

**As a** user,
**I want** to configure ProjectDocs linked to GitHub repositories,
**so that** I can sync documentation from specific repos into my Projects.

**Acceptance Criteria:**
1. Alembic migration creates `project_docs` table with fields: id (UUID), project_id (FK to projects), name, description, github_url, github_folder_path, last_synced_at, last_github_commit_date, created_at, updated_at
2. SQLAlchemy model defined for ProjectDoc with relationship to Project
3. GitHub URL validation logic: must be valid GitHub repo URL format
4. REST API endpoints implemented:
   - `POST /api/projects/{project_id}/docs` - Create ProjectDoc (validates GitHub URL)
   - `GET /api/projects/{project_id}/docs` - List ProjectDocs for a Project
   - `GET /api/project-docs/{id}` - Get ProjectDoc by ID
   - `PUT /api/project-docs/{id}` - Update ProjectDoc
   - `DELETE /api/project-docs/{id}` - Delete ProjectDoc
5. Unit tests for ProjectDoc model and API endpoints
6. Integration tests verify cascade deletes when Project is deleted

---

### Story 2.3: Implement GitHub API Integration for File Listing

**As a** developer,
**I want** to fetch file listings from GitHub repositories,
**so that** I can identify documentation files to sync.

**Acceptance Criteria:**
1. GitHub API client implemented using requests library with authentication support
2. Optional GitHub Personal Access Token via environment variable `GITHUB_TOKEN` (5000 req/hr authenticated, 60 req/hr unauthenticated)
3. Token validation on backend startup: log warning if `GITHUB_TOKEN` not set, recommend for production use
4. Function to fetch repository tree recursively for specified folder path
5. Filter files by supported extensions: .md, .csv, .yaml, .yml, .json, .txt
6. GitHub rate limit detection: parse `X-RateLimit-Remaining` and `X-RateLimit-Limit` headers
7. Exponential backoff retry logic when rate limit approached (< 5 remaining)
8. Clear error messages when rate limit exceeded (show time until reset from `X-RateLimit-Reset` header, suggest adding token if unauthenticated)
9. Unit tests with mocked GitHub API responses (both authenticated and unauthenticated modes)
10. Integration test with real public GitHub repo (e.g., AgentLab sample repo)
11. `.env.example` updated with `GITHUB_TOKEN=` (commented with instructions)
12. Documentation: README section "GitHub API Rate Limits" with instructions to create Personal Access Token

**Dev Notes:**
- Use `Authorization: Bearer {token}` header when `GITHUB_TOKEN` is set
- Unauthenticated: 60 requests/hour, Authenticated: 5000 requests/hour
- Token scopes required: `public_repo` (for public repos only, no sensitive scopes needed for POC)
- Log current rate limit on startup: "GitHub API: {remaining}/{limit} requests remaining"

---

### Story 2.4: Implement Documentation File Download and Storage

**As a** user,
**I want** documentation files downloaded from GitHub and stored locally,
**so that** I can access them without internet connectivity.

**Acceptance Criteria:**
1. Alembic migration creates `documents` table: id (UUID), project_doc_id (FK with ON DELETE CASCADE), file_path, file_name, file_type (enum: markdown, csv, yaml, json, txt), content (BLOB), file_size_bytes, github_commit_sha, created_at, updated_at
2. Function to download file content from GitHub (raw content URL, uses GitHub token if available)
3. Function to store file content in PostgreSQL BLOB storage
4. Track GitHub commit SHA for each file (for future change detection)
5. Progress tracking: log each file being processed
6. Error handling: continue sync if individual file fails, log errors
7. Unit tests for file download and storage logic
8. Integration test: sync sample repo with 10+ files, verify all stored in database
9. Integration test: delete ProjectDoc, verify all associated documents cascade deleted

---

### Story 2.5: Build Sync Orchestration and Status Tracking

**As a** user,
**I want** to trigger manual sync for a ProjectDoc with progress feedback,
**so that** I can update my local documentation with latest from GitHub.

**Acceptance Criteria:**
1. REST API endpoint `POST /api/project-docs/{id}/sync` triggers sync operation
2. Sync operation executes in background (async or Celery worker - simple async acceptable for POC)
3. Sync process:
   - Fetch repository file tree from GitHub
   - Download all supported file types
   - Store in documents table (update if exists, insert if new)
   - Update `last_synced_at` timestamp on ProjectDoc
   - Fetch and store `last_github_commit_date` for folder path
4. REST API endpoint `GET /api/project-docs/{id}/sync-status` returns sync progress
5. Frontend displays spinner during sync with "Syncing..." message
6. Frontend displays success toast notification when sync completes
7. Frontend displays error message with retry button if sync fails
8. Unit tests for sync orchestration logic
9. Integration test: trigger sync via API, verify all files downloaded and stored

---

### Story 2.6: Display Sync Status in UI

**As a** user,
**I want** to see sync status indicators for each ProjectDoc,
**so that** I know which documentation is up-to-date.

**Acceptance Criteria:**
1. Frontend fetches ProjectDoc list with sync metadata (last_synced_at, last_github_commit_date)
2. Sync status badge displayed on ProjectDoc cards:
   - Green badge "✓ Up to date" if last_synced_at >= last_github_commit_date
   - Yellow badge "⚠ Needs update" if last_synced_at < last_github_commit_date
   - Gray badge "Not synced" if last_synced_at is null
   - Red badge "⚠ Source unavailable" if GitHub API returns 404/403 when checking commit date
3. Display last sync time in human-readable format ("2 hours ago", "1 day ago")
4. "Sync" button on each ProjectDoc card triggers sync operation
5. Button shows spinner and disables during sync operation
6. Success/error toast notifications after sync completes
7. UI refreshes sync status after successful sync
8. Error tooltip for "Source unavailable" badge explains: "GitHub repository not accessible. Check URL or permissions."

---

### Story 2.7: Build Projects List and Project Overview UI

**As a** user,
**I want** to view all my Projects and select one to see its details,
**so that** I can navigate to the documentation I need.

**Acceptance Criteria:**
1. Projects page displays grid of Project cards (shadcn/ui Card component)
2. Each card shows: Project name, description (truncated), number of ProjectDocs, "View" button
3. "+ New Project" card opens dialog to create Project
4. Project Overview page shows: Project name, description (full), list of ProjectDocs as cards
5. Each ProjectDoc card shows: name, description, GitHub URL link, sync status badge, "Sync" button
6. "+ Add ProjectDoc" button opens dialog to create ProjectDoc
7. Sidebar navigation updates when Project selected (shows Project context: Overview, Explorer, Chat, Settings)
8. Breadcrumb updates: "Projects > [Project Name] > Overview"
9. Empty state displayed when no Projects exist: "No projects yet. Create your first project to get started."
10. Empty state displayed when Project has no ProjectDocs: "No documentation sources configured. Add a ProjectDoc to sync documentation from GitHub."

---

## Progress Tracking

| Story | Status | Completed |
|-------|--------|-----------|
| 2.1: Create Project Database Schema and API | ✅ Done | 2025-10-07 |
| 2.2: Create ProjectDoc Database Schema and API | ✅ Done | 2025-10-07 |
| 2.3: Implement GitHub API Integration | ✅ Done | 2025-10-07 |
| 2.4: Implement Documentation File Download and Storage | 🔲 Not Started | - |
| 2.5: Build Sync Orchestration and Status Tracking | 🔲 Not Started | - |
| 2.6: Build ProjectDoc Configuration UI | 🔲 Not Started | - |
| 2.7: Build Projects List and Project Overview UI | 🔲 Not Started | - |

**Epic Progress**: 3/7 stories complete (43%)

---

## Definition of Done

- [ ] All 7 stories completed with acceptance criteria met
- [x] Users can create Projects and ProjectDocs via API (Stories 2.1, 2.2)
- [ ] Users can create Projects and ProjectDocs via UI (Story 2.7)
- [ ] GitHub sync functionality working end-to-end (Stories 2.3, 2.4, 2.5) - 33% complete (Story 2.3 ✅)
- [ ] Sync status indicators accurate and real-time (Stories 2.5, 2.6)
- [x] All API endpoints documented in OpenAPI/Swagger (Stories 2.1, 2.2)
- [x] Unit and integration tests passing (Stories 2.1, 2.2, 2.3)
- [x] GitHub API integration with rate limiting (Story 2.3)
- [ ] UI follows shadcn/ui design system (Stories 2.6, 2.7)
- [ ] Empty states provide helpful guidance (Story 2.7)
