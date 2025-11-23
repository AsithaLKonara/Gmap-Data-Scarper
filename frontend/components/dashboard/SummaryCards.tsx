import React from 'react';
import { AnalyticsSummary } from '../../utils/api';
import GlassCard from '../ui/GlassCard';

interface SummaryCardsProps {
  summary: AnalyticsSummary;
}

export default function SummaryCards({ summary }: SummaryCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <GlassCard className="hover-lift">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Leads</p>
            <p className="text-3xl font-bold text-gradient-primary mt-2">{summary.total_leads.toLocaleString()}</p>
          </div>
          <div className="glass-subtle rounded-full p-3">
            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">Last {summary.period_days} days</p>
      </GlassCard>

      <GlassCard className="hover-lift">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Phones Found</p>
            <p className="text-3xl font-bold text-gradient-primary mt-2">{summary.phones_found.toLocaleString()}</p>
          </div>
          <div className="glass-subtle rounded-full p-3">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
          </div>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">{summary.phone_coverage.toFixed(1)}% coverage</p>
      </GlassCard>

      <GlassCard className="hover-lift">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Platforms</p>
            <p className="text-3xl font-bold text-gradient-secondary mt-2">{Object.keys(summary.platforms).length}</p>
          </div>
          <div className="glass-subtle rounded-full p-3">
            <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">Active platforms</p>
      </GlassCard>

      <GlassCard className="hover-lift">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Categories</p>
            <p className="text-3xl font-bold text-gradient-warm mt-2">{Object.keys(summary.categories).length}</p>
          </div>
          <div className="glass-subtle rounded-full p-3">
            <svg className="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
            </svg>
          </div>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">Business categories</p>
      </GlassCard>
    </div>
  );
}

