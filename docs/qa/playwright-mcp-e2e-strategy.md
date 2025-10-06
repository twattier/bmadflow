# Playwright MCP E2E Testing Strategy

**Document Type:** QA Strategy
**Owner:** Quinn (Test Architect)
**Status:** Approved
**Last Updated:** 2025-10-06

## Executive Summary

This document defines the comprehensive E2E testing strategy using Playwright MCP as the cornerstone for quality assurance, visual verification, and debugging. Playwright MCP integration (FR37-39, FR44, NFR21) enables programmatic frontend testing, screenshot capture, console monitoring, and AI-assisted test planning.

## Strategic Approach

**Core Principle:** Playwright MCP is not just a testing tool—it's an **architectural quality component** that validates design integrity, performance targets, and user experience from Day 1.

### Key Capabilities (PRD Requirements)

- **FR37:** Programmatic frontend launch for automated testing
- **FR38:** Automated screenshot capture for visual regression
- **FR39:** Console log monitoring for error detection
- **FR44:** AI-assisted manual test plan generation
- **NFR21:** E2E test execution for critical flows

---

## Critical E2E Test Scenarios

### Scenario 1: Browse Documentation Flow

**Priority:** P0 (Critical Path)
**PRD References:** FR6-FR9, Story 3.2-3.6
**Performance Targets:** Explorer load <2s, Markdown render <1s (NFR1)

```typescript
// tests/e2e/critical-flows/browse-documentation.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Browse Documentation Flow', () => {
  test('user navigates file tree and views markdown with TOC', async ({ page }) => {
    // Given: User on Explorer page with synced ProjectDoc
    await page.goto('http://localhost:3000/projects/{id}/explorer');

    // Capture initial state
    const snapshot = await page.accessibility.snapshot();

    // When: User expands folder and clicks file
    await page.click('[data-testid="folder-docs"]');
    await page.click('[data-testid="file-prd-md"]');

    // Then: Markdown renders correctly
    await expect(page.locator('[data-testid="content-viewer"]')).toBeVisible();
    await expect(page.locator('[data-testid="table-of-contents"]')).toBeVisible();

    // Performance validation
    const performanceMetrics = await page.evaluate(() => performance.getEntriesByType('navigation')[0]);
    expect(performanceMetrics.loadEventEnd - performanceMetrics.fetchStart).toBeLessThan(2000);

    // Visual verification
    await page.screenshot({ path: 'tests/e2e/visual-baselines/browse-flow-success.png' });

    // Console error check
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });
    expect(consoleErrors).toHaveLength(0);
  });

  test('mermaid diagrams render correctly', async ({ page }) => {
    await page.goto('http://localhost:3000/projects/{id}/explorer');
    await page.click('[data-testid="file-architecture-md"]');

    // Wait for Mermaid rendering
    await expect(page.locator('.mermaid svg')).toBeVisible({ timeout: 3000 });

    // Screenshot for visual verification
    await page.locator('.mermaid').screenshot({
      path: 'tests/e2e/visual-baselines/mermaid-diagram.png'
    });
  });

  test('cross-document links navigate correctly', async ({ page }) => {
    await page.goto('http://localhost:3000/projects/{id}/explorer');
    await page.click('[data-testid="file-prd-md"]');

    // Click relative link in markdown
    await page.click('a[href="./architecture.md"]');

    // Verify navigation
    await expect(page.locator('[data-testid="breadcrumb"]')).toContainText('architecture.md');
    await expect(page.locator('[data-testid="file-tree-selected"]')).toHaveAttribute('data-file', 'architecture.md');
  });
});
```

**Playwright MCP Actions:**
1. `mcp__playwright__browser_navigate` - Launch Explorer page
2. `mcp__playwright__browser_snapshot` - Capture accessibility tree
3. `mcp__playwright__browser_click` - Simulate user clicks
4. `mcp__playwright__browser_take_screenshot` - Visual baseline
5. `mcp__playwright__browser_console_messages(onlyErrors=true)` - Error detection

---

