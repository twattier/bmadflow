# Story 1.5: Dashboard Shell with 4-View Navigation

**Status:** Draft

## Story

**As a** user,
**I want** dashboard with tab navigation between 4 views,
**so that** I can explore different aspects of my project documentation.

## Acceptance Criteria

1. React application created with Vite + TypeScript + Tailwind CSS
2. shadcn/ui components installed and configured (button, card, tabs, navigation)
3. Top navigation bar displays: BMADFlow logo, project name selector (hardcoded to single project for POC), sync status indicator
4. Tab navigation shows 4 tabs with icons and labels: 📋 Scoping, 🏗️ Architecture, 📊 Epics, 🔍 Detail
5. Clicking tab navigates to corresponding route using React Router (`/scoping`, `/architecture`, `/epics`, `/detail`)
6. Active tab visually highlighted (underline + bold text per UX spec)
7. Each view renders placeholder content initially (Scoping and Detail views implemented first, Architecture and Epics added in Epic 3)
8. Responsive design works on desktop (1920×1080 and 1440×900 tested)
9. Manual test confirms: navigation between implemented views works smoothly, no console errors

## Epic

[Epic 1: Foundation, GitHub Integration & Dashboard Shell](../epics/epic-1-foundation-github-dashboard.md)

## Dependencies

- Story 1.1: Project Infrastructure Setup (frontend service running)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-01 | 1.0 | Story extracted from PRD v1.0 | Sarah (PO) |
