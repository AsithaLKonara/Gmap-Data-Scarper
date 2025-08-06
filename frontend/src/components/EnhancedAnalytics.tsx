import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Progress,
  Badge,
  Button,
  Select,
  useColorModeValue,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Divider,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
  Switch,
  FormControl,
  FormLabel,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
// Removed problematic Chakra UI icon imports
import * as api from '../api';

interface AnalyticsData {
  period: string;
  jobsCreated: number;
  leadsGenerated: number;
  exportsCompleted: number;
  crmLeads: number;
  conversionRate: number;
  revenue: number;
  goalProgress: number;
}

interface Goal {
  id: string;
  name: string;
  target: number;
  current: number;
  period: 'daily' | 'weekly' | 'monthly';
  type: 'leads' | 'revenue' | 'jobs' | 'exports';
  deadline: string;
  completed: boolean;
}

interface FunnelData {
  stage: string;
  count: number;
  conversionRate: number;
  color: string;
}

const EnhancedAnalytics: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [funnelData, setFunnelData] = useState<FunnelData[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState('30');
  const [showGoalModal, setShowGoalModal] = useState(false);
  const [newGoal, setNewGoal] = useState({
    name: '',
    target: 0,
    period: 'monthly' as const,
    type: 'leads' as const,
    deadline: ''
  });

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Remove mock data useEffect and replace with real API call
  useEffect(() => {
    async function fetchAnalytics() {
      try {
        const analytics = await api.getAnalytics(selectedPeriod);
        setAnalyticsData(analytics.data || []);
        // TODO: Replace with real API calls for goals and funnel data if available
        // setGoals(await api.getGoals());
        // setFunnelData(await api.getFunnelData());
      } catch (e) {
        setAnalyticsData([]);
        // Optionally show error toast
      }
    }
    fetchAnalytics();
  }, [selectedPeriod]);

  const currentMonth = analyticsData[analyticsData.length - 1];
  const previousMonth = analyticsData[analyticsData.length - 2];

  const calculateGrowth = (current: number, previous: number) => {
    if (previous === 0) return 100;
    return ((current - previous) / previous) * 100;
  };

  const handleAddGoal = () => {
    const goal: Goal = {
      id: Date.now().toString(),
      name: newGoal.name,
      target: newGoal.target,
      current: 0,
      period: newGoal.period,
      type: newGoal.type,
      deadline: newGoal.deadline,
      completed: false
    };

    setGoals([...goals, goal]);
    setNewGoal({ name: '', target: 0, period: 'monthly', type: 'leads', deadline: '' });
    setShowGoalModal(false);
  };

  const getGoalProgress = (goal: Goal) => {
    return Math.min((goal.current / goal.target) * 100, 100);
  };

  const getGoalColor = (goal: Goal) => {
    const progress = getGoalProgress(goal);
    if (progress >= 100) return 'green';
    if (progress >= 75) return 'blue';
    if (progress >= 50) return 'yellow';
    return 'red';
  };

  return (
    <div>
      {/* Header with Period Selector */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
        <div>
          <span className="text-2xl font-bold block">Analytics Dashboard</span>
          <span className="text-gray-600 block">Track your lead generation performance</span>
        </div>
        <div className="flex items-center gap-4">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="rounded-md border border-gray-300 p-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary w-32"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="365">Last year</option>
          </select>
          <button
            className="inline-flex items-center px-3 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-sm"
          >
            <span className="mr-2">⬇️</span>Export Report
          </button>
        </div>
      </div>
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Jobs Created */}
        <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <div className="text-gray-500 text-sm">Jobs Created</div>
          <div className="text-2xl font-bold">{currentMonth?.jobsCreated || 0}</div>
          <div className="flex items-center text-xs mt-1">
            <span className={currentMonth?.jobsCreated > previousMonth?.jobsCreated ? 'text-green-600' : 'text-red-600'}>
              {currentMonth?.jobsCreated > previousMonth?.jobsCreated ? '▲' : '▼'}
            </span>
            <span className="ml-1">
              {Math.abs(calculateGrowth(currentMonth?.jobsCreated || 0, previousMonth?.jobsCreated || 0)).toFixed(1)}%
            </span>
          </div>
        </div>
        {/* Leads Generated */}
        <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <div className="text-gray-500 text-sm">Leads Generated</div>
          <div className="text-2xl font-bold">{currentMonth?.leadsGenerated?.toLocaleString() || 0}</div>
          <div className="flex items-center text-xs mt-1">
            <span className={currentMonth?.leadsGenerated > previousMonth?.leadsGenerated ? 'text-green-600' : 'text-red-600'}>
              {currentMonth?.leadsGenerated > previousMonth?.leadsGenerated ? '▲' : '▼'}
            </span>
            <span className="ml-1">
              {Math.abs(calculateGrowth(currentMonth?.leadsGenerated || 0, previousMonth?.leadsGenerated || 0)).toFixed(1)}%
            </span>
          </div>
        </div>
        {/* Conversion Rate */}
        <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <div className="text-gray-500 text-sm">Conversion Rate</div>
          <div className="text-2xl font-bold">{(currentMonth?.conversionRate * 100).toFixed(1)}%</div>
          <div className="flex items-center text-xs mt-1">
            <span className={currentMonth?.conversionRate > previousMonth?.conversionRate ? 'text-green-600' : 'text-red-600'}>
              {currentMonth?.conversionRate > previousMonth?.conversionRate ? '▲' : '▼'}
            </span>
            <span className="ml-1">
              {Math.abs(calculateGrowth(currentMonth?.conversionRate || 0, previousMonth?.conversionRate || 0)).toFixed(1)}%
            </span>
          </div>
        </div>
        {/* Revenue */}
        <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <div className="text-gray-500 text-sm">Revenue</div>
          <div className="text-2xl font-bold">${currentMonth?.revenue?.toLocaleString() || 0}</div>
          <div className="flex items-center text-xs mt-1">
            <span className={currentMonth?.revenue > previousMonth?.revenue ? 'text-green-600' : 'text-red-600'}>
              {currentMonth?.revenue > previousMonth?.revenue ? '▲' : '▼'}
            </span>
            <span className="ml-1">
              {Math.abs(calculateGrowth(currentMonth?.revenue || 0, previousMonth?.revenue || 0)).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {/* Goals Section */}
      <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow mb-6">
        <div className="flex items-center justify-between mb-4">
          <span className="text-lg font-bold">Goals & Targets</span>
          <button
            className="inline-flex items-center px-3 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-sm"
            onClick={() => setShowGoalModal(true)}
          >
            Add Goal
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {goals.map((goal) => (
            <div key={goal.id} className="p-4 border rounded-md">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-sm">{goal.name}</span>
                <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${getGoalColor(goal) === 'green' ? 'bg-green-100 text-green-700' : getGoalColor(goal) === 'blue' ? 'bg-blue-100 text-blue-700' : getGoalColor(goal) === 'yellow' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>{getGoalProgress(goal).toFixed(0)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2">
                <div className={`${getGoalColor(goal) === 'green' ? 'bg-green-600' : getGoalColor(goal) === 'blue' ? 'bg-blue-600' : getGoalColor(goal) === 'yellow' ? 'bg-yellow-500' : 'bg-red-600'} h-2.5 rounded-full transition-all`} style={{ width: `${getGoalProgress(goal)}%` }} />
              </div>
              <span className="text-sm text-gray-600 block">{goal.current.toLocaleString()} / {goal.target.toLocaleString()} {goal.type}</span>
              <span className="text-xs text-gray-500 block">Due: {new Date(goal.deadline).toLocaleDateString()}</span>
            </div>
          ))}
        </div>
      </div>
      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Trend Chart */}
        <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <span className="text-lg font-bold mb-4 block">Performance Trends</span>
          <div className="w-full h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analyticsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="period" />
                <YAxis />
                <RechartsTooltip />
                <Legend />
                <Line type="monotone" dataKey="leadsGenerated" stroke="#3182CE" name="Leads" />
                <Line type="monotone" dataKey="revenue" stroke="#38A169" name="Revenue" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        {/* Funnel Chart */}
        <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <span className="text-lg font-bold mb-4 block">Conversion Funnel</span>
          <div className="w-full h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={funnelData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="stage" />
                <YAxis />
                <RechartsTooltip />
                <Bar dataKey="count" fill="#3182CE" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      {/* Funnel Details Table */}
      <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow mb-6">
        <span className="text-lg font-bold mb-4 block">Funnel Analysis</span>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm border-separate border-spacing-y-2">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-2 py-1 font-medium text-gray-700 text-left">Stage</th>
                <th className="px-2 py-1 font-medium text-gray-700 text-left">Count</th>
                <th className="px-2 py-1 font-medium text-gray-700 text-left">Conversion Rate</th>
                <th className="px-2 py-1 font-medium text-gray-700 text-left">Drop-off</th>
              </tr>
            </thead>
            <tbody>
              {funnelData.map((stage, index) => (
                <tr key={stage.stage} className="even:bg-gray-50">
                  <td className="px-2 py-1">
                    <div className="flex items-center space-x-2">
                      <span className="inline-block w-3 h-3 rounded-full" style={{ backgroundColor: stage.color }} />
                      <span>{stage.stage}</span>
                    </div>
                  </td>
                  <td className="px-2 py-1">{stage.count.toLocaleString()}</td>
                  <td className="px-2 py-1">{stage.conversionRate.toFixed(1)}%</td>
                  <td className="px-2 py-1">
                    {index < funnelData.length - 1 
                      ? `${((1 - funnelData[index + 1].count / stage.count) * 100).toFixed(1)}%`
                      : '-'
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      {/* Insights & Recommendations */}
      <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow mb-6">
        <span className="text-lg font-bold mb-4 block">Insights & Recommendations</span>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start p-4 bg-green-50 border border-green-200 rounded-md">
            <span className="text-green-500 mr-2">✔️</span>
            <div>
              <span className="font-semibold block">Strong Performance</span>
              <span className="text-sm text-gray-700 dark:text-gray-300 block">Your conversion rate is 20% above industry average. Keep up the great work!</span>
            </div>
          </div>
          <div className="flex items-start p-4 bg-blue-50 border border-blue-200 rounded-md">
            <span className="text-blue-500 mr-2">ℹ️</span>
            <div>
              <span className="font-semibold block">Optimization Opportunity</span>
              <span className="text-sm text-gray-700 dark:text-gray-300 block">Consider adding more specific queries to improve lead quality and conversion rates.</span>
            </div>
          </div>
          <div className="flex items-start p-4 bg-yellow-50 border border-yellow-200 rounded-md">
            <span className="text-yellow-500 mr-2">⚠️</span>
            <div>
              <span className="font-semibold block">Goal Alert</span>
              <span className="text-sm text-gray-700 dark:text-gray-300 block">You're 15% behind your monthly lead generation goal. Consider increasing your daily query volume.</span>
            </div>
          </div>
          <div className="flex items-start p-4 bg-blue-50 border border-blue-200 rounded-md">
            <span className="text-blue-500 mr-2">ℹ️</span>
            <div>
              <span className="font-semibold block">Feature Suggestion</span>
              <span className="text-sm text-gray-700 dark:text-gray-300 block">Upgrade to Pro plan to access advanced analytics and team collaboration features.</span>
            </div>
          </div>
        </div>
      </div>
      {/* Add Goal Modal */}
      {showGoalModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg w-full max-w-md mx-4 animate-fade-in">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <span className="text-lg font-bold">Add New Goal</span>
              <button onClick={() => setShowGoalModal(false)} className="text-gray-400 hover:text-gray-600">&times;</button>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Goal Name</label>
                <input
                  value={newGoal.name}
                  onChange={(e) => setNewGoal({ ...newGoal, name: e.target.value })}
                  placeholder="e.g., Generate 1000 leads this month"
                  className="w-full rounded-md border border-gray-300 p-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Target Value</label>
                <input
                  type="number"
                  value={newGoal.target}
                  onChange={(e) => setNewGoal({ ...newGoal, target: Number(e.target.value) })}
                  placeholder="1000"
                  className="w-full rounded-md border border-gray-300 p-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Goal Type</label>
                <select
                  value={newGoal.type}
                  onChange={(e) => setNewGoal({ ...newGoal, type: e.target.value as any })}
                  className="w-full rounded-md border border-gray-300 p-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary"
                >
                  <option value="leads">Leads Generated</option>
                  <option value="revenue">Revenue</option>
                  <option value="jobs">Jobs Created</option>
                  <option value="exports">Exports Completed</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Period</label>
                <select
                  value={newGoal.period}
                  onChange={(e) => setNewGoal({ ...newGoal, period: e.target.value as any })}
                  className="w-full rounded-md border border-gray-300 p-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Deadline</label>
                <input
                  type="date"
                  value={newGoal.deadline}
                  onChange={(e) => setNewGoal({ ...newGoal, deadline: e.target.value })}
                  className="w-full rounded-md border border-gray-300 p-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary"
                />
              </div>
            </div>
            <div className="flex items-center justify-end px-6 py-4 border-t border-gray-200 dark:border-gray-700 space-x-2">
              <button onClick={() => setShowGoalModal(false)} className="inline-flex items-center px-4 py-2 rounded-md bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-200 font-medium">
                Cancel
              </button>
              <button onClick={handleAddGoal} className="inline-flex items-center px-4 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
                Add Goal
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedAnalytics; 