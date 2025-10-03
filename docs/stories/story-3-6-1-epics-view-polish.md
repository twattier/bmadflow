# Story 3.6.1: Epics View - Polish & Complete

**Epic:** [Epic 3: Multi-View Documentation Dashboard](../epics/epic-3-multi-view-dashboard.md)

**Status:** Draft

---

## User Story

**As a** user,
**I want** Epics view to display status badges, story counts, and a rollup widget,
**so that** I can see epic progress and status at a glance.

---

## Context

Story 3.2 delivered a **bonus implementation** of the Epics View (EpicsView.tsx) as part of the markdown rendering work. The current implementation is ~85% complete with the following functionality:

**✅ Already Implemented:**
- AC1: Fetches documents where doc_type = 'epic' ✓
- AC5: Clicking epic navigates to Detail view ✓
- Basic card grid layout with search/filter ✓
- Loading skeleton and empty states ✓

**❌ Missing (This Story):**
- AC2: Display Status and Story Count columns
- AC3: Color-coded status badges (Draft=gray, Dev=blue, Done=green)
- AC4: Story Count from ExtractedEpic table
- AC6: Sort epics by filename/number (epic-1, epic-2, epic-3)
- AC7: Status rollup widget at top

This polish story completes the remaining 5 acceptance criteria to make Epics View production-ready.

---

## Acceptance Criteria

### AC #1: Display Status and Story Count in Cards

- Each epic card displays Status badge and Story Count alongside existing fields
- Layout: Title (top), Status badge + Story Count (middle row), Excerpt + Last Modified (bottom)
- Story Count formatted as "X stories" (e.g., "5 stories", "1 story")
- Status badge uses color-coded styling per AC #2

### AC #2: Color-Coded Status Badges

- Status badge component displays epic status from `ExtractedEpic.status` field
- Color coding per UX spec:
  - **Draft** → Gray badge (`bg-gray-100 text-gray-800`)
  - **Dev** → Blue badge (`bg-blue-100 text-blue-800`)
  - **Done** → Green badge (`bg-green-100 text-green-800`)
- Badge displays capitalized status text (e.g., "Draft", "Dev", "Done")
- Badge uses shadcn/ui Badge component with variant prop

### AC #3: Fetch ExtractedEpic Data from Backend

- Backend endpoint `GET /api/epics` returns list of epics with joined `ExtractedEpic` data
- Response includes: `document` fields + `extracted_epic` nested object with `status` and `story_count`
- Frontend creates new `useEpics()` React Query hook (or extends `useDocuments`)
- Hook fetches from `/api/epics` endpoint instead of `/api/projects/{id}/documents?type=epic`
- Fallback: If `extracted_epic` is null (not yet extracted), display status as "Draft" and story_count as 0

### AC #4: Sort Epics by Number

- Epics sorted by epic number extracted from `file_path` using regex
- Regex pattern: `/epic-(\d+)/` to extract number from filename
- Sort order: Epic 1, Epic 2, Epic 3, ... (ascending numeric order)
- Epics without number pattern appear last (alphabetical fallback)
- Implemented client-side in frontend using `useMemo()` for performance

### AC #5: Status Rollup Widget at Top

- Widget displayed above search bar with epic status summary
- Content: "X epics total | Y draft, Z in dev, W done" (e.g., "5 epics total | 1 draft, 2 in dev, 2 done")
- Widget uses Card component with subtle background (`bg-muted`)
- Counts calculated client-side from fetched epic data
- Widget responsive: Single line on desktop, stacked on mobile

---

## Tasks / Subtasks

### Task 1: Backend - Create `/api/epics` Endpoint (AC #3)

- [ ] Create `GET /api/epics` endpoint in `apps/api/src/routes/epics.py`
  - [ ] Query documents table WHERE `doc_type = 'epic'`
  - [ ] JOIN with `extracted_epics` table ON `document_id`
  - [ ] Return document fields + nested `extracted_epic` object with `status`, `story_count`
  - [ ] Handle NULL `extracted_epic` (not yet extracted): Return `{status: 'draft', story_count: 0}` as default
