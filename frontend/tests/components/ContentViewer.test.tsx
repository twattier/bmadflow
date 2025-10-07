import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ContentViewer } from '@/features/explorer/ContentViewer';
import { FileNode } from '@/api/types/document';

describe('ContentViewer', () => {
  it('renders placeholder when no file selected', () => {
    render(<ContentViewer file={null} />);

    expect(
      screen.getByText('Select a file from the tree to view its content')
    ).toBeInTheDocument();
  });

  it('displays file name when file selected', () => {
    const mockFile: FileNode = {
      id: 'file-1',
      name: 'README.md',
      type: 'file',
      path: 'docs/README.md',
      file_type: 'md',
    };

    render(<ContentViewer file={mockFile} />);

    expect(screen.getByText('README.md')).toBeInTheDocument();
    expect(
      screen.getByText('Content viewer will be implemented in Story 3.3')
    ).toBeInTheDocument();
  });
});
