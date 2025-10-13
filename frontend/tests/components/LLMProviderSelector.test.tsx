import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LLMProviderSelector } from '@/features/chat/LLMProviderSelector';
import { useLLMProviders } from '@/api/hooks/useLLMProviders';
import { vi } from 'vitest';

// Mock the hooks
vi.mock('@/api/hooks/useLLMProviders');

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
);

describe('LLMProviderSelector', () => {
  const mockOnProviderSelect = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dropdown with providers', async () => {
    const mockProviders = [
      {
        id: '1',
        provider_name: 'Ollama',
        model_name: 'llama2',
        is_default: true,
        api_config: {},
        created_at: '2024-01-01',
      },
      {
        id: '2',
        provider_name: 'OpenAI',
        model_name: 'GPT-4',
        is_default: false,
        api_config: {},
        created_at: '2024-01-01',
      },
    ];

    vi.mocked(useLLMProviders).mockReturnValue({
      data: mockProviders,
      isLoading: false,
      error: null,
    } as any); // eslint-disable-line @typescript-eslint/no-explicit-any

    render(
      <LLMProviderSelector
        onProviderSelect={mockOnProviderSelect}
        selectedProviderId="1"
      />,
      { wrapper }
    );

    await waitFor(() => {
      expect(screen.getByText('Select LLM Provider')).toBeInTheDocument();
    });
  });

  it('pre-selects default provider', async () => {
    const mockProviders = [
      {
        id: '1',
        provider_name: 'Ollama',
        model_name: 'llama2',
        is_default: true,
        api_config: {},
        created_at: '2024-01-01',
      },
    ];

    vi.mocked(useLLMProviders).mockReturnValue({
      data: mockProviders,
      isLoading: false,
      error: null,
    } as any); // eslint-disable-line @typescript-eslint/no-explicit-any

    render(
      <LLMProviderSelector
        onProviderSelect={mockOnProviderSelect}
        selectedProviderId="1"
      />,
      { wrapper }
    );

    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });
  });

  it('shows loading state', () => {
    vi.mocked(useLLMProviders).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as any); // eslint-disable-line @typescript-eslint/no-explicit-any

    render(
      <LLMProviderSelector
        onProviderSelect={mockOnProviderSelect}
      />,
      { wrapper }
    );

    expect(screen.getByText('Select LLM Provider')).toBeInTheDocument();
  });

  it('shows empty state when no providers', () => {
    vi.mocked(useLLMProviders).mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    } as any); // eslint-disable-line @typescript-eslint/no-explicit-any

    render(
      <LLMProviderSelector
        onProviderSelect={mockOnProviderSelect}
      />,
      { wrapper }
    );

    expect(
      screen.getByText(/No LLM providers configured/i)
    ).toBeInTheDocument();
  });
});
