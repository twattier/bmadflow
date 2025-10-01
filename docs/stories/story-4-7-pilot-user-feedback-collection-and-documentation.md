# Story 4.7: Pilot User Feedback Collection and Documentation

**Status:** Draft

## Story

**As a** pilot user,
**I want** feedback form to rate my BMADFlow experience and access to user documentation,
**so that** the PM can measure POC success and I can learn how to use the platform effectively.

## Acceptance Criteria

1. Feedback button in dashboard header (icon: 💬)
2. Modal form with fields: (1) Overall rating (1-5 stars), (2) "Is BMADFlow better than GitHub?" (Yes/No), (3) Favorite feature (dropdown), (4) Improvement suggestions (textarea)
3. Form submits to `/api/feedback` endpoint, stored in database
4. Thank you message after submission: "Thank you! Your feedback helps us improve BMADFlow."
5. PM can export feedback via admin endpoint: GET `/api/admin/feedback?project_id=` (CSV export)
6. Feedback form accessible from all views (persistent header button)
7. Help button (icon: ❓) in dashboard header opens user documentation modal or sidebar
8. User documentation includes: (a) Quick start guide with screenshots, (b) How to sync repositories, (c) How to navigate the 4 views, (d) How to interpret status colors, (e) FAQ section
9. Documentation written in markdown, rendered using existing MarkdownRenderer component
10. Documentation stored in `/docs/user-guide.md` file, loaded dynamically by frontend

## Epic

[Epic 4: Epic-Story Relationship Visualization](../epics/epic-4-relationship-visualization.md)

## Dependencies

- Story 1.5: Dashboard Shell with 4-View Navigation (header component)
- Story 3.2: Detail View - Markdown Rendering (reuse for documentation)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
