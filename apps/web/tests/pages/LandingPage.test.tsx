import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ProjectProvider } from '../../src/stores/ProjectContext';
import LandingPage from '../../src/pages/LandingPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

function renderWithProviders(component: React.ReactElement) {
  return render(
    <QueryClientProvider client={queryClient}>
      <ProjectProvider>
        <BrowserRouter>
          {component}
        </BrowserRouter>
      </ProjectProvider>
    </QueryClientProvider>
  );
}

describe('LandingPage', () => {
  it('renders the landing page with BMADFlow title', () => {
    renderWithProviders(<LandingPage />);

    expect(screen.getByText('BMADFlow')).toBeInTheDocument();
    expect(screen.getByText(/Load your documentation/i)).toBeInTheDocument();
  });

  it('renders add project section with form', () => {
    renderWithProviders(<LandingPage />);

    expect(screen.getByText('Add Project')).toBeInTheDocument();
    expect(screen.getByLabelText(/GitHub Repository URL/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sync now/i })).toBeInTheDocument();
  });

  it('shows validation error for invalid URL format', async () => {
    const user = userEvent.setup();

    renderWithProviders(<LandingPage />);

    const input = screen.getByLabelText(/GitHub Repository URL/i);
    const button = screen.getByRole('button', { name: /sync now/i });

    await user.type(input, 'invalid-url');
    await user.click(button);

    expect(screen.getByText(/Invalid GitHub URL format/i)).toBeInTheDocument();
  });

  it('shows validation error for empty URL', async () => {
    const user = userEvent.setup();

    renderWithProviders(<LandingPage />);

    const button = screen.getByRole('button', { name: /sync now/i });
    await user.click(button);

    expect(screen.getByText(/GitHub URL is required/i)).toBeInTheDocument();
  });

  it('accepts valid GitHub URL formats', async () => {
    const user = userEvent.setup();

    renderWithProviders(<LandingPage />);

    const input = screen.getByLabelText(/GitHub Repository URL/i);
    const button = screen.getByRole('button', { name: /sync now/i });

    // Test with https://
    await user.type(input, 'https://github.com/owner/repo');
    await user.click(button);
    expect(screen.queryByText(/Invalid GitHub URL/i)).not.toBeInTheDocument();
  });

  it('clears validation error when user types', async () => {
    const user = userEvent.setup();

    renderWithProviders(<LandingPage />);

    const input = screen.getByLabelText(/GitHub Repository URL/i);
    const button = screen.getByRole('button', { name: /sync now/i });

    // Trigger error
    await user.click(button);
    expect(screen.getByText(/GitHub URL is required/i)).toBeInTheDocument();

    // Start typing - error should disappear
    await user.type(input, 'g');
    expect(screen.queryByText(/GitHub URL is required/i)).not.toBeInTheDocument();
  });
});