### Scenario 2: Sync ProjectDoc Flow

**Priority:** P0 (Critical Path)
**PRD References:** FR3-FR5, Story 2.5-2.6
**Performance Target:** Sync <5min (NFR3)

```typescript
// tests/e2e/critical-flows/sync-projectdoc.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Sync ProjectDoc Flow', () => {
  test('user triggers sync and monitors completion', async ({ page }) => {
    // Given: User on Project Overview with unsynced ProjectDoc
    await page.goto('http://localhost:3000/projects/{id}');

    // Capture pre-sync state
    await page.screenshot({ path: 'tests/e2e/visual-baselines/pre-sync-state.png' });

    // When: User clicks Sync button
    await page.click('[data-testid="sync-button"]');

    // Then: Loading state displays
    await expect(page.locator('text=Syncing...')).toBeVisible();
    await page.screenshot({ path: 'tests/e2e/visual-baselines/sync-in-progress.png' });

    // Wait for success (max 5 minutes per NFR3)
    await expect(page.locator('text=Sync completed successfully')).toBeVisible({
      timeout: 300000
    });

    // Verify sync status updates
    await expect(page.locator('[data-testid="sync-status"]')).toContainText('✓ Up to date');
    await expect(page.locator('[data-testid="last-synced"]')).toContainText('seconds ago');

    // Capture post-sync state
    await page.screenshot({ path: 'tests/e2e/visual-baselines/post-sync-state.png' });

    // Console monitoring
    const consoleLogs = [];
    page.on('console', msg => consoleLogs.push({ type: msg.type(), text: msg.text() }));
    expect(consoleLogs.filter(log => log.type === 'error')).toHaveLength(0);
  });

  test('sync handles GitHub rate limit gracefully', async ({ page }) => {
    // Mock rate limit scenario
    await page.route('**/api/project-docs/*/sync', route => {
      route.fulfill({
        status: 429,
        body: JSON.stringify({
          error: 'Rate limit exceeded',
          reset_at: new Date(Date.now() + 3600000).toISOString()
        })
      });
    });

    await page.goto('http://localhost:3000/projects/{id}');
    await page.click('[data-testid="sync-button"]');

    // Verify error handling (NFR10)
    await expect(page.locator('.toast-error')).toContainText('Rate limit exceeded');
    await expect(page.locator('.toast-error')).toContainText('1 hour');
  });
});
```

**Playwright MCP Actions:**
1. `mcp__playwright__browser_navigate` - Load Project Overview
2. `mcp__playwright__browser_snapshot` - Pre/post sync state
3. `mcp__playwright__browser_click` - Trigger sync
4. `mcp__playwright__browser_wait_for` - Monitor progress
5. `mcp__playwright__browser_take_screenshot` - Capture stages
6. `mcp__playwright__browser_console_messages` - Validate logs

---

### Scenario 3: AI Chat with Source Attribution

**Priority:** P0 (Critical Path)
**PRD References:** FR10-FR15, Story 5.4-5.5
**Performance Target:** Response <3s cloud/<10s Ollama (NFR2)

