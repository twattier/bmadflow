import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { FileTreeResponse } from '@/api/types/document';

export function useFileTree(projectId: string) {
  return useQuery<FileTreeResponse>({
    queryKey: ['file-tree', projectId],
    queryFn: async () => {
      const { data } = await apiClient.get<FileTreeResponse>(`/projects/${projectId}/file-tree`);
      return data;
    },
    enabled: !!projectId,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}
