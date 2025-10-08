import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useDocumentNavigation } from '@/api/hooks/useDocumentNavigation';
import * as documentService from '@/api/services/documentService';
import type { FileNode } from '@/api/types/document';

// Mock the document service
vi.mock('@/api/services/documentService');

describe('useDocumentNavigation', () => {
  const mockProjectId = 'test-project-123';
  const mockCurrentDocument: FileNode = {
    id: 'doc-1',
    name: 'current.md',
    type: 'file',
    path: '/docs/current.md',
    file_type: 'md',
    size: 1024,
  };
  const mockTargetDocument: FileNode = {
    id: 'doc-2',
    name: 'target.md',
    type: 'file',
    path: '/docs/target.md',
    file_type: 'md',
    size: 2048,
  };
  const mockOnDocumentSelect = vi.fn();

  // Store original window properties
  const originalLocation = window.location;
  const originalHistory = window.history;

  beforeEach(() => {
    vi.clearAllMocks();

    // Mock window.location
    delete (window as unknown as { location: unknown }).location;
    window.location = {
      ...originalLocation,
      href: 'http://localhost:3000/projects/test-project-123/explorer',
    } as Location;

    // Mock window.history
    window.history.pushState = vi.fn();

    // Mock window.open
    window.open = vi.fn();
  });

  afterEach(() => {
    // Restore original window properties
    window.location = originalLocation;
    window.history = originalHistory;
  });

  describe('isExternalLink', () => {
    it('should return true for http:// links', () => {
      const { result } = renderHook(() =>
        useDocumentNavigation({
          projectId: mockProjectId,
          currentDocument: mockCurrentDocument,
          onDocumentSelect: mockOnDocumentSelect,
        })
      );

      expect(result.current.isExternalLink('http://example.com')).toBe(true);
    });

    it('should return true for https:// links', () => {
      const { result } = renderHook(() =>
        useDocumentNavigation({
          projectId: mockProjectId,
          currentDocument: mockCurrentDocument,
          onDocumentSelect: mockOnDocumentSelect,
        })
      );

      expect(result.current.isExternalLink('https://example.com')).toBe(true);
    });

    it('should return false for relative links', () => {
      const { result } = renderHook(() =>
        useDocumentNavigation({
          projectId: mockProjectId,
          currentDocument: mockCurrentDocument,
          onDocumentSelect: mockOnDocumentSelect,
        })
      );

      expect(result.current.isExternalLink('./file.md')).toBe(false);
      expect(result.current.isExternalLink('../file.md')).toBe(false);
      expect(result.current.isExternalLink('/absolute/path')).toBe(false);
    });

    it('should return false for anchor links', () => {
      const { result } = renderHook(() =>
        useDocumentNavigation({
          projectId: mockProjectId,
          currentDocument: mockCurrentDocument,
          onDocumentSelect: mockOnDocumentSelect,
        })
      );

      expect(result.current.isExternalLink('#section')).toBe(false);
    });
  });

  describe('isRelativeLink', () => {
    it('should return false for external links', () => {
      const { result } = renderHook(() =>
        useDocumentNavigation({
          projectId: mockProjectId,
          currentDocument: mockCurrentDocument,
          onDocumentSelect: mockOnDocumentSelect,
        })
      );

      expect(result.current.isRelativeLink('http://example.com')).toBe(false);
      expect(result.current.isRelativeLink('https://example.com')).toBe(false);
    });

    it('should return false for anchor-only links', () => {
      const { result } = renderHook(() =>
        useDocumentNavigation({
          projectId: mockProjectId,
          currentDocument: mockCurrentDocument,
          onDocumentSelect: mockOnDocumentSelect,
        })
      );

      expect(result.current.isRelativeLink('#section')).toBe(false);
    });

    it('should return true for relative file paths', () => {
      const { result } = renderHook(() =>
        useDocumentNavigation({
          projectId: mockProjectId,
          currentDocument: mockCurrentDocument,
          onDocumentSelect: mockOnDocumentSelect,
        })
      );

      expect(result.current.isRelativeLink('./file.md')).toBe(true);
      expect(result.current.isRelativeLink('../file.md')).toBe(true);
      expect(result.current.isRelativeLink('/absolute/path.md')).toBe(true);
    });
  });

  describe('handleLinkClick', () => {
    it('should open external links in new tab', async () => {
      const { result } = renderHook(() =>
        useDocumentNavigation({
          projectId: mockProjectId,
          currentDocument: mockCurrentDocument,
          onDocumentSelect: mockOnDocumentSelect,
        })
      );

      await act(async () => {
        await result.current.handleLinkClick('https://example.com');
      });

      expect(window.open).toHaveBeenCalledWith('https://example.com', '_blank', 'noopener,noreferrer');
      expect(mockOnDocumentSelect).not.toHaveBeenCalled();
    });

    it('should handle anchor-only links without navigation', async () => {
      const { result } = renderHook(() =>
        useDocumentNavigation({
          projectId: mockProjectId,
          currentDocument: mockCurrentDocument,
          onDocumentSelect: mockOnDocumentSelect,
        })
      );

      await act(async () => {
        await result.current.handleLinkClick('#section');
      });

      expect(mockOnDocumentSelect).not.toHaveBeenCalled();
      expect(window.history.pushState).not.toHaveBeenCalled();
    });

    it('should navigate to target document for relative links', async () => {
      vi.mocked(documentService.findDocumentByRelativePath).mockResolvedValue(mockTargetDocument);

      const { result } = renderHook(() =>
        useDocumentNavigation({
          projectId: mockProjectId,
          currentDocument: mockCurrentDocument,
          onDocumentSelect: mockOnDocumentSelect,
        })
      );

      await act(async () => {
        await result.current.handleLinkClick('./target.md');
      });

      expect(documentService.findDocumentByRelativePath).toHaveBeenCalledWith(
        mockProjectId,
        mockCurrentDocument.path,
        './target.md'
      );
      expect(mockOnDocumentSelect).toHaveBeenCalledWith(mockTargetDocument);
    });

    it('should update browser history when navigating to document', async () => {
      vi.mocked(documentService.findDocumentByRelativePath).mockResolvedValue(mockTargetDocument);

      const { result } = renderHook(() =>
        useDocumentNavigation({
          projectId: mockProjectId,
          currentDocument: mockCurrentDocument,
          onDocumentSelect: mockOnDocumentSelect,
        })
      );

      await act(async () => {
        await result.current.handleLinkClick('./target.md');
      });

      expect(window.history.pushState).toHaveBeenCalledWith(
        {
          filePath: mockTargetDocument.path,
          fileId: mockTargetDocument.id,
        },
        '',
        expect.stringContaining('file=')
      );
    });

    it('should handle null currentDocument gracefully', async () => {
      const { result } = renderHook(() =>
        useDocumentNavigation({
          projectId: mockProjectId,
          currentDocument: null,
          onDocumentSelect: mockOnDocumentSelect,
        })
      );

      await act(async () => {
        await result.current.handleLinkClick('./target.md');
      });

      // Should not crash, but should not navigate either
      expect(documentService.findDocumentByRelativePath).not.toHaveBeenCalled();
      expect(mockOnDocumentSelect).not.toHaveBeenCalled();
    });

    it('should handle document not found scenario', async () => {
      vi.mocked(documentService.findDocumentByRelativePath).mockResolvedValue(null);

      const { result } = renderHook(() =>
        useDocumentNavigation({
          projectId: mockProjectId,
          currentDocument: mockCurrentDocument,
          onDocumentSelect: mockOnDocumentSelect,
        })
      );

      await act(async () => {
        await result.current.handleLinkClick('./nonexistent.md');
      });

      expect(documentService.findDocumentByRelativePath).toHaveBeenCalled();
      expect(mockOnDocumentSelect).not.toHaveBeenCalled();
      expect(window.history.pushState).not.toHaveBeenCalled();
    });

    it('should handle API errors gracefully', async () => {
      vi.mocked(documentService.findDocumentByRelativePath).mockRejectedValue(
        new Error('Network error')
      );

      const { result } = renderHook(() =>
        useDocumentNavigation({
          projectId: mockProjectId,
          currentDocument: mockCurrentDocument,
          onDocumentSelect: mockOnDocumentSelect,
        })
      );

      // Should not throw
      await act(async () => {
        await result.current.handleLinkClick('./target.md');
      });

      expect(mockOnDocumentSelect).not.toHaveBeenCalled();
    });

    it('should prevent default event behavior for relative links', async () => {
      vi.mocked(documentService.findDocumentByRelativePath).mockResolvedValue(mockTargetDocument);

      const mockEvent = {
        preventDefault: vi.fn(),
      } as unknown as React.MouseEvent<HTMLAnchorElement>;

      const { result } = renderHook(() =>
        useDocumentNavigation({
          projectId: mockProjectId,
          currentDocument: mockCurrentDocument,
          onDocumentSelect: mockOnDocumentSelect,
        })
      );

      await act(async () => {
        await result.current.handleLinkClick('./target.md', mockEvent);
      });

      expect(mockEvent.preventDefault).toHaveBeenCalled();
    });

    it('should prevent default event behavior for external links', async () => {
      const mockEvent = {
        preventDefault: vi.fn(),
      } as unknown as React.MouseEvent<HTMLAnchorElement>;

      const { result } = renderHook(() =>
        useDocumentNavigation({
          projectId: mockProjectId,
          currentDocument: mockCurrentDocument,
          onDocumentSelect: mockOnDocumentSelect,
        })
      );

      await act(async () => {
        await result.current.handleLinkClick('https://example.com', mockEvent);
      });

      expect(mockEvent.preventDefault).toHaveBeenCalled();
    });
  });
});
