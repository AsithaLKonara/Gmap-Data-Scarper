/**
 * Frontend configuration
 * Environment-based configuration for API URLs and other settings
 */

const isDevelopment = process.env.NODE_ENV === 'development';

export const config = {
  // API URL - use environment variable or default to localhost
  apiUrl: process.env.NEXT_PUBLIC_API_URL || (isDevelopment ? 'http://localhost:8000' : ''),
  
  // WebSocket URL - derived from API URL
  wsUrl: (() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || (isDevelopment ? 'http://localhost:8000' : '');
    if (apiUrl.startsWith('https://')) {
      return apiUrl.replace('https://', 'wss://');
    }
    return apiUrl.replace('http://', 'ws://');
  })(),
  
  // Retry configuration
  retry: {
    maxRetries: 3,
    retryDelay: 1000, // milliseconds
  },
  
  // Timeout configuration
  timeout: {
    api: 30000, // 30 seconds
    websocket: 60000, // 60 seconds
  },
  
  // Feature flags
  features: {
    phoneHighlighting: true,
    complianceDashboard: true,
    realTimeUpdates: true,
  },
};

export default config;

