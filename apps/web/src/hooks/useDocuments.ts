import { useQuery } from '@tanstack/react-query';
import apiClient from '../services/apiClient';
import type { Document, DocType } from '../types/document';

interface UseDocumentsOptions {
  projectId: string;
  docType?: DocType;
}

export function useDocuments({ projectId, docType }: UseDocumentsOptions) {
  return useQuery({
    queryKey: ['documents', projectId, docType],
    queryFn: async () => {
      const params = docType ? `?type=${docType}` : '';
      const response = await apiClient.get<Document[]>(
        `/projects/${projectId}/documents${params}`
      );
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 10000),
    enabled: !!projectId, // Only fetch if projectId is available
  });
}
