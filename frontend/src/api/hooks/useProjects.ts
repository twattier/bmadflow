import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../client';

interface ProjectResponse {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export function useProject(projectId: string) {
  return useQuery<ProjectResponse>({
    queryKey: ['project', projectId],
    queryFn: async () => {
      const { data } = await apiClient.get<ProjectResponse>(`/projects/${projectId}`);
      return data;
    },
    enabled: !!projectId,
  });
}
