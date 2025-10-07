import { useState, useEffect, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { SyncStatusBadge } from '@/components/common/SyncStatusBadge';
import { useSyncProjectDoc } from '@/api/hooks/useProjectDocs';
import { useToast } from '@/hooks/use-toast';
import { useQueryClient } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';
import type { ProjectDocResponse } from '@/api/types/projectDoc';

interface ProjectDocCardProps {
  projectDoc: ProjectDocResponse;
}

export function ProjectDocCard({ projectDoc }: ProjectDocCardProps) {
  const syncMutation = useSyncProjectDoc();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [isSyncing, setIsSyncing] = useState(false);
  const syncStartTimeRef = useRef<string | null>(null);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Clean up polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  // Check if sync is in progress based on last_synced_at change
  const isSyncInProgress = () => {
    if (!isSyncing && !syncStartTimeRef.current) return false;

    // If we have a sync start time, check if last_synced_at has updated
    if (syncStartTimeRef.current && projectDoc.last_synced_at) {
      const syncStarted = new Date(syncStartTimeRef.current);
      const lastSynced = new Date(projectDoc.last_synced_at);

      // If last_synced_at is after our sync start time, sync is complete
      if (lastSynced > syncStarted) {
        syncStartTimeRef.current = null;
        setIsSyncing(false);
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        return false;
      }

      // Check timeout (5 minutes max)
      const now = new Date();
      const diffMinutes = (now.getTime() - syncStarted.getTime()) / 60000;
      if (diffMinutes >= 5) {
        syncStartTimeRef.current = null;
        setIsSyncing(false);
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        return false;
      }
    }

    return true;
  };

  const handleSync = async () => {
    if (isSyncInProgress()) {
      toast({
        title: 'Sync already in progress',
        description: 'Please wait for the current sync to complete.',
        variant: 'destructive',
      });
      return;
    }

    setIsSyncing(true);
    syncStartTimeRef.current = new Date().toISOString();

    try {
      await syncMutation.mutateAsync(projectDoc.id);

      // Start polling for sync completion every 2 seconds
      pollIntervalRef.current = setInterval(() => {
        queryClient.invalidateQueries({ queryKey: ['project-docs'] });
      }, 2000);
    } catch {
      setIsSyncing(false);
      syncStartTimeRef.current = null;
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
          disabled={isSyncInProgress()}
          data-testid="sync-button"
          className="w-full"
        >
          {isSyncInProgress() ? (
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
