import { useState, useEffect } from 'react';
import GlassCard from '../ui/GlassCard';

interface DashboardMetrics {
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

interface PipelineMetrics {
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

export default function AnalyticsDashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [pipeline, setPipeline] = useState<PipelineMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [dateRange, setDateRange] = useState(30);

  useEffect(() => {
    loadMetrics();
    loadPipeline();
  }, [dateRange]);

  const loadMetrics = async () => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(
        `${API_BASE_URL}/api/analytics/dashboard?date_range_days=${dateRange}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      }
    } catch (err) {
      console.error('Failed to load metrics:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadPipeline = async () => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(
        `${API_BASE_URL}/api/analytics/pipeline`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      if (response.ok) {
        const data = await response.json();
        setPipeline(data);
      }
    } catch (err) {
      console.error('Failed to load pipeline:', err);
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="text-center text-gray-500">Loading analytics...</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gradient-primary">Analytics Dashboard</h1>
        <select
          value={dateRange}
          onChange={(e) => setDateRange(Number(e.target.value))}
          className="input-glass"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
          <option value={365}>Last year</option>
        </select>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <GlassCard>
          <div className="p-4">
            <div className="text-sm text-gray-500 dark:text-gray-400">Total Leads</div>
            <div className="text-3xl font-bold mt-2">{metrics?.total_leads || 0}</div>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="p-4">
            <div className="text-sm text-gray-500 dark:text-gray-400">Phone Coverage</div>
            <div className="text-3xl font-bold mt-2">
              {metrics?.phone_coverage.toFixed(1) || 0}%
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {metrics?.leads_with_phone || 0} leads
            </div>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="p-4">
            <div className="text-sm text-gray-500 dark:text-gray-400">Email Coverage</div>
            <div className="text-3xl font-bold mt-2">
              {metrics?.email_coverage.toFixed(1) || 0}%
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {metrics?.leads_with_email || 0} leads
            </div>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="p-4">
            <div className="text-sm text-gray-500 dark:text-gray-400">Avg Lead Score</div>
            <div className="text-3xl font-bold mt-2">
              {metrics?.average_lead_score.toFixed(1) || 0}
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Pipeline Funnel */}
      {pipeline && (
        <GlassCard>
          <h2 className="text-xl font-semibold mb-4">Lead Pipeline</h2>
          <div className="space-y-3">
            {pipeline.stages.map((stage, idx) => (
              <div key={idx} className="flex items-center gap-4">
                <div className="w-32 text-sm">{stage.name}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-4">
                      <div
                        className="bg-gradient-primary h-4 rounded-full transition-all"
                        style={{ width: `${stage.percentage}%` }}
                      />
                    </div>
                    <div className="w-20 text-right text-sm font-semibold">
                      {stage.count} ({stage.percentage.toFixed(1)}%)
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      {/* Platform Breakdown */}
      {metrics && Object.keys(metrics.platform_breakdown).length > 0 && (
        <GlassCard>
          <h2 className="text-xl font-semibold mb-4">Leads by Platform</h2>
          <div className="space-y-2">
            {Object.entries(metrics.platform_breakdown)
              .sort((a, b) => b[1] - a[1])
              .map(([platform, count]) => (
                <div key={platform} className="flex items-center justify-between">
                  <span className="text-sm capitalize">{platform.replace('_', ' ')}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{
                          width: `${(count / metrics.total_leads) * 100}%`,
                        }}
                      />
                    </div>
                    <span className="text-sm font-semibold w-16 text-right">{count}</span>
                  </div>
                </div>
              ))}
          </div>
        </GlassCard>
      )}

      {/* Score Breakdown */}
      {metrics && Object.keys(metrics.score_breakdown).length > 0 && (
        <GlassCard>
          <h2 className="text-xl font-semibold mb-4">Leads by Score Category</h2>
          <div className="grid grid-cols-3 gap-4">
            {Object.entries(metrics.score_breakdown).map(([category, count]) => (
              <div key={category} className="text-center">
                <div className="text-2xl font-bold">
                  {category === 'hot' ? '🔥' : category === 'warm' ? '🟡' : '⚪'} {count}
                </div>
                <div className="text-sm text-gray-500 capitalize mt-1">{category} leads</div>
              </div>
            ))}
          </div>
        </GlassCard>
      )}
    </div>
  );
}