- [ ] Add TypeScript interface for Epic response:
  ```typescript
  interface Epic extends Document {
    extracted_epic: {
      status: 'draft' | 'dev' | 'done';
      story_count: number;
    } | null;
  }
  ```
- [ ] Unit test: Verify endpoint returns epics with extracted data
- [ ] Unit test: Verify fallback for epics without extracted data

### Task 2: Frontend - Create `useEpics()` Hook (AC #3)

- [ ] Create `useEpics()` hook in `apps/web/src/hooks/useEpics.ts`
  - [ ] Use React Query `useQuery` with key `['epics', projectId]`
  - [ ] Fetch from `/api/epics` endpoint
  - [ ] Set stale time: 5 minutes (consistent with useDocuments)
  - [ ] Set retry: 3 attempts with exponential backoff
- [ ] Update EpicsView.tsx to use `useEpics()` instead of `useDocuments()`
- [ ] Unit test: Verify hook fetches from correct endpoint
- [ ] Unit test: Verify hook returns epics with extracted data

### Task 3: Frontend - Status Badge Component (AC #2)

- [ ] Create `<StatusBadge>` component in `apps/web/src/components/StatusBadge.tsx`
  - [ ] Accept `status` prop: `'draft' | 'dev' | 'done'`
  - [ ] Use shadcn/ui Badge component
  - [ ] Implement color variants:
    - Draft: `variant="secondary"` or custom gray styling
    - Dev: `variant="default"` or custom blue styling
    - Done: Custom green styling (`bg-green-100 text-green-800`)
  - [ ] Display capitalized status text
- [ ] Unit test: Verify badge renders with correct color for each status
- [ ] Unit test: Verify badge displays capitalized text

### Task 4: Frontend - Update DocumentCard for Epics (AC #1)

- [ ] Update DocumentCard component to accept optional `epic` prop
- [ ] When `epic` prop provided, display Status badge and Story Count
- [ ] Layout adjustment:
  - [ ] Row 1: Title (existing)
  - [ ] Row 2: Status badge + Story Count (new)
  - [ ] Row 3: Excerpt + Last Modified (existing)
- [ ] Story Count display: "X stories" / "1 story" with conditional plural
- [ ] Ensure layout works on desktop and mobile (responsive)
- [ ] Unit test: Verify epic card displays status and story count
- [ ] Unit test: Verify non-epic cards render without changes

### Task 5: Frontend - Epic Sorting (AC #4)

- [ ] Implement epic sorting in EpicsView.tsx using `useMemo()`
- [ ] Extract epic number from `file_path` using regex `/epic-(\d+)/`
- [ ] Sort by extracted number (ascending)
- [ ] Fallback: Epics without number sorted alphabetically at end
- [ ] Unit test: Verify epics sorted correctly (Epic 1, Epic 2, Epic 3)
- [ ] Unit test: Verify epics without numbers appear last

### Task 6: Frontend - Status Rollup Widget (AC #5)

- [ ] Create rollup widget component above search bar in EpicsView.tsx
- [ ] Calculate status counts from fetched epic data:
  - [ ] Total count: `epics.length`
  - [ ] Draft count: `epics.filter(e => e.extracted_epic?.status === 'draft').length`
  - [ ] Dev count: `epics.filter(e => e.extracted_epic?.status === 'dev').length`
  - [ ] Done count: `epics.filter(e => e.extracted_epic?.status === 'done').length`
- [ ] Display format: "X epics total | Y draft, Z in dev, W done"
- [ ] Wrap in Card component with `bg-muted` background
- [ ] Responsive layout: Single line desktop, stacked mobile
- [ ] Unit test: Verify widget displays correct counts
- [ ] Unit test: Verify widget responsive on mobile

### Task 7: Integration Testing

- [ ] Integration test: Fetch epics from backend and render with status badges
- [ ] Integration test: Verify story counts match relationships table
- [ ] Integration test: Verify sorting by epic number
- [ ] Manual test: Test with real agent-lab epic data (3 epics)
- [ ] Manual test: Verify rollup widget shows correct totals

