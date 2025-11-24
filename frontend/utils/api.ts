/** FastAPI client functions */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Token refresh helper
let refreshPromise: Promise<string | null> | null = null;

async function getValidToken(): Promise<string | null> {
  if (typeof window === 'undefined') return null;
  
  const token = localStorage.getItem('access_token');
  const expiryTime = localStorage.getItem('token_expiry');
  
  if (!token) return null;
  
  // Check if token is expired or expiring soon (within 5 minutes)
  if (expiryTime) {
    const expiry = parseInt(expiryTime, 10);
    const now = Date.now();
    const timeUntilExpiry = expiry - now;
    
    if (timeUntilExpiry < 5 * 60 * 1000) {
      // Token expiring soon, refresh it
      if (!refreshPromise) {
        refreshPromise = refreshToken();
        refreshPromise.finally(() => {
          refreshPromise = null;
        });
      }
      return await refreshPromise;
    }
  }
  
  return token;
}

async function refreshToken(): Promise<string | null> {
  const refreshTokenValue = localStorage.getItem('refresh_token');
  if (!refreshTokenValue) {
    return null;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshTokenValue }),
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    
    const expiresIn = data.expires_in || 3600;
    const expiryTime = Date.now() + expiresIn * 1000;
    localStorage.setItem('token_expiry', expiryTime.toString());

    return data.access_token;
  } catch (error) {
    console.error('Token refresh error:', error);
    // Clear tokens on refresh failure
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_expiry');
    return null;
  }
}

export interface ScrapeRequest {
  queries: string[];
  platforms: string[];
  max_results?: number;
  headless?: boolean;
  lead_objective?: string;
  business_type?: string[];
  job_level?: string[];
  location?: string;
  radius_km?: number;
  education_level?: string[];
  field_of_study?: string;
  degree_type?: string[];
  student_only?: boolean;
  institution?: string;
  phone_only?: boolean;
}

export interface TaskStatus {
  task_id: string;
  status: string;
  progress: Record<string, number>;
  total_results: number;
  current_query?: string;
  current_platform?: string;
  started_at?: string;
  completed_at?: string;
  error?: string;
}

export async function startScraper(request: ScrapeRequest): Promise<{ task_id: string; usage?: any }> {
  const token = await getValidToken();
  const response = await retryFetch(
    `${API_BASE_URL}/api/scraper/start`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
      body: JSON.stringify(request),
    },
    config.retry
  );
  
  if (!response.ok) {
    await handleApiError(response);
  }
  
  return response.json();
}

export interface UserPlan {
  plan_type: string;
  plan_name: string;
  status: string;
  daily_limit: number | null;
  monthly_price: number | null;
  price_per_lead: number | null;
  usage: {
    plan_type: string;
    daily_limit: number | null;
    used_today: number;
    remaining_today: number | null;
    is_unlimited: boolean;
  };
}

export interface CheckoutSession {
  session_id: string;
  url: string;
  customer_id: string;
}

export async function getUserPlan(): Promise<UserPlan> {
  const token = await getValidToken();
  const response = await fetch(`${API_BASE_URL}/api/payments/subscription-status`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get user plan: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getUsageStats(): Promise<UserPlan['usage']> {
  const plan = await getUserPlan();
  return plan.usage;
}

export async function createCheckoutSession(planType: 'paid_monthly' | 'paid_usage'): Promise<CheckoutSession> {
  const token = await getValidToken();
  const response = await fetch(`${API_BASE_URL}/api/payments/create-checkout`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
    body: JSON.stringify({ plan_type: planType }),
  });
  
  if (!response.ok) {
    await handleApiError(response);
  }
  
  return response.json();
}

export async function getSubscriptionStatus(): Promise<UserPlan> {
  return getUserPlan();
}

export async function cancelSubscription(): Promise<{ status: string; message: string }> {
  const token = await getValidToken();
  const response = await fetch(`${API_BASE_URL}/api/payments/cancel-subscription`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
  });
  
  if (!response.ok) {
    await handleApiError(response);
  }
  
  return response.json();
}

export async function stopScraper(taskId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/scraper/stop/${taskId}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    await handleApiError(response);
  }
}

export async function pauseScraper(taskId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/scraper/pause/${taskId}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to pause scraper: ${response.statusText}`);
  }
}

export async function resumeScraper(taskId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/scraper/resume/${taskId}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to resume scraper: ${response.statusText}`);
  }
}

export async function getTaskStatus(taskId: string): Promise<TaskStatus> {
  const response = await fetch(`${API_BASE_URL}/api/scraper/status/${taskId}`);
  
  if (!response.ok) {
    await handleApiError(response);
  }
  
  return response.json();
}

export async function exportCSV(taskId?: string, platform?: string): Promise<Blob> {
  const params = new URLSearchParams();
  if (taskId) params.append('task_id', taskId);
  if (platform) params.append('platform', platform);
  
  const response = await fetch(`${API_BASE_URL}/api/export/csv?${params}`);
  
  if (!response.ok) {
    await handleApiError(response);
  }
  
  return response.blob();
}

export async function getBusinessTypes(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/api/filters/business-types`);
  return response.json();
}

export async function getJobLevels(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/api/filters/job-levels`);
  return response.json();
}

export async function getEducationLevels(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/api/filters/education-levels`);
  return response.json();
}

export async function getDegreeTypes(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/api/filters/degree-types`);
  return response.json();
}

