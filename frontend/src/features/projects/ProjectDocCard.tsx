import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { SyncStatusBadge } from '@/components/common/SyncStatusBadge';
import { useSyncProjectDoc } from '@/api/hooks/useProjectDocs';
import { Loader2 } from 'lucide-react';
import type { ProjectDocResponse } from '@/api/types/projectDoc';

interface ProjectDocCardProps {
  projectDoc: ProjectDocResponse;
}

export function ProjectDocCard({ projectDoc }: ProjectDocCardProps) {
  const syncMutation = useSyncProjectDoc();
  const [isSyncing, setIsSyncing] = useState(false);

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      await syncMutation.mutateAsync(projectDoc.id);
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <Card data-testid="project-doc-card">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>{projectDoc.name}</CardTitle>
            <CardDescription>
              <a
                href={projectDoc.github_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                {projectDoc.github_url}
              </a>
            </CardDescription>
          </div>
          <SyncStatusBadge projectDoc={projectDoc} />
        </div>
      </CardHeader>
      <CardContent>
        {projectDoc.description && (
          <p className="text-sm text-muted-foreground mb-4">{projectDoc.description}</p>
        )}
        <Button
          onClick={handleSync}
          disabled={isSyncing}
          data-testid="sync-button"
          className="w-full"
        >
          {isSyncing ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" data-testid="sync-spinner" />
              Syncing...
            </>
          ) : (
            'Sync'
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