---

## Dev Notes

### Current Implementation Baseline

**Existing File:** `apps/web/src/pages/EpicsView.tsx` (created in Story 3.2)

Current implementation uses `useDocuments()` hook with `docType: 'epic'` to fetch basic document data. This story upgrades to use extracted epic data for status and story count.

**Changes Required:**
1. Switch from `useDocuments()` to new `useEpics()` hook
2. Add StatusBadge component to card display
3. Add sorting logic
4. Add rollup widget

### Data Model Reference

**ExtractedEpic Table:**
```typescript
interface ExtractedEpic {
  id: string;
  document_id: string;
  epic_number: number;
  title: string;
  goal: string;
  status: 'draft' | 'dev' | 'done'; // ✅ Use this for AC #2
  story_count: number; // ✅ Use this for AC #1
  confidence_score: number;
  extracted_at: string;
}
```
[Source: docs/architecture/data-models.md]

**Epic Response Format:**
```typescript
interface Epic {
  // Document fields
  id: string;
  project_id: string;
  file_path: string; // e.g., "docs/epics/epic-3-multi-view-dashboard.md"
  content: string;
  doc_type: 'epic';
  title: string;
  excerpt: string;
  last_modified: string;

  // ExtractedEpic data (joined)
  extracted_epic: {
    status: 'draft' | 'dev' | 'done';
    story_count: number;
  } | null; // null if extraction not yet complete
}
```

### Backend Implementation Notes

**New Endpoint:** `GET /api/epics`

Location: `apps/api/src/routes/epics.py` (create new file)

**Query Pattern:**
```python
async def get_epics(project_id: str):
    query = """
        SELECT
            d.*,
            e.status,
            e.story_count
        FROM documents d
        LEFT JOIN extracted_epics e ON d.id = e.document_id
        WHERE d.project_id = :project_id
        AND d.doc_type = 'epic'
        ORDER BY d.file_path
    """
    # Return with extracted_epic nested object
```

**Fallback Handling:**
If `extracted_epic` is NULL (epic not yet extracted by Story 2.5 pipeline), return default values:
```typescript
{
  ...document,
  extracted_epic: {
    status: 'draft',
    story_count: 0
  }
}
```

### Frontend Implementation Notes

**Component Structure:**

```
EpicsView.tsx
├── useEpics() hook → Fetch from /api/epics
├── Status Rollup Widget (Card with counts)
├── Search Input (existing)
└── Epic Cards Grid
    └── DocumentCard (updated with epic props)
        ├── StatusBadge component
        └── Story Count display
```

**StatusBadge Component Design:**

Location: `apps/web/src/components/StatusBadge.tsx`

```typescript
interface StatusBadgeProps {
  status: 'draft' | 'dev' | 'done';
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const variantMap = {
    draft: 'secondary', // Gray
    dev: 'default',     // Blue
    done: 'success',    // Green (custom)
  };

  return (
    <Badge variant={variantMap[status]}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </Badge>
  );
}
```

### Epic Number Extraction

**Regex Pattern:** `/epic-(\d+)/i`

**Example Extractions:**
- `docs/epics/epic-3-multi-view-dashboard.md` → 3
- `docs/epics/epic-1-foundation.md` → 1
- `docs/epics/epic-2-extraction.md` → 2
- `docs/epics/special-epic.md` → null (no number, sort alphabetically at end)

**Implementation:**
```typescript
const sortedEpics = useMemo(() => {
  if (!epics) return [];

  return [...epics].sort((a, b) => {
    const numA = a.file_path.match(/epic-(\d+)/i)?.[1];
    const numB = b.file_path.match(/epic-(\d+)/i)?.[1];

    if (numA && numB) return parseInt(numA) - parseInt(numB);
    if (numA) return -1;
    if (numB) return 1;
    return a.file_path.localeCompare(b.file_path);
  });
}, [epics]);
```

### Testing Requirements

**Frontend Unit Testing:**
- Framework: Vitest + React Testing Library
- Location: `apps/web/src/__tests__/` or colocated
- Coverage Target: 30% for POC (critical components)