export async function getPlatforms(): Promise<string[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/filters/platforms`);
    if (!response.ok) {
      console.error('Failed to fetch platforms:', response.statusText);
      return [];
    }
    const data = await response.json();
    // Ensure we return an array
    return Array.isArray(data) ? data : [];
  } catch (error) {
    console.error('Error fetching platforms:', error);
    return [];
  }
}

export interface LeadObjective {
  value: string;
  label: string;
}

export async function getLeadObjectives(): Promise<LeadObjective[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/filters/lead-objectives`);
    if (!response.ok) {
      console.error('Failed to fetch lead objectives:', response.statusText);
      return [];
    }
    const data = await response.json();
    // Ensure we return an array
    return Array.isArray(data) ? data : [];
  } catch (error) {
    const appError = handleFetchError(error);
    logError(appError, 'getLeadObjectives');
    return [];
  }
}

export async function optOut(profileUrl: string): Promise<void> {
  const encodedUrl = encodeURIComponent(profileUrl);
  const response = await fetch(`${API_BASE_URL}/api/legal/opt-out/${encodedUrl}`, {
    method: 'DELETE',
  });
  
  if (!response.ok) {
    await handleApiError(response);
  }
}

export async function getRetentionStats(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/legal/retention/stats`);
  
  if (!response.ok) {
    throw new Error(`Failed to get retention stats: ${response.statusText}`);
  }
  
  return response.json();
}

export async function runCleanup(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/legal/retention/cleanup`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to run cleanup: ${response.statusText}`);
  }
  
  return response.json();
}

// Authentication functions
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

async function getAuthHeaders(): Promise<HeadersInit> {
  const token = await getValidToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export async function login(request: LoginRequest): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    await handleApiError(response);
  }
  
  const data = await response.json();
  
  // Store tokens and expiry
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    const expiresIn = data.expires_in || 3600;
    const expiryTime = Date.now() + expiresIn * 1000;
    localStorage.setItem('token_expiry', expiryTime.toString());
  }
  
  return data;
}

export async function register(request: RegisterRequest): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    await handleApiError(response);
  }
  
  const data = await response.json();
  
  // Store tokens and expiry
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    const expiresIn = data.expires_in || 3600;
    const expiryTime = Date.now() + expiresIn * 1000;
    localStorage.setItem('token_expiry', expiryTime.toString());
  }
  
  return data;
}

export async function refreshToken(refreshToken: string): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  
  if (!response.ok) {
    await handleApiError(response);
  }
  
  return response.json();
}

export async function getCurrentUser(): Promise<any> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers,
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get user: ${response.statusText}`);
  }
  
  return response.json();
}

// Task management functions
export async function listTasks(status?: string): Promise<any[]> {
  const params = status ? `?status=${status}` : '';
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_BASE_URL}/api/tasks${params}`, {
    headers,
  });
  
  if (!response.ok) {
    throw new Error(`Failed to list tasks: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getTask(taskId: string): Promise<TaskStatus> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
    headers,
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get task: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getQueueStatus(): Promise<any> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_BASE_URL}/api/tasks/queue/status`, {
    headers,
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get queue status: ${response.statusText}`);
  }
  
  return response.json();
}

export async function bulkStopTasks(taskIds: string[]): Promise<any> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_BASE_URL}/api/tasks/bulk/stop`, {
    method: 'POST',
    headers,
    body: JSON.stringify(taskIds),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to stop tasks: ${response.statusText}`);
  }
  
  return response.json();
}

export async function bulkPauseTasks(taskIds: string[]): Promise<any> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_BASE_URL}/api/tasks/bulk/pause`, {
    method: 'POST',
    headers,
    body: JSON.stringify(taskIds),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to pause tasks: ${response.statusText}`);
  }
  
  return response.json();
}

export async function bulkResumeTasks(taskIds: string[]): Promise<any> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_BASE_URL}/api/tasks/bulk/resume`, {
    method: 'POST',
    headers,
    body: JSON.stringify(taskIds),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to resume tasks: ${response.statusText}`);
  }
  
  return response.json();
}

// Analytics functions
export interface AnalyticsSummary {
  total_leads: number;
  phones_found: number;
  phone_coverage: number;
  platforms: Record<string, number>;
  categories: Record<string, number>;
  period_days: number;
}

export interface PlatformStats {
  [platform: string]: {
    total: number;
    phones: number;
    phone_rate: number;
    top_categories: Record<string, number>;
  };
}

export interface TimelineData {
  timeline: Array<{
    date: string;
    leads: number;
    phones: number;
  }>;
  period_days: number;
}

export interface CategoryStats {
  [category: string]: {
    total: number;
    phones: number;
    phone_rate: number;
    platforms: Record<string, number>;
  };
}

export interface ConfidenceStats {
  total_with_confidence: number;
  high_confidence: number;
  medium_confidence: number;
  low_confidence: number;
  high_percentage: number;
}

export async function getAnalyticsSummary(days: number = 7): Promise<AnalyticsSummary> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_BASE_URL}/api/analytics/summary?days=${days}`, {
    headers,
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get analytics summary: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getPlatformStats(): Promise<PlatformStats> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_BASE_URL}/api/analytics/platforms`, {
    headers,
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get platform stats: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getTimelineData(days: number = 30): Promise<TimelineData> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_BASE_URL}/api/analytics/timeline?days=${days}`, {
    headers,
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get timeline data: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getCategoryStats(): Promise<CategoryStats> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_BASE_URL}/api/analytics/categories`, {
    headers,
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get category stats: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getConfidenceStats(): Promise<ConfidenceStats> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_BASE_URL}/api/analytics/confidence`, {
    headers,
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get confidence stats: ${response.statusText}`);
  }
  
  return response.json();
}

