import { memo, useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize, { defaultSchema } from 'rehype-sanitize';
import CodeBlock from './CodeBlock';
import MermaidBlock from './MermaidBlock';
import { generateHeadingId } from '../../utils/headingId';
import './markdown.css';

interface MarkdownRendererProps {
  content: string;
  enableMermaid?: boolean;  // For future Story 3.5
  enableTOC?: boolean;       // For future Story 3.3
}

function MarkdownRenderer({ content }: MarkdownRendererProps) {
  // Pre-generate all heading IDs in a single pass to avoid StrictMode double-render issues
  const headingIds = useMemo(() => {
    const headingRegex = /^(#{2,3})\s+(.+)$/gm;
    const matches = Array.from(content.matchAll(headingRegex));
    const idCounts = new Map<string, number>();
    const ids = new Map<string, string>();

    matches.forEach((match) => {
      const text = match[2].trim();
      const id = generateHeadingId(text, idCounts);
      ids.set(text, id);
    });

    return ids;
  }, [content]);

  // enableMermaid and enableTOC for future stories 3.5 and 3.3

  // Handle escaped newlines from database (\\n -> \n)
  const processedContent = content.replace(/\\n/g, '\n').replace(/\\r/g, '\r').replace(/\\t/g, '\t');

  // GitHub-style sanitization schema
  const sanitizeSchema = {
    ...defaultSchema,
    attributes: {
      ...defaultSchema.attributes,
      // Allow href on links (but sanitize javascript:)
      a: ['href', 'title', 'target', 'rel'],
      // Allow src on images
      img: ['src', 'alt', 'title', 'width', 'height'],
      // Allow common safe tags
      div: ['className'],
      span: ['className'],
      code: ['className'],
    },
    protocols: {
      ...defaultSchema.protocols,
      // Only allow http, https, mailto protocols (blocks javascript:)
      href: ['http', 'https', 'mailto'],
      src: ['http', 'https'],
    },
    // Remove dangerous tags
    tagNames: [
      ...(defaultSchema.tagNames || []),
      'div',
      'span',
    ].filter((tag) => !['script', 'iframe', 'object', 'embed'].includes(tag)),
  };

  return (
    <div className="w-full max-w-5xl mx-auto px-4 lg:px-0">
      <article
        className="markdown-content"
        style={{
          fontSize: '16px',
          lineHeight: '1.75',
          color: 'var(--foreground)',
        }}
      >
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[
            rehypeRaw,
            [rehypeSanitize, sanitizeSchema],
          ]}
          components={{
            code(props) {
              const { node, className, children, ...rest } = props;
              const match = /language-(\w+)/.exec(className || '');
              const language = match ? match[1] : undefined;
              const isInline = !node || node.position?.start.line === node.position?.end.line;

              // Check if it's a Mermaid diagram
              if (!isInline && language === 'mermaid') {
                return <MermaidBlock>{String(children)}</MermaidBlock>;
              }

              return !isInline && (language || className) ? (
                <CodeBlock
                  language={language}
                  className={className}
                  {...rest}
                >
                  {String(children)}
                </CodeBlock>
              ) : (
                <code className={className} {...rest}>
                  {children}
                </code>
              );
            },
            // Add IDs to H2 and H3 headings for TOC scroll targets
            h2({ children, ...props }) {
              const text = String(children);
              const id = headingIds.get(text) || text.toLowerCase().replace(/\s+/g, '-');
              return <h2 id={id} {...props}>{children}</h2>;
            },
            h3({ children, ...props }) {
              const text = String(children);
              const id = headingIds.get(text) || text.toLowerCase().replace(/\s+/g, '-');
              return <h3 id={id} {...props}>{children}</h3>;
            },
            // External links open in new tab
            a({ children, href, ...props }) {
              const isExternal = href?.startsWith('http://') || href?.startsWith('https://');
              if (isExternal) {
                return (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    {...props}
                  >
                    {children}
                  </a>
                );
              }
              return <a href={href} {...props}>{children}</a>;
            },
          }}
        >
          {processedContent}
        </ReactMarkdown>
      </article>
    </div>
  );
}

// Memoize to prevent unnecessary re-renders (performance optimization)
export default memo(MarkdownRenderer);
