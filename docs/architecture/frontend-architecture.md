# Frontend Architecture

> **📖 Implementation Guide**: All code examples in this document follow patterns from [docs/context/frontend/shadcn-components.md](../context/frontend/shadcn-components.md). See [Code Examples Policy](code-examples-policy.md) for mandatory consistency rules. Use `mcp__shadcn__getComponent` for latest component documentation.

## Overview

BMADFlow's frontend is a **React 18+ Single Page Application (SPA)** built with TypeScript, Vite, and shadcn/ui Dashboard template. The architecture emphasizes component reusability, type safety through shared TypeScript definitions, and developer-first UX patterns (file trees, markdown rendering, split-view layouts).

**Key Architectural Principles:**
- **Component-Based Architecture**: Reusable React functional components
- **Type Safety**: TypeScript throughout, shared types from backend
- **Declarative UI**: React hooks for state and side effects
- **Performance First**: Code splitting, lazy loading, virtual scrolling
- **Accessibility**: WCAG 2.1 AA compliance via shadcn/ui primitives
- **Developer Experience**: Hot reload, ESLint/Prettier, clear folder structure

## Technology Stack

**Core Framework:**
- React 18+ (functional components, hooks)
- TypeScript 5.x+
- Vite 5.x+ (build tool, dev server)

**UI & Styling:**
- shadcn/ui (component library with Dashboard template)
- Tailwind CSS 3.x+ (utility-first styling)
- Lucide React (icon library)

**State Management:**
- Zustand 4.x+ (lightweight global state)
- React Context API (theme, auth context - if needed)
- TanStack Query / React Query (server state management)

**Routing:**
- React Router 6.x+ (client-side routing)

**API Communication:**
- Axios 1.x+ (HTTP client with interceptors)

**Content Rendering:**
- react-markdown 9.x+ (markdown to React components)
- react-prism-renderer (code syntax highlighting)
- react-mermaid2 (Mermaid diagram rendering)
- react-arborist (virtual file tree)

## Architecture Layers

### 1. Pages (Route Components)

**Purpose**: Top-level route components corresponding to application screens

**Structure:**
```
frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx              # Dashboard metrics + activity
│   │   ├── Projects.tsx               # Projects card grid view
│   │   ├── ProjectOverview.tsx        # Single project details + ProjectDocs
│   │   ├── DocumentationExplorer.tsx  # File tree + content viewer
│   │   ├── Chat.tsx                   # AI chatbot interface
│   │   ├── Configuration.tsx          # LLM provider configuration
│   │   └── NotFound.tsx               # 404 error page
```

**Responsibilities:**
- Define page-level layout
- Compose feature components
- Handle route parameters
- Manage page-level state
- Handle loading/error states for page data

**Example Page Component:**
```tsx
export function DocumentationExplorer() {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: fileTree, isLoading, error } = useFileTree(projectId);
  const [selectedFile, setSelectedFile] = useState<FileNode | null>(null);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay error={error} />;

  return (
    <div className="flex h-full">
      <FileTreePanel
        fileTree={fileTree}
        onSelectFile={setSelectedFile}
        className="w-1/4 border-r"
      />
      <ContentViewer
        file={selectedFile}
        className="w-3/4"
      />
    </div>
  );
}
```

---

### 2. Feature Components

**Purpose**: Reusable feature-specific components with business logic

**Structure:**
```
frontend/
├── src/
│   ├── features/
│   │   ├── projects/
│   │   │   ├── ProjectCard.tsx
│   │   │   ├── ProjectList.tsx
│   │   │   ├── CreateProjectDialog.tsx
│   │   │   └── ProjectDocCard.tsx
│   │   ├── explorer/
│   │   │   ├── FileTreePanel.tsx
│   │   │   ├── ContentViewer.tsx
│   │   │   ├── MarkdownRenderer.tsx
│   │   │   ├── CSVViewer.tsx
│   │   │   ├── CodeViewer.tsx
│   │   │   └── TableOfContents.tsx
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   ├── SourcePanel.tsx
│   │   │   ├── ConversationHistory.tsx
│   │   │   └── LLMProviderSelector.tsx
│   │   ├── dashboard/
│   │   │   ├── MetricCard.tsx
│   │   │   ├── ActivityFeed.tsx
│   │   │   └── WelcomeCard.tsx
│   │   └── configuration/
│   │       ├── LLMProviderTable.tsx
│   │       └── AddLLMProviderDialog.tsx
```

