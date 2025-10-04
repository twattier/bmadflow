/**
 * Link type classification for markdown link processing
 */
export type LinkType = 'internal' | 'external' | 'anchor' | 'broken';

/**
 * Parsed link information
 */
export interface ParsedLink {
  type: LinkType;
  href: string;
  filePath?: string;    // For internal links
  fragment?: string;    // For anchor links (#section)
}

/**
 * Parse and classify a link URL to determine its type and extract relevant parts
 *
 * @param href - The link URL from markdown
 * @returns ParsedLink object with type and extracted components
 */
export function parseLinkUrl(href: string): ParsedLink {
  // Handle empty or undefined
  if (!href || href.trim() === '') {
    return { type: 'external', href: href || '' };
  }

  const trimmedHref = href.trim();

  // External links (http:// or https://)
  if (trimmedHref.startsWith('http://') || trimmedHref.startsWith('https://')) {
    return { type: 'external', href: trimmedHref };
  }

  // Anchor links (same-page navigation)
  if (trimmedHref.startsWith('#')) {
    return {
      type: 'anchor',
      href: trimmedHref,
      fragment: trimmedHref.slice(1)
    };
  }

  // Markdown file links (internal documents)
  // Check if the link contains .md (before any fragment)
  const fragmentIndex = trimmedHref.indexOf('#');
  const pathPart = fragmentIndex !== -1
    ? trimmedHref.slice(0, fragmentIndex)
    : trimmedHref;

  if (pathPart.endsWith('.md')) {
    const fragment = fragmentIndex !== -1
      ? trimmedHref.slice(fragmentIndex + 1)
      : undefined;

    return {
      type: 'internal',
      href: trimmedHref,
      filePath: pathPart,
      fragment
    };
  }

  // All other links (treat as external for safety)
  return { type: 'external', href: trimmedHref };
}
