import { useEffect, useMemo, useState } from 'react';
import { Search, X } from 'lucide-react';
import { useProject } from '../stores/ProjectContext';
import { useEpics } from '../hooks/useEpics';
import { DocumentCard } from '../components/DocumentCard';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { EmptyState } from '../components/EmptyState';
import { Input } from '../components/ui/input';
import { Card } from '../components/ui/card';

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

  const { data: epics, isLoading, isError } = useEpics({
    projectId: currentProject?.id || agentLabProjectId,
  });

  // Sort epics by number extracted from file_path
  const sortedEpics = useMemo(() => {
    if (!epics) return [];

    return [...epics].sort((a, b) => {
      const numA = a.file_path.match(/epic-(\d+)/i)?.[1];
      const numB = b.file_path.match(/epic-(\d+)/i)?.[1];

      if (numA && numB) return parseInt(numA) - parseInt(numB);
      if (numA) return -1;
      if (numB) return 1;
      return a.file_path.localeCompare(b.file_path);
    });
  }, [epics]);

  // Filter epics by search query
  const filteredEpics = useMemo(() => {
    if (!debouncedSearch) return sortedEpics;

    return sortedEpics.filter((epic) =>
      epic.title.toLowerCase().includes(debouncedSearch.toLowerCase())
    );
  }, [sortedEpics, debouncedSearch]);

  // Calculate status counts for rollup widget
  const statusCounts = useMemo(() => {
    if (!epics) return { total: 0, draft: 0, dev: 0, done: 0 };

    return {
      total: epics.length,
      draft: epics.filter(e => e.extracted_epic?.status === 'draft').length,
      dev: epics.filter(e => e.extracted_epic?.status === 'dev').length,
      done: epics.filter(e => e.extracted_epic?.status === 'done').length,
    };
  }, [epics]);

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
            Failed to load epics
          </p>
          <p className="text-sm text-muted-foreground">
            Please try again or check your connection.
          </p>
        </div>
      </div>
    );
  }

  if (!epics || epics.length === 0) {
    return (
      <div className="container mx-auto p-6">
        <EmptyState />
      </div>
    );
  }

  const showNoResults = debouncedSearch && filteredEpics.length === 0;

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      {/* Status Rollup Widget */}
      <Card className="bg-muted p-4 mb-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 text-sm">
          <span className="font-semibold">{statusCounts.total} epics total</span>
          <span className="hidden sm:inline text-muted-foreground">|</span>
          <span className="text-muted-foreground">
            {statusCounts.draft} draft, {statusCounts.dev} in dev, {statusCounts.done} done
          </span>
        </div>
      </Card>

      {/* Search Bar */}
      <div className="mb-8">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search epics..."
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
            Showing {filteredEpics.length} of {epics.length} epics
          </p>
        )}
      </div>

      {/* Epic Cards Grid */}
      {showNoResults ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No epics match your search</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-8">
          {filteredEpics.map((epic) => (
            <DocumentCard
              key={epic.id}
              document={{
                id: epic.id,
                project_id: epic.project_id,
                file_path: epic.file_path,
                doc_type: 'epic' as const,
                title: epic.title,
                excerpt: epic.excerpt || '',
                last_modified: epic.last_modified || '',
                extraction_status: null,
                extraction_confidence: null,
              }}
              epic={epic}
            />
          ))}
        </div>
      )}
    </div>
  );
}
