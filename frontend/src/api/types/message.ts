export type MessageResponse = {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  sources: Array<{
    document_id: string;
    file_path: string;
    header_anchor: string | null;
    similarity_score: number;
  }> | null;
  created_at: string;
};

export type MessageCreate = {
  content: string;
};

export type SendMessageResponse = {
  user_message: MessageResponse;
  assistant_message: MessageResponse;
};
