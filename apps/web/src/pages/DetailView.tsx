import { useParams } from 'react-router-dom';
import { useState } from 'react';
import { useDocument } from '../hooks/useDocuments';
import MarkdownRenderer from '../components/markdown/MarkdownRenderer';
import TableOfContents from '../components/markdown/TableOfContents';
import MarkdownLoadingSkeleton from '../components/markdown/MarkdownLoadingSkeleton';
import { Card, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { AlertCircle, Menu, X } from 'lucide-react';

export default function DetailView() {
  const { documentId } = useParams<{ documentId: string }>();
  const { data: document, isLoading, error } = useDocument(documentId || '');
  const [sidebarOpen, setSidebarOpen] = useState(true);

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
    <div className="relative flex">
      {/* TOC Sidebar - collapsible on narrow screens */}
      <aside
        className={`
          fixed lg:sticky top-0 left-0 h-screen bg-background border-r
          transition-transform duration-300 ease-in-out z-40
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          ${sidebarOpen ? 'w-64' : 'w-0 lg:w-64'}
        `}
      >
        <div className="w-64">
          <TableOfContents content={document.content} />
        </div>
      </aside>

      {/* Toggle button for mobile */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="fixed top-4 left-4 z-50 lg:hidden p-2 rounded-md bg-background border shadow-sm hover:bg-accent"
        aria-label="Toggle table of contents"
      >
        {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {/* Main content area */}
      <main
        className={`
          flex-1 py-8 transition-all duration-300
          ${sidebarOpen ? 'lg:ml-0' : 'lg:ml-0'}
        `}
      >
        <MarkdownRenderer content={document.content} />
      </main>
    </div>
  );
}
