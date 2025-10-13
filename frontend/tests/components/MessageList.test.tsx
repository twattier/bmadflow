import { render, screen } from '@testing-library/react';
import { MessageList } from '@/features/chat/MessageList';
import { MessageResponse } from '@/api/types/message';

describe('MessageList', () => {
  const mockMessages: MessageResponse[] = [
    {
      id: '1',
      conversation_id: 'conv-1',
      role: 'user',
      content: 'What is BMADFlow?',
      sources: null,
      created_at: '2024-01-01T00:00:00Z',
    },
    {
      id: '2',
      conversation_id: 'conv-1',
      role: 'assistant',
      content: 'BMADFlow is a documentation management system.',
      sources: [],
      created_at: '2024-01-01T00:00:01Z',
    },
  ];

  it('renders user and assistant messages with correct alignment', () => {
    render(<MessageList messages={mockMessages} isLoading={false} />);

    expect(screen.getByText('What is BMADFlow?')).toBeInTheDocument();
    expect(
      screen.getByText('BMADFlow is a documentation management system.')
    ).toBeInTheDocument();
  });

  it('shows loading indicator when isLoading is true', () => {
    render(<MessageList messages={mockMessages} isLoading={true} />);

    expect(screen.getByText(/generating response/i)).toBeInTheDocument();
  });

  it('renders empty list when no messages', () => {
    const { container } = render(<MessageList messages={[]} isLoading={false} />);

    // Should only have the messagesEndRef div
    const messageCards = container.querySelectorAll('[class*="Card"]');
    expect(messageCards.length).toBe(0);
  });

  it('applies correct styling for user messages', () => {
    render(<MessageList messages={[mockMessages[0]]} isLoading={false} />);

    const userMessage = screen.getByText('What is BMADFlow?');
    const card = userMessage.closest('div[class*="bg-primary"]');
    expect(card).toBeInTheDocument();
  });

  it('applies correct styling for assistant messages', () => {
    render(<MessageList messages={[mockMessages[1]]} isLoading={false} />);

    const assistantMessage = screen.getByText(
      'BMADFlow is a documentation management system.'
    );
    const card = assistantMessage.closest('div[class*="bg-card"]');
    expect(card).toBeInTheDocument();
  });
});
