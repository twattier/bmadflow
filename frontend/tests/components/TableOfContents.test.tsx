import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { TableOfContents } from '@/features/explorer/TableOfContents';

describe('TableOfContents', () => {
  it('generates correct TOC structure from markdown with H1-H3 headers', () => {
    const content = `# Main Title
Some content here.

## Section 1
More content.

### Subsection 1.1
Details here.

## Section 2
Another section.

#### H4 should be ignored
This should not appear in TOC.`;

    render(<TableOfContents content={content} />);

    expect(screen.getByText('Main Title')).toBeInTheDocument();
    expect(screen.getByText('Section 1')).toBeInTheDocument();
    expect(screen.getByText('Subsection 1.1')).toBeInTheDocument();
    expect(screen.getByText('Section 2')).toBeInTheDocument();
    expect(screen.queryByText('H4 should be ignored')).not.toBeInTheDocument();
  });

  it('TOC links have correct href attributes', () => {
    const content = `# Introduction
## Getting Started
### Quick Start`;

    render(<TableOfContents content={content} />);

    const introLink = screen.getByText('Introduction').closest('a');
    const gettingStartedLink = screen.getByText('Getting Started').closest('a');
    const quickStartLink = screen.getByText('Quick Start').closest('a');

    expect(introLink).toHaveAttribute('href', '#introduction');
    expect(gettingStartedLink).toHaveAttribute('href', '#getting-started');
    expect(quickStartLink).toHaveAttribute('href', '#quick-start');
  });

  it('returns null when no headers present', () => {
    const content = 'Just some plain text without headers.';

    const { container } = render(<TableOfContents content={content} />);

    expect(container.firstChild).toBeNull();
  });

  it('handles special characters in headers', () => {
    const content = `# Hello World!
## API Reference: GET /api/users
### Section 2.1 - Overview`;

    render(<TableOfContents content={content} />);

    const link1 = screen.getByText('Hello World!').closest('a');
    const link2 = screen.getByText('API Reference: GET /api/users').closest('a');
    const link3 = screen.getByText('Section 2.1 - Overview').closest('a');

    expect(link1).toHaveAttribute('href', '#hello-world');
    expect(link2).toHaveAttribute('href', '#api-reference-get-apiusers');
    expect(link3).toHaveAttribute('href', '#section-21---overview');
  });

  it('applies correct indentation for header levels', () => {
    const content = `# H1
## H2
### H3`;

    render(<TableOfContents content={content} />);

    const h1Item = screen.getByText('H1').closest('li');
    const h2Item = screen.getByText('H2').closest('li');
    const h3Item = screen.getByText('H3').closest('li');

    expect(h1Item).toHaveStyle({ paddingLeft: '0rem' });
    expect(h2Item).toHaveStyle({ paddingLeft: '0.75rem' });
    expect(h3Item).toHaveStyle({ paddingLeft: '1.5rem' });
  });
});
