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

export default function ScopingView() {
  const { currentProject } = useProject();
  const [searchQuery, setSearchQuery] = useState('');

  // AC7: Debounce search input (300ms)
  const debouncedSearch = useDebounce(searchQuery, 300);

  // TEMPORARY FIX FOR MANUAL TESTING: Hardcode test project ID
  const testProjectId = '550e8400-e29b-41d4-a716-446655440000';

  // AC1: Fetch scoping documents with React Query
  const { data: documents, isLoading, isError } = useDocuments({
    projectId: currentProject?.id || testProjectId,
    docType: 'scoping',
  });

  // AC7: Client-side filtering by title
  const filteredDocuments = useMemo(() => {
    if (!documents) return [];
    if (!debouncedSearch) return documents;

    return documents.filter((doc) =>
      doc.title.toLowerCase().includes(debouncedSearch.toLowerCase())
    );
  }, [documents, debouncedSearch]);

  // AC1: Loading state with skeleton placeholders
  if (isLoading) {
    return (
      <div className="container mx-auto p-6">
        <LoadingSkeleton />
      </div>
    );
  }

  // AC1: Error handling
  if (isError) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
          <p className="text-destructive font-semibold mb-2">
            Failed to load scoping documents
          </p>
          <p className="text-sm text-muted-foreground">
            Please try again or check your connection.
          </p>
        </div>
      </div>
    );
  }

  // AC6: Empty state when no documents
  if (!documents || documents.length === 0) {
    return (
      <div className="container mx-auto p-6">
        <EmptyState />
      </div>
    );
  }

  // AC7: No results message when search returns empty
  const showNoResults = debouncedSearch && filteredDocuments.length === 0;

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      {/* AC7: Search input */}
      <div className="mb-8">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search scoping documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 pr-10"
          />
          {/* AC7: Clear button */}
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

        {/* AC7: Filtered count (only when search is active) */}
        {debouncedSearch && !showNoResults && (
          <p className="text-sm text-muted-foreground mt-2">
            Showing {filteredDocuments.length} of {documents.length} documents
          </p>
        )}
      </div>

      {/* AC7: No results message */}
      {showNoResults ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No documents match your search</p>
        </div>
      ) : (
        /* AC2: Responsive grid layout */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-8">
          {filteredDocuments.map((document) => (
            <DocumentCard key={document.id} document={document} />
          ))}
        </div>
      )}
    </div>
  );
}
