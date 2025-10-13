import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { LLMProviderSelector } from '@/features/chat/LLMProviderSelector';
import { MessageInput } from '@/features/chat/MessageInput';
import { MessageList } from '@/features/chat/MessageList';
import { SourcePanel } from '@/features/chat/SourcePanel';
import { Button } from '@/components/ui/button';
import { useDefaultProvider } from '@/api/hooks/useLLMProviders';
import { useCreateConversation, useConversation } from '@/api/hooks/useConversations';
import { useSendMessage } from '@/api/hooks/useMessages';
import { MessageSquare } from 'lucide-react';
import type { SourceDocument } from '@/api/types/message';

export function Chat() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [selectedProviderId, setSelectedProviderId] = useState<string | undefined>();
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [currentSource, setCurrentSource] = useState<SourceDocument | null>(null);
  const [previousSource, setPreviousSource] = useState<SourceDocument | null>(null);

  const { data: defaultProvider } = useDefaultProvider();
  const { data: conversation, isLoading: isLoadingConversation } = useConversation(conversationId);
  const createConversation = useCreateConversation();
  const sendMessage = useSendMessage();

  // Pre-select default provider on mount
  useEffect(() => {
    if (defaultProvider && !selectedProviderId) {
      setSelectedProviderId(defaultProvider.id);
    }
  }, [defaultProvider, selectedProviderId]);

  const handleStartConversation = async () => {
    if (!projectId || !selectedProviderId) return;

    try {
      const newConversation = await createConversation.mutateAsync({
        projectId,
        data: {
          llm_provider_id: selectedProviderId,
          title: 'New Conversation',
        },
      });
      setConversationId(newConversation.id);
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!conversationId) return;

    try {
      await sendMessage.mutateAsync({
        conversationId,
        content,
      });
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleSourceClick = (source: SourceDocument) => {
    setPreviousSource(currentSource);
    setCurrentSource(source);
  };

  const handleCloseSourcePanel = () => {
    setCurrentSource(null);
    setPreviousSource(null);
  };

  const handleOpenInExplorer = (filePath: string) => {
    navigate(`/projects/${projectId}/explorer?file=${encodeURIComponent(filePath)}`);
  };

  const handleNavigateToPrevious = () => {
    if (previousSource) {
      setCurrentSource(previousSource);
      setPreviousSource(null);
    }
  };

  // New conversation state - show provider selector and start button
  if (!conversationId) {
    return (
      <div className="flex flex-col h-full">
        <div className="flex-1 flex items-center justify-center">
          <div className="max-w-md w-full space-y-6 p-6">
            <div className="text-center space-y-2">
              <MessageSquare className="h-12 w-12 mx-auto text-muted-foreground" />
              <h2 className="text-2xl font-semibold">New Conversation</h2>
              <p className="text-muted-foreground">
                Select an LLM provider and ask a question about this project...
              </p>
            </div>

            <LLMProviderSelector
              selectedProviderId={selectedProviderId}
              onProviderSelect={setSelectedProviderId}
            />

            <Button
              onClick={handleStartConversation}
              disabled={!selectedProviderId || createConversation.isPending}
              className="w-full"
            >
              {createConversation.isPending ? 'Starting...' : 'Start Conversation'}
            </Button>
          </div>
        </div>

        <MessageInput
          onSendMessage={handleSendMessage}
          disabled={true}
          isLoading={false}
        />
      </div>
    );
  }

  // Conversation started - show messages and input
  return (
    <div className="flex h-full">
      <div className={`flex flex-col ${currentSource ? 'w-full md:w-3/5' : 'w-full'} transition-all duration-300`}>
        <MessageList
          messages={conversation?.messages || []}
          isLoading={sendMessage.isPending}
          onSourceClick={handleSourceClick}
        />
        <MessageInput
          onSendMessage={handleSendMessage}
          disabled={!conversationId || isLoadingConversation}
          isLoading={sendMessage.isPending}
        />
      </div>

      {currentSource && (
        <SourcePanel
          source={currentSource}
          onClose={handleCloseSourcePanel}
          onOpenInExplorer={handleOpenInExplorer}
          previousSource={previousSource}
          onNavigateToPrevious={previousSource ? handleNavigateToPrevious : undefined}
        />
      )}
    </div>
  );
}
