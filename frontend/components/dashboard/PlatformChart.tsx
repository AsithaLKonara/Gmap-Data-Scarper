import React from 'react';
import { PlatformStats } from '../../utils/api';
import GlassCard from '../ui/GlassCard';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface PlatformChartProps {
  data: PlatformStats;
}

export default function PlatformChart({ data }: PlatformChartProps) {
  const chartData = Object.entries(data).map(([platform, stats]) => ({
    platform: platform.replace('_', ' ').toUpperCase(),
    total: stats.total,
    phones: stats.phones,
    phoneRate: stats.phone_rate,
  }));

  return (
    <GlassCard>
      <h2 className="text-xl font-semibold mb-4 text-gradient-primary">Platform Statistics</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="platform" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="total" fill="#3b82f6" name="Total Leads" />
          <Bar dataKey="phones" fill="#10b981" name="Phones Found" />
        </BarChart>
      </ResponsiveContainer>
      <div className="mt-4 text-sm text-gray-600">
        <p className="font-semibold mb-2">Phone Coverage by Platform:</p>
        <div className="space-y-1">
          {Object.entries(data).map(([platform, stats]) => (
            <div key={platform} className="flex justify-between">
              <span className="capitalize">{platform.replace('_', ' ')}:</span>
              <span className="font-medium">{stats.phone_rate.toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </div>
    </GlassCard>
  );
}

