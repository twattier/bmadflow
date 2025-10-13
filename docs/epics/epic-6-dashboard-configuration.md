# Epic 6: Dashboard & Configuration

**Status**: 🚧 **READY FOR DEVELOPMENT**
**Last Updated**: 2025-10-14
**Pre-Development Review**: ✅ Complete (95/100 readiness score)
**Dependencies**: Epic 5 Complete (✅), Epic 4 Complete (✅), Epic 2 Complete (✅)

---

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
3. Activity feed includes timestamp in ISO 8601 format (2025-10-14T12:34:56Z)
4. Unit tests for metrics calculation (>70% coverage)
5. Integration tests for both API endpoints with real database queries

**Dev Notes:**

**Activity Feed Implementation (POC Simplified Approach):**
- Query `project_docs` table for last 10 synced ProjectDocs
- SQL approach:
  ```sql
  SELECT
    p.name as project_name,
    pd.name as project_doc_name,
    pd.last_synced_at as synced_at,
    COUNT(d.id) as file_count
  FROM project_docs pd
  JOIN projects p ON pd.project_id = p.id
  LEFT JOIN documents d ON d.project_doc_id = pd.id
  WHERE pd.last_synced_at IS NOT NULL
  GROUP BY p.name, pd.name, pd.last_synced_at
  ORDER BY pd.last_synced_at DESC
  LIMIT 10
  ```
- Status: Always 'success' (no error tracking in POC - acceptable limitation)
- File count: Join with documents table (COUNT(*) GROUP BY project_doc_id)
- Timestamp format: ISO 8601 (backend), frontend formats to relative time ("2 hours ago")

**Backend Architecture (Follow Epic 4-5 Patterns):**
```python
app/
├── api/routes/dashboard.py       # GET /dashboard/metrics, GET /dashboard/activity
├── services/dashboard_service.py # Business logic for metrics calculation
├── repositories/
│   └── dashboard_repository.py   # Database queries for metrics + activity
└── schemas/dashboard.py          # DashboardMetrics, ActivityFeed Pydantic models
```

**Testing:**
- Unit tests: Mock repository, test service logic (metrics calculation)
- Integration tests: Use FastAPI dependency override pattern (Epic 5 Story 5.1 learning)
- Target: >70% coverage (Epic 4-5 standard)

**Technical Notes:**
- Use SQLAlchemy `func.count()` for aggregations
- Activity feed may return <10 items if fewer ProjectDocs synced
- Timestamps use `func.now()` server-side (Epic 5 Story 5.3 learning)

**Post-MVP Enhancement:**
- Create `sync_logs` table to track individual sync operations with error messages
- Enable filtering/search in activity feed

---

### Story 6.2: Build Dashboard UI

**As a** user,
**I want** to see an overview dashboard with metrics and recent activity,
**so that** I can understand system status at a glance.

**Acceptance Criteria:**
1. Dashboard page is default route when app loads (`/`)
2. Three metric cards displayed horizontally: Total Projects, Total Doc Files, Total Chunks
3. Each card shows metric value (large font) and label
4. Recent Activity section displays list of last 10 sync operations
5. Activity list shows: Project name, ProjectDoc name, timestamp (relative format: "2 hours ago"), status icon (green check)
6. Empty state: "No activity yet. Create a project and sync documentation to get started."
7. Dashboard accessible from sidebar "Dashboard" link
8. Breadcrumb shows "Dashboard"
9. Component tests for MetricCard and ActivityFeed components
10. Welcome card integration (see Story 6.5) - card replaces empty state on first visit

**Dev Notes:**

**Component Architecture:**
```tsx
frontend/src/
├── pages/
│   └── Dashboard.tsx              # Page orchestration, API calls
├── features/dashboard/
│   ├── MetricCard.tsx             # Reusable metric display card
│   ├── ActivityFeed.tsx           # Activity list with status icons
│   └── WelcomeCard.tsx            # First-time user guidance (Story 6.5)
```

