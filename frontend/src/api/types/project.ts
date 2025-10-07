// Project response type from backend API
export interface ProjectResponse {
  id: string; // UUID
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}
