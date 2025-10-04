import { memo, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { parseLinkUrl } from '@/utils/parseLinkUrl';
import { useDocumentLink } from '@/hooks/useDocumentLink';
import { useProject } from '@/stores/ProjectContext';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

export interface DocumentLinkProps {
  href: string;
  children: React.ReactNode;
  sourceDocumentPath?: string;
  className?: string;
}

/**
 * Smart link component for markdown that handles:
 * - Internal document links (.md files) -> Navigate to Detail view
 * - External links (http/https) -> Open in new tab
 * - Anchor links (#section) -> Same-page scroll
 * - Broken links -> Show error tooltip
 */
export const DocumentLink = memo(({ href, children, sourceDocumentPath: _sourceDocumentPath, className }: DocumentLinkProps) => {
  const { currentProject } = useProject();
  const parsedLink = useMemo(() => parseLinkUrl(href || ''), [href]);

  // Resolve internal markdown links
  const { data: resolvedDoc, isLoading, error } = useDocumentLink(
    parsedLink.type === 'internal' ? parsedLink.filePath! : '',
    currentProject?.id || ''
  );

  // External links
  if (parsedLink.type === 'external') {
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className={className}
      >
        {children}
      </a>
    );
  }

  // Anchor links (same-page navigation)
  if (parsedLink.type === 'anchor') {
    return (
      <a href={href} className={className}>
        {children}
      </a>
    );
  }

  // Internal markdown links
  if (parsedLink.type === 'internal') {
    // No project loaded yet - render as disabled link
    if (!currentProject?.id) {
      return (
        <a href="#" onClick={(e) => e.preventDefault()} className={`text-muted-foreground ${className || ''}`} title="Project not loaded">
          {children}
        </a>
      );
    }

    // Loading state - show as plain text
    if (isLoading) {
      return <span className={className}>{children}</span>;
    }

    // Broken link (404 or error)
    if (error || !resolvedDoc) {
      return (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <span
                className={`text-red-600 cursor-not-allowed ${className || ''}`}
              >
                {children}
              </span>
            </TooltipTrigger>
            <TooltipContent>
              <p>Document not found</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      );
    }

    // Successful resolution - navigate to Detail view
    const targetPath = parsedLink.fragment
      ? `/detail/${resolvedDoc.id}#${parsedLink.fragment}`
      : `/detail/${resolvedDoc.id}`;

    return (
      <Link to={targetPath} className={className}>
        {children}
      </Link>
    );
  }

  // Fallback - treat as external
  return <span className={className}>{children}</span>;
});

DocumentLink.displayName = 'DocumentLink';
