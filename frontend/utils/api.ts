/** FastAPI client functions */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  const response = await fetch(`${API_BASE_URL}/api/scraper/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    const errorMessage = typeof error.detail === 'string' 
      ? error.detail 
      : error.detail?.message || error.detail?.error || `Failed to start scraper: ${response.statusText}`;
    throw new Error(errorMessage);
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
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
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
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  const response = await fetch(`${API_BASE_URL}/api/payments/create-checkout`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
    body: JSON.stringify({ plan_type: planType }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `Failed to create checkout session: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getSubscriptionStatus(): Promise<UserPlan> {
  return getUserPlan();
}

export async function cancelSubscription(): Promise<{ status: string; message: string }> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  const response = await fetch(`${API_BASE_URL}/api/payments/cancel-subscription`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `Failed to cancel subscription: ${response.statusText}`);
  }
  
  return response.json();
}

export async function stopScraper(taskId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/scraper/stop/${taskId}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to stop scraper: ${response.statusText}`);
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
    throw new Error(`Failed to get task status: ${response.statusText}`);
  }
  
  return response.json();
}

export async function exportCSV(taskId?: string, platform?: string): Promise<Blob> {
  const params = new URLSearchParams();
  if (taskId) params.append('task_id', taskId);
  if (platform) params.append('platform', platform);
  
  const response = await fetch(`${API_BASE_URL}/api/export/csv?${params}`);
  
  if (!response.ok) {
    throw new Error(`Failed to export CSV: ${response.statusText}`);
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
    console.error('Error fetching lead objectives:', error);
    return [];
  }
}

export async function optOut(profileUrl: string): Promise<void> {
  const encodedUrl = encodeURIComponent(profileUrl);
  const response = await fetch(`${API_BASE_URL}/api/legal/opt-out/${encodedUrl}`, {
    method: 'DELETE',
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw { response: { data: error } };
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

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('access_token');
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
    throw new Error(`Login failed: ${response.statusText}`);
  }
  
  return response.json();
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
    throw new Error(`Registration failed: ${response.statusText}`);
  }
  
  return response.json();
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
    throw new Error(`Token refresh failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getCurrentUser(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get user: ${response.statusText}`);
  }
  
  return response.json();
}

// Task management functions
export async function listTasks(status?: string): Promise<any[]> {
  const params = status ? `?status=${status}` : '';
  const response = await fetch(`${API_BASE_URL}/api/tasks${params}`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to list tasks: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getTask(taskId: string): Promise<TaskStatus> {
  const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get task: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getQueueStatus(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/tasks/queue/status`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get queue status: ${response.statusText}`);
  }
  
  return response.json();
}

export async function bulkStopTasks(taskIds: string[]): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/tasks/bulk/stop`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(taskIds),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to stop tasks: ${response.statusText}`);
  }
  
  return response.json();
}

export async function bulkPauseTasks(taskIds: string[]): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/tasks/bulk/pause`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(taskIds),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to pause tasks: ${response.statusText}`);
  }
  
  return response.json();
}

export async function bulkResumeTasks(taskIds: string[]): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/tasks/bulk/resume`, {
    method: 'POST',
    headers: getAuthHeaders(),
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
  const response = await fetch(`${API_BASE_URL}/api/analytics/summary?days=${days}`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get analytics summary: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getPlatformStats(): Promise<PlatformStats> {
  const response = await fetch(`${API_BASE_URL}/api/analytics/platforms`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get platform stats: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getTimelineData(days: number = 30): Promise<TimelineData> {
  const response = await fetch(`${API_BASE_URL}/api/analytics/timeline?days=${days}`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get timeline data: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getCategoryStats(): Promise<CategoryStats> {
  const response = await fetch(`${API_BASE_URL}/api/analytics/categories`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get category stats: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getConfidenceStats(): Promise<ConfidenceStats> {
  const response = await fetch(`${API_BASE_URL}/api/analytics/confidence`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get confidence stats: ${response.statusText}`);
  }
  
  return response.json();
}

