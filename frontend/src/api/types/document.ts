export type FileNode = {
  id: string;
  name: string;
  type: 'file' | 'folder';
  path: string;
  file_type?: string; // e.g., 'md', 'csv', 'yaml'
  size?: number;
  children?: FileNode[];
};

export type FileTreeResponse = {
  project_id: string;
  tree: FileNode[];
};

export type Document = {
  id: string;
  project_doc_id: string;
  file_path: string;
  file_type: string;
  file_size: number;
  content: string;
  doc_metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};
