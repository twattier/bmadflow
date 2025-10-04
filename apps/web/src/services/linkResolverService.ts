import apiClient from './apiClient';

/**
 * Response from document link resolution endpoint
 */
export interface ResolveLinkResponse {
  id: string;
  file_path: string;
  title: string;
  doc_type: 'scoping' | 'architecture' | 'epic' | 'story' | 'qa' | 'other';
}

/**
 * Resolve a markdown document link to a document ID
 *
 * @param filePath - The file path from the markdown link (can be relative or absolute)
 * @param projectId - The project ID context
 * @returns Promise resolving to document information
 * @throws Error if document not found (404) or other API errors
 */
export async function resolveDocumentLink(
  filePath: string,
  projectId: string
): Promise<ResolveLinkResponse> {
  const response = await apiClient.get<ResolveLinkResponse>('/documents/resolve', {
    params: {
      file_path: filePath,
      project_id: projectId
    }
  });

  return response.data;
}

const linkResolverService = {
  resolveDocumentLink
};

export default linkResolverService;
