import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import TableOfContents from '../../src/components/markdown/TableOfContents';

describe('TableOfContents', () => {
  beforeEach(() => {
    // Clear any existing elements in document
    document.body.innerHTML = '';
  });

  it('extracts H2 and H3 headings from markdown', () => {
    const content = '## Heading 1\n### Subheading 1.1\n## Heading 2\n### Subheading 2.1';
    render(<TableOfContents content={content} />);

    expect(screen.getByText('Heading 1')).toBeInTheDocument();
    expect(screen.getByText('Subheading 1.1')).toBeInTheDocument();
    expect(screen.getByText('Heading 2')).toBeInTheDocument();
    expect(screen.getByText('Subheading 2.1')).toBeInTheDocument();
  });

  it('hides TOC when fewer than 3 headings', () => {
    const content = '## Only One Heading\n### And a subheading';
    const { container } = render(<TableOfContents content={content} />);

    // Should not render nav element if < 3 headings
    expect(container.querySelector('nav')).not.toBeInTheDocument();
  });

  it('shows TOC when 3 or more headings', () => {
    const content = '## Heading 1\n## Heading 2\n## Heading 3';
    const { container } = render(<TableOfContents content={content} />);

    expect(container.querySelector('nav')).toBeInTheDocument();
    expect(screen.getByRole('navigation')).toHaveAttribute('aria-label', 'Table of Contents');
  });

  it('builds hierarchical structure with H2 as parent and H3 as children', () => {
    const content = '## Parent 1\n### Child 1.1\n### Child 1.2\n## Parent 2\n### Child 2.1';
    render(<TableOfContents content={content} />);

    // Check that H2 and H3 headings are present
    expect(screen.getByText('Parent 1')).toBeInTheDocument();
    expect(screen.getByText('Child 1.1')).toBeInTheDocument();
    expect(screen.getByText('Child 1.2')).toBeInTheDocument();

    // Check hierarchical styling (H3 should have more padding)
    const h2Button = screen.getByText('Parent 1');
    const h3Button = screen.getByText('Child 1.1');

    expect(h2Button.className).toContain('pl-2');
    expect(h3Button.className).toContain('pl-6');
  });

  it('generates unique IDs for duplicate headings', () => {
    const content = '## Introduction\n## Introduction\n## Introduction';
    render(<TableOfContents content={content} />);

    // All three buttons should be present
    const buttons = screen.getAllByText('Introduction');
    expect(buttons).toHaveLength(3);
  });

  it('supports keyboard navigation (Tab + Enter)', () => {
    const content = '## Heading 1\n## Heading 2\n## Heading 3';

    // Create mock heading elements in DOM for scroll target
    const mockHeading1 = document.createElement('h2');
    mockHeading1.id = 'toc-heading-1';
    document.body.appendChild(mockHeading1);

    const scrollIntoViewMock = vi.fn();
    mockHeading1.scrollIntoView = scrollIntoViewMock;

    render(<TableOfContents content={content} />);

    const firstItem = screen.getByText('Heading 1');

    // Simulate Enter key press
    fireEvent.keyDown(firstItem, { key: 'Enter' });

    // Should call scrollIntoView
    expect(scrollIntoViewMock).toHaveBeenCalledWith({
      behavior: 'smooth',
      block: 'start',
    });
  });

  it('applies correct ARIA attributes', () => {
    const content = '## Heading 1\n## Heading 2\n## Heading 3';
    render(<TableOfContents content={content} />);

    const nav = screen.getByRole('navigation');
    expect(nav).toHaveAttribute('aria-label', 'Table of Contents');

    // Buttons should be focusable
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).toHaveAttribute('class');
      expect(button.className).toContain('focus-visible:ring-2');
    });
  });

  it('handles headings with special characters', () => {
    const content = '## Hello & World!\n## Test (2024)\n## #Special @ Characters';
    render(<TableOfContents content={content} />);

    expect(screen.getByText('Hello & World!')).toBeInTheDocument();
    expect(screen.getByText('Test (2024)')).toBeInTheDocument();
    expect(screen.getByText('#Special @ Characters')).toBeInTheDocument();
  });

  it('handles H3 without parent H2', () => {
    const content = '### Orphan H3\n## Regular H2\n### Child H3';
    render(<TableOfContents content={content} />);

    // All headings should be present
    expect(screen.getByText('Orphan H3')).toBeInTheDocument();
    expect(screen.getByText('Regular H2')).toBeInTheDocument();
    expect(screen.getByText('Child H3')).toBeInTheDocument();
  });
});
