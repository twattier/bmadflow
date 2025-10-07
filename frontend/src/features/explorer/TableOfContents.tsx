import { useMemo } from 'react';
import { cn } from '@/lib/utils';
import { slug } from 'github-slugger';

interface TOCItem {
  level: number;
  text: string;
  id: string;
}

interface TableOfContentsProps {
  content: string;
  className?: string;
}

export function TableOfContents({ content, className }: TableOfContentsProps) {
  const tocItems = useMemo(() => {
    const headingRegex = /^(#{1,3})\s+(.+)$/gm;
    const items: TOCItem[] = [];
    let match;

    while ((match = headingRegex.exec(content)) !== null) {
      const level = match[1].length;
      const text = match[2].trim();
      const id = slug(text);

      items.push({ level, text, id });
    }

    return items;
  }, [content]);

  if (tocItems.length === 0) {
    return null;
  }

  return (
    <nav
      className={cn(
        'sticky top-0 max-h-[20vh] overflow-auto border-b bg-background p-4',
        className
      )}
      aria-label="Table of contents"
    >
      <h2 className="mb-2 text-sm font-semibold">Contents</h2>
      <ul className="space-y-1 text-sm">
        {tocItems.map((item, index) => (
          <li key={index} style={{ paddingLeft: `${(item.level - 1) * 0.75}rem` }}>
            <a
              href={`#${item.id}`}
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              {item.text}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