**Responsibilities:**
- Implement feature-specific UI logic
- Manage local component state
- Call API hooks for data fetching
- Handle user interactions
- Compose UI components

**Example Feature Component:**
```tsx
interface FileTreePanelProps {
  fileTree: FileNode[];
  onSelectFile: (file: FileNode) => void;
  className?: string;
}

export function FileTreePanel({ fileTree, onSelectFile, className }: FileTreePanelProps) {
  return (
    <div className={cn("overflow-auto", className)}>
      <Tree
        data={fileTree}
        onSelect={(node) => onSelectFile(node)}
        virtualizeOptions={{ overscan: 10 }}
      >
        {(node) => <FileTreeNode node={node} />}
      </Tree>
    </div>
  );
}
```

---

### 3. UI Components (shadcn/ui)

**Purpose**: Reusable UI primitives from shadcn/ui library

**Structure:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/                    # shadcn/ui components (installed via CLI)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── input.tsx
│   │   │   ├── table.tsx
│   │   │   ├── toast.tsx
│   │   │   ├── tooltip.tsx
│   │   │   └── ...
│   │   ├── layout/                # Layout components from Dashboard template
│   │   │   ├── AppShell.tsx       # Root layout with sidebar + header
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── Breadcrumb.tsx
│   │   └── common/                # Custom shared components
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorDisplay.tsx
│   │       ├── EmptyState.tsx
│   │       └── ConfirmDialog.tsx
```

**shadcn/ui Philosophy:**
- Components are **copied into your project** (not npm package)
- Full control over customization
- Built on Radix UI primitives (accessibility)
- Styled with Tailwind CSS
- TypeScript-first

**Dashboard Template Components:**
- `AppShell`: Root layout with responsive sidebar, header, breadcrumbs
- `Sidebar`: Collapsible navigation sidebar with project context
- `Header`: Top header with search, user menu, notifications
- `Breadcrumb`: Dynamic breadcrumb navigation

**Example UI Component Usage:**
```tsx
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function ProjectCard({ project }: { project: Project }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{project.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{project.description}</p>
        <Button className="mt-4" asChild>
          <Link to={`/projects/${project.id}`}>View Project</Link>
        </Button>
      </CardContent>
    </Card>
  );
}
```

---

### 4. API Layer (Hooks & Services)

**Purpose**: Abstract API communication with type-safe hooks

**Structure:**
```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts              # Axios instance with interceptors
│   │   ├── hooks/
│   │   │   ├── useProjects.ts     # Project CRUD hooks
│   │   │   ├── useProjectDocs.ts  # ProjectDoc CRUD + sync hooks
│   │   │   ├── useDocuments.ts    # Document retrieval hooks
│   │   │   ├── useFileTree.ts     # File tree hook
│   │   │   ├── useConversations.ts # Conversation hooks
│   │   │   ├── useMessages.ts     # Message send/receive hooks
│   │   │   ├── useLLMProviders.ts # LLM provider config hooks
│   │   │   ├── useSearch.ts       # Vector search hook
│   │   │   └── useDashboard.ts    # Dashboard metrics hooks
│   │   ├── services/
│   │   │   ├── projectService.ts
│   │   │   ├── chatService.ts
│   │   │   └── ...
│   │   └── types/                 # Shared TypeScript types from backend
│   │       ├── project.ts
│   │       ├── projectDoc.ts
│   │       ├── document.ts
│   │       ├── conversation.ts
│   │       └── ...
```

**Axios Client Configuration:**
```tsx
// src/api/client.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30s timeout
});

