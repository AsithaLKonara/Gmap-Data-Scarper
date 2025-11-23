import React from 'react';
import { ConfidenceStats } from '../../utils/api';
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

interface ConfidenceChartProps {
  data: ConfidenceStats;
}

export default function ConfidenceChart({ data }: ConfidenceChartProps) {
  const chartData = [
    {
      level: 'High (≥80%)',
      count: data.high_confidence,
      color: '#10b981',
    },
    {
      level: 'Medium (50-79%)',
      count: data.medium_confidence,
      color: '#f59e0b',
    },
    {
      level: 'Low (<50%)',
      count: data.low_confidence,
      color: '#ef4444',
    },
  ];

  return (
    <GlassCard>
      <h2 className="text-xl font-semibold mb-4 text-gradient-primary">Phone Confidence Distribution</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="level" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="count" fill="#3b82f6" name="Phone Count" />
        </BarChart>
      </ResponsiveContainer>
      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="text-center">
          <p className="text-2xl font-bold text-green-600">{data.high_confidence}</p>
          <p className="text-sm text-gray-600">High Confidence</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-yellow-600">{data.medium_confidence}</p>
          <p className="text-sm text-gray-600">Medium Confidence</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-red-600">{data.low_confidence}</p>
          <p className="text-sm text-gray-600">Low Confidence</p>
        </div>
      </div>
      <div className="mt-4 p-3 glass-subtle rounded-lg">
        <p className="text-sm text-gray-700 dark:text-gray-300">
          <span className="font-semibold">High Confidence Rate:</span>{' '}
          {data.high_percentage.toFixed(1)}% of phones with confidence scores
        </p>
        <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
          Total phones with confidence: {data.total_with_confidence.toLocaleString()}
        </p>
      </div>
    </GlassCard>
  );
}

