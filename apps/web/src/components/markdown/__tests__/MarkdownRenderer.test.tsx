import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MarkdownRenderer from '../MarkdownRenderer';

describe('MarkdownRenderer', () => {
  it('should render markdown headings', () => {
    render(<MarkdownRenderer content="# Hello World" />);
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Hello World');
  });

  it('should render lists with proper structure', () => {
    const content = '- Item 1\n- Item 2';
    render(<MarkdownRenderer content={content} />);
    expect(screen.getAllByRole('listitem')).toHaveLength(2);
  });

  it('should render tables with styling', () => {
    const content = '| Col1 | Col2 |\n|------|------|\n| A | B |';
    render(<MarkdownRenderer content={content} />);
    expect(screen.getByRole('table')).toBeInTheDocument();
  });

  it('should sanitize XSS content', () => {
    const content = '<script>alert("XSS")</script>';
    const { container } = render(<MarkdownRenderer content={content} />);
    expect(container.querySelector('script')).toBeNull();
  });

  it('should render blockquotes', () => {
    const content = '> This is a quote';
    const { container } = render(<MarkdownRenderer content={content} />);
    expect(container.querySelector('blockquote')).toBeInTheDocument();
  });

  it('should render inline code', () => {
    const content = 'This is `inline code` text';
    const { container } = render(<MarkdownRenderer content={content} />);
    expect(container.querySelector('code')).toHaveTextContent('inline code');
  });
});
