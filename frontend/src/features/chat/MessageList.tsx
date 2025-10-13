import { useEffect, useRef } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import type { MessageResponse, SourceDocument } from '@/api/types/message';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';
import { ChatMessageRenderer } from './ChatMessageRenderer';
import { MessageSourceLinks } from './MessageSourceLinks';

interface MessageListProps {
  messages: MessageResponse[];
  isLoading: boolean;
  onSourceClick?: (source: SourceDocument) => void;
}

export function MessageList({ messages, isLoading, onSourceClick }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current && messagesEndRef.current.scrollIntoView) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  return (
    <div className="flex-1 overflow-auto p-4 space-y-4 bg-background">
      {messages.map((message) => (
        <div
          key={message.id}
          className={cn('flex', message.role === 'user' ? 'justify-end' : 'justify-start')}
        >
          <Card
            className={cn(
              'max-w-2xl',
              message.role === 'user'
                ? 'bg-primary text-primary-foreground'
                : 'bg-card text-card-foreground border'
            )}
          >
            <CardContent className="p-4">
              {message.role === 'user' ? (
                <p className="whitespace-pre-wrap">{message.content}</p>
              ) : (
                <>
                  <ChatMessageRenderer content={message.content} />
                  {message.sources && message.sources.length > 0 && onSourceClick && (
                    <MessageSourceLinks sources={message.sources} onSourceClick={onSourceClick} />
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </div>
      ))}

      {isLoading && (
        <div className="flex justify-start">
          <Card className="max-w-2xl bg-card text-card-foreground border">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
                <div className="flex gap-1">
                  <span className="text-sm text-muted-foreground animate-pulse">
                    Generating response
                  </span>
                  <span className="text-sm text-muted-foreground animate-pulse delay-75">.</span>
                  <span className="text-sm text-muted-foreground animate-pulse delay-150">.</span>
                  <span className="text-sm text-muted-foreground animate-pulse delay-300">.</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
