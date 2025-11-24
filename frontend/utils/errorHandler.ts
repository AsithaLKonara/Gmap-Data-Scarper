/** Centralized error handling utility */

export interface ApiError {
  message: string;
  code?: string;
  statusCode?: number;
  details?: any;
}

export class AppError extends Error {
  code?: string;
  statusCode?: number;
  details?: any;

  constructor(message: string, code?: string, statusCode?: number, details?: any) {
    super(message);
    this.name = 'AppError';
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

/**
 * Parse error from API response
 */
export async function parseApiError(response: Response): Promise<ApiError> {
  let errorData: any;
  
  try {
    errorData = await response.json();
  } catch {
    // If response is not JSON, use status text
    return {
      message: response.statusText || 'An error occurred',
      statusCode: response.status,
    };
  }

  // Handle different error response formats
  let message = 'An error occurred';
  let code: string | undefined;
  let details: any;

  if (typeof errorData === 'string') {
    message = errorData;
  } else if (errorData.detail) {
    if (typeof errorData.detail === 'string') {
      message = errorData.detail;
    } else if (errorData.detail.message) {
      message = errorData.detail.message;
      code = errorData.detail.code;
      details = errorData.detail;
    } else {
      message = JSON.stringify(errorData.detail);
    }
  } else if (errorData.message) {
    message = errorData.message;
    code = errorData.code;
    details = errorData.details || errorData;
  } else if (errorData.error) {
    message = errorData.error;
    code = errorData.code;
    details = errorData;
  }

  return {
    message,
    code,
    statusCode: response.status,
    details,
  };
}

/**
 * Handle API error and throw standardized error
 */
export async function handleApiError(response: Response): Promise<never> {
  const error = await parseApiError(response);
  throw new AppError(error.message, error.code, error.statusCode, error.details);
}

/**
 * Handle fetch error (network errors, etc.)
 */
export function handleFetchError(error: unknown): AppError {
  if (error instanceof AppError) {
    return error;
  }

  if (error instanceof Error) {
    // Network errors, timeout, etc.
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return new AppError(
        'Network error: Unable to connect to server. Please check your internet connection.',
        'NETWORK_ERROR',
        0
      );
    }
    return new AppError(error.message, 'UNKNOWN_ERROR');
  }

  return new AppError('An unexpected error occurred', 'UNKNOWN_ERROR');
}

/**
 * Log error to console and/or error tracking service
 */
export function logError(error: AppError | Error, context?: string): void {
  const errorMessage = error instanceof AppError
    ? `[${error.code || 'ERROR'}] ${error.message}`
    : error.message;

  const logMessage = context ? `[${context}] ${errorMessage}` : errorMessage;

  if (error instanceof AppError && error.statusCode && error.statusCode >= 500) {
    // Server errors - log as error
    console.error(logMessage, error.details || error);
  } else if (error instanceof AppError && error.statusCode === 401) {
    // Authentication errors - log as warning
    console.warn(logMessage);
  } else {
    // Other errors - log as error
    console.error(logMessage, error);
  }

  // TODO: Send to error tracking service (Sentry, etc.)
  // if (process.env.NODE_ENV === 'production') {
  //   Sentry.captureException(error);
  // }
}

/**
 * Get user-friendly error message
 */
export function getUserFriendlyMessage(error: AppError | Error): string {
  if (error instanceof AppError) {
    // Return user-friendly messages based on error code
    switch (error.code) {
      case 'NETWORK_ERROR':
        return 'Unable to connect to the server. Please check your internet connection and try again.';
      case 'AUTH_ERROR':
      case 'UNAUTHORIZED':
        return 'Your session has expired. Please log in again.';
      case 'FORBIDDEN':
        return 'You do not have permission to perform this action.';
      case 'NOT_FOUND':
        return 'The requested resource was not found.';
      case 'VALIDATION_ERROR':
        return error.message || 'Please check your input and try again.';
      case 'RATE_LIMIT_ERROR':
        return 'Too many requests. Please wait a moment and try again.';
      default:
        return error.message || 'An error occurred. Please try again.';
    }
  }

  return error.message || 'An unexpected error occurred. Please try again.';
}

