import { describe, it, expect, vi, beforeEach } from 'vitest';
import linkResolverService from '@/services/linkResolverService';
import apiClient from '@/services/apiClient';

vi.mock('@/services/apiClient');

describe('linkResolverService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('resolveDocumentLink', () => {
    it('calls backend endpoint with correct parameters', async () => {
      const mockResponse = {
        data: {
          id: 'doc-123',
          file_path: 'docs/architecture.md',
          title: 'Architecture',
          doc_type: 'architecture' as const
        }
      };

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await linkResolverService.resolveDocumentLink(
        '../architecture.md',
        'project-123'
      );

      expect(apiClient.get).toHaveBeenCalledWith('/documents/resolve', {
        params: {
          file_path: '../architecture.md',
          project_id: 'project-123'
        }
      });

      expect(result).toEqual(mockResponse.data);
    });

    it('handles absolute paths', async () => {
      const mockResponse = {
        data: {
          id: 'doc-456',
          file_path: 'docs/epics/epic-1.md',
          title: 'Epic 1',
          doc_type: 'epic' as const
        }
      };

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await linkResolverService.resolveDocumentLink(
        '/docs/epics/epic-1.md',
        'project-123'
      );

      expect(apiClient.get).toHaveBeenCalledWith('/documents/resolve', {
        params: {
          file_path: '/docs/epics/epic-1.md',
          project_id: 'project-123'
        }
      });

      expect(result).toEqual(mockResponse.data);
    });

    it('handles 404 not found errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue({
        response: { status: 404, data: { error: 'Document not found' } }
      });

      await expect(
        linkResolverService.resolveDocumentLink('../missing.md', 'project-123')
      ).rejects.toMatchObject({
        response: { status: 404 }
      });
    });

    it('handles relative paths with complex navigation', async () => {
      const mockResponse = {
        data: {
          id: 'doc-789',
          file_path: 'docs/architecture/tech-stack.md',
          title: 'Tech Stack',
          doc_type: 'architecture' as const
        }
      };

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await linkResolverService.resolveDocumentLink(
        '../../architecture/tech-stack.md',
        'project-123'
      );

      expect(result).toEqual(mockResponse.data);
    });
  });
});
