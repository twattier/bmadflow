import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MarkdownRenderer } from '@/features/explorer/MarkdownRenderer';
import type { FileNode } from '@/api/types/document';

// Mock mermaid
vi.mock('mermaid', () => ({
  default: {
    initialize: vi.fn(),
    render: vi.fn(() => Promise.resolve({ svg: '<svg>Mermaid Diagram</svg>' })),
  },
}));

// Mock document service
vi.mock('@/api/services/documentService', () => ({
  findDocumentByRelativePath: vi.fn(),
}));

describe('MarkdownRenderer', () => {
  it('renders markdown headings', () => {
    const content = `# Heading 1
## Heading 2
### Heading 3`;

    render(<MarkdownRenderer content={content} />);

    expect(screen.getByText('Heading 1')).toBeInTheDocument();
    expect(screen.getByText('Heading 2')).toBeInTheDocument();
    expect(screen.getByText('Heading 3')).toBeInTheDocument();
  });

  it('renders markdown lists', () => {
    const content = `- Item 1
- Item 2
- Item 3

1. First
2. Second`;

    render(<MarkdownRenderer content={content} />);

    expect(screen.getByText('Item 1')).toBeInTheDocument();
    expect(screen.getByText('Item 2')).toBeInTheDocument();
    expect(screen.getByText('First')).toBeInTheDocument();
    expect(screen.getByText('Second')).toBeInTheDocument();
  });

  it('renders blockquotes', () => {
    const content = '> This is a quote';

    render(<MarkdownRenderer content={content} />);

    const blockquote = screen.getByText('This is a quote').closest('blockquote');
    expect(blockquote).toBeInTheDocument();
  });

  it('renders code blocks with syntax highlighting', () => {
    const content = '```python\nprint("Hello World")\n```';

    const { container } = render(<MarkdownRenderer content={content} />);

    const codeBlock = container.querySelector('code.language-python');
    expect(codeBlock).toBeInTheDocument();
    expect(codeBlock?.textContent).toContain('print');
    expect(codeBlock?.textContent).toContain('Hello World');
  });

  it('renders inline code differently from code blocks', () => {
    const content = 'Use `const` for variables.\n\n```javascript\nconst x = 5;\n```';

    const { container } = render(<MarkdownRenderer content={content} />);

    const inlineCode = container.querySelector('code.rounded.bg-muted');
    const blockCode = container.querySelector('code.language-javascript');

    expect(inlineCode).toBeInTheDocument();
    expect(inlineCode?.textContent).toBe('const');
    expect(blockCode).toBeInTheDocument();
    expect(blockCode?.textContent).toContain('const x = 5;');
  });

  it('supports GFM tables', () => {
    const content = `| Name | Age |
|------|-----|
| John | 30  |
| Jane | 25  |`;

    render(<MarkdownRenderer content={content} />);

    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Age')).toBeInTheDocument();
    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getByText('30')).toBeInTheDocument();
  });

  it('supports GFM strikethrough', () => {
    const content = '~~strikethrough text~~';

    render(<MarkdownRenderer content={content} />);

    const strikethrough = screen.getByText('strikethrough text').closest('del');
    expect(strikethrough).toBeInTheDocument();
  });

  it('renders links', () => {
    const content = '[Click here](https://example.com)';

    render(<MarkdownRenderer content={content} />);

    const link = screen.getByText('Click here');
    expect(link.tagName).toBe('A');
    expect(link).toHaveAttribute('href', 'https://example.com');
  });

  it('applies prose typography classes', () => {
    const content = '# Title';

    const { container } = render(<MarkdownRenderer content={content} />);

    const proseContainer = container.querySelector('.prose');
    expect(proseContainer).toBeInTheDocument();
    expect(proseContainer).toHaveClass('prose-slate');
    expect(proseContainer).toHaveClass('prose-sm');
  });

  it('renders mermaid code block as diagram', async () => {
    const content = '```mermaid\ngraph TD\nA-->B\n```';

    render(<MarkdownRenderer content={content} />);

    const diagram = await screen.findByTestId('mermaid-diagram');
    expect(diagram).toBeInTheDocument();
  });

  it('non-mermaid code blocks still render with syntax highlighting', () => {
    const content = '```javascript\nconsole.log("hello");\n```';

    const { container } = render(<MarkdownRenderer content={content} />);

    const codeBlock = container.querySelector('code.language-javascript');
    expect(codeBlock).toBeInTheDocument();
    expect(codeBlock?.textContent).toContain('console.log');
  });

  // Navigation-specific tests
  describe('Link Navigation', () => {
    const mockProjectId = 'test-project-123';
    const mockCurrentDocument: FileNode = {
      id: 'doc-1',
      name: 'current.md',
      type: 'file',
      path: '/docs/current.md',
      file_type: 'md',
      size: 1024,
    };
    let mockOnDocumentSelect: ReturnType<typeof vi.fn>;

    beforeEach(() => {
      mockOnDocumentSelect = vi.fn();
      window.open = vi.fn();
    });

    it('renders external links with target="_blank"', () => {
      const content = '[External Link](https://example.com)';

      render(
        <MarkdownRenderer
          content={content}
          projectId={mockProjectId}
          currentDocument={mockCurrentDocument}
          onDocumentSelect={mockOnDocumentSelect}
        />
      );

      const link = screen.getByText('External Link').closest('a');
      expect(link).toHaveAttribute('href', 'https://example.com');
      expect(link).toHaveAttribute('target', '_blank');
      expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });

    it('renders relative links with href attribute', () => {
      const content = '[Relative Link](./target.md)';

      render(
        <MarkdownRenderer
          content={content}
          projectId={mockProjectId}
          currentDocument={mockCurrentDocument}
          onDocumentSelect={mockOnDocumentSelect}
        />
      );

      const link = screen.getByText('Relative Link').closest('a');
      expect(link).toHaveAttribute('href', './target.md');
    });

    it('renders anchor-only links normally', () => {
      const content = '[Section Link](#overview)';

      render(
        <MarkdownRenderer
          content={content}
          projectId={mockProjectId}
          currentDocument={mockCurrentDocument}
          onDocumentSelect={mockOnDocumentSelect}
        />
      );

      const link = screen.getByText('Section Link').closest('a');
      expect(link).toHaveAttribute('href', '#overview');
      expect(link).not.toHaveAttribute('target');
    });

    it('handles links without navigation props (backward compatibility)', () => {
      const content = '[Some Link](./file.md)';

      render(<MarkdownRenderer content={content} />);

      const link = screen.getByText('Some Link').closest('a');
      expect(link).toHaveAttribute('href', './file.md');
    });

    it('renders http:// links as external', () => {
      const content = '[HTTP Link](http://example.com)';

      render(
        <MarkdownRenderer
          content={content}
          projectId={mockProjectId}
          currentDocument={mockCurrentDocument}
          onDocumentSelect={mockOnDocumentSelect}
        />
      );

      const link = screen.getByText('HTTP Link').closest('a');
      expect(link).toHaveAttribute('target', '_blank');
    });

    it('handles mixed link types in same document', () => {
      const content = `
[External](https://example.com)
[Relative](./file.md)
[Anchor](#section)
      `;

      render(
        <MarkdownRenderer
          content={content}
          projectId={mockProjectId}
          currentDocument={mockCurrentDocument}
          onDocumentSelect={mockOnDocumentSelect}
        />
      );

      const externalLink = screen.getByText('External').closest('a');
      const relativeLink = screen.getByText('Relative').closest('a');
      const anchorLink = screen.getByText('Anchor').closest('a');

      expect(externalLink).toHaveAttribute('target', '_blank');
      expect(relativeLink).toHaveAttribute('href', './file.md');
      expect(anchorLink).toHaveAttribute('href', '#section');
    });
  });
});
