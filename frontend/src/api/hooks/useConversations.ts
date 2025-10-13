import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../client';
import type {
  ConversationResponse,
  ConversationWithMessages,
  ConversationCreate,
} from '../types/conversation';

/**
 * Fetch all conversations for a project
 */
export function useConversations(projectId: string | undefined) {
  return useQuery<ConversationResponse[]>({
    queryKey: ['conversations', projectId],
    queryFn: async () => {
      if (!projectId) return [];
      const { data } = await apiClient.get<ConversationResponse[]>(
        `/projects/${projectId}/conversations`
      );
      return data;
    },
    enabled: !!projectId,
  });
}

/**
 * Fetch a single conversation with messages
 */
export function useConversation(conversationId: string | null) {
  return useQuery<ConversationWithMessages>({
    queryKey: ['conversation', conversationId],
    queryFn: async () => {
      if (!conversationId) throw new Error('No conversation ID');
      const { data } = await apiClient.get<ConversationWithMessages>(
        `/conversations/${conversationId}`
      );
      return data;
    },
    enabled: !!conversationId,
    refetchInterval: 2000, // Poll every 2s for new messages
  });
}

/**
 * Create a new conversation
 */
export function useCreateConversation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: { projectId: string; data: ConversationCreate }) => {
      const { data } = await apiClient.post<ConversationResponse>(
        `/projects/${request.projectId}/conversations`,
        request.data
      );
      return data;
    },
    onSuccess: (data) => {
      // Invalidate conversations list
      queryClient.invalidateQueries({ queryKey: ['conversations', data.project_id] });
    },
  });
}
