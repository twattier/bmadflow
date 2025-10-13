import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { Chat } from '@/pages/Chat';
import { apiClient } from '@/api/client';
import { vi } from 'vitest';

// Mock API client
vi.mock('@/api/client');

// Mock scrollIntoView for test environment
Element.prototype.scrollIntoView = vi.fn();

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>{children}</BrowserRouter>
  </QueryClientProvider>
);

// Mock useParams and useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ projectId: 'test-project-id' }),
    useNavigate: () => mockNavigate,
  };
});

describe('Source Navigation Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
  });

  it('full flow: assistant message with sources → click source → panel opens → displays document', async () => {
    const mockProviders = [
      {
        id: 'provider-1',
        provider_name: 'Ollama',
        model_name: 'llama2',
        is_default: true,
        api_config: {},
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ];

    const mockConversation = {
      id: 'conv-1',
      project_id: 'test-project-id',
      llm_provider_id: 'provider-1',
      title: 'Test Conversation',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      messages: [
        {
          id: 'msg-1',
          conversation_id: 'conv-1',
          role: 'user' as const,
          content: 'What are the project goals?',
          sources: null,
          created_at: '2024-01-01T00:00:01Z',
        },
        {
          id: 'msg-2',
          conversation_id: 'conv-1',
          role: 'assistant' as const,
          content: 'The project goals are listed in the PRD.',
          sources: [
            {
              document_id: 'doc-1',
              file_path: 'docs/prd.md',
              file_name: 'prd.md',
              header_anchor: 'goals',
              similarity_score: 0.95,
            },
          ],
          created_at: '2024-01-01T00:00:02Z',
        },
      ],
    };

    const mockDocument = {
      id: 'doc-1',
      project_doc_id: 'pd-1',
      file_path: 'docs/prd.md',
      file_type: 'md',
      file_size: 1024,
      content: '# Goals\n\nThe project aims to...',
      doc_metadata: null,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    // Mock API calls with proper conversation flow
    vi.mocked(apiClient.get).mockImplementation((url: string) => {
      if (url === '/llm-providers') {
        return Promise.resolve({ data: mockProviders });
      }
      // After conversation creation, GET /conversations/:id should return it with messages
      if (url.startsWith('/conversations/')) {
        return Promise.resolve({ data: mockConversation });
      }
      if (url === '/documents/doc-1') {
        return Promise.resolve({ data: mockDocument });
      }
      return Promise.reject(new Error(`Not found: ${url}`));
    });

    vi.mocked(apiClient.post).mockImplementation((url: string) => {
      if (url === '/projects/test-project-id/conversations') {
        // Return full conversation with messages
        return Promise.resolve({ data: mockConversation });
      }
      return Promise.reject(new Error(`Not found: ${url}`));
    });

    render(<Chat />, { wrapper });

    // Wait for Start Conversation button to be enabled (provider loaded)
    await waitFor(() => {
      const startButton = screen.getByText('Start Conversation');
      expect(startButton).not.toBeDisabled();
    });

    // Click Start Conversation
    const startButton = screen.getByText('Start Conversation');
    fireEvent.click(startButton);

    // Wait for conversation to load with messages
    await waitFor(() => {
      expect(screen.getByText('What are the project goals?')).toBeInTheDocument();
    }, { timeout: 5000 });

    await waitFor(() => {
      expect(screen.getByText('The project goals are listed in the PRD.')).toBeInTheDocument();
    });

    // Verify source link is displayed
    await waitFor(() => {
      expect(screen.getByText(/prd.md#goals/i)).toBeInTheDocument();
    });

    // Click source link
    const sourceLink = screen.getByText(/prd.md#goals/i);
    fireEvent.click(sourceLink);

    // Wait for source panel to open with document content
    await waitFor(() => {
      expect(screen.getByText('docs/prd.md')).toBeInTheDocument();
      expect(apiClient.get).toHaveBeenCalledWith('/documents/doc-1');
    });
  });

  it('click different source → panel updates to new document', async () => {
    const mockProviders = [
      {
        id: 'provider-1',
        provider_name: 'Ollama',
        model_name: 'llama2',
        is_default: true,
        api_config: {},
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ];

    const mockConversation = {
      id: 'conv-1',
      project_id: 'test-project-id',
      llm_provider_id: 'provider-1',
      title: 'Test Conversation',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      messages: [
        {
          id: 'msg-1',
          conversation_id: 'conv-1',
          role: 'assistant' as const,
          content: 'Here are the details.',
          sources: [
            {
              document_id: 'doc-1',
              file_path: 'docs/prd.md',
              file_name: 'prd.md',
              header_anchor: 'goals',
              similarity_score: 0.95,
            },
            {
              document_id: 'doc-2',
              file_path: 'docs/architecture.md',
              file_name: 'architecture.md',
              header_anchor: null,
              similarity_score: 0.87,
            },
          ],
          created_at: '2024-01-01T00:00:01Z',
        },
      ],
    };

    const mockDoc1 = {
      id: 'doc-1',
      project_doc_id: 'pd-1',
      file_path: 'docs/prd.md',
      file_type: 'md',
      file_size: 1024,
      content: '# Goals',
      doc_metadata: null,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    const mockDoc2 = {
      id: 'doc-2',
      project_doc_id: 'pd-2',
      file_path: 'docs/architecture.md',
      file_type: 'md',
      file_size: 2048,
      content: '# Architecture',
      doc_metadata: null,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    vi.mocked(apiClient.get).mockImplementation((url: string) => {
      if (url === '/llm-providers') {
        return Promise.resolve({ data: mockProviders });
      }
      if (url.startsWith('/conversations/')) {
        return Promise.resolve({ data: mockConversation });
      }
      if (url === '/documents/doc-1') {
        return Promise.resolve({ data: mockDoc1 });
      }
      if (url === '/documents/doc-2') {
        return Promise.resolve({ data: mockDoc2 });
      }
      return Promise.reject(new Error(`Not found: ${url}`));
    });

    vi.mocked(apiClient.post).mockImplementation((url: string) => {
      if (url === '/projects/test-project-id/conversations') {
        return Promise.resolve({ data: mockConversation });
      }
      return Promise.reject(new Error(`Not found: ${url}`));
    });

    render(<Chat />, { wrapper });

    // Wait for Start Conversation button to be enabled
    await waitFor(() => {
      const startButton = screen.getByText('Start Conversation');
      expect(startButton).not.toBeDisabled();
    });

    // Click Start Conversation
    fireEvent.click(screen.getByText('Start Conversation'));

    // Wait for sources to appear
    await waitFor(() => {
      expect(screen.getByText(/prd.md#goals/i)).toBeInTheDocument();
      expect(screen.getByText(/^architecture.md$/i)).toBeInTheDocument();
    }, { timeout: 5000 });

    // Click first source
    fireEvent.click(screen.getByText(/prd.md#goals/i));

    // Wait for first document to load
    await waitFor(() => {
      expect(screen.getByText('docs/prd.md')).toBeInTheDocument();
    });

    // Click second source
    fireEvent.click(screen.getByText(/^architecture.md$/i));

    // Wait for panel to update to second document
    await waitFor(() => {
      expect(screen.getByText('docs/architecture.md')).toBeInTheDocument();
    });
  });

  it('close panel → chat returns to full width', async () => {
    const mockProviders = [
      {
        id: 'provider-1',
        provider_name: 'Ollama',
        model_name: 'llama2',
        is_default: true,
        api_config: {},
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ];

    const mockConversation = {
      id: 'conv-1',
      project_id: 'test-project-id',
      llm_provider_id: 'provider-1',
      title: 'Test Conversation',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      messages: [
        {
          id: 'msg-1',
          conversation_id: 'conv-1',
          role: 'assistant' as const,
          content: 'Here are the details.',
          sources: [
            {
              document_id: 'doc-1',
              file_path: 'docs/prd.md',
              file_name: 'prd.md',
              header_anchor: 'goals',
              similarity_score: 0.95,
            },
          ],
          created_at: '2024-01-01T00:00:01Z',
        },
      ],
    };

    vi.mocked(apiClient.get).mockImplementation((url: string) => {
      if (url === '/llm-providers') {
        return Promise.resolve({ data: mockProviders });
      }
      if (url.startsWith('/conversations/')) {
        return Promise.resolve({ data: mockConversation });
      }
      if (url === '/documents/doc-1') {
        return Promise.resolve({
          data: {
            id: 'doc-1',
            project_doc_id: 'pd-1',
            file_path: 'docs/prd.md',
            file_type: 'md',
            file_size: 1024,
            content: '# Goals',
            doc_metadata: null,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
          },
        });
      }
      return Promise.reject(new Error('Not found'));
    });

    vi.mocked(apiClient.post).mockResolvedValue({
      data: mockConversation,
    });

    render(<Chat />, { wrapper });

    // Wait for Start Conversation button to be enabled
    await waitFor(() => {
      const startButton = screen.getByText('Start Conversation');
      expect(startButton).not.toBeDisabled();
    });

    // Click Start Conversation
    fireEvent.click(screen.getByText('Start Conversation'));

    // Wait for sources to appear
    await waitFor(() => {
      expect(screen.getByText(/prd.md#goals/i)).toBeInTheDocument();
    }, { timeout: 5000 });

    // Click source link
    fireEvent.click(screen.getByText(/prd.md#goals/i));

    // Wait for panel to open
    await waitFor(() => {
      expect(screen.getByText('docs/prd.md')).toBeInTheDocument();
    });

    // Close panel
    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);

    // Wait for panel to close
    await waitFor(() => {
      expect(screen.queryByText('docs/prd.md')).not.toBeInTheDocument();
    });
  });

  it('"Open in Explorer" button navigates to documentation explorer', async () => {
    const mockProviders = [
      {
        id: 'provider-1',
        provider_name: 'Ollama',
        model_name: 'llama2',
        is_default: true,
        api_config: {},
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ];

    const mockConversation = {
      id: 'conv-1',
      project_id: 'test-project-id',
      llm_provider_id: 'provider-1',
      title: 'Test Conversation',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      messages: [
        {
          id: 'msg-1',
          conversation_id: 'conv-1',
          role: 'assistant' as const,
          content: 'Here are the details.',
          sources: [
            {
              document_id: 'doc-1',
              file_path: 'docs/prd.md',
              file_name: 'prd.md',
              header_anchor: 'goals',
              similarity_score: 0.95,
            },
          ],
          created_at: '2024-01-01T00:00:01Z',
        },
      ],
    };

    vi.mocked(apiClient.get).mockImplementation((url: string) => {
      if (url === '/llm-providers') {
        return Promise.resolve({ data: mockProviders });
      }
      if (url.startsWith('/conversations/')) {
        return Promise.resolve({ data: mockConversation });
      }
      if (url === '/documents/doc-1') {
        return Promise.resolve({
          data: {
            id: 'doc-1',
            project_doc_id: 'pd-1',
            file_path: 'docs/prd.md',
            file_type: 'md',
            file_size: 1024,
            content: '# Goals',
            doc_metadata: null,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
          },
        });
      }
      return Promise.reject(new Error('Not found'));
    });

    vi.mocked(apiClient.post).mockResolvedValue({
      data: mockConversation,
    });

    render(<Chat />, { wrapper });

    // Wait for Start Conversation button to be enabled
    await waitFor(() => {
      const startButton = screen.getByText('Start Conversation');
      expect(startButton).not.toBeDisabled();
    });

    // Click Start Conversation
    fireEvent.click(screen.getByText('Start Conversation'));

    // Wait for sources to appear and click
    await waitFor(() => {
      expect(screen.getByText(/prd.md#goals/i)).toBeInTheDocument();
    }, { timeout: 5000 });

    fireEvent.click(screen.getByText(/prd.md#goals/i));

    // Wait for panel to open
    await waitFor(() => {
      expect(screen.getByText('Open in Explorer')).toBeInTheDocument();
    });

    // Click "Open in Explorer"
    fireEvent.click(screen.getByText('Open in Explorer'));

    // Verify navigation was called with correct explorer route and file path
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/projects/test-project-id/explorer?file=docs%2Fprd.md');
    });
  });
});
