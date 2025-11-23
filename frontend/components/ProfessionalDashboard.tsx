import { useState, useMemo } from 'react';
import { formatPhone, copyToClipboard } from '../utils/phone';
import { showToast } from '../utils/toast';

interface ProfessionalDashboardProps {
  results: any[];
  progress: Record<string, number>;
  taskId: string | null;
}

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: 'blue' | 'green' | 'purple' | 'orange' | 'red';
}

function StatCard({ title, value, subtitle, icon, trend, color = 'blue' }: StatCardProps) {
  const colorClasses = {
    blue: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30',
    green: 'from-green-500/20 to-emerald-500/20 border-green-500/30',
    purple: 'from-purple-500/20 to-pink-500/20 border-purple-500/30',
    orange: 'from-orange-500/20 to-amber-500/20 border-orange-500/30',
    red: 'from-red-500/20 to-rose-500/20 border-red-500/30',
  };

  return (
    <div className={`glass-strong rounded-xl p-6 border bg-gradient-to-br ${colorClasses[color]} hover:scale-105 transition-transform duration-200`}>
      <div className="flex items-start justify-between mb-4">
        <div className="text-3xl">{icon}</div>
        {trend && (
          <div className={`text-sm font-semibold ${trend.isPositive ? 'text-green-400' : 'text-red-400'}`}>
            {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
          </div>
        )}
      </div>
      <div className="space-y-1">
        <div className="text-2xl font-bold text-white">{value}</div>
        <div className="text-sm text-gray-400 font-medium">{title}</div>
        {subtitle && <div className="text-xs text-gray-500 mt-1">{subtitle}</div>}
      </div>
    </div>
  );
}

export default function ProfessionalDashboard({ results, progress, taskId }: ProfessionalDashboardProps) {
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'hot' | 'warm' | 'low'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Calculate statistics
  const stats = useMemo(() => {
    const totalLeads = results.length;
    const leadsWithPhone = results.filter(r => r.phones && r.phones.length > 0).length;
    const hotLeads = results.filter(r => {
      const score = r.lead_score || 0;
      return score >= 80;
    }).length;
    const warmLeads = results.filter(r => {
      const score = r.lead_score || 0;
      return score >= 50 && score < 80;
    }).length;
    const lowLeads = results.filter(r => {
      const score = r.lead_score || 0;
      return score < 50;
    }).length;
    
    const avgScore = totalLeads > 0
      ? Math.round(results.reduce((sum, r) => sum + (r.lead_score || 0), 0) / totalLeads)
      : 0;

    const totalPlatforms = Object.keys(progress).length;
    const totalProgress = Object.values(progress).reduce((sum, val) => sum + val, 0);

    return {
      totalLeads,
      leadsWithPhone,
      hotLeads,
      warmLeads,
      lowLeads,
      avgScore,
      totalPlatforms,
      totalProgress,
    };
  }, [results, progress]);

  // Filter results
  const filteredResults = useMemo(() => {
    let filtered = results;

    // Filter by lead score category
    if (selectedFilter !== 'all') {
      filtered = filtered.filter(r => {
        const score = r.lead_score || 0;
        if (selectedFilter === 'hot') return score >= 80;
        if (selectedFilter === 'warm') return score >= 50 && score < 80;
        if (selectedFilter === 'low') return score < 50;
        return true;
      });
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(r => {
        const name = (r.display_name || '').toLowerCase();
        const location = (r.location || r.city || '').toLowerCase();
        const phone = r.phones?.some((p: any) => 
          (p.raw_phone || '').toLowerCase().includes(query) ||
          (p.normalized_e164 || '').toLowerCase().includes(query)
        );
        return name.includes(query) || location.includes(query) || phone;
      });
    }

    return filtered;
  }, [results, selectedFilter, searchQuery]);

  const getLeadScoreBadge = (score: number) => {
    if (score >= 80) {
      return <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-500/20 text-red-400 border border-red-500/30">🔥 Hot</span>;
    }
    if (score >= 50) {
      return <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">🟡 Warm</span>;
    }
    return <span className="px-2 py-1 text-xs font-semibold rounded-full bg-gray-500/20 text-gray-400 border border-gray-500/30">⚪ Low</span>;
  };

  const handleCopyPhone = async (phone: string) => {
    try {
      await copyToClipboard(phone);
      showToast('Phone number copied to clipboard', 'success', 2000);
    } catch (error) {
      console.error('Failed to copy phone:', error);
      showToast('Failed to copy phone number', 'error', 2000);
    }
  };

  return (
    <div className="h-full flex flex-col space-y-6 p-6 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gradient-primary mb-2">Lead Intelligence Dashboard</h1>
          <p className="text-gray-400">Real-time lead collection and analysis</p>
        </div>
        {taskId && (
          <div className="flex items-center gap-2 glass-subtle px-4 py-2 rounded-lg">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium">Active</span>
          </div>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Leads"
          value={stats.totalLeads}
          subtitle={`${stats.leadsWithPhone} with phone numbers`}
          icon="📊"
          color="blue"
        />
        <StatCard
          title="Hot Leads"
          value={stats.hotLeads}
          subtitle={`${stats.totalLeads > 0 ? Math.round((stats.hotLeads / stats.totalLeads) * 100) : 0}% of total`}
          icon="🔥"
          color="red"
        />
        <StatCard
          title="Avg Lead Score"
          value={stats.avgScore}
          subtitle="Quality indicator"
          icon="⭐"
          color="purple"
        />
        <StatCard
          title="Platforms Active"
          value={stats.totalPlatforms}
          subtitle={`${stats.totalProgress} total results`}
          icon="🌐"
          color="green"
        />
      </div>

      {/* Filters and Search */}
      <div className="glass-strong rounded-xl p-4 border border-white/10">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search leads by name, location, or phone..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 glass-subtle rounded-lg border border-white/10 focus:border-primary/50 focus:outline-none text-sm"
            />
          </div>
          
          {/* Filter Buttons */}
          <div className="flex gap-2">
            {(['all', 'hot', 'warm', 'low'] as const).map((filter) => (
              <button
                key={filter}
                onClick={() => setSelectedFilter(filter)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  selectedFilter === filter
                    ? 'glass-strong border border-primary/50 text-primary'
                    : 'glass-subtle border border-white/10 text-gray-400 hover:text-white'
                }`}
              >
                {filter === 'all' ? 'All' : filter === 'hot' ? '🔥 Hot' : filter === 'warm' ? '🟡 Warm' : '⚪ Low'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Results Table */}
      <div className="glass-strong rounded-xl border border-white/10 overflow-hidden flex-1 flex flex-col">
        {/* Table Header */}
        <div className="px-6 py-4 border-b border-white/10 bg-gradient-to-r from-white/5 to-transparent">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Leads ({filteredResults.length})</h2>
            <div className="text-sm text-gray-400">
              Showing {filteredResults.length} of {results.length} leads
            </div>
          </div>
        </div>

        {/* Table Content */}
        <div className="flex-1 overflow-y-auto">
          {filteredResults.length === 0 ? (
            <div className="flex items-center justify-center h-64 text-gray-400">
              <div className="text-center">
                <div className="text-4xl mb-4">🔍</div>
                <p className="text-lg font-medium mb-2">No leads found</p>
                <p className="text-sm">Try adjusting your filters or start a new search</p>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-white/5">
              {filteredResults.map((result, idx) => {
                const phones = result.phones || [];
                const primaryPhone = phones[0];
                const leadScore = result.lead_score || 0;

                return (
                  <div
                    key={idx}
                    className="px-6 py-4 hover:bg-white/5 transition-colors cursor-pointer group"
                  >
                    <div className="flex items-start justify-between gap-4">
                      {/* Main Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold text-white truncate">
                            {result.display_name || 'Unknown'}
                          </h3>
                          {getLeadScoreBadge(leadScore)}
                          {leadScore > 0 && (
                            <span className="text-xs text-gray-500">({leadScore}/100)</span>
                          )}
                        </div>
                        
                        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400">
                          {result.location && (
                            <div className="flex items-center gap-1">
                              <span>📍</span>
                              <span>{result.location}</span>
                            </div>
                          )}
                          {result.city && result.city !== result.location && (
                            <div className="flex items-center gap-1">
                              <span>🏙️</span>
                              <span>{result.city}</span>
                            </div>
                          )}
                          {primaryPhone && (
                            <div className="flex items-center gap-2">
                              <span>📞</span>
                              <span className="font-mono text-primary">
                                {formatPhone(primaryPhone.normalized_e164 || primaryPhone.raw_phone)}
                              </span>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleCopyPhone(primaryPhone.normalized_e164 || primaryPhone.raw_phone);
                                }}
                                className="opacity-0 group-hover:opacity-100 transition-opacity text-xs px-2 py-1 glass-subtle rounded hover:glass"
                              >
                                Copy
                              </button>
                            </div>
                          )}
                        </div>

                        {/* Additional Info */}
                        {(result.keywords || result.estimated_revenue || result.employee_count) && (
                          <div className="flex flex-wrap gap-3 mt-2 text-xs text-gray-500">
                            {result.keywords && result.keywords.length > 0 && (
                              <div className="flex items-center gap-1">
                                <span>🏷️</span>
                                <span>{result.keywords.slice(0, 3).join(', ')}</span>
                              </div>
                            )}
                            {result.estimated_revenue && (
                              <div className="flex items-center gap-1">
                                <span>💰</span>
                                <span>${result.estimated_revenue.toLocaleString()}</span>
                              </div>
                            )}
                            {result.employee_count && (
                              <div className="flex items-center gap-1">
                                <span>👥</span>
                                <span>{result.employee_count} employees</span>
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        {primaryPhone && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleCopyPhone(primaryPhone.normalized_e164 || primaryPhone.raw_phone);
                            }}
                            className="px-3 py-1.5 text-xs font-medium glass-subtle rounded-lg hover:glass border border-white/10"
                          >
                            Copy Phone
                          </button>
                        )}
                        <button
                          className="px-3 py-1.5 text-xs font-medium glass-subtle rounded-lg hover:glass border border-white/10"
                        >
                          View Details
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

