import type { Message } from '@/types';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import { User, Sparkles } from 'lucide-react';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={cn('flex gap-4 mb-6', isUser ? 'flex-row-reverse' : 'flex-row')}>
      <Avatar className={cn('h-9 w-9 shrink-0', isUser ? 'bg-primary' : 'bg-accent')}>
        <AvatarFallback className={cn(isUser ? 'bg-primary text-primary-foreground' : 'bg-accent text-accent-foreground')}>
          {isUser ? <User className="h-4 w-4" /> : <Sparkles className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>

      <div
        className={cn(
          'max-w-[80%] rounded-2xl px-4 py-3',
          isUser
            ? 'bg-primary text-primary-foreground rounded-tr-sm'
            : 'bg-card border border-border rounded-tl-sm'
        )}
      >
        <div className="markdown-content text-[15px] leading-relaxed whitespace-pre-wrap break-words">
          {message.content}
        </div>
      </div>
    </div>
  );
}
