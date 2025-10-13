// Project response type from backend API
export type Project = {
  id: string; // UUID
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
};

// Legacy alias for backwards compatibility
export type ProjectResponse = Project;

export type ProjectCreateRequest = {
  name: string;
  description?: string;
};

export type ProjectUpdateRequest = {
  name?: string;
  description?: string;
};