```typescript
// tests/e2e/critical-flows/ai-chat-sources.spec.ts
import { test, expect } from '@playwright/test';

test.describe('AI Chat Flow', () => {
  test('user chats with AI and navigates to source with header anchor', async ({ page }) => {
    // Given: User on Chat page with synced Project
    await page.goto('http://localhost:3000/projects/{id}/chat');

    // Capture initial chat UI
    await page.screenshot({ path: 'tests/e2e/visual-baselines/chat-initial.png' });

    // When: User selects LLM and sends message
    await page.selectOption('[data-testid="llm-provider"]', 'ollama-llama2');
    await page.fill('[data-testid="message-input"]', 'What are the performance targets?');

    const startTime = Date.now();
    await page.click('[data-testid="send-button"]');

    // Then: Response begins streaming
    await expect(page.locator('.message-assistant')).toBeVisible({ timeout: 10000 });
    const responseTime = Date.now() - startTime;
    expect(responseTime).toBeLessThan(10000); // NFR2: <10s Ollama

    // Source links displayed with header anchors
    await expect(page.locator('.source-links')).toBeVisible();
    await expect(page.locator('a[href*="#performance-targets"]')).toBeVisible();

    // Screenshot with sources
    await page.screenshot({ path: 'tests/e2e/visual-baselines/chat-with-sources.png' });

    // When: User clicks source link
    await page.click('a[href*="prd.md#performance-targets"]');

    // Then: Source panel slides in (60fps animation per NFR9)
    await expect(page.locator('[data-testid="source-panel"]')).toBeVisible();

    // Verify auto-scroll to anchor section
    const anchorElement = await page.locator('#performance-targets');
    await expect(anchorElement).toBeInViewport();

    // Verify temporary highlight
    await expect(anchorElement).toHaveClass(/highlighted/);

    // Screenshot source panel
    await page.screenshot({ path: 'tests/e2e/visual-baselines/source-panel-open.png' });

    // Console streaming validation
    const streamingLogs = [];
    page.on('console', msg => {
      if (msg.text().includes('streaming')) streamingLogs.push(msg.text());
    });
    expect(streamingLogs.length).toBeGreaterThan(0);
  });

  test('conversation persists in history', async ({ page }) => {
    await page.goto('http://localhost:3000/projects/{id}/chat');

    // Send message
    await page.fill('[data-testid="message-input"]', 'Test question');
    await page.click('[data-testid="send-button"]');
    await expect(page.locator('.message-assistant')).toBeVisible();

    // Navigate away and back
    await page.goto('http://localhost:3000/projects/{id}/overview');
    await page.goto('http://localhost:3000/projects/{id}/chat');

    // Open history
    await page.click('[data-testid="history-button"]');

    // Verify conversation in history
    await expect(page.locator('[data-testid="history-panel"]')).toContainText('Test question');
  });
});
```

**Playwright MCP Actions:**
1. `mcp__playwright__browser_navigate` - Load Chat page
2. `mcp__playwright__browser_type` - Input message
3. `mcp__playwright__browser_click` - Send & click source
4. `mcp__playwright__browser_wait_for` - Response streaming
5. `mcp__playwright__browser_take_screenshot` - Chat states
6. `mcp__playwright__browser_console_messages` - Streaming logs

---

## Debugging Workflows with Playwright MCP

### Workflow 1: Visual Debug on Test Failure

```yaml
Trigger: E2E test fails

Process:
  1. Capture screenshot at exact failure point
     Tool: mcp__playwright__browser_take_screenshot
     File: .ai/e2e-failures/failure-{timestamp}.png

  2. Extract console errors
     Tool: mcp__playwright__browser_console_messages(onlyErrors=true)
     Output: Error logs with stack traces

  3. Capture full accessibility snapshot
     Tool: mcp__playwright__browser_snapshot
     Output: DOM state JSON for analysis

  4. Capture network activity
     Tool: mcp__playwright__browser_network_requests
     Output: API calls, response times, failures

  5. Package debug artifacts
     Location: .ai/e2e-failures/{test-name}-{timestamp}/
     Contents:
       - screenshot.png
       - console-errors.json
       - dom-snapshot.json
       - network-log.json
       - test-output.log

Output: Complete debug package for investigation
```

### Workflow 2: Performance Bottleneck Detection

```yaml
Trigger: NFR performance target missed (e.g., sync >5min, query >3s)

Process:
  1. Launch with network monitoring
     Tool: mcp__playwright__browser_navigate + browser_network_requests

  2. Execute slow operation
     - Trigger sync/RAG query/markdown render
     - Record timing metrics

  3. Analyze network waterfall
     - Identify slow API calls
     - Check payload sizes
     - Detect sequential vs parallel requests

  4. Capture browser performance metrics
     Code: page.evaluate(() => performance.getEntriesByType('navigation'))

  5. Screenshot loading state
     Tool: mcp__playwright__browser_take_screenshot
     File: performance-bottleneck-{operation}.png

  6. Generate performance report
     Metrics:
       - Time to First Byte (TTFB)
       - First Contentful Paint (FCP)
       - Time to Interactive (TTI)
       - API response times
       - Bundle size impact

Output: Performance analysis with optimization recommendations
```

