import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Projects } from '@/pages/Projects';

// Mock the hooks
vi.mock('@/api/hooks/useProjects', () => ({
  useProjects: vi.fn(),
}));

vi.mock('@/api/hooks/useProjectDocs', () => ({
  useProjectDocs: () => ({
    data: [],
  }),
}));

import { useProjects } from '@/api/hooks/useProjects';

describe('Projects Page', () => {
  const renderWithProviders = (component: React.ReactElement) => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });

    return render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>{component}</QueryClientProvider>
      </BrowserRouter>
    );
  };

  it('displays empty state when no projects', () => {
    vi.mocked(useProjects).mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    } as ReturnType<typeof useProjects>);

    renderWithProviders(<Projects />);
    expect(screen.getByText(/No projects yet/)).toBeInTheDocument();
  });

  it('displays project grid when projects exist', () => {
    vi.mocked(useProjects).mockReturnValue({
      data: [
        { id: '1', name: 'Project 1', description: null, created_at: '', updated_at: '' },
        { id: '2', name: 'Project 2', description: null, created_at: '', updated_at: '' },
      ],
      isLoading: false,
      error: null,
    } as ReturnType<typeof useProjects>);

    renderWithProviders(<Projects />);
    expect(screen.getByText('Project 1')).toBeInTheDocument();
    expect(screen.getByText('Project 2')).toBeInTheDocument();
  });

  it('displays new project card', () => {
    vi.mocked(useProjects).mockReturnValue({
      data: [{ id: '1', name: 'Project 1', description: null, created_at: '', updated_at: '' }],
      isLoading: false,
      error: null,
    } as ReturnType<typeof useProjects>);

    renderWithProviders(<Projects />);
    expect(screen.getByTestId('new-project-card')).toBeInTheDocument();
  });
});
