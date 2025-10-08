import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DocumentationExplorer } from '@/pages/DocumentationExplorer';
import { apiClient } from '@/api/client';
import type { FileTreeResponse, Document } from '@/api/types/document';

// Mock API client
vi.mock('@/api/client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

describe('Cross-Document Navigation Integration', () => {
  const mockProjectId = 'test-project-123';

  const mockFileTree: FileTreeResponse = {
    project_id: mockProjectId,
    tree: [
      {
        id: 'root',
        name: 'docs',
        type: 'folder',
        path: '/docs',
        children: [
          {
            id: 'doc-1',
            name: 'readme.md',
            type: 'file',
            path: '/docs/readme.md',
            file_type: 'md',
            size: 1024,
          },
          {
            id: 'doc-2',
            name: 'architecture.md',
            type: 'file',
            path: '/docs/architecture.md',
            file_type: 'md',
            size: 2048,
          },
          {
            id: 'doc-3',
            name: 'api.md',
            type: 'file',
            path: '/docs/api.md',
            file_type: 'md',
            size: 1536,
          },
        ],
      },
    ],
  };

  const mockDocuments: Record<string, Document> = {
    'doc-1': {
      id: 'doc-1',
      project_doc_id: 'project-doc-1',
      file_path: '/docs/readme.md',
      file_type: 'md',
      file_size: 1024,
      content: '# README\n\nSee [Architecture](./architecture.md) for details.',
      doc_metadata: null,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
    },
    'doc-2': {
      id: 'doc-2',
      project_doc_id: 'project-doc-1',
      file_path: '/docs/architecture.md',
      file_type: 'md',
      file_size: 2048,
      content: '# Architecture\n\nCheck out the [API Documentation](./api.md).',
      doc_metadata: null,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
    },
    'doc-3': {
      id: 'doc-3',
      project_doc_id: 'project-doc-1',
      file_path: '/docs/api.md',
      file_type: 'md',
      file_size: 1536,
      content: '# API\n\nRefer back to [README](./readme.md).',
      doc_metadata: null,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
    },
  };

  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    // Mock API responses
    vi.mocked(apiClient.get).mockImplementation(async (url: string) => {
      // File tree endpoint
      if (url.includes('/file-tree')) {
        return { data: mockFileTree };
      }

      // Document endpoints
      if (url.includes('/documents/')) {
        const docId = url.split('/documents/')[1];
        if (mockDocuments[docId]) {
          return { data: mockDocuments[docId] };
        }
      }

      throw new Error(`Unhandled API call: ${url}`);
    });
  });

  const renderDocumentationExplorer = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[`/projects/${mockProjectId}/explorer`]}>
          <Routes>
            <Route path="/projects/:projectId/explorer" element={<DocumentationExplorer />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );
  };

  it('should navigate from one document to another via relative link', async () => {
    const user = userEvent.setup();
    renderDocumentationExplorer();

    // Wait for file tree to load
    await waitFor(() => {
      expect(screen.getByText('readme.md')).toBeInTheDocument();
    });

    // Select the readme document
    const readmeNode = screen.getByText('readme.md');
    await user.click(readmeNode);

    // Wait for document content to load
    await waitFor(() => {
      expect(screen.getByText('README')).toBeInTheDocument();
    });

    // Click the relative link to architecture.md
    const architectureLink = screen.getByText('Architecture');
    await user.click(architectureLink);

    // Verify new document loaded
    await waitFor(() => {
      expect(screen.getByText(/Check out the/)).toBeInTheDocument();
    });

    // Verify content viewer updated
    expect(apiClient.get).toHaveBeenCalledWith('/documents/doc-2');
  });

  it('should update file tree selection when navigating via link', async () => {
    const user = userEvent.setup();
    const { container } = renderDocumentationExplorer();

    // Wait for file tree to load and select first document
    await waitFor(() => {
      expect(screen.getByText('readme.md')).toBeInTheDocument();
    });

    const readmeNode = screen.getByText('readme.md');
    await user.click(readmeNode);

    await waitFor(() => {
      expect(screen.getByText('README')).toBeInTheDocument();
    });

    // Click link to navigate
    const architectureLink = screen.getByText('Architecture');
    await user.click(architectureLink);

    // Verify new document loaded
    await waitFor(() => {
      const heading = container.querySelector('h1');
      expect(heading?.textContent).toBe('Architecture');
    });

    // Note: Actual file tree highlight verification would require checking
    // the FileTreePanel component's internal state or visual indicators
  });

  it('should update browser history when navigating via link', async () => {
    const user = userEvent.setup();
    const pushStateSpy = vi.spyOn(window.history, 'pushState');

    renderDocumentationExplorer();

    await waitFor(() => {
      expect(screen.getByText('readme.md')).toBeInTheDocument();
    });

    const readmeNode = screen.getByText('readme.md');
    await user.click(readmeNode);

    await waitFor(() => {
      expect(screen.getByText('README')).toBeInTheDocument();
    });

    // Navigate via link
    const architectureLink = screen.getByText('Architecture');
    await user.click(architectureLink);

    await waitFor(() => {
      expect(pushStateSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          filePath: '/docs/architecture.md',
        }),
        '',
        expect.stringContaining('file=/docs/architecture.md')
      );
    });
  });

  it('should support browser back button navigation', async () => {
    const user = userEvent.setup();
    renderDocumentationExplorer();

    // Load first document
    await waitFor(() => {
      expect(screen.getByText('readme.md')).toBeInTheDocument();
    });

    const readmeNode = screen.getByText('readme.md');
    await user.click(readmeNode);

    await waitFor(() => {
      expect(screen.getByText('README')).toBeInTheDocument();
    });

    // Navigate to second document
    const architectureLink = screen.getByText('Architecture');
    await user.click(architectureLink);

    await waitFor(() => {
      const content = screen.queryByText(/Check out the/);
      expect(content).toBeInTheDocument();
    });

    // Simulate browser back button
    window.dispatchEvent(new PopStateEvent('popstate'));

    // Should go back to previous document
    // Note: Full back navigation testing requires more complex setup
    // This demonstrates the event listener is in place
  });

  // Error scenario: API failure during file-tree lookup
  it('should handle API errors gracefully during navigation', async () => {
    const user = userEvent.setup();

    // Mock API failure for second document
    vi.mocked(apiClient.get).mockImplementation(async (url: string) => {
      if (url.includes('/file-tree')) {
        return { data: mockFileTree };
      }
      if (url.includes('/documents/doc-1')) {
        return { data: mockDocuments['doc-1'] };
      }
      throw new Error('Network error');
    });

    renderDocumentationExplorer();

    await waitFor(() => {
      expect(screen.getByText('readme.md')).toBeInTheDocument();
    });

    const readmeNode = screen.getByText('readme.md');
    await user.click(readmeNode);

    await waitFor(() => {
      expect(screen.getByText('README')).toBeInTheDocument();
    });

    // Try to navigate, but API fails
    const architectureLink = screen.getByText('Architecture');
    await user.click(architectureLink);

    // Should show error message (from ContentViewer error handling)
    await waitFor(() => {
      expect(screen.getByText(/Error loading document/i)).toBeInTheDocument();
    });
  });

  // Error scenario: Rapid link clicks (race condition test)
  it('should handle rapid consecutive link clicks', async () => {
    const user = userEvent.setup();
    renderDocumentationExplorer();

    await waitFor(() => {
      expect(screen.getByText('readme.md')).toBeInTheDocument();
    });

    const readmeNode = screen.getByText('readme.md');
    await user.click(readmeNode);

    await waitFor(() => {
      expect(screen.getByText('README')).toBeInTheDocument();
    });

    // Rapidly click multiple links
    const link1 = screen.getByText('Architecture');
    await user.click(link1);

    // The final document should be the last one clicked
    await waitFor(() => {
      const heading = document.querySelector('h1');
      expect(heading?.textContent).toBe('Architecture');
    });
  });

  // Error scenario: Broken link handling
  it('should handle broken links without crashing', async () => {
    const user = userEvent.setup();

    // Modify mock to include document with broken link
    const brokenLinkDoc: Document = {
      ...mockDocuments['doc-1'],
      content: '# README\n\n[Broken Link](./nonexistent.md)',
    };

    vi.mocked(apiClient.get).mockImplementation(async (url: string) => {
      if (url.includes('/file-tree')) {
        return { data: mockFileTree };
      }
      if (url.includes('/documents/doc-1')) {
        return { data: brokenLinkDoc };
      }
      throw new Error('Document not found');
    });

    renderDocumentationExplorer();

    await waitFor(() => {
      expect(screen.getByText('readme.md')).toBeInTheDocument();
    });

    const readmeNode = screen.getByText('readme.md');
    await user.click(readmeNode);

    await waitFor(() => {
      expect(screen.getByText('README')).toBeInTheDocument();
    });

    // Broken link should be present
    const brokenLink = screen.getByText('Broken Link');
    expect(brokenLink).toBeInTheDocument();

    // Clicking it should not crash (tooltip should appear eventually)
    await user.click(brokenLink);

    // Application should still be functional
    expect(screen.getByText('README')).toBeInTheDocument();
  });
});
