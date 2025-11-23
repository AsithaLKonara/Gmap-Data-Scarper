import { useState, useEffect } from 'react';
import {
  subscribeToPushNotifications,
  unsubscribeFromPushNotifications,
  updateNotificationPreferences,
  getNotificationPreferences,
  isPushNotificationSupported,
  isNotificationPermissionGranted,
  NotificationPreferences,
} from '../utils/pushNotifications';
import GlassCard from './ui/GlassCard';
import GlassButton from './ui/GlassButton';
import GlassInput from './ui/GlassInput';
import ErrorDisplay from './ErrorDisplay';

export default function PushNotificationService() {
  const [isSupported, setIsSupported] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    task_completion: true,
    task_errors: true,
    task_paused: false,
    task_resumed: false,
  });
  const [endpoint, setEndpoint] = useState<string | null>(null);

  useEffect(() => {
    // Check if push notifications are supported
    setIsSupported(isPushNotificationSupported());

    // Check if already subscribed
    checkSubscriptionStatus();

    // Load preferences
    loadPreferences();
  }, []);

  const checkSubscriptionStatus = async () => {
    try {
      if ('serviceWorker' in navigator && 'PushManager' in window) {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();

        if (subscription) {
          setIsSubscribed(true);
          setEndpoint(subscription.endpoint);
        } else {
          setIsSubscribed(false);
          setEndpoint(null);
        }
      }
    } catch (error) {
      console.error('Error checking subscription status:', error);
    }
  };

  const loadPreferences = async () => {
    try {
      const prefs = await getNotificationPreferences();
      if (prefs) {
        setPreferences(prefs);
      }
    } catch (error) {
      console.error('Error loading preferences:', error);
    }
  };

  const handleSubscribe = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Check permission first
      const permission = await isNotificationPermissionGranted();
      if (!permission) {
        setError('Notification permission denied. Please enable notifications in your browser settings.');
        setIsLoading(false);
        return;
      }

      // Subscribe to push notifications
      const subscription = await subscribeToPushNotifications();
      if (subscription) {
        setIsSubscribed(true);
        setEndpoint(subscription.endpoint);
      } else {
        setError('Failed to subscribe to push notifications');
      }
    } catch (error: any) {
      setError(error.message || 'Failed to subscribe to push notifications');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUnsubscribe = async () => {
    if (!endpoint) return;

    setIsLoading(true);
    setError(null);

    try {
      const success = await unsubscribeFromPushNotifications(endpoint);
      if (success) {
        setIsSubscribed(false);
        setEndpoint(null);
      } else {
        setError('Failed to unsubscribe from push notifications');
      }
    } catch (error: any) {
      setError(error.message || 'Failed to unsubscribe from push notifications');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreferenceChange = async (
    key: keyof NotificationPreferences,
    value: boolean
  ) => {
    const newPreferences = { ...preferences, [key]: value };
    setPreferences(newPreferences);

    if (endpoint) {
      try {
        await updateNotificationPreferences(endpoint, newPreferences);
      } catch (error) {
        console.error('Error updating preferences:', error);
        // Revert on error
        setPreferences(preferences);
      }
    }
  };

  // Note: Push message handling is done in service worker (sw.js)
  // This component only manages subscription and preferences

  if (!isSupported) {
    return (
      <GlassCard className="p-4">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Push notifications are not supported in this browser.
        </p>
      </GlassCard>
    );
  }

  return (
    <GlassCard className="p-6">
      <h2 className="text-xl font-semibold mb-4 text-gradient-primary">
        Push Notifications
      </h2>

      {error && (
        <ErrorDisplay
          error={error}
          onDismiss={() => setError(null)}
          variant="error"
        />
      )}

      <div className="space-y-4">
        {/* Subscription Status */}
        <div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Status: {isSubscribed ? 'Subscribed' : 'Not Subscribed'}
          </p>
          {isSubscribed && endpoint && (
            <p className="text-xs text-gray-500 dark:text-gray-500 truncate">
              {endpoint}
            </p>
          )}
        </div>

        {/* Subscribe/Unsubscribe Button */}
        <div>
          {isSubscribed ? (
            <GlassButton
              onClick={handleUnsubscribe}
              disabled={isLoading}
              variant="error"
              gradient
              className="w-full"
            >
              {isLoading ? 'Unsubscribing...' : 'Unsubscribe'}
            </GlassButton>
          ) : (
            <GlassButton
              onClick={handleSubscribe}
              disabled={isLoading}
              variant="primary"
              gradient
              className="w-full"
            >
              {isLoading ? 'Subscribing...' : 'Subscribe to Notifications'}
            </GlassButton>
          )}
        </div>

        {/* Notification Preferences */}
        {isSubscribed && (
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-gradient-primary">
              Notification Preferences
            </h3>
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={preferences.task_completion}
                  onChange={(e) =>
                    handlePreferenceChange('task_completion', e.target.checked)
                  }
                  className="w-4 h-4 rounded accent-primary"
                />
                <span>Task completion</span>
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={preferences.task_errors}
                  onChange={(e) =>
                    handlePreferenceChange('task_errors', e.target.checked)
                  }
                  className="w-4 h-4 rounded accent-primary"
                />
                <span>Task errors</span>
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={preferences.task_paused}
                  onChange={(e) =>
                    handlePreferenceChange('task_paused', e.target.checked)
                  }
                  className="w-4 h-4 rounded accent-primary"
                />
                <span>Task paused</span>
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={preferences.task_resumed}
                  onChange={(e) =>
                    handlePreferenceChange('task_resumed', e.target.checked)
                  }
                  className="w-4 h-4 rounded accent-primary"
                />
                <span>Task resumed</span>
              </label>
            </div>
          </div>
        )}
      </div>
    </GlassCard>
  );
}

