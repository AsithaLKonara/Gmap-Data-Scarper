import React, { useEffect, useState } from 'react';
import { Bell, CheckCircle, XCircle } from 'lucide-react';
import { Badge } from './badge';
import { Button } from './button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './dialog';
import { useToast } from '@/hooks/use-toast';

interface Notification {
  id: string;
  title: string;
  description?: string;
  read: boolean;
  createdAt: string;
  type?: 'info' | 'success' | 'error';
}

export const NotificationCenter: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const { toast } = useToast();

  // Simulate fetching notifications (replace with real API call)
  useEffect(() => {
    // TODO: Replace with real API call and WebSocket for real-time
    setNotifications([
      { id: '1', title: 'Welcome!', description: 'Thanks for joining.', read: false, createdAt: new Date().toISOString(), type: 'success' },
      { id: '2', title: 'New Lead Added', description: 'A new lead was added to your CRM.', read: false, createdAt: new Date().toISOString(), type: 'info' },
      { id: '3', title: 'Upgrade Required', description: 'Upgrade your plan to access more features.', read: true, createdAt: new Date().toISOString(), type: 'error' },
    ]);
  }, []);

  // Mark notification as read
  const markAsRead = (id: string) => {
    setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, read: true } : n));
  };

  // Mark all as read
  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  // Show toast for new notifications (simulate real-time)
  useEffect(() => {
    const unread = notifications.filter(n => !n.read);
    if (unread.length > 0) {
      const latest = unread[0];
      toast({
        title: latest.title,
        description: latest.description,
      });
    }
  }, [notifications, toast]);

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="relative">
      <Button variant="ghost" size="icon" onClick={() => setOpen(true)} aria-label="Open notifications">
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <Badge variant="destructive" className="absolute -top-1 -right-1">{unreadCount}</Badge>
        )}
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Notifications</DialogTitle>
            {unreadCount > 0 && (
              <Button variant="outline" size="sm" onClick={markAllAsRead} className="ml-auto">Mark all as read</Button>
            )}
          </DialogHeader>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {notifications.length === 0 && <div className="text-muted-foreground text-center py-8">No notifications</div>}
            {notifications.map((n) => (
              <div key={n.id} className={`flex items-start gap-3 p-3 rounded-md border ${n.read ? 'bg-muted' : 'bg-background'}`}>
                {n.type === 'success' && <CheckCircle className="text-green-500 h-5 w-5 mt-1" />}
                {n.type === 'error' && <XCircle className="text-red-500 h-5 w-5 mt-1" />}
                {(!n.type || n.type === 'info') && <Bell className="text-blue-500 h-5 w-5 mt-1" />}
                <div className="flex-1">
                  <div className="font-medium">{n.title}</div>
                  {n.description && <div className="text-sm text-muted-foreground">{n.description}</div>}
                  <div className="text-xs text-muted-foreground mt-1">{new Date(n.createdAt).toLocaleString()}</div>
                </div>
                {!n.read && (
                  <Button variant="ghost" size="sm" onClick={() => markAsRead(n.id)}>Mark as read</Button>
                )}
              </div>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}; 