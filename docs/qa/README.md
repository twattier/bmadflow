# QA Documentation Hub

**Owner:** Quinn (Test Architect & Quality Advisor)
**Last Updated:** 2025-10-06

## Overview

This directory contains comprehensive quality assurance documentation for BMADFlow, including test strategies, quality gates, architectural testability assessments, and testing best practices.

---

## 📚 Core Documents

### 1. [Early Test Architecture](./early-test-architecture.md)
**Purpose:** Foundation for test-first development from Story 1.1

**Key Topics:**
- Test infrastructure setup (pytest, vitest, Playwright)
- RED-GREEN-REFACTOR pattern
- Test data management (builders, factories, fixtures)
- Backend/frontend test environment configuration
- Testing best practices and patterns

**When to Use:**
- Starting any new story (test-first approach)
- Setting up test infrastructure
- Creating test data builders
- Establishing testing patterns

---

### 2. [Playwright MCP E2E Testing Strategy](./playwright-mcp-e2e-strategy.md)
**Purpose:** Comprehensive E2E testing using Playwright MCP as quality cornerstone

**Key Topics:**
- Critical E2E test scenarios (Browse, Sync, Chat)
- Playwright MCP integration (FR37-39, FR44)
- Visual regression testing framework
- Debug workflows (failure analysis, performance detection)
- 6-gate quality checklist

**When to Use:**
- Writing E2E tests for user flows
- Visual regression testing
- Performance validation
- Debugging test failures
- Pre-release quality gates

---

### 3. [Architecture Testability Review](./architecture-testability-review.md) *(Coming Soon)*
**Purpose:** Assessment of BMADFlow architecture from testability perspective

**Key Topics:**
- Controllability, observability, debuggability analysis
- External service dependency risks
- Test isolation strategies
- Quality attribute validation

**When to Use:**
- Architectural design review
- Identifying testability gaps
- Risk assessment for external dependencies

---

## 🎯 Quick Start Guide

### For Developers Starting Story 1.1-1.3

