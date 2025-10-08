import { useState, useEffect, useCallback } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { FileTreePanel } from '@/features/explorer/FileTreePanel';
import { ContentViewer } from '@/features/explorer/ContentViewer';
import type { FileNode } from '@/api/types/document';
import { useFileTree } from '@/api/hooks/useFileTree';

/**
 * Recursively find a file node by path in the tree
 */
function findFileByPath(nodes: FileNode[], path: string): FileNode | null {
  for (const node of nodes) {
    if (node.path === path && node.type === 'file') {
      return node;
    }
    if (node.children) {
      const found = findFileByPath(node.children, path);
      if (found) return found;
    }
  }
  return null;
}

export function DocumentationExplorer() {
  const { projectId } = useParams<{ projectId: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedFile, setSelectedFile] = useState<FileNode | null>(null);

  // Fetch file tree to enable URL-based file selection
  const { data: fileTreeData } = useFileTree(projectId || '');

  // Handle document selection with URL update
  const handleDocumentSelect = useCallback(
    (document: FileNode) => {
      setSelectedFile(document);

      // Update URL search params to reflect selected file
      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.set('file', document.path);
      setSearchParams(newSearchParams, { replace: false });
    },
    [searchParams, setSearchParams]
  );

  // Initialize selected file from URL on mount and when file tree loads
  useEffect(() => {
    const filePath = searchParams.get('file');
    if (filePath && fileTreeData?.tree && !selectedFile) {
      const file = findFileByPath(fileTreeData.tree, filePath);
      if (file) {
        setSelectedFile(file);
      }
    }
  }, [searchParams, fileTreeData, selectedFile]);

  // Handle browser back/forward button
  useEffect(() => {
    const handlePopState = () => {
      const params = new URLSearchParams(window.location.search);
      const filePath = params.get('file');

      if (filePath && fileTreeData?.tree) {
        const file = findFileByPath(fileTreeData.tree, filePath);
        if (file) {
          setSelectedFile(file);
        }
      } else {
        setSelectedFile(null);
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [fileTreeData]);

  if (!projectId) {
    return (
      <div className="p-4">
        <p className="text-destructive">Project ID is required</p>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] gap-4 p-4">
      <FileTreePanel
        projectId={projectId}
        selectedFile={selectedFile}
        onSelectFile={handleDocumentSelect}
        className="w-1/4 border rounded-lg"
      />
      <ContentViewer
        file={selectedFile}
        className="flex-1"
        projectId={projectId}
        onDocumentSelect={handleDocumentSelect}
      />
    </div>
  );
}
