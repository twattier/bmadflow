import { apiClient } from '@/api/client';
import type { FileTreeResponse, FileNode, Document } from '@/api/types/document';

/**
 * Normalize a file path by resolving '.' and '..' segments
 */
function normalizePath(path: string): string {
  const segments = path.split('/').filter(Boolean);
  const normalized: string[] = [];

  for (const segment of segments) {
    if (segment === '.') {
      continue; // Current directory, skip
    } else if (segment === '..') {
      normalized.pop(); // Parent directory, go up one level
    } else {
      normalized.push(segment);
    }
  }

  return '/' + normalized.join('/');
}

/**
 * Get the directory path from a file path
 */
function getDirectoryPath(filePath: string): string {
  const segments = filePath.split('/').filter(Boolean);
  segments.pop(); // Remove the filename
  return '/' + segments.join('/');
}

/**
 * Resolve a relative path from a current file path
 */
function resolveRelativePath(currentFilePath: string, relativePath: string): string {
  // Remove any anchor fragments
  const pathWithoutAnchor = relativePath.split('#')[0];

  // If path starts with '/', it's absolute
  if (pathWithoutAnchor.startsWith('/')) {
    return normalizePath(pathWithoutAnchor);
  }

  // Get current directory
  const currentDir = getDirectoryPath(currentFilePath);

  // Join current directory with relative path
  const fullPath = `${currentDir}/${pathWithoutAnchor}`;

  return normalizePath(fullPath);
}

/**
 * Recursively search for a document by path in the file tree
 */
function findNodeByPath(nodes: FileNode[], targetPath: string): FileNode | null {
  for (const node of nodes) {
    // Normalize both paths for comparison
    const normalizedNodePath = normalizePath(node.path);
    const normalizedTargetPath = normalizePath(targetPath);

    if (normalizedNodePath === normalizedTargetPath && node.type === 'file') {
      return node;
    }

    // Recursively search children if this is a folder
    if (node.children && node.children.length > 0) {
      const found = findNodeByPath(node.children, targetPath);
      if (found) {
        return found;
      }
    }
  }

  return null;
}

/**
 * Find a document by relative path from the current file
 *
 * @param projectId - The project ID
 * @param currentFilePath - The current file's absolute path
 * @param relativePath - The relative path to resolve (e.g., './file.md', '../dir/file.md')
 * @returns The matching FileNode or null if not found
 */
export async function findDocumentByRelativePath(
  projectId: string,
  currentFilePath: string,
  relativePath: string
): Promise<FileNode | null> {
  try {
    // Fetch the file tree
    const { data } = await apiClient.get<FileTreeResponse>(`/projects/${projectId}/file-tree`);

    // Resolve the relative path to an absolute path
    const resolvedPath = resolveRelativePath(currentFilePath, relativePath);

    // Search for the document in the tree
    return findNodeByPath(data.tree, resolvedPath);
  } catch (error) {
    console.error('Error finding document by relative path:', error);
    return null;
  }
}

/**
 * Fetch document content by document ID
 *
 * @param documentId - The document ID
 * @returns The document object or null if not found
 */
export async function fetchDocumentById(documentId: string): Promise<Document | null> {
  try {
    const { data } = await apiClient.get<Document>(`/documents/${documentId}`);
    return data;
  } catch (error) {
    console.error('Error fetching document by ID:', error);
    return null;
  }
}
