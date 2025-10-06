# Epic 6: Dashboard & Configuration

## Epic Goal

Build the dashboard with project metrics and activity feed, global LLM configuration UI, and keyboard shortcuts for power users.

## Stories

### Story 6.1: Build Dashboard Metrics API

**As a** developer,
**I want** API endpoints for dashboard metrics,
**so that** the UI can display statistics.

**Acceptance Criteria:**
1. REST API endpoint `GET /api/dashboard/metrics` returns:
   - total_projects (count)
   - total_documents (count)
   - total_embeddings (count)
   - total_conversations (count)
2. REST API endpoint `GET /api/dashboard/activity` returns recent sync operations (last 10):
   - project_name, project_doc_name, synced_at (timestamp), file_count, status (success/error)
3. Activity feed includes timestamp in human-readable format
4. Unit tests for metrics calculation

---

### Story 6.2: Build Dashboard UI

**As a** user,
**I want** to see an overview dashboard with metrics and recent activity,
**so that** I can understand system status at a glance.

**Acceptance Criteria:**
1. Dashboard page is default route when app loads
2. Three metric cards displayed horizontally: Total Projects, Total Doc Files, Total Chunks
3. Each card shows metric value (large font) and label
4. Recent Activity section displays list of last 10 sync operations
5. Activity list shows: Project name, ProjectDoc name, timestamp, status icon (green check or red X)
6. Empty state: "No activity yet. Create a project and sync documentation to get started."
7. Dashboard accessible from sidebar "Dashboard" link
8. Breadcrumb shows "Dashboard"

---

### Story 6.3: Build Global Configuration UI

**As a** user,
**I want** to view and manage LLM providers in a configuration page,
**so that** I can control which models are available for chat.

**Acceptance Criteria:**
1. Configuration page accessible from sidebar "Configuration" link
2. Table displays configured LLM providers: Provider, Model Name, Default (checkbox)
3. "+ Add Model" button opens dialog with form:
   - Provider dropdown (OpenAI, Google Gemini, LiteLLM, Ollama)
   - Model name input
   - Set as default checkbox
4. Form validation: provider and model name required
5. Save creates LLM provider via API
6. Setting default unchecks previous default
7. Delete button on each row (confirmation dialog)
8. Empty state: "No LLM providers configured. Add your first model to enable chat functionality."
9. Note displayed: "API credentials configured via environment variables (.env file)"

---

### Story 6.4: Implement Keyboard Shortcuts

**As a** user,
**I want** keyboard shortcuts for common actions,
**so that** I can navigate efficiently.

**Acceptance Criteria:**
1. Keyboard shortcuts implemented:
   - `Ctrl+K` or `Cmd+K`: Focus search/navigation input
   - `Ctrl+N` or `Cmd+N`: New conversation (when on Chat page)
   - `Ctrl+/` or `Cmd+/`: Show keyboard shortcuts help overlay
   - `Esc`: Close modals/panels/overlays
2. Shortcuts work globally across application
3. Help overlay displays all shortcuts when triggered
4. Visual indicator shown when shortcut triggered (brief flash or animation)
5. Shortcuts documented in README.md

---

### Story 6.5: Implement Empty States and Contextual Help

**As a** user,
**I want** helpful guidance when I'm new to the platform,
**so that** I understand how to get started.

**Acceptance Criteria:**
1. All major screens have empty states with clear next actions (implemented in previous stories)
2. Tooltips added to key UI elements:
   - Sync button: "Fetch latest documentation from GitHub"
   - LLM dropdown: "Select which AI model to use for this conversation"
   - Source link: "View source document in side panel"
3. First-time user flow: Dashboard shows "Welcome to BMADFlow" card with steps:
   - Step 1: Create a Project
   - Step 2: Add ProjectDoc and sync from GitHub
   - Step 3: Explore documentation or chat with AI
4. Welcome card dismissible (hidden after first Project created)
5. Help icon in top header opens help overlay (keyboard shortcuts)

---

## Definition of Done

- [ ] All 5 stories completed with acceptance criteria met
- [ ] Dashboard displays metrics and recent activity feed
- [ ] Configuration page allows LLM provider management
- [ ] Keyboard shortcuts implemented for common actions
- [ ] Empty states provide helpful onboarding guidance
- [ ] Welcome card guides first-time users
- [ ] All API endpoints documented in OpenAPI/Swagger
- [ ] Unit and integration tests passing
- [ ] UI follows shadcn/ui design system
- [ ] Help overlay documents all keyboard shortcuts
