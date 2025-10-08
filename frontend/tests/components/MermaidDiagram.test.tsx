import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MermaidDiagram } from '@/features/explorer/MermaidDiagram';

// Mock mermaid
vi.mock('mermaid', () => ({
  default: {
    initialize: vi.fn(),
    render: vi.fn(),
  },
}));

import mermaid from 'mermaid';

describe('MermaidDiagram', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders valid flowchart diagram successfully', async () => {
    const chart = 'graph TD\nA-->B';
    (mermaid.render as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      svg: '<svg>Flowchart</svg>',
    });

    render(<MermaidDiagram chart={chart} />);

    const diagram = screen.getByTestId('mermaid-diagram');
    expect(diagram).toBeInTheDocument();

    await waitFor(() => {
      expect(mermaid.render).toHaveBeenCalled();
      const callArgs = (mermaid.render as unknown as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(callArgs[0]).toMatch(/^mermaid-/);
      expect(callArgs[1]).toBe(chart);
    });
  });

  it('renders valid sequence diagram successfully', async () => {
    const chart = 'sequenceDiagram\nAlice->>Bob: Hello';
    (mermaid.render as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      svg: '<svg>Sequence</svg>',
    });

    render(<MermaidDiagram chart={chart} />);

    const diagram = screen.getByTestId('mermaid-diagram');
    expect(diagram).toBeInTheDocument();

    await waitFor(() => {
      expect(mermaid.render).toHaveBeenCalled();
      const callArgs = (mermaid.render as unknown as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(callArgs[0]).toMatch(/^mermaid-/);
      expect(callArgs[1]).toBe(chart);
    });
  });

  it('displays error message for malformed Mermaid syntax', async () => {
    const invalidChart = 'invalid mermaid syntax';
    (mermaid.render as unknown as ReturnType<typeof vi.fn>).mockRejectedValue(
      new Error('Parse error')
    );

    render(<MermaidDiagram chart={invalidChart} />);

    await waitFor(() => {
      expect(screen.getByText(/Parse error/i)).toBeInTheDocument();
    });
  });

  it('displays fallback code block if mermaid library fails to load', async () => {
    const chart = 'graph TD\nA-->B';
    (mermaid.render as unknown as ReturnType<typeof vi.fn>).mockRejectedValue(
      new Error('Library failed')
    );

    render(<MermaidDiagram chart={chart} />);

    await waitFor(() => {
      const errorElement = screen.getByText(/Library failed/i);
      expect(errorElement).toBeInTheDocument();
    });
  });

  it('diagram has responsive width styling applied', () => {
    const chart = 'graph TD\nA-->B';
    (mermaid.render as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      svg: '<svg>Test</svg>',
    });

    render(<MermaidDiagram chart={chart} />);

    const diagram = screen.getByTestId('mermaid-diagram');
    expect(diagram).toHaveClass('w-full');
    expect(diagram).toHaveClass('overflow-x-auto');
  });

  it('has proper accessibility attributes', () => {
    const chart = 'graph TD\nA-->B';
    (mermaid.render as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      svg: '<svg>Test</svg>',
    });

    render(<MermaidDiagram chart={chart} />);

    const diagram = screen.getByTestId('mermaid-diagram');
    expect(diagram).toHaveAttribute('role', 'img');
    expect(diagram).toHaveAttribute('aria-label', 'Mermaid diagram');
  });
});
