export type DocType = 'scoping' | 'architecture' | 'epic' | 'story' | 'qa' | 'other';

export type ExtractionStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

export interface Document {
  id: string;
  project_id: string;
  file_path: string;
  doc_type: DocType;
  title: string;
  excerpt: string;
  content?: string; // Only present in detail view
  last_modified: string;
  extraction_status: ExtractionStatus | null;
  extraction_confidence: number | null;
  created_at?: string;
  updated_at?: string;
}

export type DocumentListResponse = Omit<Document, 'content'>;

export interface DocumentDetailResponse extends Document {
  content: string;
}
