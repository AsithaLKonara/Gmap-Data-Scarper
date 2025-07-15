import React, { useEffect, useState, useRef } from 'react';
import { Bell, CheckCircle, XCircle } from 'lucide-react';
import { Badge } from './badge';
import { Button } from './button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './dialog';
import { useToast } from '@/hooks/use-toast';
import { useQuery, useMutation, gql } from '@apollo/client';
import { useTranslation } from 'react-i18next';

interface Notification {
  id: string;
  title: string;
  description?: string;
  read: boolean;
  createdAt: string;
  type?: 'info' | 'success' | 'error';
}

const NOTIFICATIONS_QUERY = gql`
  query Notifications {
    notifications {
      id
      type
      message
      read
      created_at
    }
  }
`;

const MARK_READ_MUTATION = gql`
  mutation MarkNotificationRead($notificationId: Int!) {
    markNotificationRead(notificationId: $notificationId) {
      notification {
        id
        read
      }
    }
  }
`;

export const NotificationCenter: React.FC = () => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const { toast } = useToast();
  const wsRef = useRef<WebSocket | null>(null);
  const { data, refetch } = useQuery(NOTIFICATIONS_QUERY, { fetchPolicy: 'network-only' });
  const [markRead] = useMutation(MARK_READ_MUTATION);

  // Fetch notifications from GraphQL
  useEffect(() => {
    if (data && data.notifications) {
      setNotifications(
        data.notifications.map((n: any) => ({
          id: n.id,
          title: n.type === 'success' ? 'Success' : n.type === 'error' ? 'Error' : 'Notification',
          description: n.message,
          read: n.read,
          createdAt: n.created_at,
          type: n.type || 'info',
        }))
      );
    }
  }, [data]);

  // WebSocket for real-time notifications
  useEffect(() => {
    const jwt = localStorage.getItem('token');
    if (!jwt) return;
    const wsUrl = `${process.env.REACT_APP_API_URL?.replace(/^http/, 'ws')}/ws/notifications?token=${jwt}`;
    const ws = new window.WebSocket(wsUrl);
    wsRef.current = ws;
    ws.onmessage = (event) => {
      const n = JSON.parse(event.data);
      setNotifications((prev) => [
        {
          id: n.id,
          title: n.type === 'success' ? 'Success' : n.type === 'error' ? 'Error' : 'Notification',
          description: n.message,
          read: n.read,
          createdAt: n.created_at,
          type: n.type || 'info',
        },
        ...prev,
      ]);
      refetch();
    };
    ws.onclose = () => { wsRef.current = null; };
    return () => { ws.close(); };
  }, [refetch]);

  // Mark notification as read
  const markAsRead = async (id: string) => {
    await markRead({ variables: { notificationId: parseInt(id) } });
    setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, read: true } : n));
    refetch();
  };

  // Mark all as read
  const markAllAsRead = async () => {
    await Promise.all(
      notifications.filter((n) => !n.read).map((n) => markRead({ variables: { notificationId: parseInt(n.id) } }))
    );
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    refetch();
  };

  // Show toast for new notifications
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
      <Button variant="ghost" size="icon" onClick={() => setOpen(true)} aria-label={t('Open notifications')}>
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <Badge variant="destructive" className="absolute -top-1 -right-1">{unreadCount}</Badge>
        )}
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{t('Notifications')}</DialogTitle>
            {unreadCount > 0 && (
              <Button variant="outline" size="sm" onClick={markAllAsRead} className="ml-auto">{t('Mark all as read')}</Button>
            )}
          </DialogHeader>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {notifications.length === 0 && <div className="text-muted-foreground text-center py-8">{t('No notifications')}</div>}
            {notifications.map((n) => (
              <div key={n.id} className={`flex items-start gap-3 p-3 rounded-md border ${n.read ? 'bg-muted' : 'bg-background'}`}>
                {n.type === 'success' && <CheckCircle className="text-green-500 h-5 w-5 mt-1" />}
                {n.type === 'error' && <XCircle className="text-red-500 h-5 w-5 mt-1" />}
                {(!n.type || n.type === 'info') && <Bell className="text-blue-500 h-5 w-5 mt-1" />}
                <div className="flex-1">
                  <div className="font-medium">{t(n.title)}</div>
                  {n.description && <div className="text-sm text-muted-foreground">{n.description}</div>}
                  <div className="text-xs text-muted-foreground mt-1">{new Date(n.createdAt).toLocaleString()}</div>
                </div>
                {!n.read && (
                  <Button variant="ghost" size="sm" onClick={() => markAsRead(n.id)}>{t('Mark as read')}</Button>
                )}
              </div>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}; 