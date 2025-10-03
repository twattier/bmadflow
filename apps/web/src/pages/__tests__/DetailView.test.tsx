import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import DetailView from '../DetailView';
import * as useDocumentsHook from '../../hooks/useDocuments';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  </BrowserRouter>
);

describe('DetailView', () => {
  it('should display loading skeleton while fetching', () => {
    vi.spyOn(useDocumentsHook, 'useDocument').mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as any);

    render(<DetailView />, { wrapper });
    expect(screen.getByTestId('markdown-skeleton')).toBeInTheDocument();
  });

  it('should display error message on API failure', () => {
    vi.spyOn(useDocumentsHook, 'useDocument').mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Failed to fetch'),
    } as any);

    render(<DetailView />, { wrapper });
    expect(screen.getByText('Failed to load document. Please try again.')).toBeInTheDocument();
  });

  it('should fetch and display document content', async () => {
    const mockDocument = {
      id: '1',
      project_id: 'proj-1',
      file_path: 'test.md',
      content: '# Test Document\n\nThis is a test.',
      doc_type: 'scoping',
      title: 'Test Document',
      excerpt: 'This is a test',
      last_modified: '2025-01-01',
      extraction_status: 'completed',
      extraction_confidence: 0.95,
    };

    vi.spyOn(useDocumentsHook, 'useDocument').mockReturnValue({
      data: mockDocument,
      isLoading: false,
      error: null,
    } as any);

    render(<DetailView />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Test Document')).toBeInTheDocument();
    });
  });
});