### Workflow 3: Cross-Browser Compatibility Check

```yaml
Trigger: Before release or major UI change

Process:
  1. Configure multi-browser execution
     Browsers: chromium, firefox, webkit
     Config: playwright.config.ts projects array

  2. Run critical paths per browser
     Tests: Browse, Sync, Chat flows

  3. Capture screenshots per browser
     Tool: mcp__playwright__browser_take_screenshot
     Files:
       - chrome-{flow}.png
       - firefox-{flow}.png
       - webkit-{flow}.png

  4. Compare visual consistency
     Method: Side-by-side screenshot comparison
     Tool: pixelmatch for pixel-level diff

  5. Check browser-specific errors
     Tool: mcp__playwright__browser_console_messages
     Per browser: Collect unique errors

  6. Document compatibility issues
     Report: Browser support matrix

Output: Compatibility matrix with browser-specific issues
```

---

## Visual Regression Testing

### Strategy: Baseline + Diff Detection

```yaml
Approach: Screenshot-based regression testing
Tool: Playwright MCP + pixelmatch

Baseline Creation:
  1. Capture golden screenshots for UI states
     - Dashboard empty state
     - Project list with data
     - Explorer with file tree
     - Chat with conversation
     - Source panel open

  2. Store baselines
     Location: tests/e2e/visual-baselines/
     Structure:
       /browse/
       /sync/
       /chat/
       /components/

  3. Version control baselines
     Git: Commit to repository for team consistency

Test Execution:
  1. Run E2E flow with Playwright MCP
  2. Capture current screenshots
     Tool: mcp__playwright__browser_take_screenshot

  3. Compare with baseline
     Code:
       const baseline = fs.readFileSync('baseline.png');
       const current = fs.readFileSync('current.png');
       const diff = pixelmatch(baseline, current, null, width, height, {
         threshold: 0.1  // 10% pixel diff tolerance
       });

  4. Flag visual regressions
     Fail Criteria: Pixel diff > threshold
     Output: Diff image highlighting changes

  5. Update baseline if intentional
     Review: Approve visual change
     Action: Replace baseline screenshot
```

### Visual Quality Gates

```yaml
Gate 1: Component Rendering
  Test: shadcn/ui components render correctly
  Method: Screenshot each component isolated
  Pass Criteria:
    - No pixel diff from baseline
    - WCAG contrast 4.5:1 normal / 3:1 large (NFR8)
    - Focus indicators visible (2px ring)

Gate 2: Layout Consistency
  Test: Split-view layouts maintain proportions
  Method: Screenshot at viewport sizes ≥1024px (NFR7)
  Pass Criteria:
    - Explorer: 25/75 split maintained
    - Chat: 60/40 split with source panel
    - Cumulative Layout Shift (CLS) = 0

Gate 3: Animation Smoothness
  Test: Panel animations run at 60fps (NFR9)
  Method:
    - Capture keyframe screenshots
    - Analyze frame sequence
  Pass Criteria:
    - Hardware-accelerated CSS transforms
    - No frame drops or stuttering
    - Smooth slide-in transitions

Gate 4: Cross-Document Navigation
  Test: Relative links and anchors work
  Method:
    - Click link → screenshot destination
    - Verify scroll position
  Pass Criteria:
    - Correct document loaded
    - Auto-scroll to anchor section
    - Section highlighted temporarily
```

---

## E2E Quality Gate Checklist