**API Integration:**
- Use React Query hooks (Epic 3-5 pattern)
- `useDashboardMetrics()` → `GET /api/dashboard/metrics`
- `useDashboardActivity()` → `GET /api/dashboard/activity`
- Loading states: shadcn/ui Skeleton components
- Error states: shadcn/ui Alert component

**UI Components (shadcn/ui):**
- MetricCard: Use `Card`, `CardHeader`, `CardContent` from shadcn/ui
- ActivityFeed: Use `ScrollArea` for scrollable list
- Status icon: Use `CheckCircle2` icon from Lucide React (green for success)
- Timestamp: Use `date-fns` `formatDistanceToNow()` for relative time (Epic 5 Story 5.6 pattern)

**Empty State vs Welcome Card:**
- First visit + no projects: Show Welcome card (Story 6.5)
- Has projects + no activity: Show empty state (AC#6)

**Testing:**
- Component tests: React Testing Library
- Test metric card rendering with mock data
- Test activity feed with various states (empty, loading, populated)
- Test relative timestamp formatting

**Technical Notes:**
- Follow Epic 5 accessibility patterns (WCAG 2.1 AA compliance)
- Use React.memo() for performance (MetricCard, ActivityFeed)
- Mobile-responsive: Stack metric cards vertically on small screens

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
10. Component tests for LLMProviderTable and AddProviderDialog components

**Dev Notes:**

**Backend API Status: ✅ COMPLETE**
- Epic 5 Story 5.1 already implemented full backend
- API endpoints ready: `GET /api/llm-providers`, `POST /api/llm-providers`, `PUT /api/llm-providers/{id}`, `DELETE /api/llm-providers/{id}`, `PUT /api/llm-providers/{id}/set-default`
- Test coverage: 25/25 tests passing, 94% coverage
- Seed script creates default Ollama provider (llama3)

**This is a Pure Frontend Story** - Backend fully implemented, just needs UI wrapper

**Component Architecture:**
```tsx
frontend/src/
├── pages/
│   └── Configuration.tsx           # Page with table + add button
├── features/configuration/
│   ├── LLMProviderTable.tsx        # Table with edit/delete actions
│   └── AddProviderDialog.tsx       # Form dialog for create
```

**API Integration:**
- Use React Query hooks (Epic 3-5 pattern)
- `useLLMProviders()` → `GET /api/llm-providers`
- `useCreateLLMProvider()` → `POST /api/llm-providers`
- `useUpdateLLMProvider()` → `PUT /api/llm-providers/{id}`
- `useDeleteLLMProvider()` → `DELETE /api/llm-providers/{id}`
- `useSetDefaultProvider()` → `PUT /api/llm-providers/{id}/set-default`
- Optimistic updates + cache invalidation on mutations

**UI Components (shadcn/ui):**
- Table: Use `Table`, `TableHeader`, `TableBody`, `TableRow` from shadcn/ui
- Add button: Use `Button` with `Plus` icon from Lucide React
- Dialog: Use `Dialog`, `DialogContent`, `DialogHeader`, `DialogTitle`, `DialogDescription`
- Form: Use `Form`, `Select`, `Input`, `Checkbox` from shadcn/ui
- Delete confirmation: Use `AlertDialog` from shadcn/ui

**Form Validation:**
- Use React Hook Form + Zod schema (Epic 2 pattern)
- Provider required, model_name required
- Default checkbox optional (default: false)

**Testing:**
- Component tests: React Testing Library
- Test table rendering with mock providers
- Test add dialog form submission
- Test delete confirmation dialog
- Test default checkbox toggle (unchecks previous default)

**Technical Notes:**
- Follow Epic 5 accessibility patterns (DialogDescription required for WCAG 2.1 AA)
- Reuse form patterns from Epic 2 (CreateProjectDialog, CreateProjectDocDialog)
- Empty state uses same pattern as Epic 2-5

**Estimated Effort:** 4 hours (fastest story - backend complete)

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
3. Help overlay displays all shortcuts in shadcn/ui Dialog with table layout
4. Visual indicator: Toast notification shows shortcut action ("Search focused", "New conversation")
5. Shortcuts documented in README.md
6. [P0] Shortcuts disabled when activeElement is input/textarea/contenteditable (prevents conflicts)
7. [P0] Shortcuts work in modals/dialogs (except when typing in form fields)
8. [P1] Integration tests for all 4 shortcuts + conflict handling

**Dev Notes:**

**Implementation Approach:**
- Use `react-hotkeys-hook` library for clean hook-based API
- Install: `npm install react-hotkeys-hook`
- Register shortcuts at AppShell level for global scope
- Pass `enableOnFormTags: false` to prevent conflicts with input fields

**Architecture:**
```tsx
frontend/src/
├── hooks/
│   └── useKeyboardShortcuts.ts    # Global shortcut registration
├── components/
│   └── KeyboardShortcutsDialog.tsx # Help overlay (Ctrl+/)
└── layouts/
    └── AppShell.tsx               # Call useKeyboardShortcuts() here
```

**Example Implementation:**
```tsx
// hooks/useKeyboardShortcuts.ts
import { useHotkeys } from 'react-hotkeys-hook';
import { useToast } from '@/components/ui/use-toast';
import { useNavigate } from 'react-router-dom';

export function useKeyboardShortcuts(searchInputRef: RefObject<HTMLInputElement>) {
  const { toast } = useToast();
  const navigate = useNavigate();

  // Ctrl+K: Focus search
  useHotkeys('ctrl+k, cmd+k', (e) => {
    e.preventDefault();
    if (document.activeElement?.tagName === 'INPUT') return; // Prevent conflict
    searchInputRef.current?.focus();
    toast({ description: 'Search focused' });
  }, { enableOnFormTags: false });

  // Ctrl+N: New conversation (only on Chat page)
  useHotkeys('ctrl+n, cmd+n', (e) => {
    e.preventDefault();
    if (window.location.pathname.includes('/chat')) {
      navigate('/projects/:id/chat'); // Reset to new conversation
      toast({ description: 'New conversation' });
    }
  }, { enableOnFormTags: false });

  // Ctrl+/: Show help overlay
  useHotkeys('ctrl+/, cmd+/', (e) => {
    e.preventDefault();
    setShowHelpDialog(true);
  }, { enableOnFormTags: false });

  // Esc: Close modals (handled by shadcn/ui Dialog by default)
}
```

**Help Overlay (Ctrl+/):**
- Use shadcn/ui `Dialog`, `DialogContent`, `DialogHeader`, `DialogTitle`, `DialogDescription`
- Display shortcuts in `Table` component:
  | Shortcut | Action |
  |----------|--------|
  | Ctrl+K / Cmd+K | Focus search |
  | Ctrl+N / Cmd+N | New conversation (Chat page) |
  | Ctrl+/ / Cmd+/ | Show keyboard shortcuts |
  | Esc | Close modals/panels |

**Visual Feedback:**
- Use shadcn/ui `useToast()` hook to show toast notification
- Toast duration: 2000ms (2 seconds)
- Toast position: bottom-right
- Toast style: Default (not destructive)

**Conflict Handling:**
- `enableOnFormTags: false` prevents shortcuts in input/textarea/select
- Additional check: `if (document.activeElement?.tagName === 'INPUT') return;`
- Esc key closes modals (built into shadcn/ui Dialog, no custom code needed)

**Testing:**
- Component tests: Test useKeyboardShortcuts hook with mock refs
- Integration tests: Test all 4 shortcuts fire correctly
- Conflict tests: Verify shortcuts disabled when typing in input field
- Modal tests: Verify Esc closes Dialog components
- Expected: 8-12 tests total

**Technical Notes:**
- Follow Epic 5 accessibility patterns (DialogDescription required)
- README.md update: Add "Keyboard Shortcuts" section with table
- Works cross-platform (Ctrl on Windows/Linux, Cmd on macOS)

**Accessibility:**
- Keyboard shortcuts enhance accessibility for power users
- Help overlay accessible via keyboard (Ctrl+/)
- All shortcuts documented in help overlay + README

**Estimated Effort:** 6 hours

---

### Story 6.5: Implement Empty States and Contextual Help

**As a** user,
**I want** helpful guidance when I'm new to the platform,
**so that** I understand how to get started.

**Acceptance Criteria:**
1. All major screens have empty states with clear next actions (implemented in previous stories)
2. Tooltips added to key UI elements using shadcn/ui Tooltip component:
   - Sync button: "Fetch latest documentation from GitHub"
   - LLM dropdown: "Select which AI model to use for this conversation"
   - Source link: "View source document in side panel"
3. First-time user flow: Dashboard shows "Welcome to BMADFlow" card with steps:
   - Step 1: Create a Project
   - Step 2: Add ProjectDoc and sync from GitHub
   - Step 3: Explore documentation or chat with AI
4. Welcome card dismissible (hidden after first Project created)
5. Help icon in top header opens help overlay (keyboard shortcuts from Story 6.4)
6. Component tests for WelcomeCard and tooltip interactions

**Dev Notes:**

**Welcome Card Persistence:**
- Store dismissal in localStorage:
  - Key: `'bmadflow_welcome_dismissed'`
  - Value: `'true'` when dismissed, `null` otherwise
- Check on Dashboard mount:
  ```tsx
  const dismissed = localStorage.getItem('bmadflow_welcome_dismissed') === 'true';
  const { data: projects } = useProjects();
  const showWelcome = !dismissed && (projects?.length === 0);
  ```
- Dismiss when:
  - User clicks "X" button on Welcome card, OR
  - User creates first Project (auto-dismiss)

**Welcome Card Display Logic:**
```tsx
// Dashboard.tsx
const dismissed = localStorage.getItem('bmadflow_welcome_dismissed') === 'true';
const { data: projects } = useProjects();
const { data: activity } = useDashboardActivity();

// Show Welcome card if: not dismissed AND no projects exist
const showWelcome = !dismissed && (projects?.length === 0);

// Show activity empty state if: has projects BUT no activity
const showActivityEmpty = (projects?.length > 0) && (activity?.length === 0);

const handleDismissWelcome = () => {
  localStorage.setItem('bmadflow_welcome_dismissed', 'true');
  setShowWelcome(false);
};

// Auto-dismiss when first project created
useEffect(() => {
  if (projects?.length > 0 && showWelcome) {
    handleDismissWelcome();
  }
}, [projects?.length]);
```

**Component Architecture:**
```tsx
frontend/src/
├── features/dashboard/
│   └── WelcomeCard.tsx            # First-time user guidance
├── components/common/
│   └── TooltipWrapper.tsx         # Reusable tooltip wrapper
```

**Tooltip Implementation (shadcn/ui):**
- Use shadcn/ui `Tooltip`, `TooltipTrigger`, `TooltipContent`, `TooltipProvider` components
- Wrap existing components with tooltip:
  ```tsx
  <TooltipProvider>
    <Tooltip>
      <TooltipTrigger asChild>
        <Button onClick={handleSync}>Sync</Button>
      </TooltipTrigger>
      <TooltipContent>
        <p>Fetch latest documentation from GitHub</p>
      </TooltipContent>
    </Tooltip>
  </TooltipProvider>
  ```

**Welcome Card Content:**
- Use shadcn/ui `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`
- Icon: `Sparkles` or `BookOpen` from Lucide React
- Three-step numbered list with icons
- Dismiss button: `X` icon in top-right corner
- Primary CTA: "Create Your First Project" button (links to Projects page)

**Testing:**
- Component tests: Test WelcomeCard rendering, dismiss functionality
- LocalStorage tests: Mock localStorage, test persistence
- Tooltip tests: Test tooltip visibility on hover/focus
- Auto-dismiss test: Verify Welcome card hides when first project created
- Expected: 6-8 tests total

**Technical Notes:**
- Follow Epic 5 accessibility patterns (WCAG 2.1 AA compliance)
- Tooltips have `role="tooltip"` and proper ARIA labels (built into shadcn/ui)
- Welcome card persists dismissal across browser sessions (localStorage)
- Help icon in header triggers Story 6.4 KeyboardShortcutsDialog

**Empty States Summary (Cross-Story Reference):**
- Dashboard (no projects): Welcome card (this story)
- Dashboard (no activity): "No activity yet..." (Story 6.2 AC#6)
- Projects (no projects): "No projects yet..." (Epic 2 implemented)
- Configuration (no LLM providers): "No LLM providers..." (Story 6.3 AC#8)
- Chat (no conversation): "New Conversation" state (Epic 5 Story 5.4 implemented)

**Estimated Effort:** 4 hours

---

## Definition of Done

**Epic 6 Complete When:**

- [ ] All 5 stories completed with acceptance criteria met
- [ ] **Backend (Story 6.1)**:
  - [ ] Dashboard metrics API operational (`/api/dashboard/metrics`)
  - [ ] Activity feed API operational (`/api/dashboard/activity`)
  - [ ] >70% test coverage (unit + integration tests)
  - [ ] OpenAPI documentation complete
- [ ] **Frontend (Stories 6.2-6.5)**:
  - [ ] Dashboard UI displays metrics cards and activity feed
  - [ ] Configuration page allows LLM provider management
  - [ ] Keyboard shortcuts implemented (4 shortcuts + help overlay)
  - [ ] Empty states provide helpful onboarding guidance
  - [ ] Welcome card guides first-time users
  - [ ] Component tests passing (10-15 tests per story)
- [ ] **Integration**:
  - [ ] Dashboard loads in <2s with production data
  - [ ] Keyboard shortcuts respond in <100ms
  - [ ] All tooltips display correctly on hover/focus
  - [ ] Welcome card persists dismissal across sessions
- [ ] **Quality**:
  - [ ] UI follows shadcn/ui design system
  - [ ] WCAG 2.1 AA compliance (DialogDescription in all modals)
  - [ ] README.md updated with keyboard shortcuts section
  - [ ] Zero critical bugs
- [ ] **Test Coverage**:
  - [ ] Backend: >70% coverage (Story 6.1)
  - [ ] Frontend: Component tests for all feature components
  - [ ] Integration tests for keyboard shortcuts

---

## Pre-Development Checklist

**Complete before starting Story 6.1:**

### Environment Setup ✅ **READY**
- [x] Epic 5 complete (6/6 stories Done, 100% ACs met)
- [x] shadcn/ui Dashboard template installed (Epic 1)
- [x] LLM Providers API operational (Epic 5 Story 5.1, 25/25 tests passing)
- [x] Database schema stable (no migrations needed for Epic 6)
- [x] React Query configured (Epic 3)
- [x] Zustand store initialized (Epic 3)

### Documentation Review ✅ **COMPLETE**
- [x] Reviewed Epic 5 retrospective (93.5/100 quality, 179 tests, 99.3% pass rate)
- [x] Reviewed Epic 4 retrospective (95.8/100 quality, 120 tests, 100% pass rate)
- [x] Reviewed [frontend-architecture.md](../architecture/frontend-architecture.md)
- [x] Reviewed [tech-stack.md](../architecture/tech-stack.md)
- [x] Reviewed [coding-standards.md](../architecture/coding-standards.md)

### Story Readiness ✅ **COMPLETE**
- [x] Story 6.1: Dev Notes added (activity feed schema clarified)
- [x] Story 6.2: Dev Notes added (component architecture, API integration)
- [x] Story 6.3: Dev Notes added (pure frontend story, backend complete)
- [x] Story 6.4: Dev Notes added (keyboard shortcuts implementation, conflict handling)
- [x] Story 6.5: Dev Notes added (Welcome card persistence, localStorage key)

### Dependencies ✅ **ALL MET**
- [x] Epic 5 Story 5.1 (LLM Providers API) - ✅ Complete
- [x] Epic 5 Story 5.3 (Conversations table) - ✅ Complete
- [x] Epic 4 Story 4.3 (Chunks table) - ✅ Complete
- [x] Epic 2 (Projects/ProjectDocs) - ✅ Complete

---

## Technical Architecture

### Frontend Architecture (Stories 6.2-6.5)

**Component Structure:**
```
frontend/src/
├── pages/
│   ├── Dashboard.tsx               # Story 6.2: Metrics + activity feed
│   └── Configuration.tsx           # Story 6.3: LLM provider management
├── features/
│   ├── dashboard/
│   │   ├── MetricCard.tsx          # Story 6.2: Reusable metric card
│   │   ├── ActivityFeed.tsx        # Story 6.2: Activity list
│   │   └── WelcomeCard.tsx         # Story 6.5: First-time user guidance
│   ├── configuration/
│   │   ├── LLMProviderTable.tsx    # Story 6.3: Provider table
│   │   └── AddProviderDialog.tsx   # Story 6.3: Add provider form
├── hooks/
│   └── useKeyboardShortcuts.ts     # Story 6.4: Global shortcut registration
├── components/
│   ├── KeyboardShortcutsDialog.tsx # Story 6.4: Help overlay
│   └── common/
│       └── TooltipWrapper.tsx      # Story 6.5: Reusable tooltip wrapper
└── layouts/
    └── AppShell.tsx                # Story 6.4: Call useKeyboardShortcuts()
```

### Backend Architecture (Story 6.1)

**Service Structure:**
```python
backend/app/
├── api/routes/
│   └── dashboard.py                # GET /dashboard/metrics, /dashboard/activity
├── services/
│   └── dashboard_service.py        # Business logic for metrics calculation
├── repositories/
│   └── dashboard_repository.py     # Database queries
└── schemas/
    └── dashboard.py                # DashboardMetrics, ActivityFeed Pydantic models
```

**Database Queries (Story 6.1):**
- Metrics: COUNT aggregations on projects, documents, chunks, conversations tables
- Activity: JOIN project_docs + projects + documents (GROUP BY, ORDER BY last_synced_at DESC LIMIT 10)

---

## Risk Management

### High Priority Risks ✅ **MITIGATED**

1. **Activity Feed Schema Ambiguity (Story 6.1)** - ✅ Resolved
   - **Issue**: No `sync_logs` table exists
   - **Mitigation**: Dev Notes specify POC approach (query project_docs table, status always 'success')
   - **Impact**: Low - acceptable limitation for POC

2. **Keyboard Shortcut Conflicts (Story 6.4)** - ✅ Resolved
   - **Issue**: Shortcuts could fire in input fields
   - **Mitigation**: AC#6 added (shortcuts disabled in input/textarea), Dev Notes specify `enableOnFormTags: false`
   - **Impact**: Low - conflict handling specified

3. **Welcome Card Persistence (Story 6.5)** - ✅ Resolved
   - **Issue**: Dismissal tracking unclear
   - **Mitigation**: Dev Notes specify localStorage key (`bmadflow_welcome_dismissed`)
   - **Impact**: Low - persistence strategy defined

### Medium Priority Risks

4. **Missing Integration Tests (Story 6.4)** - ⚠️ Acceptable
   - **Issue**: AC#8 marked [P1] (nice-to-have)
   - **Mitigation**: Component tests sufficient, integration tests can be added post-MVP
   - **Impact**: Low - manual testing validates flows

### Low Priority Risks ✅ **ACCEPTABLE**

5. **Dashboard Load Performance** - ✅ Low risk
   - **Target**: <2s load time
   - **Mitigation**: Use React Query caching, SQLAlchemy eager loading
   - **Impact**: Low - metrics queries are simple aggregations

---

## Success Metrics

**Epic 6 Success = Meeting These Targets:**

| Metric | Target | How Measured |
|--------|--------|--------------|
| **Story Completion** | 5/5 (100%) | All ACs met, QA approved |
| **Test Coverage** | >70% backend | pytest --cov |
| **Quality Score** | >85/100 avg | QA gate per story (Epic 5 achieved 93.5/100) |
| **Zero Blocking Issues** | 0 critical bugs | QA validation |
| **Dashboard Load Time** | <2s | Manual testing with production data |
| **Keyboard Shortcut Response** | <100ms | Manual testing with user input |

---

## Execution Timeline

| Story | Estimated Effort | Priority | Dependencies | Parallelizable |
|-------|------------------|----------|--------------|----------------|
| **6.1** | 1 day (4 hrs) | P0 | None | No (blocks 6.2) |
| **6.2** | 1 day (6 hrs) | P0 | Story 6.1 | No (depends on 6.1) |
| **6.3** | 0.5 day (4 hrs) | P0 | None (backend complete) | Yes (parallel with 6.4/6.5) |
| **6.4** | 1 day (6 hrs) | P1 | None | Yes (parallel with 6.3/6.5) |
| **6.5** | 0.5 day (4 hrs) | P1 | None | Yes (parallel with 6.3/6.4) |
| **Total** | **4 days** | - | - | - |

**Recommended Execution Order:**
1. **Day 1**: Story 6.1 (Backend API) - **Sequential** (must complete first)
2. **Day 2**: Story 6.2 (Dashboard UI) - **Sequential** (depends on 6.1)
3. **Day 3**: Story 6.3 (Configuration UI) + Story 6.4 (Keyboard Shortcuts) - **Parallel**
4. **Day 4**: Story 6.5 (Empty States) + QA review - **Final**

**Aggressive Timeline (Epic 5 velocity):**
- Epic 5 completed 6 stories in 2 days (67% faster than estimated)
- If Epic 6 follows same velocity: **2-3 days total**

---

## Lessons from Epic 5 Retrospective

### Applied to Epic 6 ✅

1. **FastAPI Dependency Override Pattern** (Epic 5 Retro #1)
   - **Story 6.1**: Integration tests use `app.dependency_overrides[get_db]`
   - **Learning**: Prevents asyncpg connection pool conflicts

2. **Accessibility Proactivity** (Epic 5 Retro #5)
   - **Story 6.4**: DialogDescription added to KeyboardShortcutsDialog upfront
   - **Story 6.5**: Tooltip ARIA labels verified (built into shadcn/ui)
   - **Learning**: SheetDescription/DialogDescription required for WCAG 2.1 AA

3. **Type Contract Alignment** (Epic 5 Retro #3)
   - **Story 6.1**: Pydantic schemas explicitly define all response fields
   - **Learning**: Backend must serialize all fields frontend expects

4. **Task Priority Labels** (Epic 5 Retro #2)
   - **Story 6.4 AC#8**: Marked [P1] (integration tests nice-to-have)
   - **Story 6.4 AC#6-7**: Marked [P0] (conflict handling required)
   - **Learning**: Clear prioritization prevents scope creep

5. **Per-Story QA Gates** (Epic 5 Retro #4)
   - **All stories**: QA reviews before marking Done
   - **Learning**: Proactive QA prevents post-deployment rework

---

## Next Steps

**You are now ready to start Story 6.1!** 🚀

**Story 6.1 Execution Plan:**
1. Create Pydantic schemas (`DashboardMetrics`, `ActivityFeed` in `app/schemas/dashboard.py`)
2. Create `DashboardRepository` with metrics + activity queries
3. Create `DashboardService` for business logic
4. Create REST API endpoints in `app/api/routes/dashboard.py`
5. Write unit tests (mock repository, test service logic)
6. Write integration tests (FastAPI dependency override pattern)
7. Production validation: Test both endpoints via curl
8. QA gate: Submit for review

**Estimated Time**: 1 day (4 hours)

---

**Document Status**: ✅ **READY FOR DEVELOPMENT** (95/100 readiness)
**Approved By**: Product Manager (John)
**Date**: 2025-10-14
**Next Review**: After Story 6.2 complete (mid-epic checkpoint)
