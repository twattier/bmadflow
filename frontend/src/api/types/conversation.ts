import type { MessageResponse } from './message';

export type ConversationCreate = {
  llm_provider_id: string;
  title?: string;
};

export type ConversationResponse = {
  id: string;
  project_id: string;
  llm_provider_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  llm_provider?: {
    id: string;
    provider_name: string;
    model_name: string;
  };
};

export type ConversationWithMessages = ConversationResponse & {
  messages: MessageResponse[];
};
