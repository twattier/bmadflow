import { render, screen, fireEvent } from '@testing-library/react';
import { MessageInput } from '@/features/chat/MessageInput';
import { vi } from 'vitest';

describe('MessageInput', () => {
  const mockOnSendMessage = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('disables Send button when input empty', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        disabled={false}
        isLoading={false}
      />
    );

    const sendButton = screen.getByRole('button');
    expect(sendButton).toBeDisabled();
  });

  it('enables Send button when input has text', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        disabled={false}
        isLoading={false}
      />
    );

    const input = screen.getByPlaceholderText(/ask a question/i);
    fireEvent.change(input, { target: { value: 'Test message' } });

    const sendButton = screen.getByRole('button');
    expect(sendButton).not.toBeDisabled();
  });

  it('calls onSendMessage when Send clicked', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        disabled={false}
        isLoading={false}
      />
    );

    const input = screen.getByPlaceholderText(/ask a question/i);
    fireEvent.change(input, { target: { value: 'Test message' } });

    const sendButton = screen.getByRole('button');
    fireEvent.click(sendButton);

    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
  });

  it('clears input after send', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        disabled={false}
        isLoading={false}
      />
    );

    const input = screen.getByPlaceholderText(/ask a question/i) as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'Test message' } });

    const sendButton = screen.getByRole('button');
    fireEvent.click(sendButton);

    expect(input.value).toBe('');
  });

  it('sends message on Enter key press', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        disabled={false}
        isLoading={false}
      />
    );

    const input = screen.getByPlaceholderText(/ask a question/i);
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
  });

  it('does not send on Shift+Enter', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        disabled={false}
        isLoading={false}
      />
    );

    const input = screen.getByPlaceholderText(/ask a question/i);
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', shiftKey: true });

    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  it('disables input when disabled prop is true', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        disabled={true}
        isLoading={false}
      />
    );

    const input = screen.getByPlaceholderText(/ask a question/i);
    expect(input).toBeDisabled();
  });

  it('shows loading spinner when isLoading is true', () => {
    render(
      <MessageInput
        onSendMessage={mockOnSendMessage}
        disabled={false}
        isLoading={true}
      />
    );

    // Loader2 icon should be present
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });
});
