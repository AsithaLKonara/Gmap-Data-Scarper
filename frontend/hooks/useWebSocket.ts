/** WebSocket hook for real-time updates with batching support and automatic reconnection */
import { useEffect, useRef, useState, useCallback } from 'react';

interface UseWebSocketOptions {
  batch?: boolean;
  batchInterval?: number;
  maxBatchSize?: number;
  reconnect?: boolean;
  maxReconnectAttempts?: number;
  reconnectInterval?: number;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

export default function useWebSocket(
  url: string | null,
  options: UseWebSocketOptions = {}
): string | null {
  const {
    batch = false,
    batchInterval = 100,
    maxBatchSize = 50,
    reconnect = true,
    maxReconnectAttempts = 10,
    reconnectInterval = 1000,
    onConnect,
    onDisconnect,
    onError,
  } = options;
  
  const [message, setMessage] = useState<string | null>(null);
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);
  const messageQueueRef = useRef<any[]>([]);
  const batchTimerRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);
  const shouldReconnectRef = useRef<boolean>(true);
  const urlRef = useRef<string | null>(null);

  const processBatch = useCallback(() => {
    if (messageQueueRef.current.length === 0) return;
    const batch = [...messageQueueRef.current];
    messageQueueRef.current = [];
    // Return the last message from batch (or could return array)
    setMessage(batch[batch.length - 1]);
  }, []);

  const connect = useCallback(() => {
    if (!urlRef.current || typeof window === 'undefined') {
      return;
    }

    // Don't reconnect if we've exceeded max attempts
    if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
      console.error('WebSocket: Max reconnection attempts reached');
      setConnectionState('error');
      return;
    }

    // Don't reconnect if we shouldn't
    if (!shouldReconnectRef.current) {
      return;
    }

    setConnectionState('connecting');

    // Convert HTTP URL to WebSocket URL and add token if available
    let wsUrl = urlRef.current.replace('http://', 'ws://').replace('https://', 'wss://');
    
    // Add authentication token from localStorage if available
    const token = localStorage.getItem('access_token');
    if (token) {
      const separator = wsUrl.includes('?') ? '&' : '?';
      wsUrl = `${wsUrl}${separator}token=${encodeURIComponent(token)}`;
    }

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket: Connected');
        setConnectionState('connected');
        reconnectAttemptsRef.current = 0; // Reset on successful connection
        
        if (onConnect) {
          onConnect();
        }
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
        setConnectionState('error');
        
        if (onError) {
          onError(error);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket: Closed', event.code, event.reason);
        setConnectionState('disconnected');
        
        // Process any remaining batched messages
        if (batch && messageQueueRef.current.length > 0) {
          processBatch();
        }

        if (onDisconnect) {
          onDisconnect();
        }

        // Attempt to reconnect if enabled and not a normal closure
        if (reconnect && shouldReconnectRef.current && event.code !== 1000) {
          reconnectAttemptsRef.current += 1;
          
          // Exponential backoff: delay = baseInterval * 2^(attempts-1)
          const delay = reconnectInterval * Math.pow(2, reconnectAttemptsRef.current - 1);
          // Cap at 30 seconds
          const cappedDelay = Math.min(delay, 30000);
          
          console.log(`WebSocket: Reconnecting in ${cappedDelay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
          
          reconnectTimerRef.current = setTimeout(() => {
            connect();
          }, cappedDelay);
        }
      };
    } catch (error) {
      console.error('WebSocket: Connection error', error);
      setConnectionState('error');
      
      // Attempt to reconnect
      if (reconnect && shouldReconnectRef.current) {
        reconnectAttemptsRef.current += 1;
        const delay = reconnectInterval * Math.pow(2, reconnectAttemptsRef.current - 1);
        const cappedDelay = Math.min(delay, 30000);
        
        reconnectTimerRef.current = setTimeout(() => {
          connect();
        }, cappedDelay);
      }
    }
  }, [batch, batchInterval, maxBatchSize, reconnect, maxReconnectAttempts, reconnectInterval, onConnect, onDisconnect, onError, processBatch]);

  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') {
      return;
    }

    // Update URL ref
    urlRef.current = url;

    if (!url) {
      setMessage(null);
      setConnectionState('disconnected');
      shouldReconnectRef.current = false;
      
      // Close existing connection
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      return;
    }

    // Reset reconnection state
    shouldReconnectRef.current = true;
    reconnectAttemptsRef.current = 0;

    // Start batch processing timer if batching enabled
    if (batch) {
      batchTimerRef.current = setInterval(() => {
        if (messageQueueRef.current.length > 0) {
          processBatch();
        }
      }, batchInterval);
    }

    // Connect
    connect();

    return () => {
      shouldReconnectRef.current = false;
      
      if (batchTimerRef.current) {
        clearInterval(batchTimerRef.current);
        batchTimerRef.current = null;
      }
      
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
      
      if (wsRef.current) {
        if (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING) {
          wsRef.current.close();
        }
        wsRef.current = null;
      }
    };
  }, [url, batch, batchInterval, connect, processBatch]);

  return message;
}

