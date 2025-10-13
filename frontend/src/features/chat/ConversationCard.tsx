import React from 'react';
import { formatDistanceToNow } from 'date-fns';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { ConversationResponse } from '@/api/types/conversation';

interface ConversationCardProps {
  conversation: ConversationResponse;
  onSelectConversation: (id: string) => void;
}

export const ConversationCard: React.FC<ConversationCardProps> = React.memo(
  ({ conversation, onSelectConversation }) => {
    // Truncate title to 50 characters
    const displayTitle =
      conversation.title.length > 50 ? `${conversation.title.slice(0, 50)}...` : conversation.title;

    // Format relative timestamp
    const relativeTime = formatDistanceToNow(new Date(conversation.updated_at), {
      addSuffix: true,
    });

    // Extract LLM provider info (will be present from backend join)
    const providerBadge = conversation.llm_provider
      ? `${conversation.llm_provider.provider_name} - ${conversation.llm_provider.model_name}`
      : 'Unknown Provider';

    const handleClick = () => {
      onSelectConversation(conversation.id);
    };

    return (
      <Card
        className="cursor-pointer transition-shadow hover:shadow-md"
        onClick={handleClick}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleClick();
          }
        }}
        aria-label={`Load conversation: ${displayTitle}`}
      >
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-medium">{displayTitle}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <Badge variant="secondary" className="text-xs">
                {providerBadge}
              </Badge>
              <span className="text-xs text-muted-foreground">{relativeTime}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }
);

ConversationCard.displayName = 'ConversationCard';
