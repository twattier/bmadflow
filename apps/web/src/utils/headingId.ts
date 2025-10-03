// Shared utility for generating consistent heading IDs across components
// Used by both MarkdownRenderer (to add IDs to headings) and TableOfContents (to link to them)

export function generateHeadingId(text: string, idCounts: Map<string, number>): string {
  const baseId = 'toc-' + text
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '');

  const count = idCounts.get(baseId) || 0;
  idCounts.set(baseId, count + 1);

  return count > 0 ? `${baseId}-${count}` : baseId;
}
