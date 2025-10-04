import { useQuery } from '@tanstack/react-query';
import { resolveDocumentLink, type ResolveLinkResponse } from '../services/linkResolverService';

/**
 * Hook to resolve a markdown document link to a document ID
 *
 * Uses React Query to cache resolution results for 5 minutes
 *
 * @param filePath - The file path from the markdown link
 * @param projectId - The project ID context
 * @returns React Query result with document information or error
 */
export function useDocumentLink(filePath: string, projectId: string) {
  return useQuery<ResolveLinkResponse>({
    queryKey: ['document-link', projectId, filePath],
    queryFn: () => resolveDocumentLink(filePath, projectId),
    staleTime: 5 * 60 * 1000,        // 5 minutes
    retry: 1,                         // Only retry once for 404s
    enabled: !!filePath && !!projectId,
    // Don't throw errors - let component handle 404 state
    throwOnError: false,
  });
}
