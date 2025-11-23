import React from 'react';
import { CategoryStats } from '../../utils/api';
import GlassCard from '../ui/GlassCard';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';

interface CategoryChartProps {
  data: CategoryStats;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4'];

export default function CategoryChart({ data }: CategoryChartProps) {
  const chartData = Object.entries(data)
    .map(([category, stats]) => ({
      name: category || 'Unknown',
      value: stats.total,
      phones: stats.phones,
      phoneRate: stats.phone_rate,
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10); // Top 10 categories

  return (
    <GlassCard>
      <h2 className="text-xl font-semibold mb-4 text-gradient-primary">Top Categories</h2>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-4 text-sm text-gray-600">
        <p className="font-semibold mb-2">Top Categories by Phone Coverage:</p>
        <div className="space-y-1 max-h-32 overflow-y-auto">
          {chartData
            .sort((a, b) => b.phoneRate - a.phoneRate)
            .slice(0, 5)
            .map((item) => (
              <div key={item.name} className="flex justify-between">
                <span>{item.name}:</span>
                <span className="font-medium">{item.phoneRate.toFixed(1)}%</span>
              </div>
            ))}
        </div>
      </div>
    </GlassCard>
  );
}

