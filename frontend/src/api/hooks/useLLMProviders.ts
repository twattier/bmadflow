import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../client';
import type { LLMProviderResponse } from '../types/llmProvider';

/**
 * Fetch all LLM providers
 */
export function useLLMProviders() {
  return useQuery<LLMProviderResponse[]>({
    queryKey: ['llm-providers'],
    queryFn: async () => {
      const { data } = await apiClient.get<LLMProviderResponse[]>('/llm-providers');
      return data;
    },
  });
}

/**
 * Get the default LLM provider
 */
export function useDefaultProvider() {
  const { data: providers, ...rest } = useLLMProviders();
  const defaultProvider = providers?.find((p) => p.is_default) || null;

  return {
    data: defaultProvider,
    ...rest,
  };
}
