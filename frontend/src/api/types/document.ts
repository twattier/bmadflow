export interface FileNode {
  id: string;
  name: string;
  type: 'file' | 'folder';
  path: string;
  file_type?: string; // e.g., 'md', 'csv', 'yaml'
  size?: number;
  children?: FileNode[];
}

export interface FileTreeResponse {
  project_id: string;
  tree: FileNode[];
}
