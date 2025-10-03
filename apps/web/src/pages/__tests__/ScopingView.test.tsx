import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { ProjectProvider } from '../../stores/ProjectContext';
import ScopingView from '../ScopingView';
import * as useDocumentsHook from '../../hooks/useDocuments';
import type { Document } from '../../types/document';

// Mock data
const mockDocuments: Document[] = [
  {
    id: '1',
    project_id: 'proj-1',
    file_path: 'docs/scoping/prd.md',
    doc_type: 'scoping',
    title: 'Product Requirements Document',
    excerpt: 'BMADFlow is a self-hosted dashboard for documentation visualization...',
    last_modified: '2025-10-01T14:32:15Z',
    extraction_status: 'completed',
    extraction_confidence: 0.95,
  },
  {
    id: '2',
    project_id: 'proj-1',
    file_path: 'docs/scoping/research.md',
    doc_type: 'scoping',
    title: 'Market Research Document',
    excerpt: 'Analysis of competing documentation tools...',
    last_modified: '2025-10-02T10:20:00Z',
    extraction_status: 'completed',
    extraction_confidence: 0.88,
  },
  {
    id: '3',
    project_id: 'proj-1',
    file_path: 'docs/scoping/use-cases.md',
    doc_type: 'scoping',
    title: 'Use Cases Specification',
    excerpt: 'Primary use cases for BMADFlow platform...',
    last_modified: '2025-10-03T09:15:00Z',
    extraction_status: 'pending',
    extraction_confidence: null,
  },
];

// Test wrapper component
function TestWrapper({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ProjectProvider>{children}</ProjectProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

describe('ScopingView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // AC1: API integration
  it('should fetch and display scoping documents', async () => {
    vi.spyOn(useDocumentsHook, 'useDocuments').mockReturnValue({
      data: mockDocuments,
      isLoading: false,
      isError: false,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    render(
      <TestWrapper>
        <ScopingView />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Product Requirements Document')).toBeInTheDocument();
      expect(screen.getByText('Market Research Document')).toBeInTheDocument();
      expect(screen.getByText('Use Cases Specification')).toBeInTheDocument();
    });
  });

  // AC2: Grid layout
  it('should display cards in responsive grid layout', () => {
    vi.spyOn(useDocumentsHook, 'useDocuments').mockReturnValue({
      data: mockDocuments,
      isLoading: false,
      isError: false,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    const { container } = render(
      <TestWrapper>
        <ScopingView />
      </TestWrapper>
    );

    const grid = container.querySelector('.grid');
    expect(grid).toHaveClass('grid-cols-1');
    expect(grid).toHaveClass('md:grid-cols-2');
    expect(grid).toHaveClass('lg:grid-cols-3');
  });

  // AC5: Loading state
  it('should show skeleton loaders while fetching', () => {
    vi.spyOn(useDocumentsHook, 'useDocuments').mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    const { container } = render(
      <TestWrapper>
        <ScopingView />
      </TestWrapper>
    );

    const skeletons = container.querySelectorAll('[data-skeleton]');
    expect(skeletons).toHaveLength(6);
  });

  // AC6: Empty state
  it('should show empty state when no documents', async () => {
    vi.spyOn(useDocumentsHook, 'useDocuments').mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    render(
      <TestWrapper>
        <ScopingView />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('No scoping documents found')).toBeInTheDocument();
      expect(
        screen.getByText(/Check your repository structure/i)
      ).toBeInTheDocument();
    });
  });

  // AC1: Error handling
  it('should show error message on API failure', async () => {
    vi.spyOn(useDocumentsHook, 'useDocuments').mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    render(
      <TestWrapper>
        <ScopingView />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Failed to load scoping documents')).toBeInTheDocument();
    });
  });

  // AC7: Search functionality
  it('should filter documents by search query', async () => {
    vi.spyOn(useDocumentsHook, 'useDocuments').mockReturnValue({
      data: mockDocuments,
      isLoading: false,
      isError: false,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    render(
      <TestWrapper>
        <ScopingView />
      </TestWrapper>
    );

    const searchInput = screen.getByPlaceholderText('Search scoping documents...');

    // Type search query that matches "Product Requirements"
    fireEvent.change(searchInput, { target: { value: 'Product' } });

    // Wait for debounce (300ms) and filtering
    await waitFor(
      () => {
        expect(screen.getByText('Showing 1 of 3 documents')).toBeInTheDocument();
      },
      { timeout: 500 }
    );

    // Only Product Requirements should be visible
    expect(screen.getByText('Product Requirements Document')).toBeInTheDocument();
    expect(screen.queryByText('Market Research Document')).not.toBeInTheDocument();
  });

  // AC7: Clear search button
  it('should clear search when clear button clicked', async () => {
    vi.spyOn(useDocumentsHook, 'useDocuments').mockReturnValue({
      data: mockDocuments,
      isLoading: false,
      isError: false,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    render(
      <TestWrapper>
        <ScopingView />
      </TestWrapper>
    );

    const searchInput = screen.getByPlaceholderText(
      'Search scoping documents...'
    ) as HTMLInputElement;

    // Type search query
    fireEvent.change(searchInput, { target: { value: 'Research' } });

    await waitFor(() => {
      expect(searchInput.value).toBe('Research');
    });

    // Click clear button
    const clearButton = screen.getByRole('button', { name: /clear search/i });
    fireEvent.click(clearButton);

    await waitFor(() => {
      expect(searchInput.value).toBe('');
    });
  });

  // AC7: No results message
  it('should show no results message when search returns empty', async () => {
    vi.spyOn(useDocumentsHook, 'useDocuments').mockReturnValue({
      data: mockDocuments,
      isLoading: false,
      isError: false,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    render(
      <TestWrapper>
        <ScopingView />
      </TestWrapper>
    );

    const searchInput = screen.getByPlaceholderText('Search scoping documents...');

    // Search for non-existent document
    fireEvent.change(searchInput, { target: { value: 'nonexistent' } });

    await waitFor(
      () => {
        expect(screen.getByText('No documents match your search')).toBeInTheDocument();
      },
      { timeout: 500 }
    );
  });
});
