import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Sheet, SheetContent } from '@/components/ui/sheet';
import { cn } from '@/lib/utils';
import { Plus, MessageSquare, Trash2, LogOut } from 'lucide-react';

interface Session {
  id: string;
  title: string | null;
}

interface SidebarProps {
  sessions: Session[];
  currentSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onNewChat: () => void;
  onClearHistory: (sessionId: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

function SidebarContent({
  sessions,
  currentSessionId,
  onSelectSession,
  onNewChat,
  onClearHistory,
}: Omit<SidebarProps, 'isOpen' | 'onClose'>) {
  const { user, logout } = useAuth();

  return (
    <div className="flex h-full flex-col bg-sidebar">
      {/* Header */}
      <div className="p-4">
        <Button onClick={onNewChat} className="w-full justify-center gap-2">
          <Plus className="h-4 w-4" />
          新对话
        </Button>
      </div>

      {/* Sessions list */}
      <ScrollArea className="flex-1 px-3">
        <div className="mb-2 px-2 text-xs font-medium text-muted-foreground uppercase tracking-wider">
          历史对话
        </div>
        <div className="space-y-1 pb-4">
          {sessions.length === 0 ? (
            <div className="py-8 text-center">
              <MessageSquare className="mx-auto h-8 w-8 text-muted-foreground/50 mb-2" />
              <p className="text-sm text-muted-foreground">暂无对话历史</p>
            </div>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={cn(
                  'group flex items-center gap-3 rounded-lg px-3 py-2.5 cursor-pointer transition-colors',
                  currentSessionId === session.id
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground'
                )}
                onClick={() => onSelectSession(session.id)}
              >
                <MessageSquare className="h-4 w-4 shrink-0" />
                <span className="flex-1 truncate text-sm">
                  {session.title || '新对话'}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onClearHistory(session.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 rounded transition-all"
                >
                  <Trash2 className="h-3.5 w-3.5 text-muted-foreground hover:text-destructive" />
                </button>
              </div>
            ))
          )}
        </div>
      </ScrollArea>

      {/* User section */}
      <Separator />
      <div className="p-4">
        <div className="flex items-center gap-3">
          <Avatar className="h-9 w-9">
            <AvatarFallback className="bg-primary text-primary-foreground text-sm">
              {user?.email?.charAt(0).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.email}</p>
            <p className="text-xs text-muted-foreground">
              {user?.is_active ? '已激活' : '未激活'}
            </p>
          </div>
          <Button variant="ghost" size="icon" onClick={logout} className="h-8 w-8">
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}

export function Sidebar(props: SidebarProps) {
  const { isOpen, onClose, ...contentProps } = props;

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex w-72 shrink-0 border-r border-sidebar-border">
        <SidebarContent {...contentProps} />
      </aside>

      {/* Mobile sidebar */}
      <Sheet open={isOpen} onOpenChange={onClose}>
        <SheetContent side="left" className="w-72 p-0">
          <SidebarContent {...contentProps} />
        </SheetContent>
      </Sheet>
    </>
  );
}
