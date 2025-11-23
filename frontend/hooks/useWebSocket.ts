/** WebSocket hook for real-time updates with batching support */
import { useEffect, useRef, useState } from 'react';

interface UseWebSocketOptions {
  batch?: boolean;
  batchInterval?: number;
  maxBatchSize?: number;
}

export default function useWebSocket(
  url: string | null,
  options: UseWebSocketOptions = {}
): string | null {
  const { batch = false, batchInterval = 100, maxBatchSize = 50 } = options;
  const [message, setMessage] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const messageQueueRef = useRef<any[]>([]);
  const batchTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') {
      return;
    }

    if (!url) {
      setMessage(null);
      return;
    }

    // Convert HTTP URL to WebSocket URL
    const wsUrl = url.replace('http://', 'ws://').replace('https://', 'wss://');
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    const processBatch = () => {
      if (messageQueueRef.current.length === 0) return;
      const batch = [...messageQueueRef.current];
      messageQueueRef.current = [];
      // Return the last message from batch (or could return array)
      setMessage(batch[batch.length - 1]);
    };

    ws.onopen = () => {
      // Connection established
    };

    ws.onmessage = (event) => {
      if (batch) {
        try {
          const data = JSON.parse(event.data);
          messageQueueRef.current.push(data);
          if (messageQueueRef.current.length >= maxBatchSize) {
            processBatch();
          }
        } catch {
          messageQueueRef.current.push(event.data);
        }
      } else {
        setMessage(event.data);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      // Process any remaining batched messages
      if (batch && messageQueueRef.current.length > 0) {
        processBatch();
      }
    };

    // Start batch processing timer if batching enabled
    if (batch) {
      batchTimerRef.current = setInterval(() => {
        if (messageQueueRef.current.length > 0) {
          processBatch();
        }
      }, batchInterval);
    }

    return () => {
      if (batchTimerRef.current) {
        clearInterval(batchTimerRef.current);
      }
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
    };
  }, [url, batch, batchInterval, maxBatchSize]);

  return message;
}