// Request interceptor (add auth tokens if needed in future)
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token to headers if exists
    // const token = localStorage.getItem('auth_token');
    // if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (handle errors globally)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Global error handling
    if (error.response?.status === 404) {
      console.error('Resource not found:', error.response.data);
    } else if (error.response?.status === 500) {
      console.error('Server error:', error.response.data);
    }
    return Promise.reject(error);
  }
);
```

**React Query Hooks Pattern:**
```tsx
// src/api/hooks/useProjects.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../client';
import { Project, CreateProjectRequest } from '../types/project';

export function useProjects() {
  return useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: async () => {
      const { data } = await apiClient.get<Project[]>('/projects');
      return data;
    },
  });
}

export function useProject(projectId: string) {
  return useQuery<Project>({
    queryKey: ['projects', projectId],
    queryFn: async () => {
      const { data } = await apiClient.get<Project>(`/projects/${projectId}`);
      return data;
    },
    enabled: !!projectId,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: CreateProjectRequest) => {
      const { data } = await apiClient.post<Project>('/projects', request);
      return data;
    },
    onSuccess: () => {
      // Invalidate projects list to refetch
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}
```

**Sync Operation Hook (with progress):**
```tsx
// src/api/hooks/useProjectDocs.ts
export function useSyncProjectDoc() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (projectDocId: string) => {
      const { data } = await apiClient.post(`/project-docs/${projectDocId}/sync`);
      return data;
    },
    onSuccess: (data, projectDocId) => {
      // Show success toast
      toast.success('Sync completed successfully');

      // Invalidate project doc query to refetch updated sync status
      queryClient.invalidateQueries({ queryKey: ['project-docs', projectDocId] });

      // Invalidate file tree (new files may have been added)
      queryClient.invalidateQueries({ queryKey: ['file-tree'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Sync failed');
    },
  });
}
```

---

### 5. State Management

**Global State (Zustand):**

**Purpose**: Lightweight global state for app-wide concerns

**Use Cases:**
- Selected project context
- Theme preferences (light/dark)
- UI state (sidebar collapsed/expanded)
- Active conversation ID

**Store Structure:**
```tsx
// src/store/appStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppState {
  // Current project context
  selectedProjectId: string | null;
  setSelectedProjectId: (id: string | null) => void;

  // UI state
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;

  // Theme
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      selectedProjectId: null,
      setSelectedProjectId: (id) => set({ selectedProjectId: id }),

      sidebarCollapsed: false,
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

      theme: 'light',
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'bmadflow-app-state', // localStorage key
    }
  )
);
```

**Usage:**
```tsx
function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useAppStore();

  return (
    <aside className={cn("transition-all", sidebarCollapsed ? "w-16" : "w-64")}>
      <Button onClick={toggleSidebar}>
        {sidebarCollapsed ? <ChevronRight /> : <ChevronLeft />}
      </Button>
      {/* Sidebar content */}
    </aside>
  );
}
```

**Server State (React Query):**

**Purpose**: Cache and synchronize server state

**Benefits:**
- Automatic background refetching
- Optimistic updates
- Cache invalidation
- Loading/error states
- Request deduplication

**Configuration:**
```tsx
// src/main.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>
);
```

---

### 6. Routing

**Router Configuration:**
```tsx
// src/router.tsx
import { createBrowserRouter } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: 'projects',
        element: <Projects />,
      },
      {
        path: 'projects/:projectId',
        element: <ProjectOverview />,
      },
      {
        path: 'projects/:projectId/explorer',
        element: <DocumentationExplorer />,
      },
      {
        path: 'projects/:projectId/chat',
        element: <Chat />,
      },
      {
        path: 'configuration',
        element: <Configuration />,
      },
      {
        path: '*',
        element: <NotFound />,
      },
    ],
  },
]);
```

**Navigation Patterns:**
```tsx
// Programmatic navigation
import { useNavigate } from 'react-router-dom';

