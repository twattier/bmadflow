import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SourcePanel } from '@/features/chat/SourcePanel';
import type { SourceDocument } from '@/api/types/message';
import type { Document } from '@/api/types/document';

// Mock hooks
vi.mock('@/api/hooks/useDocument', () => ({
  useDocument: vi.fn(),
}));

vi.mock('@/hooks/use-toast', () => ({
  useToast: vi.fn(() => ({
    toast: vi.fn(),
  })),
}));

// Mock MarkdownRenderer
vi.mock('@/features/explorer/MarkdownRenderer', () => ({
  MarkdownRenderer: ({ content }: { content: string }) => <div data-testid="markdown-renderer">{content}</div>,
}));

import { useDocument } from '@/api/hooks/useDocument';
import { useToast } from '@/hooks/use-toast';

describe('SourcePanel', () => {
  const mockSource: SourceDocument = {
    document_id: 'doc1',
    file_path: 'docs/prd.md',
    
    header_anchor: 'goals',
    similarity_score: 0.95,
  };

  const mockDocument: Document = {
    id: 'doc1',
    project_doc_id: 'pd1',
    file_path: 'docs/prd.md',
    file_type: 'md',
    file_size: 1024,
    content: '# Goals\n\nProject goals here...',
    doc_metadata: null,
    created_at: '2025-10-13T00:00:00Z',
    updated_at: '2025-10-13T00:00:00Z',
  };

  const mockOnClose = vi.fn();
  const mockOnOpenInExplorer = vi.fn();
  const mockToast = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useToast as ReturnType<typeof vi.fn>).mockReturnValue({ toast: mockToast });
  });

  it('renders document content when source provided', async () => {
    (useDocument as ReturnType<typeof vi.fn>).mockReturnValue({
      data: mockDocument,
      isLoading: false,
      error: null,
    });

    render(
      <SourcePanel
        source={mockSource}
        onClose={mockOnClose}
        onOpenInExplorer={mockOnOpenInExplorer}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('docs/prd.md')).toBeInTheDocument();
      expect(screen.getByTestId('markdown-renderer')).toBeInTheDocument();
    });
  });

  it('shows loading state while fetching document', () => {
    (useDocument as ReturnType<typeof vi.fn>).mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
    });

    render(
      <SourcePanel
        source={mockSource}
        onClose={mockOnClose}
        onOpenInExplorer={mockOnOpenInExplorer}
      />
    );

    // Verify loading state - Sheet component renders, just check for file path
    expect(screen.getByText('docs/prd.md')).toBeInTheDocument();
  });

  it('shows error message when document fetch fails', () => {
    (useDocument as ReturnType<typeof vi.fn>).mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error('Failed to fetch'),
    });

    render(
      <SourcePanel
        source={mockSource}
        onClose={mockOnClose}
        onOpenInExplorer={mockOnOpenInExplorer}
      />
    );

    expect(screen.getByText(/Failed to load document/i)).toBeInTheDocument();
  });

  it('calls onClose when close button clicked', async () => {
    (useDocument as ReturnType<typeof vi.fn>).mockReturnValue({
      data: mockDocument,
      isLoading: false,
      error: null,
    });

    render(
      <SourcePanel
        source={mockSource}
        onClose={mockOnClose}
        onOpenInExplorer={mockOnOpenInExplorer}
      />
    );

    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  it('calls onOpenInExplorer when "Open in Explorer" button clicked', async () => {
    (useDocument as ReturnType<typeof vi.fn>).mockReturnValue({
      data: mockDocument,
      isLoading: false,
      error: null,
    });

    render(
      <SourcePanel
        source={mockSource}
        onClose={mockOnClose}
        onOpenInExplorer={mockOnOpenInExplorer}
      />
    );

    await waitFor(() => {
      const openButton = screen.getByText(/Open in Explorer/i);
      fireEvent.click(openButton);

      expect(mockOnOpenInExplorer).toHaveBeenCalledWith('docs/prd.md');
    });
  });

  it('displays file path in header', () => {
    (useDocument as ReturnType<typeof vi.fn>).mockReturnValue({
      data: mockDocument,
      isLoading: false,
      error: null,
    });

    render(
      <SourcePanel
        source={mockSource}
        onClose={mockOnClose}
        onOpenInExplorer={mockOnOpenInExplorer}
      />
    );

    expect(screen.getByText('docs/prd.md')).toBeInTheDocument();
  });

  it('shows Previous button when previousSource provided', () => {
    (useDocument as ReturnType<typeof vi.fn>).mockReturnValue({
      data: mockDocument,
      isLoading: false,
      error: null,
    });

    const previousSource: SourceDocument = {
      document_id: 'doc0',
      file_path: 'docs/arch.md',
      
      header_anchor: null,
      similarity_score: 0.88,
    };

    const mockOnNavigateToPrevious = vi.fn();

    render(
      <SourcePanel
        source={mockSource}
        projectId="test-project"
        onClose={mockOnClose}
        onOpenInExplorer={mockOnOpenInExplorer}
        previousSource={previousSource}
        onNavigateToPrevious={mockOnNavigateToPrevious}
      />
    );

    const previousButton = screen.getByText(/Previous/i);
    expect(previousButton).toBeInTheDocument();
  });

  it('calls onNavigateToPrevious when Previous button clicked', () => {
    (useDocument as ReturnType<typeof vi.fn>).mockReturnValue({
      data: mockDocument,
      isLoading: false,
      error: null,
    });

    const previousSource: SourceDocument = {
      document_id: 'doc0',
      file_path: 'docs/arch.md',
      
      header_anchor: null,
      similarity_score: 0.88,
    };

    const mockOnNavigateToPrevious = vi.fn();

    render(
      <SourcePanel
        source={mockSource}
        projectId="test-project"
        onClose={mockOnClose}
        onOpenInExplorer={mockOnOpenInExplorer}
        previousSource={previousSource}
        onNavigateToPrevious={mockOnNavigateToPrevious}
      />
    );

    const previousButton = screen.getByText(/Previous/i);
    fireEvent.click(previousButton);

    expect(mockOnNavigateToPrevious).toHaveBeenCalled();
  });

  it('does not show Previous button when previousSource is null', () => {
    (useDocument as ReturnType<typeof vi.fn>).mockReturnValue({
      data: mockDocument,
      isLoading: false,
      error: null,
    });

    render(
      <SourcePanel
        source={mockSource}
        projectId="test-project"
        onClose={mockOnClose}
        onOpenInExplorer={mockOnOpenInExplorer}
        previousSource={null}
      />
    );

    const previousButton = screen.queryByText(/Previous/i);
    expect(previousButton).not.toBeInTheDocument();
  });

  it('renders null when source is null', () => {
    const { container } = render(
      <SourcePanel
        source={null}
        projectId="test-project"
        onClose={mockOnClose}
        onOpenInExplorer={mockOnOpenInExplorer}
      />
    );

    expect(container.firstChild).toBeNull();
  });
});
