import React from 'react';
import { TimelineData } from '../../utils/api';
import GlassCard from '../ui/GlassCard';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface TimelineChartProps {
  data: TimelineData;
}

export default function TimelineChart({ data }: TimelineChartProps) {
  const chartData = data.timeline.map((item) => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    leads: item.leads,
    phones: item.phones,
  }));

  return (
    <GlassCard>
      <h2 className="text-xl font-semibold mb-4 text-gradient-primary">Timeline Trends</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="leads" stroke="#3b82f6" name="Leads" strokeWidth={2} />
          <Line type="monotone" dataKey="phones" stroke="#10b981" name="Phones" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
      <p className="mt-4 text-sm text-gray-600">Last {data.period_days} days</p>
    </GlassCard>
  );
}