function ProjectCard({ project }: { project: Project }) {
  const navigate = useNavigate();

  return (
    <Card onClick={() => navigate(`/projects/${project.id}`)}>
      {/* Card content */}
    </Card>
  );
}

// Link navigation
import { Link } from 'react-router-dom';

<Link to={`/projects/${projectId}/explorer`}>Browse Docs</Link>
```

---

## Key Feature Implementations

### 1. File Tree Navigation (react-arborist)

**Purpose**: Virtual scrolling file tree for large documentation sets

**Implementation:**
```tsx
import { Tree } from 'react-arborist';

interface FileNode {
  id: string;
  name: string;
  type: 'file' | 'folder';
  path: string;
  children?: FileNode[];
}

export function FileTreePanel({ projectId }: { projectId: string }) {
  const { data: fileTree } = useFileTree(projectId);
  const [selectedNode, setSelectedNode] = useState<FileNode | null>(null);

  return (
    <Tree
      data={fileTree}
      idAccessor="id"
      openByDefault={false}
      width="100%"
      height={800}
      indent={24}
      rowHeight={32}
      onSelect={(nodes) => setSelectedNode(nodes[0]?.data)}
    >
      {({ node, style, dragHandle }) => (
        <div style={style} className="flex items-center gap-2 px-2 hover:bg-accent">
          <div {...dragHandle}>
            {node.isLeaf ? (
              <FileIcon className="h-4 w-4" />
            ) : (
              node.isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />
            )}
          </div>
          <span className="text-sm">{node.data.name}</span>
        </div>
      )}
    </Tree>
  );
}
```

**Performance Optimization:**
- Virtual scrolling handles 1000+ files
- Lazy loading of folder children
- Memoized tree nodes

---

### 2. Markdown Rendering with react-markdown

**Implementation:**
```tsx
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

