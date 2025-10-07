import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../client';
import { useToast } from '@/hooks/use-toast';
import type { ProjectDocResponse, ProjectDocCreateRequest } from '../types/projectDoc';

export function useProjectDocs(projectId: string) {
  return useQuery<ProjectDocResponse[]>({
    queryKey: ['project-docs', projectId],
    queryFn: async () => {
      const { data } = await apiClient.get<ProjectDocResponse[]>(`/projects/${projectId}/docs`);
      return data;
    },
    enabled: !!projectId,
  });
}

export function useCreateProjectDoc(projectId: string) {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (request: ProjectDocCreateRequest) => {
      const { data } = await apiClient.post<ProjectDocResponse>(
        `/projects/${projectId}/docs`,
        request
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project-docs', projectId] });
      toast({
        title: 'ProjectDoc created',
        description: 'Documentation source added successfully',
      });
    },
    onError: (error: unknown) => {
      let errorMessage = 'Failed to create ProjectDoc';
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { detail?: string; message?: string } } };
        errorMessage =
          axiosError.response?.data?.detail || axiosError.response?.data?.message || errorMessage;
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      toast({
        title: 'Creation failed',
        description: errorMessage,
        variant: 'destructive',
      });
    },
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
        title: 'Sync started',
        description:
          'Documentation is being synced in the background. This may take a few moments.',
      });
      // Invalidate queries to trigger refetch - this will update the sync status
      queryClient.invalidateQueries({ queryKey: ['project-docs'] });

      // Schedule a refetch after 3 seconds to show updated sync time
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['project-docs'] });
      }, 3000);
    },
    onError: (error: unknown) => {
      let errorMessage = 'Failed to sync documentation';
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { detail?: string; message?: string } } };
        errorMessage =
          axiosError.response?.data?.detail || axiosError.response?.data?.message || errorMessage;
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      toast({
        title: 'Sync failed',
        description: errorMessage,
        variant: 'destructive',
      });
    },
  });
}
