import { Tree } from 'react-arborist';
import { ChevronRight, ChevronDown, FileText, Table, FileCode, Folder } from 'lucide-react';
import { useFileTree } from '@/api/hooks/useFileTree';
import type { FileNode } from '@/api/types/document';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { cn } from '@/lib/utils';

interface FileTreePanelProps {
  projectId: string;
  onSelectFile: (file: FileNode) => void;
  className?: string;
}

export function FileTreePanel({ projectId, onSelectFile, className }: FileTreePanelProps) {
  const { data, isLoading, error } = useFileTree(projectId);

  if (isLoading) {
    return (
      <div className={className}>
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className={cn('p-4', className)}>
        <p className="text-destructive text-sm">Failed to load file tree</p>
      </div>
    );
  }

  if (!data?.tree || data.tree.length === 0) {
    return (
      <div className={cn('p-4', className)}>
        <p className="text-muted-foreground text-sm">
          No documents synced. Go to Overview and sync a ProjectDoc to get started.
        </p>
      </div>
    );
  }

  const getFileIcon = (node: FileNode) => {
    if (node.type === 'folder') {
      return <Folder className="h-4 w-4 text-muted-foreground" />;
    }

    const fileType = node.file_type?.toLowerCase();
    if (fileType === 'md') {
      return <FileText className="h-4 w-4 text-blue-500" />;
    }
    if (fileType === 'csv') {
      return <Table className="h-4 w-4 text-green-500" />;
    }
    if (fileType === 'yaml' || fileType === 'json') {
      return <FileCode className="h-4 w-4 text-orange-500" />;
    }
    return <FileText className="h-4 w-4 text-muted-foreground" />;
  };

  const handleNodeClick = (node: { data: FileNode; toggle: () => void }) => {
    if (node.data.type === 'folder') {
      node.toggle();
    } else {
      onSelectFile(node.data);
    }
  };

  return (
    <div className={cn('overflow-auto', className)} data-testid="file-tree">
      <Tree
        data={data.tree}
        idAccessor={(node) => node.id || node.path}
        initialOpenState={{ 0: true }}
        width="100%"
        height={800}
        indent={24}
        rowHeight={32}
      >
        {({ node, style, dragHandle }) => (
          <div
            style={style}
            className={cn(
              'flex items-center gap-2 px-2 hover:bg-accent cursor-pointer',
              node.isSelected && 'bg-accent'
            )}
            onClick={() => handleNodeClick(node)}
            {...dragHandle}
          >
            <div className="flex items-center">
              {node.data.type === 'folder' ? (
                node.isOpen ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )
              ) : (
                <span className="w-4" />
              )}
            </div>
            {getFileIcon(node.data)}
            <span className="text-sm truncate">{node.data.name}</span>
          </div>
        )}
      </Tree>
    </div>
  );
}
