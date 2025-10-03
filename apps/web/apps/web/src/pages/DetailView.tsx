import { useParams } from 'react-router-dom';
import { useDocument } from '../hooks/useDocuments';
import MarkdownRenderer from '../components/markdown/MarkdownRenderer';
import MarkdownLoadingSkeleton from '../components/markdown/MarkdownLoadingSkeleton';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { AlertCircle } from 'lucide-react';

export default function DetailView() {
  const { documentId } = useParams<{ documentId: string }>();
  const { data: document, isLoading, error } = useDocument(documentId || '');

  if (isLoading) {
    return <MarkdownLoadingSkeleton />;
  }

  if (error || !document) {
    return (
      <div className="container mx-auto p-6 max-w-3xl">
        <Card className="border-destructive">
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-destructive" />
              <CardTitle className="text-destructive">Error</CardTitle>
            </div>
            <CardDescription>
              Failed to load document. Please try again.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <MarkdownRenderer content={document.content} />
    </div>
  );
}
