import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Send, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="border-t border-border bg-background p-4 md:p-6">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
        <div className="flex items-end gap-3 rounded-2xl border border-input bg-card p-3 focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2 focus-within:ring-offset-background transition-shadow">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入消息..."
            disabled={disabled}
            rows={1}
            className="flex-1 resize-none bg-transparent text-foreground placeholder:text-muted-foreground focus:outline-none text-[15px] leading-relaxed disabled:opacity-50 py-1.5 px-1"
          />
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground hidden sm:block">
              Shift + Enter 换行
            </span>
            <Button
              type="submit"
              size="icon"
              disabled={disabled || !message.trim()}
              className="h-10 w-10 shrink-0"
            >
              {disabled ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}
