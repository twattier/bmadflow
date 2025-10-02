export interface Project {
  id: string;
  name: string;
  github_url: string;
  last_sync_timestamp: string | null;
  sync_status: 'idle' | 'syncing' | 'error';
  sync_progress: { processed: number; total: number; current_file?: string } | null;
  created_at: string;
  updated_at: string;
}

export interface SyncStatusResponse {
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  processed_count: number;
  total_count: number;
  error_message: string | null;
  retry_allowed: boolean;
}

export interface SyncTriggerResponse {
  sync_task_id: string;
  message: string;
}
