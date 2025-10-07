import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import { FileTreePanel } from '@/features/explorer/FileTreePanel';
import { useFileTree } from '@/api/hooks/useFileTree';

// Mock the useFileTree hook
vi.mock('@/api/hooks/useFileTree');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('FileTreePanel', () => {
  it('renders loading state when fetching file tree', () => {
    vi.mocked(useFileTree).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as any);

    const { container } = render(<FileTreePanel projectId="123" onSelectFile={vi.fn()} />, {
      wrapper: createWrapper(),
    });

    expect(container.querySelector('.animate-spin')).toBeTruthy();
  });

  it('renders empty state when no documents synced', () => {
    vi.mocked(useFileTree).mockReturnValue({
      data: { project_id: '123', tree: [] },
      isLoading: false,
      error: null,
    } as any);

    render(<FileTreePanel projectId="123" onSelectFile={vi.fn()} />, {
      wrapper: createWrapper(),
    });

    expect(
      screen.getByText(/No documents synced. Go to Overview and sync a ProjectDoc to get started./i)
    ).toBeInTheDocument();
  });

  it('renders error state when fetch fails', () => {
    vi.mocked(useFileTree).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Failed to fetch'),
    } as any);

    render(<FileTreePanel projectId="123" onSelectFile={vi.fn()} />, {
      wrapper: createWrapper(),
    });

    expect(screen.getByText(/Failed to load file tree/i)).toBeInTheDocument();
  });

  it('renders file tree with folders and files', () => {
    const mockFileTree = [
      {
        id: 'folder-1',
        name: 'docs',
        type: 'folder' as const,
        path: 'docs',
        children: [
          {
            id: 'file-1',
            name: 'README.md',
            type: 'file' as const,
            path: 'docs/README.md',
            file_type: 'md',
          },
        ],
      },
    ];

    vi.mocked(useFileTree).mockReturnValue({
      data: { project_id: '123', tree: mockFileTree },
      isLoading: false,
      error: null,
    } as any);

    render(<FileTreePanel projectId="123" onSelectFile={vi.fn()} />, {
      wrapper: createWrapper(),
    });

    expect(screen.getByTestId('file-tree')).toBeInTheDocument();
    expect(screen.getByText('docs')).toBeInTheDocument();
  });
});
