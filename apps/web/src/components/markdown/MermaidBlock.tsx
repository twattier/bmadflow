import { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

interface MermaidBlockProps {
  children: string;
}

mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  themeVariables: {
    primaryColor: '#dbeafe',
    primaryTextColor: '#1e3a8a',
    primaryBorderColor: '#3b82f6',
    lineColor: '#64748b',
    secondaryColor: '#e9d5ff',
    tertiaryColor: '#d1fae5',
    mainBkg: '#f1f5f9',
    secondBkg: '#e2e8f0',
    tertiaryBkg: '#fef3c7',
    clusterBkg: '#f8fafc',
    fontSize: '14px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  },
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'basis',
    padding: 30,
    nodeSpacing: 80,
    rankSpacing: 100,
    diagramPadding: 20,
  },
  gantt: {
    numberSectionStyles: 4,
    axisFormat: '%Y-%m-%d',
  },
});

export default function MermaidBlock({ children }: MermaidBlockProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const render = async () => {
      if (!containerRef.current) return;
      try {
        const id = 'diagram-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
        const result = await mermaid.render(id, children.trim());
        containerRef.current.innerHTML = result.svg;
        
        // Add better styling to the SVG
        const svg = containerRef.current.querySelector('svg');
        if (svg) {
          svg.style.maxWidth = '100%';
          svg.style.height = 'auto';
        }
      } catch (e) {
        console.error('Mermaid error:', e);
        if (containerRef.current) {
          containerRef.current.innerHTML = `<div style="padding:1rem;background:#fee2e2;border:1px solid #fecaca;border-radius:6px;color:#991b1b;font-size:14px"><strong>Diagram Error</strong><br/>Could not render Mermaid diagram</div>`;
        }
      }
    };
    render();
  }, [children]);

  return (
    <div 
      ref={containerRef} 
      style={{ 
        margin: '1.5rem 0', 
        padding: '1.5rem', 
        backgroundColor: '#f8fafc', 
        borderRadius: '8px', 
        border: '1px solid #e2e8f0',
        overflow: 'auto',
        minHeight: '200px',
      }} 
    />
  );
}
