/** API functions for analytics. */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface DashboardMetrics {
  total_leads: number;
  leads_with_phone: number;
  leads_with_email: number;
  phone_coverage: number;
  email_coverage: number;
  average_lead_score: number;
  platform_breakdown: Record<string, number>;
  score_breakdown: Record<string, number>;
  business_type_breakdown: Record<string, number>;
  location_breakdown: Record<string, number>;
  daily_trend: Array<{ date: string; count: number }>;
}

export interface PipelineMetrics {
  stages: Array<{
    name: string;
    count: number;
    percentage: number;
  }>;
  conversion_rates: {
    contact_rate: number;
    verification_rate: number;
    quality_rate: number;
    hot_rate: number;
  };
}

export interface ForecastData {
  forecast: Array<{ date: string; estimated_leads: number }>;
  trend: 'growing' | 'declining' | 'stable';
  estimated_leads: number;
  average_daily: number;
}

async function getAuthHeaders(): Promise<HeadersInit> {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
}

export async function getDashboardMetrics(dateRangeDays: number = 30, teamId?: string): Promise<DashboardMetrics> {
  const params = new URLSearchParams({ date_range_days: dateRangeDays.toString() });
  if (teamId) params.append('team_id', teamId);
  
  const response = await fetch(`${API_BASE_URL}/api/analytics/dashboard?${params}`, {
    headers: await getAuthHeaders(),
  });
  if (!response.ok) throw new Error('Failed to get dashboard metrics');
  return response.json();
}

export async function getPipelineMetrics(teamId?: string): Promise<PipelineMetrics> {
  const params = teamId ? new URLSearchParams({ team_id: teamId }) : '';
  const response = await fetch(`${API_BASE_URL}/api/analytics/pipeline?${params}`, {
    headers: await getAuthHeaders(),
  });
  if (!response.ok) throw new Error('Failed to get pipeline metrics');
  return response.json();
}

export async function getForecast(daysAhead: number = 30): Promise<ForecastData> {
  const response = await fetch(`${API_BASE_URL}/api/analytics/forecast?days_ahead=${daysAhead}`, {
    headers: await getAuthHeaders(),
  });
  if (!response.ok) throw new Error('Failed to get forecast');
  return response.json();
}

