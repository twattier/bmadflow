export type ProjectDocResponse = {
  id: string; // UUID
  project_id: string;
  name: string;
  description: string | null;
  github_url: string;
  github_folder_path: string | null;
  last_synced_at: string | null; // ISO datetime string
  last_github_commit_date: string | null;
  created_at: string;
  updated_at: string;
};

export type SyncStatusResponse = {
  status: 'idle' | 'syncing' | 'completed' | 'failed';
  message: string;
  last_synced_at: string | null;
  last_github_commit_date: string | null;
};

export type ProjectDocCreateRequest = {
  name: string;
  description?: string;
  github_url: string;
  github_folder_path?: string;
};
