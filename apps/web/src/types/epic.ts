export type EpicStatus = 'draft' | 'dev' | 'done';

export interface ExtractedEpic {
  status: EpicStatus;
  story_count: number;
}

export interface Epic {
  // Document fields
  id: string;
  project_id: string;
  file_path: string;
  content: string;
  doc_type: 'epic';
  title: string;
  excerpt: string | null;
  last_modified: string | null;

  // Nested extracted_epic data
  extracted_epic: ExtractedEpic | null;
}