**Backend Unit Testing:**
- Framework: pytest + pytest-asyncio
- Location: `apps/api/tests/`
- Coverage Target: 50% for POC

**Test Files to Create:**
- `apps/web/src/hooks/__tests__/useEpics.test.ts`
- `apps/web/src/components/__tests__/StatusBadge.test.tsx`
- `apps/api/tests/test_epics_routes.py`

---

## Dependencies

**Upstream (Must Complete First):**
- ✅ Story 3.2: Detail View - Markdown Rendering - **COMPLETE**
  - Provides: EpicsView.tsx baseline implementation
- ✅ Story 2.5: Extraction Pipeline - **COMPLETE**
  - Provides: ExtractedEpic table with status and story_count
- ✅ Epic 1 Story 1.5: Dashboard Shell - **COMPLETE**
  - Provides: Navigation structure

**No New Dependencies Required:**
- shadcn/ui Badge component (already installed)
- React Query (already configured)
- Existing DocumentCard component (extend with epic props)

**Downstream (This Story Blocks):**
- None - This is a polish story, doesn't block other work

---

## Testing

### Unit Tests

**File:** `apps/web/src/hooks/__tests__/useEpics.test.ts`

```typescript
describe('useEpics', () => {
  it('should fetch epics from /api/epics endpoint', async () => {
    // Test hook fetches correct endpoint
  });

  it('should return epics with extracted_epic data', async () => {
    // Test response includes status and story_count
  });

  it('should handle epics without extracted_epic (NULL)', async () => {
    // Test fallback to default values
  });
});
```

**File:** `apps/web/src/components/__tests__/StatusBadge.test.tsx`

```typescript
describe('StatusBadge', () => {
  it('should render draft status with gray styling', () => {
    render(<StatusBadge status="draft" />);
    expect(screen.getByText('Draft')).toHaveClass('bg-gray-100');
  });

  it('should render dev status with blue styling', () => {
    render(<StatusBadge status="dev" />);
    expect(screen.getByText('Dev')).toHaveClass('bg-blue-100');
  });

  it('should render done status with green styling', () => {
    render(<StatusBadge status="done" />);
    expect(screen.getByText('Done')).toHaveClass('bg-green-100');
  });
});
```

**File:** `apps/api/tests/test_epics_routes.py`

```python
@pytest.mark.asyncio
async def test_get_epics_with_extracted_data(client: AsyncClient):
    response = await client.get("/api/epics?project_id=test-project")
    assert response.status_code == 200
    epics = response.json()
    assert len(epics) > 0
    assert epics[0]["extracted_epic"]["status"] in ["draft", "dev", "done"]
    assert isinstance(epics[0]["extracted_epic"]["story_count"], int)

@pytest.mark.asyncio
async def test_get_epics_without_extracted_data(client: AsyncClient):
    # Test epics without extracted_epic fallback to defaults
    response = await client.get("/api/epics?project_id=test-project")
    assert response.status_code == 200
    epics = response.json()
    epic_without_extraction = [e for e in epics if e["extracted_epic"] is None]
    # Verify fallback behavior
```

### Integration Tests

**File:** `apps/web/src/pages/__tests__/EpicsView.integration.test.tsx`

```typescript
describe('EpicsView Integration', () => {
  it('should load epics with status badges and story counts', async () => {
    render(<EpicsView />);
    await waitFor(() => {
      expect(screen.getByText('Draft')).toBeInTheDocument();
      expect(screen.getByText(/5 stories/)).toBeInTheDocument();
    });
  });

  it('should display status rollup widget with correct counts', async () => {
    render(<EpicsView />);
    await waitFor(() => {
      expect(screen.getByText(/3 epics total/)).toBeInTheDocument();
    });
  });

  it('should sort epics by number (Epic 1, Epic 2, Epic 3)', async () => {
    render(<EpicsView />);
    await waitFor(() => {
      const epicCards = screen.getAllByTestId('epic-card');
      expect(epicCards[0]).toHaveTextContent('Epic 1');
      expect(epicCards[1]).toHaveTextContent('Epic 2');
      expect(epicCards[2]).toHaveTextContent('Epic 3');
    });
  });
});
```

