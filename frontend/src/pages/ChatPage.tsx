import { useState, useRef, useEffect, useCallback } from 'react';
import type { Message, Session } from '@/types';
import { api } from '@/services/api';
import { MessageBubble } from '@/components/MessageBubble';
import { ChatInput } from '@/components/ChatInput';
import { Sidebar } from '@/components/Sidebar';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Menu, Sparkles, MessageSquare, Clock, Calculator, HelpCircle } from 'lucide-react';

const quickActions = [
  { icon: MessageSquare, text: '介绍一下你自己', query: '你好，请介绍一下你自己' },
  { icon: Clock, text: '现在几点了？', query: '现在几点了？' },
  { icon: Calculator, text: '帮我计算', query: '帮我计算 123 * 456' },
  { icon: HelpCircle, text: '你能做什么？', query: '你能做什么？' },
];

export function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // 加载会话列表
  const loadSessions = useCallback(async () => {
    try {
      const response = await api.getSessions();
      setSessions(response.sessions);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  }, []);

  // 页面加载时获取会话列表
  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  const loadHistory = useCallback(async (sessionId: string) => {
    try {
      const history = await api.getChatHistory(sessionId);
      setMessages(history.messages);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  }, []);

  const handleSelectSession = useCallback(async (sessionId: string) => {
    setCurrentSessionId(sessionId);
    await loadHistory(sessionId);
    setSidebarOpen(false);
  }, [loadHistory]);

  const handleNewChat = useCallback(() => {
    setCurrentSessionId(null);
    setMessages([]);
    setSidebarOpen(false);
  }, []);

  const handleClearHistory = useCallback(async (sessionId: string) => {
    try {
      await api.clearChatHistory(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (currentSessionId === sessionId) {
        setCurrentSessionId(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
  }, [currentSessionId]);

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = { role: 'user', content };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const assistantMessage: Message = { role: 'assistant', content: '' };
      setMessages((prev) => [...prev, assistantMessage]);

      let fullContent = '';
      let newSessionId = currentSessionId;

      for await (const chunk of api.streamMessage({
        message: content,
        session_id: currentSessionId || undefined,
      })) {
        if (chunk.startsWith('session_id:')) {
          newSessionId = chunk.split(':')[1].trim();
          if (!currentSessionId) {
            setCurrentSessionId(newSessionId);
            setSessions((prev) => [
              { id: newSessionId!, title: content.slice(0, 30) },
              ...prev,
            ]);
          }
          continue;
        }

        fullContent += chunk;
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: 'assistant',
            content: fullContent,
          };
          return updated;
        });
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      try {
        const response = await api.sendMessage({
          message: content,
          session_id: currentSessionId || undefined,
        });

        setMessages((prev) => {
          const filtered = prev.filter(
            (m, i) => !(i === prev.length - 1 && m.role === 'assistant' && !m.content)
          );
          return [...filtered, { role: 'assistant', content: response.message }];
        });

        if (!currentSessionId) {
          setCurrentSessionId(response.session_id);
          setSessions((prev) => [
            { id: response.session_id, title: content.slice(0, 30) },
            ...prev,
          ]);
        }
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
        setMessages((prev) => [
          ...prev.slice(0, -1),
          {
            role: 'assistant',
            content: '抱歉，发送消息时出现错误。请稍后重试。',
          },
        ]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-background">
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onClearHistory={handleClearHistory}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="flex items-center gap-4 px-4 py-3 border-b border-border">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </Button>

          <div className="flex items-center gap-3">
            <Avatar className="h-9 w-9 bg-primary">
              <AvatarFallback className="bg-primary text-primary-foreground">
                <Sparkles className="h-4 w-4" />
              </AvatarFallback>
            </Avatar>
            <div>
              <h1 className="font-semibold">AI Agent</h1>
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <span className={`h-1.5 w-1.5 rounded-full ${isLoading ? 'bg-amber-500 animate-pulse' : 'bg-emerald-500'}`} />
                {isLoading ? '正在思考...' : '在线'}
              </div>
            </div>
          </div>
        </header>

        {/* Messages */}
        <ScrollArea className="flex-1">
          <div className="max-w-4xl mx-auto px-4 md:px-6 py-6">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 text-center">
                <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-primary">
                  <Sparkles className="h-10 w-10 text-primary-foreground" />
                </div>

                <h2 className="text-2xl font-bold mb-2">你好，有什么可以帮你？</h2>
                <p className="text-muted-foreground max-w-md mb-10">
                  我是您的 AI 助手，可以帮助您回答问题、进行计算、获取时间等
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-xl">
                  {quickActions.map((item) => (
                    <button
                      key={item.text}
                      onClick={() => handleSendMessage(item.query)}
                      className="group flex items-center gap-3 rounded-xl border border-border bg-card p-4 text-left transition-colors hover:bg-accent"
                    >
                      <item.icon className="h-5 w-5 text-muted-foreground group-hover:text-foreground" />
                      <span className="text-sm text-muted-foreground group-hover:text-foreground">
                        {item.text}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((message, index) => (
                  <MessageBubble key={index} message={message} />
                ))}
                {isLoading && messages[messages.length - 1]?.role === 'user' && (
                  <div className="flex gap-4 mb-6">
                    <Avatar className="h-9 w-9 shrink-0 bg-accent">
                      <AvatarFallback className="bg-accent text-accent-foreground">
                        <Sparkles className="h-4 w-4" />
                      </AvatarFallback>
                    </Avatar>
                    <div className="rounded-2xl rounded-tl-sm bg-card border border-border px-4 py-3">
                      <div className="flex gap-1.5">
                        <span className="h-2 w-2 rounded-full bg-muted-foreground typing-dot" />
                        <span className="h-2 w-2 rounded-full bg-muted-foreground typing-dot" />
                        <span className="h-2 w-2 rounded-full bg-muted-foreground typing-dot" />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>
        </ScrollArea>

        <ChatInput onSend={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}
