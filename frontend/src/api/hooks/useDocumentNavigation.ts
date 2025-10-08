import { useCallback } from 'react';
import type { FileNode } from '@/api/types/document';
import { findDocumentByRelativePath } from '@/api/services/documentService';

interface UseDocumentNavigationParams {
  projectId: string;
  currentDocument: FileNode | null;
  onDocumentSelect: (document: FileNode) => void;
}

interface UseDocumentNavigationReturn {
  handleLinkClick: (href: string, event?: React.MouseEvent<HTMLAnchorElement>) => Promise<void>;
  isExternalLink: (href: string) => boolean;
  isRelativeLink: (href: string) => boolean;
}

/**
 * Hook for handling document navigation from markdown links
 *
 * @param projectId - The current project ID
 * @param currentDocument - The currently displayed document (FileNode)
 * @param onDocumentSelect - Callback to invoke when a new document is selected
 * @returns Object with handleLinkClick function and link type checkers
 */
export function useDocumentNavigation({
  projectId,
  currentDocument,
  onDocumentSelect,
}: UseDocumentNavigationParams): UseDocumentNavigationReturn {
  /**
   * Check if a link is external (http:// or https://)
   */
  const isExternalLink = useCallback((href: string): boolean => {
    return href.startsWith('http://') || href.startsWith('https://');
  }, []);

  /**
   * Check if a link is relative (not external and not an anchor-only link)
   */
  const isRelativeLink = useCallback(
    (href: string): boolean => {
      // External links are not relative
      if (isExternalLink(href)) {
        return false;
      }

      // Anchor-only links (#section) are not cross-document relative links
      if (href.startsWith('#')) {
        return false;
      }

      // Everything else is considered a relative link
      return true;
    },
    [isExternalLink]
  );

  /**
   * Handle link clicks for both external and relative links
   */
  const handleLinkClick = useCallback(
    async (href: string, event?: React.MouseEvent<HTMLAnchorElement>) => {
      // External links: open in new tab
      if (isExternalLink(href)) {
        if (event) {
          event.preventDefault();
        }
        window.open(href, '_blank', 'noopener,noreferrer');
        return;
      }

      // Anchor-only links: let browser handle default scroll behavior
      if (href.startsWith('#')) {
        return;
      }

      // Relative links: handle cross-document navigation
      if (isRelativeLink(href) && currentDocument) {
        if (event) {
          event.preventDefault();
        }

        try {
          // Find the target document
          const targetDocument = await findDocumentByRelativePath(
            projectId,
            currentDocument.path,
            href
          );

          if (targetDocument) {
            // Update browser history
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.set('file', targetDocument.path);
            window.history.pushState(
              { filePath: targetDocument.path, fileId: targetDocument.id },
              '',
              newUrl.toString()
            );

            // Trigger document selection
            onDocumentSelect(targetDocument);
          } else {
            console.warn(`Document not found for relative path: ${href}`);
          }
        } catch (error) {
          console.error('Error navigating to document:', error);
        }
      }
    },
    [isExternalLink, isRelativeLink, currentDocument, projectId, onDocumentSelect]
  );

  return {
    handleLinkClick,
    isExternalLink,
    isRelativeLink,
  };
}