### Manual Testing Checklist

**Desktop Testing (1440×900):**
- [ ] Navigate to Epics view from main navigation
- [ ] Verify status rollup widget displays at top with correct counts
- [ ] Verify each epic card shows Status badge with correct color
- [ ] Verify each epic card shows Story Count (e.g., "5 stories")
- [ ] Verify epics sorted by number (Epic 1, Epic 2, Epic 3)
- [ ] Verify clicking epic card navigates to Detail view
- [ ] Test search functionality with status badges visible

**Tablet Testing (768×1024):**
- [ ] Verify rollup widget responsive (stacked if needed)
- [ ] Verify epic cards remain readable with status/count

**Mobile Testing (375×667):**
- [ ] Verify rollup widget stacks vertically
- [ ] Verify status badges and counts visible on small cards

**Cross-Browser Testing:**
- [ ] Chrome: Verify all features work
- [ ] Firefox: Verify all features work
- [ ] Safari: Verify all features work

**Edge Cases:**
- [ ] Test with epic that has no extracted_epic data (should show "Draft", "0 stories")
- [ ] Test with epic filename without number pattern (should appear at end)
- [ ] Test with empty epics list (should show empty state)

---

## Definition of Done

- [ ] All 5 acceptance criteria implemented and verified
- [ ] Backend `/api/epics` endpoint created and tested
- [ ] Frontend `useEpics()` hook created and tested
- [ ] StatusBadge component created and tested
- [ ] Epic sorting by number implemented
- [ ] Status rollup widget implemented
- [ ] Unit tests written and passing (8+ tests)
- [ ] Integration tests passing
- [ ] Manual testing completed (desktop, tablet, mobile)
- [ ] No console errors or warnings
- [ ] Code reviewed (self-review or peer review)
- [ ] EpicsView production-ready with all original Story 3.6 AC complete

---

## Estimated Effort

**4 hours** (0.5 days)

**Breakdown:**
- Backend endpoint + tests: 1 hour
- useEpics() hook + tests: 0.5 hours
- StatusBadge component + tests: 0.5 hours
- DocumentCard updates: 0.5 hours
- Epic sorting logic: 0.5 hours
- Rollup widget: 0.5 hours
- Integration testing: 0.5 hours
- Manual testing: 0.5 hours

**Complexity:** Low-Medium
**Risk Level:** Low

**Risk Factors:**
- ExtractedEpic data may be NULL for some epics → Mitigated with fallback defaults
- Natural sort by epic number may miss edge cases → Mitigated with alphabetical fallback

---

## Success Criteria

**Story is complete when:**
1. Epics view displays status badges, story counts, and rollup widget
2. All 5 AC met and verified with tests
3. Epic sorting works correctly (Epic 1, Epic 2, Epic 3)
4. Status badges use correct color coding (Draft=gray, Dev=blue, Done=green)
5. Story counts accurate from ExtractedEpic table
6. Rollup widget shows correct totals
7. EpicsView is production-ready (all original Story 3.6 AC complete)

---

## Notes

- This is a **quick win polish story** (~4 hours) that completes the mostly-done Epics View
- The ExtractedEpic table already has `status` and `story_count` fields from Story 2.5
- Backend endpoint is straightforward (LEFT JOIN query)
- Frontend changes are incremental additions to existing components
- High user value: Status visibility is core to epic progress tracking

---

## Dev Agent Record

### Agent Model Used

_This section will be populated by the development agent._

### Debug Log References

_This section will be populated by the development agent._

### Completion Notes

_This section will be populated by the development agent._

### File List

_This section will be populated by the development agent._

---

## QA Results

_This section will be populated by the QA agent after implementation review._

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-03 | 1.0 | Story 3.6.1 created to complete Epics View polish. Consolidates 5 missing AC from original Story 3.6: status badges, story count, rollup widget, sorting, and ExtractedEpic data integration. Estimated 4 hours. Status: Draft | Sarah (PO) |
