import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { LLMProviderSelector } from '@/features/chat/LLMProviderSelector';
import { MessageInput } from '@/features/chat/MessageInput';
import { MessageList } from '@/features/chat/MessageList';
import { SourcePanel } from '@/features/chat/SourcePanel';
import { ConversationHistoryPanel } from '@/features/chat/ConversationHistoryPanel';
import { Button } from '@/components/ui/button';
import { useDefaultProvider } from '@/api/hooks/useLLMProviders';
import {
  useCreateConversation,
  useConversation,
  useConversations,
} from '@/api/hooks/useConversations';
import { useSendMessage } from '@/api/hooks/useMessages';
import { MessageSquare, Clock, Plus } from 'lucide-react';
import type { SourceDocument } from '@/api/types/message';

export function Chat() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [selectedProviderId, setSelectedProviderId] = useState<string | undefined>();
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [currentSource, setCurrentSource] = useState<SourceDocument | null>(null);
  const [previousSource, setPreviousSource] = useState<SourceDocument | null>(null);
  const [activeSidePanel, setActiveSidePanel] = useState<'none' | 'source' | 'history'>('none');

  const { data: defaultProvider } = useDefaultProvider();
  const { data: conversation, isLoading: isLoadingConversation } = useConversation(conversationId);
  const { data: conversations = [] } = useConversations(projectId || '');
  const createConversation = useCreateConversation();
  const sendMessage = useSendMessage();

  // Pre-select default provider on mount
  useEffect(() => {
    if (defaultProvider && !selectedProviderId) {
      setSelectedProviderId(defaultProvider.id);
    }
  }, [defaultProvider, selectedProviderId]);

  const handleSendMessage = async (content: string) => {
    if (!projectId || !selectedProviderId) return;

    try {
      // If no conversation exists, create one first with the message content as title
      let activeConversationId = conversationId;

      if (!activeConversationId) {
        // Use first 50 chars of message as conversation title
        let title = content.trim().slice(0, 50);
        if (content.trim().length > 50) {
          title += '...';
        }

        const newConversation = await createConversation.mutateAsync({
          projectId,
          data: {
            llm_provider_id: selectedProviderId,
            title: title,
          },
        });
        activeConversationId = newConversation.id;
        setConversationId(activeConversationId);
      }

      // Send the message
      await sendMessage.mutateAsync({
        conversationId: activeConversationId,
        content,
      });
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleSourceClick = (source: SourceDocument) => {
    setPreviousSource(currentSource);
    setCurrentSource(source);
    setActiveSidePanel('source');
  };

  const handleCloseSourcePanel = () => {
    setCurrentSource(null);
    setPreviousSource(null);
    setActiveSidePanel('none');
  };

  const handleOpenHistory = () => {
    setActiveSidePanel('history');
  };

  const handleCloseHistory = () => {
    setActiveSidePanel('none');
  };

  const handleSelectConversation = (selectedConversationId: string) => {
    setConversationId(selectedConversationId);
    setActiveSidePanel('none');
  };

  const handleNewConversation = () => {
    setConversationId(null);
    setCurrentSource(null);
    setPreviousSource(null);
    setActiveSidePanel('none');
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

  // New conversation state - show provider selector and message input
  if (!conversationId) {
    return (
      <div className="flex flex-col h-full">
        {/* Chat Header */}
        <div className="flex items-center justify-between px-4 py-2 border-b">
          <h2 className="text-lg font-semibold">New Conversation</h2>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleOpenHistory}
              aria-label="Open conversation history"
            >
              <Clock className="h-4 w-4 mr-1" />
              History
            </Button>
          </div>
        </div>

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
          </div>
        </div>

        <MessageInput
          onSendMessage={handleSendMessage}
          disabled={!selectedProviderId || createConversation.isPending}
          isLoading={createConversation.isPending || sendMessage.isPending}
        />

        {/* History Panel */}
        {projectId && (
          <ConversationHistoryPanel
            conversations={conversations}
            onSelectConversation={handleSelectConversation}
            onClose={handleCloseHistory}
            projectId={projectId}
            open={activeSidePanel === 'history'}
          />
        )}
      </div>
    );
  }

  // Conversation started - show messages and input
  const isPanelOpen = activeSidePanel !== 'none';

  return (
    <div className="flex flex-col h-full">
      {/* Chat Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b">
        <h2 className="text-lg font-semibold">{conversation?.title || 'Chat'}</h2>
        <div className="flex items-center gap-2">
          {conversationId && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleNewConversation}
              aria-label="Start new conversation"
            >
              <Plus className="h-4 w-4 mr-1" />
              New
            </Button>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={handleOpenHistory}
            aria-label="Open conversation history"
          >
            <Clock className="h-4 w-4 mr-1" />
            History
          </Button>
        </div>
      </div>

      {/* Chat Content */}
      <div className="flex flex-1 overflow-hidden">
        <div
          className={`flex flex-col ${isPanelOpen ? 'w-full md:w-3/5' : 'w-full'} transition-all duration-300`}
        >
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

        {activeSidePanel === 'source' && currentSource && (
          <SourcePanel
            source={currentSource}
            onClose={handleCloseSourcePanel}
            onOpenInExplorer={handleOpenInExplorer}
            previousSource={previousSource}
            onNavigateToPrevious={previousSource ? handleNavigateToPrevious : undefined}
          />
        )}
      </div>

      {/* History Panel */}
      {projectId && (
        <ConversationHistoryPanel
          conversations={conversations}
          onSelectConversation={handleSelectConversation}
          onClose={handleCloseHistory}
          projectId={projectId}
          open={activeSidePanel === 'history'}
        />
      )}
    </div>
  );
}