export function MarkdownRenderer({ content }: { content: string }) {
  return (
    <div className="prose prose-slate max-w-none dark:prose-invert">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <SyntaxHighlighter
                style={vscDarkPlus}
                language={match[1]}
                PreTag="div"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          a({ node, href, children, ...props }) {
            // Handle relative links
            if (href?.startsWith('./') || href?.startsWith('../')) {
              return (
                <Link to={resolveRelativePath(href)} className="text-primary hover:underline">
                  {children}
                </Link>
              );
            }
            // External links open in new tab
            return (
              <a href={href} target="_blank" rel="noopener noreferrer" {...props}>
                {children}
              </a>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
```

---

### 3. Mermaid Diagram Rendering

**Implementation:**
```tsx
import mermaid from 'mermaid';
import { useEffect, useRef } from 'react';

mermaid.initialize({ startOnLoad: false, theme: 'default' });

export function MermaidDiagram({ chart }: { chart: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current) {
      try {
        mermaid.render('mermaid-diagram', chart).then(({ svg }) => {
          if (ref.current) {
            ref.current.innerHTML = svg;
          }
        });
      } catch (error) {
        console.error('Mermaid rendering failed:', error);
        if (ref.current) {
          ref.current.innerHTML = `<pre class="text-destructive">Invalid Mermaid syntax</pre>`;
        }
      }
    }
  }, [chart]);

  return <div ref={ref} className="my-4" />;
}
```

---

### 4. Chat Interface with Source Attribution

**Implementation:**
```tsx
export function ChatInterface({ projectId }: { projectId: string }) {
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const { data: messages } = useMessages(conversationId);
  const sendMessage = useSendMessage();

  const handleSend = async () => {
    if (!input.trim()) return;

    // Create conversation if first message
    if (!conversationId) {
      const newConversation = await createConversation(projectId);
      setConversationId(newConversation.id);
    }

    await sendMessage.mutateAsync({
      conversationId: conversationId!,
      content: input,
    });

    setInput('');
  };

  return (
    <div className="flex flex-col h-full">
      <MessageList messages={messages} />

      <div className="p-4 border-t">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask a question..."
          />
          <Button onClick={handleSend} disabled={!input.trim()}>
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}

function MessageList({ messages }: { messages?: Message[] }) {
  return (
    <div className="flex-1 overflow-auto p-4 space-y-4">
      {messages?.map((message) => (
        <div
          key={message.id}
          className={cn(
            "flex",
            message.role === 'user' ? 'justify-end' : 'justify-start'
          )}
        >
          <Card className={cn(
            "max-w-2xl",
            message.role === 'user' ? 'bg-primary text-primary-foreground' : ''
          )}>
            <CardContent className="pt-4">
              <p className="whitespace-pre-wrap">{message.content}</p>

              {message.sources && message.sources.length > 0 && (
                <div className="mt-4 pt-4 border-t">
                  <p className="text-sm font-medium mb-2">Sources:</p>
                  <div className="flex flex-wrap gap-2">
                    {message.sources.map((source, idx) => (
                      <SourceLink key={idx} source={source} />
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      ))}
    </div>
  );
}
```

---

## Performance Optimizations

### Code Splitting

**Route-Based Splitting:**
```tsx
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Chat = lazy(() => import('./pages/Chat'));
const Explorer = lazy(() => import('./pages/DocumentationExplorer'));

// Wrap routes in Suspense
<Suspense fallback={<LoadingSpinner />}>
  <Routes>
    <Route path="/" element={<Dashboard />} />
    <Route path="/chat" element={<Chat />} />
    <Route path="/explorer" element={<Explorer />} />
  </Routes>
</Suspense>
```

### Memoization

**Expensive Computations:**
```tsx
import { useMemo } from 'react';

function FileTreePanel({ fileTree }: { fileTree: FileNode[] }) {
  const flattenedTree = useMemo(() => {
    return flattenFileTree(fileTree); // Expensive operation
  }, [fileTree]);

  return <Tree data={flattenedTree} />;
}
```

**Component Memoization:**
```tsx
import { memo } from 'react';

export const FileTreeNode = memo(({ node }: { node: FileNode }) => {
  return (
    <div className="flex items-center gap-2">
      <FileIcon />
      <span>{node.name}</span>
    </div>
  );
});
```

### Virtual Scrolling

**react-arborist** handles virtual scrolling for file trees

**react-window** for long message lists (optional enhancement):
```tsx
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={messages.length}
  itemSize={80}
  width="100%"
>
  {({ index, style }) => (
    <div style={style}>
      <MessageCard message={messages[index]} />
    </div>
  )}
</FixedSizeList>
```

---

## Accessibility (WCAG 2.1 AA)

### shadcn/ui Compliance

All shadcn/ui components are built on **Radix UI primitives**, which provide:
- Keyboard navigation
- ARIA attributes
- Focus management
- Screen reader support

### 🎯 Required Accessibility Patterns

**Pattern Discovered**: Epic 5 Stories 5.5 and 5.6 (both required SheetDescription fix during QA)

#### 1. Sheet Component with Description (CRITICAL)

**WCAG 2.1 AA Requirement**: All Radix UI Sheet primitives MUST include `SheetDescription` for screen readers, even if visually hidden.

**Why This Pattern?**
- **Problem**: Radix UI Sheet emits `aria-describedby` warnings without SheetDescription → accessibility compliance failure
- **Solution**: Always add SheetDescription with `sr-only` class (screen reader only, visually hidden)
- **Impact**: Satisfies WCAG 2.1 AA requirements for dialog descriptions

**Implementation:**

```tsx
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetClose,
} from '@/components/ui/sheet';

// ✅ CORRECT: Sheet with SheetDescription
export function SourcePanel({ source, onClose }: SourcePanelProps) {
  return (
    <Sheet open={!!source} onOpenChange={onClose}>
      <SheetContent side="right" className="w-2/5">
        <SheetHeader>
          <SheetTitle>{source.file_path}</SheetTitle>
          {/* REQUIRED: SheetDescription with sr-only for screen readers */}
          <SheetDescription className="sr-only">
            View document source with content preview
          </SheetDescription>
        </SheetHeader>
        {/* Sheet body content */}
      </SheetContent>
    </Sheet>
  );
}

// ❌ INCORRECT: Sheet without SheetDescription (accessibility violation)
export function SourcePanel({ source, onClose }: SourcePanelProps) {
  return (
    <Sheet open={!!source} onOpenChange={onClose}>
      <SheetContent side="right" className="w-2/5">
        <SheetHeader>
          <SheetTitle>{source.file_path}</SheetTitle>
          {/* Missing SheetDescription → aria-describedby warning */}
        </SheetHeader>
      </SheetContent>
    </Sheet>
  );
}
```

**Best Practices:**
1. **Always include SheetDescription** - even if content seems self-explanatory
2. **Use descriptive text** - explain what the sheet contains/does ("View conversation history", "Document source preview")
3. **Apply sr-only class** - visually hide description while keeping it accessible to screen readers
4. **Test with screen readers** - verify NVDA/JAWS/VoiceOver announce description

**Component Checklist:**
- [ ] Sheet components include SheetDescription with sr-only class
- [ ] Form inputs have associated labels (htmlFor / aria-label)
- [ ] Interactive elements keyboard accessible (Tab, Enter, Escape)
- [ ] Color contrast meets WCAG 2.1 AA (4.5:1 for text)

#### 2. Dialog Component with Description

**Same pattern applies to Dialog primitives:**

```tsx
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';

export function CreateProjectDialog({ isOpen, onClose }: DialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create New Project</DialogTitle>
          <DialogDescription className="sr-only">
            Form to create a new project with name and description
          </DialogDescription>
        </DialogHeader>
        {/* Dialog form content */}
      </DialogContent>
    </Dialog>
  );
}
```

### Custom Accessibility Patterns

**Focus Management:**
```tsx
import { useEffect, useRef } from 'react';

function Dialog({ isOpen }: { isOpen: boolean }) {
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) {
      closeButtonRef.current?.focus(); // Focus close button on open
    }
  }, [isOpen]);

  return (
    <DialogPrimitive.Root open={isOpen}>
      <DialogPrimitive.Content>
        <DialogPrimitive.Close ref={closeButtonRef}>Close</DialogPrimitive.Close>
      </DialogPrimitive.Content>
    </DialogPrimitive.Root>
  );
}
```

**Keyboard Shortcuts:**
```tsx
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    // Ctrl/Cmd + K: Focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      searchInputRef.current?.focus();
    }

    // Esc: Close panels
    if (e.key === 'Escape') {
      closeAllPanels();
    }
  };

  document.addEventListener('keydown', handleKeyDown);
  return () => document.removeEventListener('keydown', handleKeyDown);
}, []);
```

**Color Contrast:**
- shadcn/ui default theme meets WCAG AA standards
- Tested with Lighthouse and axe DevTools

### Automated Accessibility Testing

**Recommended Tools:**
- `jest-axe` or `@axe-core/react` for automated a11y checks in component tests
- Lighthouse CI for accessibility audits in CI/CD pipeline
- axe DevTools browser extension for manual testing

**Example Component Test with jest-axe:**
```tsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { SourcePanel } from '@/features/chat/SourcePanel';

expect.extend(toHaveNoViolations);

test('SourcePanel has no accessibility violations', async () => {
  const { container } = render(
    <SourcePanel
      source={{ document_id: '123', file_path: 'docs/prd.md', header_anchor: null }}
      onClose={() => {}}
    />
  );

  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

---

## Related Documentation

- **High Level Architecture**: [high-level-architecture.md](high-level-architecture.md)
- **UX Specification**: [/docs/ux-specification.md](../ux-specification.md)
- **shadcn/ui Components**: [/docs/context/frontend/shadcn-components.md](../context/frontend/shadcn-components.md)
- **Component Library**: Use `mcp__shadcn__getComponent` for documentation during development

---