```yaml
PRE-RELEASE QUALITY GATE - PLAYWRIGHT MCP VERIFICATION

═══════════════════════════════════════════════════════
GATE 1: CRITICAL PATH COVERAGE (NFR21)
═══════════════════════════════════════════════════════
□ Browse Documentation Flow
  □ File tree loads in <2s
  □ Markdown renders in <1s (NFR1)
  □ TOC auto-generated correctly
  □ Mermaid diagrams render
  □ Cross-document links work
  □ CSV tables display properly
  □ YAML/JSON syntax highlighted
  □ Screenshot captured for baseline

□ Sync ProjectDoc Flow
  □ Sync button triggers operation
  □ Loading state displays
  □ Sync completes in <5min (NFR3)
  □ Success toast shows
  □ Status updates to "✓ Up to date"
  □ Console logs clean (no errors)
  □ Screenshot at each stage

□ AI Chat Flow
  □ LLM provider selection works
  □ Message input enabled
  □ Response begins <3s cloud/<10s Ollama (NFR2)
  □ Source attribution displays
  □ Header anchor navigation works
  □ Source panel slides in smoothly (60fps, NFR9)
  □ Conversation persists in history
  □ Screenshot of chat with sources

═══════════════════════════════════════════════════════
GATE 2: PERFORMANCE VALIDATION (NFR1-4, 9)
═══════════════════════════════════════════════════════
□ Frontend Performance
  □ Explorer page load <2s
  □ Markdown render <1s (typical BMAD docs)
  □ Panel animations 60fps (hardware-accelerated CSS)
  □ Network requests monitored

□ Backend Performance
  □ RAG query response <3s (cloud LLM)
  □ RAG query response <10s (Ollama)
  □ Vector search <500ms (NFR4)
  □ Sync operation <5min per ProjectDoc (NFR3)

□ Performance Artifacts
  □ Network waterfall captured
  □ Console timing logs saved
  □ Screenshots of loading states
  □ Performance report generated

═══════════════════════════════════════════════════════
GATE 3: VISUAL REGRESSION (NFR7, 8)
═══════════════════════════════════════════════════════
□ Component Consistency
  □ shadcn/ui components match baseline
  □ Color contrast meets WCAG 4.5:1 / 3:1
  □ Focus indicators visible (2px ring)
  □ Icons render correctly (Lucide)

□ Layout Stability
  □ Explorer 25/75 split maintained
  □ Chat 60/40 split with source panel
  □ No layout shift (CLS = 0)
  □ Desktop ≥1024px tested

□ Visual Artifacts
  □ Baseline screenshots stored
  □ Diff images generated (if changes)
  □ Pixel diff < threshold (0.1)
  □ Intentional changes approved

═══════════════════════════════════════════════════════
GATE 4: ERROR HANDLING & RESILIENCE (NFR10, 11)
═══════════════════════════════════════════════════════
□ Error Scenarios
  □ GitHub rate limit handled gracefully
  □ Malformed markdown displays error without breaking
  □ Invalid Mermaid shows inline error
  □ Network failure shows retry button
  □ Ollama unavailable shows clear error

□ Console Monitoring
  □ No JavaScript errors (onlyErrors=true)
  □ No 404s in network tab
  □ No CORS errors
  □ Clean browser console on happy path

□ Error Artifacts
  □ Error screenshots captured
  □ Console error logs saved
  □ Network failure scenarios documented

═══════════════════════════════════════════════════════
GATE 5: ACCESSIBILITY (NFR8, FR42)
═══════════════════════════════════════════════════════
□ Keyboard Navigation
  □ Ctrl+K/Cmd+K focuses search
  □ Ctrl+N/Cmd+N creates new conversation
  □ Esc closes modals/panels
  □ Tab order logical
  □ All interactive elements accessible

□ WCAG 2.1 AA Compliance
  □ Color contrast verified
  □ ARIA labels present
  □ Semantic HTML used
  □ Focus indicators visible
  □ Alt text on images

□ Accessibility Artifacts
  □ Keyboard navigation video recorded
  □ Contrast audit report
  □ axe-core violations = 0

═══════════════════════════════════════════════════════
GATE 6: INTEGRATION HEALTH (FR37-39)
═══════════════════════════════════════════════════════
□ External Services
  □ GitHub API integration tested
  □ Ollama connectivity validated
  □ pgAdmin accessible at :5050
  □ Backend health endpoint returns 200

□ MCP Integration
  □ Playwright MCP programmatic launch works
  □ Screenshot capture successful
  □ Console monitoring active
  □ Test plan generation validated (FR44)

□ Integration Artifacts
  □ API response samples saved
  □ Service health checks documented
  □ Integration test logs clean

═══════════════════════════════════════════════════════
FINAL DECISION MATRIX
═══════════════════════════════════════════════════════
Total Gates: 6
Gates Passed: ___/6
Critical Issues: ___
Blocking Issues: ___

Decision:
[ ] PASS - All gates passed, ready for release
[ ] PASS WITH CONCERNS - Minor issues documented, release approved
[ ] FAIL - Blocking issues found, fix before release
[ ] WAIVED - Issues accepted, documented rationale

Reviewed By: Quinn (QA)
Date: __________
Artifacts Location: .ai/e2e-test-results/
```

