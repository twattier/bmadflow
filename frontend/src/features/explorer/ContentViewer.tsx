import type { FileNode } from '@/api/types/document';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface ContentViewerProps {
  file: FileNode | null;
  className?: string;
}

export function ContentViewer({ file, className }: ContentViewerProps) {
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
        <p className="text-muted-foreground">Content viewer will be implemented in Story 3.3</p>
      </CardContent>
    </Card>
  );
}
