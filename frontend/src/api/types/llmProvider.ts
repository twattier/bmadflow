export type LLMProviderResponse = {
  id: string;
  provider_name: string;
  model_name: string;
  is_default: boolean;
  api_config: Record<string, unknown>;
  created_at: string;
};
