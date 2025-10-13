import { render, screen, fireEvent } from '@testing-library/react';
import { ConversationCard } from '@/features/chat/ConversationCard';
import type { ConversationResponse } from '@/api/types/conversation';
import { vi } from 'vitest';

// Mock date-fns
vi.mock('date-fns', () => ({
  formatDistanceToNow: vi.fn(() => '2 hours ago'),
}));

describe('ConversationCard', () => {
  const mockConversation: ConversationResponse = {
    id: 'conv-123',
    project_id: 'proj-1',
    llm_provider_id: 'llm-1',
    title: 'How does RAG work?',
    created_at: '2025-10-13T10:00:00Z',
    updated_at: '2025-10-13T12:00:00Z',
    llm_provider: {
      id: 'llm-1',
      provider_name: 'ollama',
      model_name: 'llama3',
    },
  };

  const mockOnSelect = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders conversation title', () => {
    render(<ConversationCard conversation={mockConversation} onSelectConversation={mockOnSelect} />);

    expect(screen.getByText('How does RAG work?')).toBeInTheDocument();
  });

  it('renders relative timestamp', () => {
    render(<ConversationCard conversation={mockConversation} onSelectConversation={mockOnSelect} />);

    expect(screen.getByText('2 hours ago')).toBeInTheDocument();
  });

  it('renders LLM provider badge', () => {
    render(<ConversationCard conversation={mockConversation} onSelectConversation={mockOnSelect} />);

    expect(screen.getByText('ollama - llama3')).toBeInTheDocument();
  });

  it('calls onSelectConversation when card clicked', () => {
    render(<ConversationCard conversation={mockConversation} onSelectConversation={mockOnSelect} />);

    const card = screen.getByRole('button', { name: /Load conversation: How does RAG work?/i });
    fireEvent.click(card);

    expect(mockOnSelect).toHaveBeenCalledWith('conv-123');
    expect(mockOnSelect).toHaveBeenCalledTimes(1);
  });

  it('calls onSelectConversation when Enter key pressed', () => {
    render(<ConversationCard conversation={mockConversation} onSelectConversation={mockOnSelect} />);

    const card = screen.getByRole('button', { name: /Load conversation: How does RAG work?/i });
    fireEvent.keyDown(card, { key: 'Enter' });

    expect(mockOnSelect).toHaveBeenCalledWith('conv-123');
  });

  it('calls onSelectConversation when Space key pressed', () => {
    render(<ConversationCard conversation={mockConversation} onSelectConversation={mockOnSelect} />);

    const card = screen.getByRole('button', { name: /Load conversation: How does RAG work?/i });
    fireEvent.keyDown(card, { key: ' ' });

    expect(mockOnSelect).toHaveBeenCalledWith('conv-123');
  });

  it('truncates long title to 50 chars', () => {
    const longTitle =
      'This is a very long conversation title that exceeds fifty characters and should be truncated';
    const mockLongTitleConversation: ConversationResponse = {
      ...mockConversation,
      title: longTitle,
    };

    render(
      <ConversationCard
        conversation={mockLongTitleConversation}
        onSelectConversation={mockOnSelect}
      />
    );

    const displayedTitle = screen.getByText(/This is a very long conversation title/);
    expect(displayedTitle.textContent).toHaveLength(53); // 50 chars + "..."
    expect(displayedTitle.textContent).toContain('...');
  });

  it('does not truncate title when exactly 50 chars', () => {
    const exactTitle = '12345678901234567890123456789012345678901234567890'; // Exactly 50 chars
    const mockExactTitleConversation: ConversationResponse = {
      ...mockConversation,
      title: exactTitle,
    };

    render(
      <ConversationCard
        conversation={mockExactTitleConversation}
        onSelectConversation={mockOnSelect}
      />
    );

    const displayedTitle = screen.getByText(exactTitle);
    expect(displayedTitle.textContent).toBe(exactTitle);
    expect(displayedTitle.textContent).not.toContain('...');
  });

  it('shows "Unknown Provider" when llm_provider is missing', () => {
    const conversationWithoutProvider: ConversationResponse = {
      ...mockConversation,
      llm_provider: undefined,
    };

    render(
      <ConversationCard
        conversation={conversationWithoutProvider}
        onSelectConversation={mockOnSelect}
      />
    );

    expect(screen.getByText('Unknown Provider')).toBeInTheDocument();
  });

  it('applies hover styling classes', () => {
    const { container } = render(
      <ConversationCard conversation={mockConversation} onSelectConversation={mockOnSelect} />
    );

    const card = container.querySelector('[role="button"]');
    expect(card).toHaveClass('cursor-pointer');
    expect(card).toHaveClass('hover:shadow-md');
  });
});
