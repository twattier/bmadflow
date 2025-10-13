import { render, screen, fireEvent } from '@testing-library/react';
import { ConversationHistoryPanel } from '@/features/chat/ConversationHistoryPanel';
import type { ConversationResponse } from '@/api/types/conversation';
import { vi } from 'vitest';

// Mock date-fns
vi.mock('date-fns', () => ({
  formatDistanceToNow: vi.fn(() => '2 hours ago'),
}));

describe('ConversationHistoryPanel', () => {
  const mockConversations: ConversationResponse[] = [
    {
      id: 'conv-1',
      project_id: 'proj-1',
      llm_provider_id: 'llm-1',
      title: 'First Conversation',
      created_at: '2025-10-13T10:00:00Z',
      updated_at: '2025-10-13T12:00:00Z',
      llm_provider: {
        id: 'llm-1',
        provider_name: 'ollama',
        model_name: 'llama3',
      },
    },
    {
      id: 'conv-2',
      project_id: 'proj-1',
      llm_provider_id: 'llm-2',
      title: 'Second Conversation',
      created_at: '2025-10-13T11:00:00Z',
      updated_at: '2025-10-13T13:00:00Z',
      llm_provider: {
        id: 'llm-2',
        provider_name: 'openai',
        model_name: 'gpt-4',
      },
    },
    {
      id: 'conv-3',
      project_id: 'proj-1',
      llm_provider_id: 'llm-1',
      title: 'Third Conversation',
      created_at: '2025-10-13T09:00:00Z',
      updated_at: '2025-10-13T14:00:00Z',
      llm_provider: {
        id: 'llm-1',
        provider_name: 'ollama',
        model_name: 'mistral',
      },
    },
  ];

  const mockOnSelect = vi.fn();
  const mockOnClose = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders panel title', () => {
    render(
      <ConversationHistoryPanel
        conversations={mockConversations}
        onSelectConversation={mockOnSelect}
        onClose={mockOnClose}
        projectId="proj-1"
        open={true}
      />
    );

    expect(screen.getByText('Conversation History')).toBeInTheDocument();
  });

  it('renders all conversation cards when conversations provided', () => {
    render(
      <ConversationHistoryPanel
        conversations={mockConversations}
        onSelectConversation={mockOnSelect}
        onClose={mockOnClose}
        projectId="proj-1"
        open={true}
      />
    );

    expect(screen.getByText('First Conversation')).toBeInTheDocument();
    expect(screen.getByText('Second Conversation')).toBeInTheDocument();
    expect(screen.getByText('Third Conversation')).toBeInTheDocument();
  });

  it('calls onSelectConversation when card clicked', () => {
    render(
      <ConversationHistoryPanel
        conversations={mockConversations}
        onSelectConversation={mockOnSelect}
        onClose={mockOnClose}
        projectId="proj-1"
        open={true}
      />
    );

    const firstCard = screen.getByRole('button', {
      name: /Load conversation: First Conversation/i,
    });
    fireEvent.click(firstCard);

    expect(mockOnSelect).toHaveBeenCalledWith('conv-1');
    expect(mockOnSelect).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when close button clicked', () => {
    render(
      <ConversationHistoryPanel
        conversations={mockConversations}
        onSelectConversation={mockOnSelect}
        onClose={mockOnClose}
        projectId="proj-1"
        open={true}
      />
    );

    const closeButton = screen.getByRole('button', { name: /Close conversation history/i });
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('shows empty state when no conversations', () => {
    render(
      <ConversationHistoryPanel
        conversations={[]}
        onSelectConversation={mockOnSelect}
        onClose={mockOnClose}
        projectId="proj-1"
        open={true}
      />
    );

    expect(screen.getByText('No conversation history yet')).toBeInTheDocument();
    expect(screen.getByText('Start a new conversation to get started.')).toBeInTheDocument();
  });

  it('does not render panel when open is false', () => {
    const { container } = render(
      <ConversationHistoryPanel
        conversations={mockConversations}
        onSelectConversation={mockOnSelect}
        onClose={mockOnClose}
        projectId="proj-1"
        open={false}
      />
    );

    // Sheet component uses display: none when closed
    // Check that SheetContent is not visible
    const sheetContent = container.querySelector('[role="dialog"]');
    expect(sheetContent).not.toBeInTheDocument();
  });

  it('renders conversations in order provided', () => {
    render(
      <ConversationHistoryPanel
        conversations={mockConversations}
        onSelectConversation={mockOnSelect}
        onClose={mockOnClose}
        projectId="proj-1"
        open={true}
      />
    );

    const cards = screen.getAllByRole('button', { name: /Load conversation:/i });

    // Check order matches the mockConversations array
    expect(cards[0]).toHaveTextContent('First Conversation');
    expect(cards[1]).toHaveTextContent('Second Conversation');
    expect(cards[2]).toHaveTextContent('Third Conversation');
  });

  it('renders LLM provider badges for each conversation', () => {
    render(
      <ConversationHistoryPanel
        conversations={mockConversations}
        onSelectConversation={mockOnSelect}
        onClose={mockOnClose}
        projectId="proj-1"
        open={true}
      />
    );

    expect(screen.getByText('ollama - llama3')).toBeInTheDocument();
    expect(screen.getByText('openai - gpt-4')).toBeInTheDocument();
    expect(screen.getByText('ollama - mistral')).toBeInTheDocument();
  });

  it('renders relative timestamps for each conversation', () => {
    render(
      <ConversationHistoryPanel
        conversations={mockConversations}
        onSelectConversation={mockOnSelect}
        onClose={mockOnClose}
        projectId="proj-1"
        open={true}
      />
    );

    // All timestamps should render with the mocked "2 hours ago" value
    const timestamps = screen.getAllByText('2 hours ago');
    expect(timestamps).toHaveLength(3);
  });

});
