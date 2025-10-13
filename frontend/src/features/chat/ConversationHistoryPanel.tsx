import React from 'react';
import { X, Inbox } from 'lucide-react';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { ConversationCard } from './ConversationCard';
import type { ConversationResponse } from '@/api/types/conversation';

interface ConversationHistoryPanelProps {
  conversations: ConversationResponse[];
  onSelectConversation: (id: string) => void;
  onClose: () => void;
  projectId: string;
  open: boolean;
}

export const ConversationHistoryPanel: React.FC<ConversationHistoryPanelProps> = ({
  conversations,
  onSelectConversation,
  onClose,
  open,
}) => {
  return (
    <Sheet open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <SheetContent side="right" className="w-2/5 flex flex-col">
        <SheetHeader className="border-b pb-4">
          <div className="flex items-center justify-between">
            <SheetTitle>Conversation History</SheetTitle>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              aria-label="Close conversation history"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
          <SheetDescription className="sr-only">
            View and select from your recent conversations
          </SheetDescription>
        </SheetHeader>

        <div className="flex-1 overflow-auto py-4">
          {conversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
              <Inbox className="h-12 w-12 mb-4 opacity-50" />
              <p className="text-lg font-medium">No conversation history yet</p>
              <p className="text-sm mt-2">Start a new conversation to get started.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {conversations.map((conversation) => (
                <ConversationCard
                  key={conversation.id}
                  conversation={conversation}
                  onSelectConversation={onSelectConversation}
                />
              ))}
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
};
