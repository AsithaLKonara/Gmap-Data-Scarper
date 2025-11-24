/** Retry utility with exponential backoff */
import { AppError } from './errorHandler';

export interface RetryOptions {
  maxRetries?: number;
  initialDelay?: number;
  maxDelay?: number;
  backoffMultiplier?: number;
  retryableStatusCodes?: number[];
  retryableErrors?: string[];
}

const DEFAULT_OPTIONS: Required<RetryOptions> = {
  maxRetries: 3,
  initialDelay: 1000, // 1 second
  maxDelay: 30000, // 30 seconds
  backoffMultiplier: 2,
  retryableStatusCodes: [408, 429, 500, 502, 503, 504], // Timeout, Rate limit, Server errors
  retryableErrors: ['NetworkError', 'TimeoutError', 'Failed to fetch'],
};

/**
 * Retry a function with exponential backoff
 */
export async function retry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  let lastError: Error | AppError | null = null;

  for (let attempt = 0; attempt <= opts.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error | AppError;

      // Don't retry on last attempt
      if (attempt === opts.maxRetries) {
        throw lastError;
      }

      // Check if error is retryable
      if (!isRetryableError(error, opts)) {
        throw lastError;
      }

      // Calculate delay with exponential backoff
      const delay = Math.min(
        opts.initialDelay * Math.pow(opts.backoffMultiplier, attempt),
        opts.maxDelay
      );

      // Wait before retrying
      await sleep(delay);
    }
  }

  throw lastError || new Error('Retry failed');
}

/**
 * Check if error is retryable
 */
function isRetryableError(
  error: unknown,
  options: Required<RetryOptions>
): boolean {
  // Check for network errors
  if (error instanceof Error) {
    const errorName = error.name || error.constructor.name;
    if (options.retryableErrors.some((e) => errorName.includes(e))) {
      return true;
    }

    // Check for fetch network errors
    if (error.message.includes('fetch') || error.message.includes('network')) {
      return true;
    }
  }

  // Check for AppError with retryable status codes
  if (error instanceof AppError && error.statusCode) {
    return options.retryableStatusCodes.includes(error.statusCode);
  }

  return false;
}

/**
 * Sleep for specified milliseconds
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Retry fetch with exponential backoff
 */
export async function retryFetch(
  url: string,
  options: RequestInit = {},
  retryOptions: RetryOptions = {}
): Promise<Response> {
  return retry(
    async () => {
      const response = await fetch(url, options);
      
      // Check if response status is retryable
      const opts = { ...DEFAULT_OPTIONS, ...retryOptions };
      if (!response.ok && opts.retryableStatusCodes.includes(response.status)) {
        throw new AppError(
          `Request failed with status ${response.status}`,
          'HTTP_ERROR',
          response.status
        );
      }
      
      return response;
    },
    retryOptions
  );
}

