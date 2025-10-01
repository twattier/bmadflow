# Frontend Architecture

## Component Organization

```
apps/web/src/
├── components/
│   ├── ui/            # shadcn/ui base components
│   ├── layout/        # Header, TabNavigation, Breadcrumbs, Sidebar
│   ├── cards/         # DocumentCard, StatusCard, EpicCard
│   ├── markdown/      # MarkdownRenderer, TableOfContents, CodeBlock, MermaidDiagram
│   ├── epics/         # EpicStoryTable, EpicStoryGraph, StatusRollupWidget
│   └── sync/          # SyncStatusIndicator, SyncProgressToast, ProjectSetupModal
├── pages/             # LandingPage, ScopingView, ArchitectureView, EpicsView, DetailView
├── services/          # apiClient, projectsService, documentsService, epicsService
├── hooks/             # useProjects, useDocuments, useSyncStatus, useToast
├── stores/            # ThemeContext, ProjectContext
├── utils/             # formatDate, parseMarkdown, validation
├── styles/            # globals.css, theme.css
├── App.tsx
└── main.tsx
```

## Routing Structure

```typescript
/ → Landing/Project Setup
/scoping → Scoping View
/architecture → Architecture View
/epics → Epics View
/detail/:documentId → Detail View
```

## State Management

- **Server State:** React Query (5-min stale time, automatic refetch on window focus)
- **UI State:** React Context (current project, theme)
- **Local State:** useState for component-specific state
- **Form State:** Controlled components with useState

## API Client Setup

```typescript
// Axios instance with interceptors
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// Response interceptor for global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log to Sentry, show toast notification
    return Promise.reject(error);
  }
);
```

---
