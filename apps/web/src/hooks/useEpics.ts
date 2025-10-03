import { useQuery } from '@tanstack/react-query';
import apiClient from '../services/apiClient';
import type { Epic } from '../types/epic';

interface UseEpicsOptions {
  projectId: string;
}

export function useEpics({ projectId }: UseEpicsOptions) {
  return useQuery({
    queryKey: ['epics', projectId],
    queryFn: async () => {
      const response = await apiClient.get<Epic[]>(`/epics?project_id=${projectId}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 10000),
    enabled: !!projectId,
  });
}
