import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../client';
import type { Document } from '../types/document';

export function useDocument(documentId: string | null) {
  return useQuery<Document>({
    queryKey: ['documents', documentId],
    queryFn: async () => {
      const { data } = await apiClient.get<Document>(`/documents/${documentId}`);
      return data;
    },
    enabled: !!documentId,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}
