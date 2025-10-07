import type { FileNode } from '@/api/types/document';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useDocument } from '@/api/hooks/useDocument';
import { MarkdownRenderer } from './MarkdownRenderer';
import { TableOfContents } from './TableOfContents';

interface ContentViewerProps {
  file: FileNode | null;
  className?: string;
}

export function ContentViewer({ file, className }: ContentViewerProps) {
  const { data: document, isLoading, error } = useDocument(file?.id || null);

  if (!file) {
    return (
      <Card className={className}>
        <CardContent className="flex items-center justify-center h-full min-h-[400px]">
          <p className="text-muted-foreground">Select a file from the tree to view its content</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{file.name}</CardTitle>
      </CardHeader>
      <CardContent className="overflow-auto">
        {isLoading && <p className="text-muted-foreground">Loading...</p>}

        {error && <p className="text-destructive">Error loading document: {error.message}</p>}

        {document && file.file_type === 'md' && (
          <div>
            <TableOfContents content={document.content} />
            <MarkdownRenderer content={document.content} className="mt-4" />
          </div>
        )}

        {document && file.file_type !== 'md' && (
          <p className="text-muted-foreground">
            File viewer for {file.file_type} files coming soon
          </p>
        )}
      </CardContent>
    </Card>
  );
}
