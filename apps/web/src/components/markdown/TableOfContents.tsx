import { useMemo, useEffect, useState, useRef } from 'react';
import { generateHeadingId } from '../../utils/headingId';

interface HeadingNode {
  id: string;
  text: string;
  level: 2 | 3;
  children?: HeadingNode[];
}

interface TableOfContentsProps {
  content: string;
  enableActiveTracking?: boolean;
}

function TableOfContents({ content, enableActiveTracking = true }: TableOfContentsProps) {
  const [activeId, setActiveId] = useState<string>('');
  const observerRef = useRef<IntersectionObserver | null>(null);

  // Extract headings from markdown content
  const headings = useMemo(() => extractHeadings(content), [content]);

  // Setup Intersection Observer for active section tracking
  useEffect(() => {
    if (!enableActiveTracking || headings.length === 0) return;

    // Check browser support
    if (!('IntersectionObserver' in window)) {
      console.warn('IntersectionObserver not supported, active tracking disabled');
      return;
    }

    const observerOptions = {
      root: null,
      rootMargin: '-80px 0px -80% 0px',
      threshold: 0,
    };

    const handleIntersection = (entries: IntersectionObserverEntry[]) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setActiveId(entry.target.id);
        }
      });
    };

    observerRef.current = new IntersectionObserver(handleIntersection, observerOptions);

    // Observe all heading elements
    const allHeadingIds = getAllHeadingIds(headings);
    allHeadingIds.forEach((id) => {
      const element = document.getElementById(id);
      if (element) {
        observerRef.current?.observe(element);
      }
    });

    return () => {
      observerRef.current?.disconnect();
    };
  }, [headings, enableActiveTracking]);

  // Hide TOC if fewer than 3 total headings (AC7)
  const totalHeadingCount = getAllHeadingIds(headings).length;
  if (totalHeadingCount < 3) {
    return null;
  }

  const handleScrollTo = (headingId: string) => {
    const element = document.getElementById(headingId);
    element?.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent, headingId: string) => {
    if (e.key === 'Enter') {
      handleScrollTo(headingId);
    }
  };

  return (
    <nav
      role="navigation"
      aria-label="Table of Contents"
      className="sticky top-0 h-screen overflow-y-auto py-4"
    >
      <h3 className="text-sm font-semibold text-foreground mb-3 px-2">
        Table of Contents
      </h3>
      <ul className="space-y-1">
        {headings.map((heading) => (
          <li key={heading.id}>
            <button
              onClick={() => handleScrollTo(heading.id)}
              onKeyDown={(e) => handleKeyDown(e, heading.id)}
              aria-current={activeId === heading.id ? 'location' : undefined}
              className={`
                w-full text-left px-2 py-1.5 text-sm rounded-sm
                transition-colors duration-200
                hover:bg-accent hover:text-accent-foreground
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring
                ${
                  activeId === heading.id
                    ? 'bg-primary/10 text-primary font-medium'
                    : 'text-muted-foreground'
                }
                ${heading.level === 2 ? 'pl-2' : 'pl-6'}
              `}
            >
              {heading.text}
            </button>
            {heading.children && heading.children.length > 0 && (
              <ul className="mt-1 space-y-1">
                {heading.children.map((child) => (
                  <li key={child.id}>
                    <button
                      onClick={() => handleScrollTo(child.id)}
                      onKeyDown={(e) => handleKeyDown(e, child.id)}
                      aria-current={activeId === child.id ? 'location' : undefined}
                      className={`
                        w-full text-left px-2 py-1.5 text-sm rounded-sm
                        transition-colors duration-200
                        hover:bg-accent hover:text-accent-foreground
                        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring
                        ${
                          activeId === child.id
                            ? 'bg-primary/10 text-primary font-medium'
                            : 'text-muted-foreground'
                        }
                        pl-6
                      `}
                    >
                      {child.text}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </nav>
  );
}

// Helper function to extract headings from markdown
function extractHeadings(content: string): HeadingNode[] {
  const headingRegex = /^(#{2,3})\s+(.+)$/gm;
  const matches = Array.from(content.matchAll(headingRegex));

  // Build hierarchical structure: H2 as parents, H3 as children
  const hierarchical: HeadingNode[] = [];
  let currentH2: HeadingNode | null = null;
  const idCounts = new Map<string, number>();

  matches.forEach((match) => {
    const level = match[1].length as 2 | 3;
    const text = match[2].trim();

    // Use shared ID generation function to match MarkdownRenderer
    const id = generateHeadingId(text, idCounts);

    if (level === 2) {
      currentH2 = { id, text, level: 2, children: [] };
      hierarchical.push(currentH2);
    } else if (level === 3) {
      const h3Node: HeadingNode = { id, text, level: 3 };
      if (currentH2) {
        currentH2.children = currentH2.children || [];
        currentH2.children.push(h3Node);
      } else {
        // H3 without parent H2, add as top-level
        hierarchical.push(h3Node);
      }
    }
  });

  return hierarchical;
}

// Get all heading IDs (including nested ones) for observer
function getAllHeadingIds(headings: HeadingNode[]): string[] {
  const ids: string[] = [];
  headings.forEach((heading) => {
    ids.push(heading.id);
    if (heading.children) {
      heading.children.forEach((child) => ids.push(child.id));
    }
  });
  return ids;
}

export default TableOfContents;
