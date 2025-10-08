import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import rehypeRaw from 'rehype-raw';
import rehypeSlug from 'rehype-slug';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { cn } from '@/lib/utils';
import { MermaidDiagram } from './MermaidDiagram';
import { useDocumentNavigation } from '@/api/hooks/useDocumentNavigation';
import type { FileNode } from '@/api/types/document';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface MarkdownRendererProps {
  content: string;
  className?: string;
  projectId?: string;
  currentDocument?: FileNode | null;
  onDocumentSelect?: (document: FileNode) => void;
}

export function MarkdownRenderer({
  content,
  className,
  projectId,
  currentDocument,
  onDocumentSelect,
}: MarkdownRendererProps) {
  // Map to track broken links
  const [brokenLinks, setBrokenLinks] = useState<Set<string>>(new Set());

  // Use navigation hook only if all required props are provided
  const navigationEnabled = !!(projectId && currentDocument && onDocumentSelect);
  const navigation = useDocumentNavigation({
    projectId: projectId || '',
    currentDocument: currentDocument || null,
    onDocumentSelect: onDocumentSelect || (() => {}),
  });

  // Reset broken links when content changes
  useEffect(() => {
    setBrokenLinks(new Set());
  }, [content]);

  return (
    <TooltipProvider>
      <div
        className={cn(
          'prose prose-slate prose-sm max-w-none dark:prose-invert prose-headings:mb-2 prose-headings:mt-4 prose-p:my-2 prose-ul:my-2 prose-ol:my-2 prose-li:my-1',
          className
        )}
      >
        <ReactMarkdown
          remarkPlugins={[remarkGfm, remarkBreaks]}
          rehypePlugins={[rehypeRaw, rehypeSlug, rehypeAutolinkHeadings]}
          components={{
            code(props) {
              const { children, className, node, ...rest } = props;
              const match = /language-(\w+)/.exec(className || '');
              const language = match ? match[1] : '';
              const inline = !node || node.position?.start.line === node.position?.end.line;

              // Handle Mermaid diagrams
              if (!inline && language === 'mermaid') {
                return <MermaidDiagram chart={String(children)} />;
              }

              // Handle other code blocks with syntax highlighting
              if (!inline && match) {
                return (
                  <SyntaxHighlighter
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    style={vscDarkPlus as any}
                    language={language}
                    PreTag="div"
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                );
              }

              // Inline code
              return (
                <code className={cn('rounded bg-muted px-1 py-0.5', className)} {...rest}>
                  {children}
                </code>
              );
            },
            a(props) {
              const { children, href, ...rest } = props;

              if (!href) {
                return <a {...rest}>{children}</a>;
              }

              // External links - open in new tab
              if (navigationEnabled && navigation.isExternalLink(href)) {
                return (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                    {...rest}
                  >
                    {children}
                  </a>
                );
              }

              // Anchor-only links - let browser handle default behavior
              if (href.startsWith('#')) {
                return (
                  <a href={href} {...rest}>
                    {children}
                  </a>
                );
              }

              // Relative links - handle cross-document navigation
              if (navigationEnabled && navigation.isRelativeLink(href)) {
                const isBroken = brokenLinks.has(href);

                const handleClick = async (e: React.MouseEvent<HTMLAnchorElement>) => {
                  e.preventDefault();
                  await navigation.handleLinkClick(href, e);

                  // Check if navigation was successful by verifying the link wasn't broken
                  // This is a simple heuristic - if the link click didn't navigate, mark as broken
                  // In a real implementation, we'd want more robust broken link detection
                  if (currentDocument) {
                    const { findDocumentByRelativePath } = await import(
                      '@/api/services/documentService'
                    );
                    const found = await findDocumentByRelativePath(
                      projectId || '',
                      currentDocument.path,
                      href
                    );
                    if (!found && !brokenLinks.has(href)) {
                      setBrokenLinks((prev) => new Set(prev).add(href));
                    }
                  }
                };

                // If link is broken, show tooltip
                if (isBroken) {
                  return (
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <span
                          className="text-muted-foreground cursor-not-allowed underline decoration-dotted"
                          {...rest}
                        >
                          {children}
                        </span>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Document not found</p>
                      </TooltipContent>
                    </Tooltip>
                  );
                }

                // Normal relative link
                return (
                  <a
                    href={href}
                    onClick={handleClick}
                    className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 cursor-pointer"
                    {...rest}
                  >
                    {children}
                  </a>
                );
              }

              // Default link behavior (navigation not enabled)
              return (
                <a href={href} {...rest}>
                  {children}
                </a>
              );
            },
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </TooltipProvider>
  );
}
