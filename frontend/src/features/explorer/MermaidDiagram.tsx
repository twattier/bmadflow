import { useEffect, useRef, useState } from 'react';
import { cn } from '@/lib/utils';

interface MermaidDiagramProps {
  chart: string;
  className?: string;
}

export function MermaidDiagram({ chart, className }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const renderDiagram = async () => {
      if (!containerRef.current) return;

      try {
        // Dynamic import to ensure client-side only
        const mermaid = (await import('mermaid')).default;

        // Detect dark mode
        const isDark = document.documentElement.classList.contains('dark');

        // Configure mermaid
        mermaid.initialize({
          startOnLoad: false,
          theme: isDark ? 'dark' : 'neutral',
          securityLevel: 'loose',
          fontFamily: 'ui-sans-serif, system-ui, sans-serif',
        });

        const id = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const { svg } = await mermaid.render(id, chart);

        if (mounted && containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
      } catch (err) {
        console.error('Mermaid rendering error:', err);
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to render diagram');
        }
      }
    };

    renderDiagram();

    return () => {
      mounted = false;
    };
  }, [chart]);

  if (error) {
    return (
      <div className="my-4 p-4 bg-destructive/10 text-destructive rounded">
        <p className="font-semibold">Mermaid Diagram Error:</p>
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={cn('mermaid-diagram my-4 w-full overflow-x-auto', className)}
      data-testid="mermaid-diagram"
      role="img"
      aria-label="Mermaid diagram"
    />
  );
}
