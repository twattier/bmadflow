import { useEffect, useMemo, useState } from 'react';
import { Search, X } from 'lucide-react';
import { useProject } from '../stores/ProjectContext';
import { useDocuments } from '../hooks/useDocuments';
import { DocumentCard } from '../components/DocumentCard';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { EmptyState } from '../components/EmptyState';
import { Input } from '../components/ui/input';

// Debounce hook for search
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

export default function EpicsView() {
  const { currentProject } = useProject();
  const [searchQuery, setSearchQuery] = useState('');

  const debouncedSearch = useDebounce(searchQuery, 300);

  // TEMPORARY: Hardcode agent-lab project ID
  const agentLabProjectId = '7e4d469f-dd82-42ab-93a1-bc240e175c29';

  const { data: documents, isLoading, isError } = useDocuments({
    projectId: currentProject?.id || agentLabProjectId,
    docType: 'epic',
  });

  const filteredDocuments = useMemo(() => {
    if (!documents) return [];
    if (!debouncedSearch) return documents;

    return documents.filter((doc) =>
      doc.title.toLowerCase().includes(debouncedSearch.toLowerCase())
    );
  }, [documents, debouncedSearch]);

  if (isLoading) {
    return (
      <div className="container mx-auto p-6">
        <LoadingSkeleton />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
          <p className="text-destructive font-semibold mb-2">
            Failed to load epic documents
          </p>
          <p className="text-sm text-muted-foreground">
            Please try again or check your connection.
          </p>
        </div>
      </div>
    );
  }

  if (!documents || documents.length === 0) {
    return (
      <div className="container mx-auto p-6">
        <EmptyState />
      </div>
    );
  }

  const showNoResults = debouncedSearch && filteredDocuments.length === 0;

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-8">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search epic documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 pr-10"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
              aria-label="Clear search"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {debouncedSearch && !showNoResults && (
          <p className="text-sm text-muted-foreground mt-2">
            Showing {filteredDocuments.length} of {documents.length} documents
          </p>
        )}
      </div>

      {showNoResults ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No documents match your search</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-8">
          {filteredDocuments.map((document) => (
            <DocumentCard key={document.id} document={document} />
          ))}
        </div>
      )}
    </div>
  );
}
