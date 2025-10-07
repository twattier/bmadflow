// Project response type from backend API
export interface Project {
  id: string; // UUID
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

// Legacy alias for backwards compatibility
export type ProjectResponse = Project;

export interface ProjectCreateRequest {
  name: string;
  description?: string;
}

export interface ProjectUpdateRequest {
  name?: string;
  description?: string;
}