1. **Read:** [Early Test Architecture - Layer 1: Test Infrastructure](./early-test-architecture.md#layer-1-test-infrastructure-story-11-13)
2. **Setup:** Backend test environment (pytest, conftest.py)
3. **Setup:** Frontend test environment (vitest, Playwright)
4. **Write:** First RED-GREEN-REFACTOR test

### For Developers Writing API Tests (Epic 2-4)

1. **Read:** [Early Test Architecture - Pattern 1: RED-GREEN-REFACTOR](./early-test-architecture.md#pattern-1-red-green-refactor-all-stories)
2. **Read:** [Early Test Architecture - Pattern 2: Mock External Dependencies](./early-test-architecture.md#pattern-2-mock-external-dependencies-epic-2-4)
3. **Use:** Test data builders for complex objects
4. **Follow:** AAA pattern (Arrange-Act-Assert)

### For Developers Writing E2E Tests (Story 1.6, Epic 3-5)

1. **Read:** [Playwright MCP E2E Strategy - Critical Scenarios](./playwright-mcp-e2e-strategy.md#critical-e2e-test-scenarios)
2. **Setup:** Playwright MCP integration
3. **Create:** Visual baselines for flows
4. **Write:** E2E tests using MCP tools

### For Pre-Release Quality Validation

1. **Execute:** [6-Gate E2E Quality Checklist](./playwright-mcp-e2e-strategy.md#e2e-quality-gate-checklist)
2. **Validate:** Performance targets (NFR1-4, 9)
3. **Verify:** Visual regression tests pass
4. **Check:** Console errors clean
5. **Generate:** Release readiness report

---

## 📊 Quality Standards

### Coverage Targets (NFR18)

| Layer | Target | Tool |
|-------|--------|------|
| Backend Services | 70%+ | pytest-cov |
| Backend Repositories | 70%+ | pytest-cov |
| Frontend Components | 60%+ | vitest coverage |
| E2E Critical Flows | 100% | Playwright |

### Performance Targets (NFR1-4, 9)

| Operation | Target | Validation Method |
|-----------|--------|-------------------|
| Markdown Render | <1s | Playwright performance API |
| RAG Query (Cloud) | <3s | Playwright network timing |
| RAG Query (Ollama) | <10s | Playwright network timing |
| Vector Search | <500ms | Backend integration tests |
| Sync Operation | <5min | E2E test with timeout |
| Panel Animations | 60fps | Visual inspection + screenshots |

### Quality Gates

**Gate 1: Critical Path Coverage**
- Browse Documentation Flow ✅
- Sync ProjectDoc Flow ✅
- AI Chat Flow ✅

**Gate 2: Performance Validation**
- All NFR targets met ✅

**Gate 3: Visual Regression**
- Pixel diff < 0.1 threshold ✅
- WCAG 2.1 AA compliance ✅

**Gate 4: Error Handling**
- Console errors = 0 ✅
- Graceful degradation ✅

**Gate 5: Accessibility**
- Keyboard navigation ✅
- ARIA compliance ✅

**Gate 6: Integration Health**
- External services validated ✅
- MCP integration working ✅

---

## 🔧 Testing Tools & Configuration

### Backend Testing Stack

```bash
# Test Framework
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Mocking & Data
pytest-mock==3.12.0
faker==20.1.0
freezegun==1.4.0

# API Testing
httpx==0.25.2
```

**Configuration:** `backend/pytest.ini`, `backend/.env.test`

### Frontend Testing Stack

```json
{
  "vitest": "^1.0.4",
  "@testing-library/react": "^14.1.2",
  "@testing-library/user-event": "^14.5.1",
  "@playwright/test": "^1.40.1",
  "@faker-js/faker": "^8.3.1"
}
```

**Configuration:** `frontend/vitest.config.ts`, `frontend/playwright.config.ts`

---

## 🚀 Test Execution Commands

### Backend Tests

```bash
# Run all tests with coverage
cd backend
pytest

# Run specific test file
pytest tests/integration/api/test_projects_api.py

# Run with verbose output
pytest -v

# View coverage report
open htmlcov/index.html
```

### Frontend Tests

```bash
# Run component tests
cd frontend
npm test

# Run with coverage
npm test -- --coverage

# Run E2E tests
npm run test:e2e

# Run E2E in UI mode
npx playwright test --ui

# Run specific E2E test
npx playwright test tests/e2e/browse-documentation.spec.ts
```

---

## 📁 Directory Structure

```
docs/qa/
├── README.md                           # This file
├── early-test-architecture.md          # Test-first development guide
├── playwright-mcp-e2e-strategy.md     # E2E testing strategy
├── architecture-testability-review.md  # Architecture assessment (coming soon)
└── gates/                              # Quality gate decisions
    └── {epic}.{story}-{slug}.yml      # Individual gate files
```

---

## 🎯 QA Command Reference

As Quinn (Test Architect), I offer these commands:

### Available Commands

1. **help** - Show command list
2. **gate {story}** - Execute quality gate decision for a story
3. **nfr-assess {story}** - Validate non-functional requirements
4. **review {story}** - Comprehensive review (QA Results + gate decision)
5. **risk-profile {story}** - Generate risk assessment matrix
6. **test-design {story}** - Create comprehensive test scenarios
7. **trace {story}** - Map requirements to tests using Given-When-Then
8. **exit** - Return to normal mode

**Example Usage:**
```
*review story-1-6-hello-bmadflow
*nfr-assess story-2-5-sync-orchestration
*test-design story-5-4-chat-ui
```

---

## 📖 Related Documentation

- **Testing Strategy:** [docs/architecture/testing-strategy.md](../architecture/testing-strategy.md)
- **PRD Testing Requirements:** [docs/prd.md#testing-requirements](../prd.md)
- **Architecture Overview:** [docs/architecture/high-level-architecture.md](../architecture/high-level-architecture.md)
- **Security & Performance:** [docs/architecture/security-performance.md](../architecture/security-performance.md)

---

## ✅ Quality Commitment

**BMADFlow Quality Standards:**

1. **Test-First Development** - Write tests before implementation
2. **70%+ Backend Coverage** - Enforce via pytest-cov
3. **100% Critical Path E2E** - All user flows tested
4. **Zero Visual Regression** - Baseline + diff validation
5. **Performance Validated** - All NFR targets met
6. **Accessibility Compliant** - WCAG 2.1 AA

**Quality Gate Decision:** PASS, PASS WITH CONCERNS, FAIL, or WAIVED

---

**Last Updated:** 2025-10-06
**Maintained By:** Quinn (Test Architect)
**Status:** ✅ Active
