import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CodeBlock from '../CodeBlock';

describe('CodeBlock', () => {
  it('should render code with syntax highlighting', () => {
    const { container } = render(<CodeBlock language="typescript">const x = 1;</CodeBlock>);
    const codeElement = container.querySelector('code.language-typescript');
    expect(codeElement).toBeInTheDocument();
    expect(codeElement?.textContent).toBe('const x = 1;');
  });

  it('should display language label', () => {
    render(<CodeBlock language="typescript">const x = 1;</CodeBlock>);
    expect(screen.getByText('typescript')).toBeInTheDocument();
  });

  it('should display copy button', () => {
    render(<CodeBlock language="typescript">const x = 1;</CodeBlock>);
    expect(screen.getByRole('button', { name: /copy/i })).toBeInTheDocument();
  });

  it('should copy code to clipboard on button click', async () => {
    const writeTextMock = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, {
      clipboard: {
        writeText: writeTextMock,
      },
    });

    render(<CodeBlock language="typescript">const x = 1;</CodeBlock>);

    const copyButton = screen.getByRole('button', { name: /copy/i });
    fireEvent.click(copyButton);

    await waitFor(() => {
      expect(writeTextMock).toHaveBeenCalledWith('const x = 1;');
    });
  });

  it('should show success feedback after copy', async () => {
    const writeTextMock = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, {
      clipboard: {
        writeText: writeTextMock,
      },
    });

    render(<CodeBlock language="typescript">const x = 1;</CodeBlock>);

    const copyButton = screen.getByRole('button', { name: /copy/i });
    fireEvent.click(copyButton);

    await waitFor(() => {
      expect(screen.getByLabelText(/copy/i)).toBeInTheDocument();
    });
  });

  it('should show fallback tooltip when clipboard API unavailable', async () => {
    // Remove clipboard API
    const originalClipboard = navigator.clipboard;
    Object.defineProperty(navigator, 'clipboard', {
      value: undefined,
      writable: true,
    });

    render(<CodeBlock language="python">print("hello")</CodeBlock>);

    const copyButton = screen.getByRole('button', { name: /copy/i });
    fireEvent.click(copyButton);

    await waitFor(() => {
      expect(screen.getByText(/Press Ctrl\+C to copy/i)).toBeInTheDocument();
    });

    // Restore
    Object.defineProperty(navigator, 'clipboard', {
      value: originalClipboard,
      writable: true,
    });
  });
});
