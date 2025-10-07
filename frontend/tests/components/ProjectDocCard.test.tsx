import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ProjectDocCard } from '@/features/projects/ProjectDocCard';
import { ProjectDocResponse } from '@/api/types/projectDoc';

// Mock the toast hook
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

describe('ProjectDocCard', () => {
  const mockProjectDoc: ProjectDocResponse = {
    id: '123',
    project_id: 'proj-1',
    name: 'Test Docs',
    description: 'Test description',
    github_url: 'https://github.com/test/repo',
    github_folder_path: null,
    last_synced_at: '2025-10-07T10:00:00Z',
    last_github_commit_date: '2025-10-07T09:00:00Z',
    created_at: '2025-10-01T00:00:00Z',
    updated_at: '2025-10-01T00:00:00Z',
  };

  const renderWithClient = (component: React.ReactElement) => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    return render(
      <QueryClientProvider client={queryClient}>{component}</QueryClientProvider>
    );
  };

  it('displays project doc information correctly', () => {
    renderWithClient(<ProjectDocCard projectDoc={mockProjectDoc} />);

    expect(screen.getByText('Test Docs')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
    expect(screen.getByText('https://github.com/test/repo')).toBeInTheDocument();
  });

  it('displays sync status badge', () => {
    renderWithClient(<ProjectDocCard projectDoc={mockProjectDoc} />);

    const badge = screen.getByTestId('sync-status-badge');
    expect(badge).toBeInTheDocument();
  });

  it('displays sync button', () => {
    renderWithClient(<ProjectDocCard projectDoc={mockProjectDoc} />);

    const syncButton = screen.getByTestId('sync-button');
    expect(syncButton).toBeInTheDocument();
    expect(syncButton).toHaveTextContent('Sync');
  });

  it('displays spinner when sync button is clicked', async () => {
    renderWithClient(<ProjectDocCard projectDoc={mockProjectDoc} />);

    const syncButton = screen.getByTestId('sync-button');
    fireEvent.click(syncButton);

    // Button should be disabled during sync
    expect(syncButton).toBeDisabled();
  });
});
