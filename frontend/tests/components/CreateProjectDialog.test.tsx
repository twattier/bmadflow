import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CreateProjectDialog } from '@/features/projects/CreateProjectDialog';

// Mock the toast hook
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

describe('CreateProjectDialog', () => {
  const mockOnOpenChange = vi.fn();

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

  it('validates required name field', async () => {
    renderWithClient(<CreateProjectDialog open={true} onOpenChange={mockOnOpenChange} />);

    const submitButton = screen.getByTestId('create-project-button');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByTestId('name-error')).toHaveTextContent('Project name is required');
    });
  });

  it('validates max length', async () => {
    renderWithClient(<CreateProjectDialog open={true} onOpenChange={mockOnOpenChange} />);

    const nameInput = screen.getByTestId('project-name-input');
    fireEvent.change(nameInput, { target: { value: 'a'.repeat(256) } });

    const submitButton = screen.getByTestId('create-project-button');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByTestId('name-error')).toHaveTextContent('must be 255 characters or less');
    });
  });

  it('accepts valid input', () => {
    renderWithClient(<CreateProjectDialog open={true} onOpenChange={mockOnOpenChange} />);

    const nameInput = screen.getByTestId('project-name-input');
    const descriptionInput = screen.getByTestId('project-description-input');

    fireEvent.change(nameInput, { target: { value: 'My Project' } });
    fireEvent.change(descriptionInput, { target: { value: 'Project description' } });

    expect(nameInput).toHaveValue('My Project');
    expect(descriptionInput).toHaveValue('Project description');
  });
});
