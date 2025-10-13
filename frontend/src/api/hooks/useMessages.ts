import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../client';
import type { MessageCreate, SendMessageResponse } from '../types/message';

/**
 * Send a message in a conversation
 */
export function useSendMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: { conversationId: string; content: string }) => {
      const messageData: MessageCreate = { content: request.content };
      const { data } = await apiClient.post<SendMessageResponse>(
        `/conversations/${request.conversationId}/messages`,
        messageData
      );
      return data;
    },
    onSuccess: (data, variables) => {
      // Invalidate conversation to refetch messages
      queryClient.invalidateQueries({ queryKey: ['conversation', variables.conversationId] });
    },
  });
}
