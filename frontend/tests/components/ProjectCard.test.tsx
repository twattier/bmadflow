import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ProjectCard } from '@/features/projects/ProjectCard';
import { Project } from '@/api/types/project';

// Mock the hooks
vi.mock('@/api/hooks/useProjectDocs', () => ({
  useProjectDocs: () => ({
    data: [{ id: '1' }, { id: '2' }],
  }),
}));

describe('ProjectCard', () => {
  const mockProject: Project = {
    id: 'proj-123',
    name: 'Test Project',
    description: 'This is a very long description that should be truncated after two lines to test the text ellipsis functionality',
    created_at: '2025-10-01T00:00:00Z',
    updated_at: '2025-10-01T00:00:00Z',
  };

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

  it('displays project name', () => {
    renderWithProviders(<ProjectCard project={mockProject} />);
    expect(screen.getByText('Test Project')).toBeInTheDocument();
  });

  it('displays truncated description', () => {
    renderWithProviders(<ProjectCard project={mockProject} />);
    expect(screen.getByText(/This is a very long description/)).toBeInTheDocument();
  });

  it('displays ProjectDoc count', () => {
    renderWithProviders(<ProjectCard project={mockProject} />);
    expect(screen.getByText('2 documents')).toBeInTheDocument();
  });

  it('displays View button', () => {
    renderWithProviders(<ProjectCard project={mockProject} />);
    expect(screen.getByTestId('view-button')).toBeInTheDocument();
  });
});
