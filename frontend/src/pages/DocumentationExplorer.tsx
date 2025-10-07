import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { FileTreePanel } from '@/features/explorer/FileTreePanel';
import { ContentViewer } from '@/features/explorer/ContentViewer';
import type { FileNode } from '@/api/types/document';

export function DocumentationExplorer() {
  const { projectId } = useParams<{ projectId: string }>();
  const [selectedFile, setSelectedFile] = useState<FileNode | null>(null);

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
        onSelectFile={setSelectedFile}
        className="w-1/4 border rounded-lg"
      />
      <ContentViewer file={selectedFile} className="flex-1" />
    </div>
  );
}
