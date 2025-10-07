import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../client';
import { useToast } from '@/hooks/use-toast';
import type { ProjectDocResponse } from '../types/projectDoc';

export function useProjectDocs(projectId: string) {
  return useQuery<ProjectDocResponse[]>({
    queryKey: ['project-docs', projectId],
    queryFn: async () => {
      const { data } = await apiClient.get<ProjectDocResponse[]>(
        `/projects/${projectId}/docs`
      );
      return data;
    },
    enabled: !!projectId,
  });
}

export function useSyncProjectDoc() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (projectDocId: string) => {
      const { data } = await apiClient.post(`/project-docs/${projectDocId}/sync`);
      return data;
    },
    onSuccess: () => {
      toast({
        title: 'Sync completed',
        description: 'Documentation synced successfully',
      });
      // Invalidate queries to trigger refetch
      queryClient.invalidateQueries({ queryKey: ['project-docs'] });
    },
    onError: (error: unknown) => {
      const errorMessage =
        error instanceof Error
          ? error.message
          : 'Failed to sync documentation';
      toast({
        title: 'Sync failed',
        description: errorMessage,
        variant: 'destructive',
      });
    },
  });
}
