import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DocumentLink } from '@/components/markdown/DocumentLink';

// Mock the useDocumentLink hook
vi.mock('@/hooks/useDocumentLink', () => ({
  useDocumentLink: vi.fn()
}));

// Mock the useProject hook to provide a current project
vi.mock('@/stores/ProjectContext', () => ({
  useProject: vi.fn(),
  ProjectProvider: ({ children }: { children: React.ReactNode }) => children
}));

import { useDocumentLink } from '@/hooks/useDocumentLink';
import { useProject } from '@/stores/ProjectContext';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {ui}
      </BrowserRouter>
    </QueryClientProvider>
  );
}

describe('DocumentLink', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Mock useProject to return a current project
    vi.mocked(useProject).mockReturnValue({
      currentProject: {
        id: 'test-project-123',
        name: 'Test Project',
        github_url: 'https://github.com/test/repo',
        sync_status: 'idle',
        sync_progress: null,
        last_sync_timestamp: null,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      },
      setCurrentProject: vi.fn(),
    });

    // Default mock for non-internal links (empty query)
    vi.mocked(useDocumentLink).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as any);
  });

  describe('External links', () => {
    it('renders external link with target="_blank"', () => {
      renderWithProviders(
        <DocumentLink href="https://github.com">
          GitHub
        </DocumentLink>
      );

      const link = screen.getByText('GitHub');
      expect(link).toHaveAttribute('href', 'https://github.com');
      expect(link).toHaveAttribute('target', '_blank');
      expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });

    it('renders http links as external', () => {
      renderWithProviders(
        <DocumentLink href="http://example.com">
          Example
        </DocumentLink>
      );

      const link = screen.getByText('Example');
      expect(link).toHaveAttribute('target', '_blank');
      expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });
  });

  describe('Anchor links', () => {
    it('renders anchor link for same-page navigation', () => {
      renderWithProviders(
        <DocumentLink href="#section">
          Section
        </DocumentLink>
      );

      const link = screen.getByText('Section');
      expect(link).toHaveAttribute('href', '#section');
      expect(link).not.toHaveAttribute('target');
    });
  });

  describe('Internal markdown links', () => {
    it('renders loading state while resolving', () => {
      vi.mocked(useDocumentLink).mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
      } as any);

      renderWithProviders(
        <DocumentLink href="../architecture.md">
          Architecture
        </DocumentLink>
      );

      const span = screen.getByText('Architecture');
      expect(span.tagName).toBe('SPAN');
    });

    it('renders React Router Link when resolved successfully', () => {
      vi.mocked(useDocumentLink).mockReturnValue({
        data: {
          id: 'doc-123',
          file_path: 'docs/architecture.md',
          title: 'Architecture',
          doc_type: 'architecture'
        },
        isLoading: false,
        error: null,
      } as any);

      renderWithProviders(
        <DocumentLink href="../architecture.md">
          Architecture
        </DocumentLink>
      );

      const link = screen.getByText('Architecture');
      expect(link).toHaveAttribute('href', '/detail/doc-123');
      expect(link.tagName).toBe('A');
    });

    it('includes fragment in link when present', () => {
      vi.mocked(useDocumentLink).mockReturnValue({
        data: {
          id: 'doc-123',
          file_path: 'docs/epic-1.md',
          title: 'Epic 1',
          doc_type: 'epic'
        },
        isLoading: false,
        error: null,
      } as any);

      renderWithProviders(
        <DocumentLink href="../epic-1.md#story-1-1">
          Story 1.1
        </DocumentLink>
      );

      const link = screen.getByText('Story 1.1');
      expect(link).toHaveAttribute('href', '/detail/doc-123#story-1-1');
    });

    it('renders broken link with red text and tooltip', () => {
      vi.mocked(useDocumentLink).mockReturnValue({
        data: undefined,
        isLoading: false,
        error: { response: { status: 404 } },
      } as any);

      renderWithProviders(
        <DocumentLink href="../missing.md">
          Missing Doc
        </DocumentLink>
      );

      const brokenLink = screen.getByText('Missing Doc');
      expect(brokenLink).toHaveClass('text-red-600');
      expect(brokenLink).toHaveClass('cursor-not-allowed');
      expect(brokenLink.tagName).toBe('SPAN');
    });
  });

  describe('Custom className', () => {
    it('applies custom className to external links', () => {
      renderWithProviders(
        <DocumentLink href="https://example.com" className="custom-class">
          Link
        </DocumentLink>
      );

      const link = screen.getByText('Link');
      expect(link).toHaveClass('custom-class');
    });

    it('applies custom className to anchor links', () => {
      renderWithProviders(
        <DocumentLink href="#section" className="custom-class">
          Link
        </DocumentLink>
      );

      const link = screen.getByText('Link');
      expect(link).toHaveClass('custom-class');
    });
  });
});
