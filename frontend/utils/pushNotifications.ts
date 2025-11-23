/**
 * Push notification utilities for Web Push API.
 */

export interface PushSubscriptionData {
  endpoint: string;
  keys: {
    p256dh: string;
    auth: string;
  };
}

export interface NotificationPreferences {
  task_completion: boolean;
  task_errors: boolean;
  task_paused: boolean;
  task_resumed: boolean;
}

/**
 * Subscribe to push notifications.
 */
export async function subscribeToPushNotifications(
  deviceInfo?: Record<string, any>
): Promise<PushSubscriptionData | null> {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    console.warn('Push notifications are not supported in this browser');
    return null;
  }

  try {
    // Register service worker
    const registration = await navigator.serviceWorker.ready;

    // Request notification permission
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') {
      console.warn('Notification permission denied');
      return null;
    }

    // Get push subscription
    let subscription = await registration.pushManager.getSubscription();

    // If no subscription, create one
    if (!subscription) {
      // Get VAPID public key from backend (or use environment variable)
      const vapidPublicKey = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY || '';

      if (!vapidPublicKey) {
        console.warn('VAPID public key not configured');
        return null;
      }

      // Create subscription
      const key = urlBase64ToUint8Array(vapidPublicKey);
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: key.buffer as ArrayBuffer,
      });
    }

    // Convert subscription to JSON
    const subscriptionData: PushSubscriptionData = {
      endpoint: subscription.endpoint,
      keys: {
        p256dh: btoa(
          String.fromCharCode(...Array.from(new Uint8Array(subscription.getKey('p256dh')!)))
        ),
        auth: btoa(
          String.fromCharCode(...Array.from(new Uint8Array(subscription.getKey('auth')!)))
        ),
      },
    };

    // Send subscription to backend
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/notifications/subscribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        subscription: subscriptionData,
        device_info: deviceInfo || {
          userAgent: navigator.userAgent,
          platform: navigator.platform,
          language: navigator.language,
        },
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to subscribe to push notifications');
    }

    const result = await response.json();
    console.log('Subscribed to push notifications:', result);

    return subscriptionData;
  } catch (error) {
    console.error('Error subscribing to push notifications:', error);
    return null;
  }
}

/**
 * Unsubscribe from push notifications.
 */
export async function unsubscribeFromPushNotifications(
  endpoint: string
): Promise<boolean> {
  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();

    if (subscription && subscription.endpoint === endpoint) {
      await subscription.unsubscribe();
    }

    // Notify backend
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/notifications/unsubscribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ endpoint }),
    });

    if (!response.ok) {
      throw new Error('Failed to unsubscribe from push notifications');
    }

    console.log('Unsubscribed from push notifications');
    return true;
  } catch (error) {
    console.error('Error unsubscribing from push notifications:', error);
    return false;
  }
}

/**
 * Update notification preferences.
 */
export async function updateNotificationPreferences(
  endpoint: string,
  preferences: NotificationPreferences
): Promise<boolean> {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/notifications/preferences`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ endpoint, preferences }),
    });

    if (!response.ok) {
      throw new Error('Failed to update notification preferences');
    }

    console.log('Notification preferences updated');
    return true;
  } catch (error) {
    console.error('Error updating notification preferences:', error);
    return false;
  }
}

/**
 * Get notification preferences.
 */
export async function getNotificationPreferences(): Promise<NotificationPreferences | null> {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/notifications/subscriptions`);

    if (!response.ok) {
      throw new Error('Failed to get notification preferences');
    }

    const result = await response.json();
    if (result.subscriptions && result.subscriptions.length > 0) {
      return result.subscriptions[0].notification_preferences || {
        task_completion: true,
        task_errors: true,
        task_paused: false,
        task_resumed: false,
      };
    }

    return null;
  } catch (error) {
    console.error('Error getting notification preferences:', error);
    return null;
  }
}

/**
 * Check if push notifications are supported.
 */
export function isPushNotificationSupported(): boolean {
  return (
    'serviceWorker' in navigator &&
    'PushManager' in window &&
    'Notification' in window
  );
}

/**
 * Check if notification permission is granted.
 */
export async function isNotificationPermissionGranted(): Promise<boolean> {
  if (!('Notification' in window)) {
    return false;
  }

  const permission = await Notification.requestPermission();
  return permission === 'granted';
}

/**
 * Convert VAPID public key from URL-safe base64 to Uint8Array.
 */
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }

  return outputArray;
}

/**
 * Show a local notification (for testing).
 */
export function showLocalNotification(
  title: string,
  body: string,
  icon?: string,
  data?: Record<string, any>
): void {
  if (!('Notification' in window)) {
    console.warn('Notifications are not supported in this browser');
    return;
  }

  if (Notification.permission === 'granted') {
    new Notification(title, {
      body,
      icon: icon || '/icon-192.png',
      badge: '/icon-192.png',
      data,
      tag: 'lead-intelligence',
      requireInteraction: false,
    });
  }
}

