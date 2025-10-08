import { describe, it, expect, vi, beforeEach } from 'vitest';
import { findDocumentByRelativePath } from '@/api/services/documentService';
import { apiClient } from '@/api/client';
import type { FileTreeResponse } from '@/api/types/document';

// Mock the API client
vi.mock('@/api/client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

describe('documentService', () => {
  const mockProjectId = 'test-project-123';

  const mockFileTree: FileTreeResponse = {
    project_id: mockProjectId,
    tree: [
      {
        id: '1',
        name: 'root',
        type: 'folder',
        path: '/root',
        children: [
          {
            id: '2',
            name: 'docs',
            type: 'folder',
            path: '/root/docs',
            children: [
              {
                id: '3',
                name: 'readme.md',
                type: 'file',
                path: '/root/docs/readme.md',
                file_type: 'md',
                size: 1024,
              },
              {
                id: '4',
                name: 'architecture.md',
                type: 'file',
                path: '/root/docs/architecture.md',
                file_type: 'md',
                size: 2048,
              },
              {
                id: '5',
                name: 'subdir',
                type: 'folder',
                path: '/root/docs/subdir',
                children: [
                  {
                    id: '6',
                    name: 'nested.md',
                    type: 'file',
                    path: '/root/docs/subdir/nested.md',
                    file_type: 'md',
                    size: 512,
                  },
                ],
              },
            ],
          },
          {
            id: '7',
            name: 'src',
            type: 'folder',
            path: '/root/src',
            children: [
              {
                id: '8',
                name: 'index.ts',
                type: 'file',
                path: '/root/src/index.ts',
                file_type: 'ts',
                size: 256,
              },
            ],
          },
          {
            id: '9',
            name: 'another file.md',
            type: 'file',
            path: '/root/another file.md',
            file_type: 'md',
            size: 128,
          },
        ],
      },
    ],
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Default mock: return the file tree
    vi.mocked(apiClient.get).mockResolvedValue({ data: mockFileTree });
  });

  describe('findDocumentByRelativePath', () => {
    it('should find document with relative path in same directory (./file.md)', async () => {
      const currentPath = '/root/docs/readme.md';
      const relativePath = './architecture.md';

      const result = await findDocumentByRelativePath(mockProjectId, currentPath, relativePath);

      expect(result).not.toBeNull();
      expect(result?.path).toBe('/root/docs/architecture.md');
      expect(result?.name).toBe('architecture.md');
    });

    it('should find document with relative path in parent directory (../file.md)', async () => {
      const currentPath = '/root/docs/readme.md';
      const relativePath = '../another file.md';

      const result = await findDocumentByRelativePath(mockProjectId, currentPath, relativePath);

      expect(result).not.toBeNull();
      expect(result?.path).toBe('/root/another file.md');
      expect(result?.name).toBe('another file.md');
    });

    it('should find document with relative path in nested subdirectory (./subdir/file.md)', async () => {
      const currentPath = '/root/docs/readme.md';
      const relativePath = './subdir/nested.md';

      const result = await findDocumentByRelativePath(mockProjectId, currentPath, relativePath);

      expect(result).not.toBeNull();
      expect(result?.path).toBe('/root/docs/subdir/nested.md');
      expect(result?.name).toBe('nested.md');
    });

    it('should find document with absolute path (/path/to/file.md)', async () => {
      const currentPath = '/root/docs/readme.md';
      const relativePath = '/root/src/index.ts';

      const result = await findDocumentByRelativePath(mockProjectId, currentPath, relativePath);

      expect(result).not.toBeNull();
      expect(result?.path).toBe('/root/src/index.ts');
      expect(result?.name).toBe('index.ts');
    });

    it('should return null for non-existent file', async () => {
      const currentPath = '/root/docs/readme.md';
      const relativePath = './nonexistent.md';

      const result = await findDocumentByRelativePath(mockProjectId, currentPath, relativePath);

      expect(result).toBeNull();
    });

    // Edge case: Multiple parent directory segments (../../grandparent/file.md)
    it('should handle multiple parent directory segments (../../file.md)', async () => {
      const currentPath = '/root/docs/subdir/nested.md';
      const relativePath = '../../src/index.ts';

      const result = await findDocumentByRelativePath(mockProjectId, currentPath, relativePath);

      expect(result).not.toBeNull();
      expect(result?.path).toBe('/root/src/index.ts');
    });

    // Edge case: Paths with trailing slashes
    it('should handle paths with trailing slashes', async () => {
      const currentPath = '/root/docs/readme.md';
      const relativePath = './subdir/';

      const result = await findDocumentByRelativePath(mockProjectId, currentPath, relativePath);

      // Trailing slash should resolve to directory, which won't match a file
      expect(result).toBeNull();
    });

    // Edge case: URL-encoded characters in paths
    it('should handle URL-encoded characters in paths', async () => {
      const currentPath = '/root/docs/readme.md';
      const relativePath = '../another file.md'; // Space in filename

      const result = await findDocumentByRelativePath(mockProjectId, currentPath, relativePath);

      expect(result).not.toBeNull();
      expect(result?.name).toBe('another file.md');
    });

    // Edge case: Anchor fragments in relative links
    it('should handle anchor fragments in relative links (./file.md#section)', async () => {
      const currentPath = '/root/docs/readme.md';
      const relativePath = './architecture.md#overview';

      const result = await findDocumentByRelativePath(mockProjectId, currentPath, relativePath);

      expect(result).not.toBeNull();
      expect(result?.path).toBe('/root/docs/architecture.md');
      expect(result?.name).toBe('architecture.md');
    });

    it('should call API with correct project ID', async () => {
      const currentPath = '/root/docs/readme.md';
      const relativePath = './architecture.md';

      await findDocumentByRelativePath(mockProjectId, currentPath, relativePath);

      expect(apiClient.get).toHaveBeenCalledWith(`/projects/${mockProjectId}/file-tree`);
    });

    it('should return null on API error', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Network error'));

      const currentPath = '/root/docs/readme.md';
      const relativePath = './architecture.md';

      const result = await findDocumentByRelativePath(mockProjectId, currentPath, relativePath);

      expect(result).toBeNull();
    });

    it('should handle empty file tree', async () => {
      vi.mocked(apiClient.get).mockResolvedValue({
        data: { project_id: mockProjectId, tree: [] },
      });

      const currentPath = '/root/docs/readme.md';
      const relativePath = './architecture.md';

      const result = await findDocumentByRelativePath(mockProjectId, currentPath, relativePath);

      expect(result).toBeNull();
    });

    // Edge case: Relative path without ./ prefix
    it('should handle relative path without ./ prefix (subdir/file.md)', async () => {
      const currentPath = '/root/docs/readme.md';
      const relativePath = 'subdir/nested.md';

      const result = await findDocumentByRelativePath(mockProjectId, currentPath, relativePath);

      expect(result).not.toBeNull();
      expect(result?.path).toBe('/root/docs/subdir/nested.md');
    });

    // Edge case: Path normalization with redundant segments
    it('should normalize paths with redundant segments (./././file.md)', async () => {
      const currentPath = '/root/docs/readme.md';
      const relativePath = './././architecture.md';

      const result = await findDocumentByRelativePath(mockProjectId, currentPath, relativePath);

      expect(result).not.toBeNull();
      expect(result?.path).toBe('/root/docs/architecture.md');
    });
  });
});
