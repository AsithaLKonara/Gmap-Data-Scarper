import React, { useEffect, useState } from 'react';
import {
  getAnalyticsSummary,
  getPlatformStats,
  getTimelineData,
  getCategoryStats,
  getConfidenceStats,
  AnalyticsSummary,
  PlatformStats,
  TimelineData,
  CategoryStats,
  ConfidenceStats,
} from '../utils/api';
import SummaryCards from './dashboard/SummaryCards';
import PlatformChart from './dashboard/PlatformChart';
import TimelineChart from './dashboard/TimelineChart';
import CategoryChart from './dashboard/CategoryChart';
import ConfidenceChart from './dashboard/ConfidenceChart';
import { showToast } from '../utils/toast';
import GlassCard from './ui/GlassCard';
import LoadingSkeleton from './LoadingSkeleton';
import ErrorDisplay from './ErrorDisplay';

export default function Dashboard() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [platformStats, setPlatformStats] = useState<PlatformStats | null>(null);
  const [timeline, setTimeline] = useState<TimelineData | null>(null);
  const [categoryStats, setCategoryStats] = useState<CategoryStats | null>(null);
  const [confidenceStats, setConfidenceStats] = useState<ConfidenceStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summaryDays, setSummaryDays] = useState(7);
  const [timelineDays, setTimelineDays] = useState(30);

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [summaryData, platformsData, timelineData, categoriesData, confidenceData] = await Promise.all([
        getAnalyticsSummary(summaryDays),
        getPlatformStats(),
        getTimelineData(timelineDays),
        getCategoryStats(),
        getConfidenceStats(),
      ]);
      
      setSummary(summaryData);
      setPlatformStats(platformsData);
      setTimeline(timelineData);
      setCategoryStats(categoriesData);
      setConfidenceStats(confidenceData);
    } catch (err: any) {
      const errorMsg = err.message || 'Failed to load dashboard data';
      setError(errorMsg);
      showToast(errorMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, [summaryDays, timelineDays]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSkeleton variant="card" className="w-full max-w-md" />
      </div>
    );
  }

  if (error) {
    return (
      <ErrorDisplay
        error={error}
        onDismiss={() => setError(null)}
        title="Error loading dashboard"
        variant="error"
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Period Selectors */}
      <GlassCard>
        <div className="flex gap-4 items-center flex-wrap">
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium">Summary Period:</label>
            <select
              value={summaryDays}
              onChange={(e) => setSummaryDays(Number(e.target.value))}
              className="input-glass px-3 py-1 text-sm"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={365}>Last year</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium">Timeline Period:</label>
            <select
              value={timelineDays}
              onChange={(e) => setTimelineDays(Number(e.target.value))}
              className="input-glass px-3 py-1 text-sm"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={365}>Last year</option>
            </select>
          </div>
          <button
            onClick={fetchAllData}
            className="ml-auto glass px-4 py-2 rounded-lg hover:glass-strong transition-all text-sm"
          >
            Refresh
          </button>
        </div>
      </GlassCard>

      {/* Summary Cards */}
      {summary && <SummaryCards summary={summary} />}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {platformStats && <PlatformChart data={platformStats} />}
        {timeline && <TimelineChart data={timeline} />}
        {categoryStats && <CategoryChart data={categoryStats} />}
        {confidenceStats && <ConfidenceChart data={confidenceStats} />}
      </div>
    </div>
  );
}