---

## Implementation Roadmap

### Phase 1: Foundation (Story 1.6)
- **Deliverable:** First Playwright MCP test for "Hello BMADFlow"
- **Setup:** Install Playwright, configure MCP integration
- **Test:** Basic navigation + screenshot capture

### Phase 2: Explorer Flow (Story 3.2-3.6)
- **Deliverable:** Complete Browse Documentation tests
- **Setup:** Visual baseline screenshots
- **Tests:** File tree, markdown rendering, Mermaid diagrams

### Phase 3: Sync Flow (Story 2.5-2.6)
- **Deliverable:** Sync operation E2E tests
- **Setup:** Performance monitoring
- **Tests:** Sync trigger, progress, completion, error handling

### Phase 4: Chat Flow (Story 5.4-5.5)
- **Deliverable:** AI Chat with source navigation tests
- **Setup:** LLM response mocking
- **Tests:** Chat flow, source attribution, history

### Phase 5: Quality Gates (Before Release)
- **Deliverable:** Full 6-gate quality checklist execution
- **Setup:** Automated gate validation
- **Output:** Release readiness report

---

## Recommended File Structure

```
frontend/tests/e2e/
├── critical-flows/
│   ├── browse-documentation.spec.ts
│   ├── sync-projectdoc.spec.ts
│   └── ai-chat-sources.spec.ts
├── visual-regression/
│   ├── baselines/              # Golden screenshots
│   │   ├── browse/
│   │   ├── sync/
│   │   └── chat/
│   ├── current/                # Test run screenshots
│   └── diffs/                  # Visual diff images
├── debug-workflows/
│   ├── failure-debug.ts
│   ├── performance-analysis.ts
│   └── browser-compat.ts
├── playwright-mcp-helpers/
│   ├── screenshot-helper.ts
│   ├── console-monitor.ts
│   └── visual-diff.ts
└── setup/
    ├── test-data.ts            # E2E fixtures
    └── global-setup.ts
```

---

## Success Metrics

### Quality Metrics
- ✅ **100% critical path coverage** - All 3 flows tested
- ✅ **Zero visual regressions** - Pixel diff < 0.1 threshold
- ✅ **Performance validated** - All NFR targets met
- ✅ **Console clean** - No JavaScript errors
- ✅ **Accessibility compliant** - WCAG 2.1 AA

### Process Metrics
- ✅ **Test execution time** - <10min for full E2E suite
- ✅ **Debug time reduction** - <30min from failure to root cause
- ✅ **Visual regression detection** - <5min per flow
- ✅ **Cross-browser validation** - 3 browsers in <15min

---

## Related Documentation

- **Testing Strategy:** [docs/architecture/testing-strategy.md](../architecture/testing-strategy.md)
- **PRD Testing Requirements:** [docs/prd.md#testing-requirements](../prd.md)
- **Early Test Architecture:** [docs/qa/early-test-architecture.md](./early-test-architecture.md)
- **Playwright MCP Documentation:** https://github.com/browserbase/mcp-server-playwright

---

**Document Status:** ✅ Approved for Implementation
**Next Action:** Execute Phase 1 (Story 1.6) - First Playwright MCP test
