import { Button } from '@/components/ui/button';
import type { SourceDocument } from '@/api/types/message';

interface MessageSourceLinksProps {
  sources: SourceDocument[];
  onSourceClick: (source: SourceDocument) => void;
}

export function MessageSourceLinks({ sources, onSourceClick }: MessageSourceLinksProps) {
  // Don't render anything if sources array is empty
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 pt-3 border-t border-border">
      <div className="text-sm text-muted-foreground mb-2">Sources:</div>
      <ul className="list-disc list-inside space-y-1">
        {sources.map((source, index) => {

          // Handle legacy data or malformed sources
          // Skip sources that don't have minimal required data
          if (!source || (!source.file_path && !source.document_id)) {
            console.warn(`Skipping invalid source at index ${index}:`, source);
            return null;
          }

          // Extract filename from file_path (e.g., "docs/prd.md" -> "prd.md")
          const filePath = typeof source?.file_path === 'string' ? source.file_path : '';
          const fileName = filePath ? (filePath.split('/').pop() || filePath) : `source-${index + 1}`;

          // Format link text: filename#anchor or just filename
          const linkText = source?.header_anchor
            ? `${fileName}#${source.header_anchor}`
            : fileName;

          return (
            <li key={`${source.document_id || `source-${index}`}-${index}`} className="text-sm">
              <Button
                variant="link"
                className="h-auto p-0 text-primary hover:underline"
                onClick={() => onSourceClick(source)}
                title={`File: ${filePath || 'unknown'}`}
              >
                {linkText}
              </Button>
            </li>
          );
        }).filter(Boolean)}
      </ul>
    </div>
  );
}
