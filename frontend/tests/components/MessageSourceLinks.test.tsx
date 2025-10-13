import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MessageSourceLinks } from '@/features/chat/MessageSourceLinks';
import type { SourceDocument } from '@/api/types/message';

describe('MessageSourceLinks', () => {
  const mockSources: SourceDocument[] = [
    {
      document_id: 'doc1',
      file_path: 'docs/prd.md',
      header_anchor: 'goals',
      similarity_score: 0.95,
    },
    {
      document_id: 'doc2',
      file_path: 'docs/architecture.md',
      header_anchor: null,
      similarity_score: 0.87,
    },
  ];

  it('renders source links with correct format when anchor exists', () => {
    const mockOnClick = vi.fn();
    render(<MessageSourceLinks sources={mockSources} onSourceClick={mockOnClick} />);

    expect(screen.getByText(/Sources:/i)).toBeInTheDocument();
    expect(screen.getByText(/prd.md#goals/i)).toBeInTheDocument();
  });

  it('renders source links without anchor when anchor is null', () => {
    const mockOnClick = vi.fn();
    render(<MessageSourceLinks sources={mockSources} onSourceClick={mockOnClick} />);

    expect(screen.getByText(/^architecture\.md$/i)).toBeInTheDocument();
  });

  it('calls onSourceClick when link clicked', () => {
    const mockOnClick = vi.fn();
    render(<MessageSourceLinks sources={mockSources} onSourceClick={mockOnClick} />);

    const firstLink = screen.getByText(/prd.md#goals/i);
    fireEvent.click(firstLink);

    expect(mockOnClick).toHaveBeenCalledWith(mockSources[0]);
    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('calls onSourceClick with correct source for each link', () => {
    const mockOnClick = vi.fn();
    render(<MessageSourceLinks sources={mockSources} onSourceClick={mockOnClick} />);

    const firstLink = screen.getByText(/prd.md#goals/i);
    const secondLink = screen.getByText(/^architecture\.md$/i);

    fireEvent.click(firstLink);
    expect(mockOnClick).toHaveBeenCalledWith(mockSources[0]);

    fireEvent.click(secondLink);
    expect(mockOnClick).toHaveBeenCalledWith(mockSources[1]);
  });

  it('renders nothing when sources array is empty', () => {
    const mockOnClick = vi.fn();
    const { container } = render(<MessageSourceLinks sources={[]} onSourceClick={mockOnClick} />);

    expect(container.firstChild).toBeNull();
  });

  it('renders nothing when sources is null', () => {
    const mockOnClick = vi.fn();
    const { container } = render(
      <MessageSourceLinks sources={null as unknown as SourceDocument[]} onSourceClick={mockOnClick} />
    );

    expect(container.firstChild).toBeNull();
  });

  it('renders multiple source links', () => {
    const mockOnClick = vi.fn();
    const multipleSources: SourceDocument[] = [
      ...mockSources,
      {
        document_id: 'doc3',
        file_path: 'docs/readme.md',
        header_anchor: 'installation',
        similarity_score: 0.82,
      },
    ];

    render(<MessageSourceLinks sources={multipleSources} onSourceClick={mockOnClick} />);

    expect(screen.getByText(/prd.md#goals/i)).toBeInTheDocument();
    expect(screen.getByText(/^architecture\.md$/i)).toBeInTheDocument();
    expect(screen.getByText(/readme.md#installation/i)).toBeInTheDocument();
  });

  it('uses Button component with link variant', () => {
    const mockOnClick = vi.fn();
    const { container } = render(
      <MessageSourceLinks sources={[mockSources[0]]} onSourceClick={mockOnClick} />
    );

    const button = container.querySelector('button');
    expect(button).toBeInTheDocument();
  });

  it('displays sources label', () => {
    const mockOnClick = vi.fn();
    render(<MessageSourceLinks sources={mockSources} onSourceClick={mockOnClick} />);

    const label = screen.getByText(/^Sources:$/);
    expect(label).toBeInTheDocument();
  });

  it('formats link text correctly without brackets', () => {
    const mockOnClick = vi.fn();
    render(<MessageSourceLinks sources={[mockSources[0]]} onSourceClick={mockOnClick} />);

    const link = screen.getByText(/prd.md#goals/i);
    expect(link).toBeInTheDocument();
    // Verify no brackets in the text
    expect(link.textContent).not.toContain('[');
    expect(link.textContent).not.toContain(']');
  });
});
