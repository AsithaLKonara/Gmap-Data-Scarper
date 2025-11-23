/**WebSocket message batching utility for performance optimization.*/
import { useEffect, useRef, useState } from 'react';

interface BatchedMessage {
  timestamp: number;
  data: any;
}

/**
 * Hook for batched WebSocket messages.
 * Batches messages and processes them in intervals to reduce re-renders.
 */
export function useBatchedWebSocket(
  url: string | null,
  batchInterval: number = 100, // Batch messages every 100ms
  maxBatchSize: number = 50 // Max messages per batch
) {
  const [batchedMessages, setBatchedMessages] = useState<any[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const messageQueueRef = useRef<BatchedMessage[]>([]);
  const batchTimerRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  useEffect(() => {
    if (!url) {
      return;
    }

    let isMounted = true;

    const connect = () => {
      try {
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
          if (isMounted) {
            reconnectAttemptsRef.current = 0;
            console.log('[WebSocket] Connected');
          }
        };

        ws.onmessage = (event) => {
          if (!isMounted) return;

          try {
            const data = JSON.parse(event.data);
            messageQueueRef.current.push({
              timestamp: Date.now(),
              data,
            });

            // Process batch if queue is full
            if (messageQueueRef.current.length >= maxBatchSize) {
              processBatch();
            }
          } catch (e) {
            // If not JSON, treat as plain text
            messageQueueRef.current.push({
              timestamp: Date.now(),
              data: event.data,
            });
          }
        };

        ws.onerror = (error) => {
          console.error('[WebSocket] Error:', error);
        };

        ws.onclose = () => {
          if (isMounted && reconnectAttemptsRef.current < maxReconnectAttempts) {
            reconnectAttemptsRef.current++;
            const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
            reconnectTimerRef.current = setTimeout(() => {
              if (isMounted) {
                connect();
              }
            }, delay);
          }
        };
      } catch (error) {
        console.error('[WebSocket] Connection error:', error);
      }
    };

    const processBatch = () => {
      if (messageQueueRef.current.length === 0) return;

      const batch = [...messageQueueRef.current];
      messageQueueRef.current = [];

      if (isMounted) {
        setBatchedMessages((prev) => [...prev, ...batch.map((m) => m.data)]);
      }
    };

    // Start batch processing timer
    batchTimerRef.current = setInterval(() => {
      if (messageQueueRef.current.length > 0) {
        processBatch();
      }
    }, batchInterval);

    connect();

    return () => {
      isMounted = false;
      if (batchTimerRef.current) {
        clearInterval(batchTimerRef.current);
      }
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url, batchInterval, maxBatchSize]);

  return batchedMessages;
}

