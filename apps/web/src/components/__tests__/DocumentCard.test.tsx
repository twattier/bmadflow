import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { DocumentCard } from '../DocumentCard';
import type { Document } from '../../types/document';

const mockDocument: Document = {
  id: 'doc-1',
  project_id: 'proj-1',
  file_path: 'docs/scoping/prd.md',
  doc_type: 'scoping',
  title: 'Product Requirements Document',
  excerpt: 'BMADFlow is a self-hosted dashboard for documentation visualization...',
  last_modified: '2025-10-01T14:32:15Z',
  extraction_status: 'completed',
  extraction_confidence: 0.95,
};

function TestWrapper({ children }: { children: React.ReactNode }) {
  return <BrowserRouter>{children}</BrowserRouter>;
}

describe('DocumentCard', () => {
  // AC3: Card content display
  it('should display document title', () => {
    render(
      <TestWrapper>
        <DocumentCard document={mockDocument} />
      </TestWrapper>
    );

    expect(screen.getByText('Product Requirements Document')).toBeInTheDocument();
  });

  it('should display document excerpt', () => {
    render(
      <TestWrapper>
        <DocumentCard document={mockDocument} />
      </TestWrapper>
    );

    expect(
      screen.getByText(/BMADFlow is a self-hosted dashboard/i)
    ).toBeInTheDocument();
  });

  it('should display relative last modified date', () => {
    render(
      <TestWrapper>
        <DocumentCard document={mockDocument} />
      </TestWrapper>
    );

    // date-fns formatDistanceToNow will show something like "X days ago"
    expect(screen.getByText(/ago/i)).toBeInTheDocument();
  });

  it('should display status badge when extraction_status is present', () => {
    render(
      <TestWrapper>
        <DocumentCard document={mockDocument} />
      </TestWrapper>
    );

    expect(screen.getByText('completed')).toBeInTheDocument();
  });

  it('should not display status badge when extraction_status is null', () => {
    const docWithoutStatus = { ...mockDocument, extraction_status: null };

    render(
      <TestWrapper>
        <DocumentCard document={docWithoutStatus} />
      </TestWrapper>
    );

    expect(screen.queryByText('completed')).not.toBeInTheDocument();
  });

  // AC4: Card is a link to detail view
  it('should render as a link to detail view', () => {
    const { container } = render(
      <TestWrapper>
        <DocumentCard document={mockDocument} />
      </TestWrapper>
    );

    const link = container.querySelector('a');
    expect(link).toHaveAttribute('href', '/detail/doc-1');
  });

  // AC4: Hover and focus states
  it('should have hover transition class', () => {
    const { container } = render(
      <TestWrapper>
        <DocumentCard document={mockDocument} />
      </TestWrapper>
    );

    const link = container.querySelector('a');
    expect(link).toHaveClass('hover:shadow-lg');
    expect(link).toHaveClass('transition-shadow');
  });

  it('should have focus-visible ring for keyboard navigation', () => {
    const { container } = render(
      <TestWrapper>
        <DocumentCard document={mockDocument} />
      </TestWrapper>
    );

    const link = container.querySelector('a');
    expect(link).toHaveClass('focus-visible:ring-2');
    expect(link).toHaveClass('focus-visible:ring-primary');
  });

  // AC3: Typography specifications
  it('should have correct typography classes', () => {
    const { container } = render(
      <TestWrapper>
        <DocumentCard document={mockDocument} />
      </TestWrapper>
    );

    const title = container.querySelector('h3');
    expect(title).toHaveClass('text-lg');
    expect(title).toHaveClass('font-semibold');
    expect(title).toHaveClass('line-clamp-2');
    expect(title).toHaveClass('leading-[1.4]');
  });
});
