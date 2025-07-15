import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Button,
  Badge,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  Input,
  FormControl,
  FormLabel,
  Select,
  InputGroup,
  InputLeftElement,
  Icon,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  useColorMode,
  useColorModeValue,
} from '@chakra-ui/react';
import * as api from '../api';
import { SearchIcon, ChevronDownIcon, DownloadIcon } from '@chakra-ui/icons';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from 'recharts';
import { useTranslation } from 'react-i18next';

interface User {
  id: number;
  email: string;
  plan: string;
  created_at: string;
  queries_today: number;
  last_query_date: string;
}

interface Job {
  id: number;
  queries: string;
  status: string;
  result: string | null;
  csv_path: string | null;
  user_id: number;
  user_email: string | null;
  created_at: string;
  updated_at: string;
}

interface AdminStats {
  user_count: number;
  job_count: number;
  active_users_today: number;
}

interface LogEntry {
  timestamp: string;
  message: string;
  level: string;
}

interface AuditLog {
  id: number;
  admin_email: string;
  action: string;
  target_type: string;
  target_id: number | null;
  target_email: string | null;
  details: any;
  created_at: string;
}

interface AnalyticsData {
  userGrowth: any;
  jobTrends: any;
  planDistribution: any;
  activeUsers: any;
}

const AdminDashboard: React.FC = () => {
  const { t } = useTranslation();
  const [users, setUsers] = useState<User[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [newPassword, setNewPassword] = useState('');
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  // User table pagination/filter state
  const [userPage, setUserPage] = useState(1);
  const [userPageSize, setUserPageSize] = useState(20);
  const [userEmailFilter, setUserEmailFilter] = useState('');
  const [userPlanFilter, setUserPlanFilter] = useState('');
  const [userTotal, setUserTotal] = useState(0);
  // Job table pagination/filter state
  const [jobPage, setJobPage] = useState(1);
  const [jobPageSize, setJobPageSize] = useState(20);
  const [jobUserEmailFilter, setJobUserEmailFilter] = useState('');
  const [jobStatusFilter, setJobStatusFilter] = useState('');
  const [jobTotal, setJobTotal] = useState(0);
  const [userTableLoading, setUserTableLoading] = useState(false);
  const [jobTableLoading, setJobTableLoading] = useState(false);
  const [banDialogUser, setBanDialogUser] = useState<User | null>(null);
  const [resetDialogUser, setResetDialogUser] = useState<User | null>(null);
  const [isBanDialogOpen, setIsBanDialogOpen] = useState(false);
  const [isResetDialogOpen, setIsResetDialogOpen] = useState(false);
  const banDialogCancelRef = useRef<HTMLButtonElement>(null);
  const resetDialogCancelRef = useRef<HTMLButtonElement>(null);
  // Audit logs pagination/filter state
  const [auditPage, setAuditPage] = useState(1);
  const [auditPageSize, setAuditPageSize] = useState(20);
  const [auditActionFilter, setAuditActionFilter] = useState('');
  const [auditAdminEmailFilter, setAuditAdminEmailFilter] = useState('');
  const [auditTargetTypeFilter, setAuditTargetTypeFilter] = useState('');
  const [auditTotal, setAuditTotal] = useState(0);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [auditTableLoading, setAuditTableLoading] = useState(false);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [analyticsPeriod, setAnalyticsPeriod] = useState(30);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [systemPerformance, setSystemPerformance] = useState<any>(null);
  const [systemLoading, setSystemLoading] = useState(false);
  const { colorMode, toggleColorMode } = useColorMode();
  const [dashboardLayout, setDashboardLayout] = useState('default');
  const [showAdvancedCharts, setShowAdvancedCharts] = useState(true);

  useEffect(() => {
    fetchData();
    // Initialize WebSocket connection
    const token = localStorage.getItem('token');
    if (token) {
      const ws = api.createWebSocketConnection(token);
      setWsConnection(ws);
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'notification') {
          const notification = JSON.parse(data.data);
          setNotifications(prev => [notification, ...prev.slice(0, 9)]); // Keep last 10
          
          // Show toast notification
          toast({
            title: notification.type === 'system' ? 'System Update' : 'Notification',
            description: notification.message,
            status: 'info',
            duration: 5000,
            isClosable: true,
            position: 'top-right',
          });
          
          // Refresh dashboard data
          fetchData();
          fetchAnalytics();
        }
      };
    }

    return () => {
      if (wsConnection) {
        wsConnection.close();
      }
    };
  }, []);

  useEffect(() => {
    fetchSystemHealth();
    const interval = setInterval(fetchSystemHealth, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [usersData, jobsData, statsData, logsData] = await Promise.all([
        api.adminGetUsers(),
        api.adminGetJobs(),
        api.adminGetStats(),
        api.adminGetLogs(),
      ]);
      setUsers(usersData.results || []);
      setJobs(jobsData.results || []);
      setStats(statsData);
      setLogs(logsData.logs || []);
      setError(null);
    } catch (err: any) {
      setError(err.message);
      toast({
        title: 'Error fetching data',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleBanUser = async (userId: number) => {
    try {
      await api.adminBanUser(userId);
      setUsers(users.map(user => 
        user.id === userId ? { ...user, plan: 'banned' } : user
      ));
      toast({
        title: 'User banned',
        description: 'User has been banned successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (err: any) {
      toast({
        title: 'Error banning user',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleUnbanUser = async (userId: number) => {
    try {
      await api.adminUnbanUser(userId);
      setUsers(users.map(user => 
        user.id === userId ? { ...user, plan: 'free' } : user
      ));
      toast({
        title: 'User unbanned',
        description: 'User has been unbanned successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (err: any) {
      toast({
        title: 'Error unbanning user',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleResetPassword = async () => {
    if (!selectedUser || !newPassword.trim()) return;
    
    try {
      await api.adminResetPassword(selectedUser.id, newPassword);
      toast({
        title: 'Password reset',
        description: 'User password has been reset successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      onClose();
      setNewPassword('');
      setSelectedUser(null);
    } catch (err: any) {
      toast({
        title: 'Error resetting password',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const openResetPasswordModal = (user: User) => {
    setSelectedUser(user);
    setNewPassword('');
    onOpen();
  };

  const getPlanColor = (plan: string) => {
    switch (plan.toLowerCase()) {
      case 'free': return 'gray';
      case 'basic': return 'blue';
      case 'premium': return 'purple';
      case 'enterprise': return 'green';
      default: return 'gray';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Fetch users/jobs with filters/pagination
  useEffect(() => {
    fetchUsers();
  }, [userPage, userPageSize, userEmailFilter, userPlanFilter]);
  useEffect(() => {
    fetchJobs();
  }, [jobPage, jobPageSize, jobUserEmailFilter, jobStatusFilter]);

  const fetchUsers = async () => {
    try {
      setUserTableLoading(true);
      const data = await api.adminGetUsers({
        page: userPage,
        pageSize: userPageSize,
        email: userEmailFilter,
        plan: userPlanFilter,
      });
      setUsers(data.results);
      setUserTotal(data.total);
      setError(null);
    } catch (err: any) {
      setError(err.message);
      setUsers([]);
    } finally {
      setUserTableLoading(false);
    }
  };

  const fetchJobs = async () => {
    try {
      setJobTableLoading(true);
      const data = await api.adminGetJobs({
        page: jobPage,
        pageSize: jobPageSize,
        userEmail: jobUserEmailFilter,
        status: jobStatusFilter,
      });
      setJobs(data.results);
      setJobTotal(data.total);
      setError(null);
    } catch (err: any) {
      setError(err.message);
      setJobs([]);
    } finally {
      setJobTableLoading(false);
    }
  };

  const openBanDialog = (user: User) => {
    setBanDialogUser(user);
    setIsBanDialogOpen(true);
  };

  const openUnbanDialog = (user: User) => {
    setBanDialogUser(user);
    setIsBanDialogOpen(true);
  };

  const openResetDialog = (user: User) => {
    setResetDialogUser(user);
    setIsResetDialogOpen(true);
  };

  const confirmBan = () => {
    if (banDialogUser) {
      if (banDialogUser.plan === 'banned') {
        handleUnbanUser(banDialogUser.id);
      } else {
        handleBanUser(banDialogUser.id);
      }
    }
    setIsBanDialogOpen(false);
    setBanDialogUser(null);
  };

  const confirmReset = () => {
    if (resetDialogUser && newPassword.trim()) {
      handleResetPassword();
    }
    setIsResetDialogOpen(false);
    setResetDialogUser(null);
  };

  useEffect(() => {
    fetchAuditLogs();
  }, [auditPage, auditPageSize, auditActionFilter, auditAdminEmailFilter, auditTargetTypeFilter]);

  const fetchAuditLogs = async () => {
    try {
      setAuditTableLoading(true);
      const data = await api.adminGetAuditLogs({
        page: auditPage,
        pageSize: auditPageSize,
        action: auditActionFilter,
        adminEmail: auditAdminEmailFilter,
        targetType: auditTargetTypeFilter,
      });
      setAuditLogs(data.results);
      setAuditTotal(data.total);
      setError(null);
    } catch (err: any) {
      setError(err.message);
      setAuditLogs([]);
    } finally {
      setAuditTableLoading(false);
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'ban_user': return 'red';
      case 'unban_user': return 'green';
      case 'reset_password': return 'blue';
      default: return 'gray';
    }
  };

  const formatAuditDetails = (details: any) => {
    if (!details) return 'No details';
    if (typeof details === 'object') {
      return Object.entries(details)
        .map(([key, value]) => `${key}: ${value}`)
        .join(', ');
    }
    return String(details);
  };

  useEffect(() => {
    fetchAnalytics();
  }, [analyticsPeriod]);

  const fetchAnalytics = async () => {
    try {
      setAnalyticsLoading(true);
      const [userGrowth, jobTrends, planDistribution, activeUsers] = await Promise.all([
        api.adminGetUserGrowth(analyticsPeriod),
        api.adminGetJobTrends(analyticsPeriod),
        api.adminGetPlanDistribution(),
        api.adminGetActiveUsers(Math.min(analyticsPeriod, 7)),
      ]);
      setAnalyticsData({
        userGrowth,
        jobTrends,
        planDistribution,
        activeUsers,
      });
    } catch (err: any) {
      console.error('Error fetching analytics:', err);
    } finally {
      setAnalyticsLoading(false);
    }
  };

  const renderUserGrowthChart = () => {
    if (!analyticsData?.userGrowth?.data) return null;
    
    const data = analyticsData.userGrowth.data.slice(-analyticsPeriod);
    
    return (
      <Box bg="dark.700" p={4} borderRadius="md" h="300px">
        <Text color="gray.300" fontSize="sm" mb={3}>User Growth Trend</Text>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="date" 
              stroke="#9CA3AF"
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => new Date(value).toLocaleDateString()}
            />
            <YAxis stroke="#9CA3AF" tick={{ fontSize: 12 }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1F2937', 
                border: '1px solid #374151',
                borderRadius: '8px'
              }}
              labelStyle={{ color: '#9CA3AF' }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="new_users" 
              stroke="#10B981" 
              strokeWidth={2}
              name="New Users"
            />
            <Line 
              type="monotone" 
              dataKey="total_users" 
              stroke="#3B82F6" 
              strokeWidth={2}
              name="Total Users"
            />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    );
  };

  const renderJobTrendsChart = () => {
    if (!analyticsData?.jobTrends?.data) return null;
    
    const data = analyticsData.jobTrends.data.slice(-analyticsPeriod);
    
    return (
      <Box bg="dark.700" p={4} borderRadius="md" h="300px">
        <Text color="gray.300" fontSize="sm" mb={3}>Job Trends</Text>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="date" 
              stroke="#9CA3AF"
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => new Date(value).toLocaleDateString()}
            />
            <YAxis stroke="#9CA3AF" tick={{ fontSize: 12 }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1F2937', 
                border: '1px solid #374151',
                borderRadius: '8px'
              }}
              labelStyle={{ color: '#9CA3AF' }}
            />
            <Legend />
            <Area 
              type="monotone" 
              dataKey="completed" 
              stackId="1"
              stroke="#10B981" 
              fill="#10B981" 
              fillOpacity={0.6}
              name="Completed"
            />
            <Area 
              type="monotone" 
              dataKey="pending" 
              stackId="1"
              stroke="#F59E0B" 
              fill="#F59E0B" 
              fillOpacity={0.6}
              name="Pending"
            />
            <Area 
              type="monotone" 
              dataKey="failed" 
              stackId="1"
              stroke="#EF4444" 
              fill="#EF4444" 
              fillOpacity={0.6}
              name="Failed"
            />
          </AreaChart>
        </ResponsiveContainer>
      </Box>
    );
  };

  const renderPlanDistribution = () => {
    if (!analyticsData?.planDistribution?.plans) return null;
    
    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];
    
    return (
      <Box bg="dark.700" p={4} borderRadius="md" h="300px">
        <Text color="gray.300" fontSize="sm" mb={3}>Plan Distribution</Text>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={analyticsData.planDistribution.plans}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="count"
            >
              {analyticsData.planDistribution.plans.map((entry: any, index: number) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1F2937', 
                border: '1px solid #374151',
                borderRadius: '8px'
              }}
              labelStyle={{ color: '#9CA3AF' }}
            />
          </PieChart>
        </ResponsiveContainer>
      </Box>
    );
  };

  const renderActiveUsersChart = () => {
    if (!analyticsData?.activeUsers?.data) return null;
    
    const data = analyticsData.activeUsers.data;
    
    return (
      <Box bg="dark.700" p={4} borderRadius="md" h="300px">
        <Text color="gray.300" fontSize="sm" mb={3}>Active Users</Text>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="date" 
              stroke="#9CA3AF"
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => new Date(value).toLocaleDateString()}
            />
            <YAxis stroke="#9CA3AF" tick={{ fontSize: 12 }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1F2937', 
                border: '1px solid #374151',
                borderRadius: '8px'
              }}
              labelStyle={{ color: '#9CA3AF' }}
            />
            <Bar dataKey="active_users" fill="#3B82F6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Box>
    );
  };

  const testNotification = async () => {
    try {
      await api.testNotification();
      toast({
        title: 'Test Notification Sent',
        description: 'Check the notification stream',
        status: 'success',
        duration: 3000,
      });
    } catch (err: any) {
      toast({
        title: 'Error',
        description: err.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  const fetchSystemHealth = async () => {
    try {
      setSystemLoading(true);
      const [health, performance] = await Promise.all([
        api.getSystemHealth(),
        api.getSystemPerformance()
      ]);
      setSystemHealth(health);
      setSystemPerformance(performance);
    } catch (err: any) {
      console.error('Error fetching system health:', err);
    } finally {
      setSystemLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'green';
      case 'slow': return 'yellow';
      case 'error': return 'red';
      default: return 'gray';
    }
  };

  const renderSystemHealth = () => {
    if (!systemHealth) return null;
    
    return (
      <Box bg="dark.800" p={6} borderRadius="lg" mb={6}>
        <HStack justify="space-between" mb={6}>
          <Heading size="md">System Health</Heading>
          <Button
            size="sm"
            onClick={fetchSystemHealth}
            colorScheme="brand"
            variant="outline"
            isLoading={systemLoading}
          >
            Refresh
          </Button>
        </HStack>
        
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mb={6}>
          <Box bg="dark.700" p={4} borderRadius="md">
            <Text color="gray.400" fontSize="sm">CPU Usage</Text>
            <Text fontSize="2xl" fontWeight="bold" color="brand.400">
              {systemHealth.system?.cpu_percent || 0}%
            </Text>
          </Box>
          <Box bg="dark.700" p={4} borderRadius="md">
            <Text color="gray.400" fontSize="sm">Memory Usage</Text>
            <Text fontSize="2xl" fontWeight="bold" color="brand.400">
              {systemHealth.system?.memory_percent || 0}%
            </Text>
          </Box>
          <Box bg="dark.700" p={4} borderRadius="md">
            <Text color="gray.400" fontSize="sm">Database</Text>
            <HStack>
              <Text fontSize="2xl" fontWeight="bold" color={getStatusColor(systemHealth.database?.status)}>
                {systemHealth.database?.response_time_ms || 0}ms
              </Text>
              <Badge colorScheme={getStatusColor(systemHealth.database?.status)}>
                {systemHealth.database?.status || 'unknown'}
              </Badge>
            </HStack>
          </Box>
          <Box bg="dark.700" p={4} borderRadius="md">
            <Text color="gray.400" fontSize="sm">API Response</Text>
            <HStack>
              <Text fontSize="2xl" fontWeight="bold" color={getStatusColor(systemHealth.api?.status)}>
                {systemHealth.api?.response_time_ms || 0}ms
              </Text>
              <Badge colorScheme={getStatusColor(systemHealth.api?.status)}>
                {systemHealth.api?.status || 'unknown'}
              </Badge>
            </HStack>
          </Box>
        </SimpleGrid>
        
        {systemPerformance && (
          <Box bg="dark.700" p={4} borderRadius="md" h="300px">
            <Text color="gray.300" fontSize="sm" mb={3}>Performance Over Time</Text>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={systemPerformance.data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="timestamp" 
                  stroke="#9CA3AF"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                />
                <YAxis stroke="#9CA3AF" tick={{ fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px'
                  }}
                  labelStyle={{ color: '#9CA3AF' }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="cpu_percent" 
                  stroke="#EF4444" 
                  strokeWidth={2}
                  name="CPU %"
                />
                <Line 
                  type="monotone" 
                  dataKey="memory_percent" 
                  stroke="#3B82F6" 
                  strokeWidth={2}
                  name="Memory %"
                />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        )}
      </Box>
    );
  };

  const exportDashboardAsPDF = () => {
    // In a real implementation, you'd use a library like jsPDF or html2pdf
    // For now, we'll create a simple export
    const dashboardData = {
      timestamp: new Date().toISOString(),
      stats: stats,
      analytics: analyticsData,
      systemHealth: systemHealth,
      users: users || [],
      jobs: jobs || [],
    };
    
    const dataStr = JSON.stringify(dashboardData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `admin-dashboard-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: 'Dashboard Exported',
      description: 'Dashboard data has been exported successfully',
      status: 'success',
      duration: 3000,
    });
  };

  const toggleLayout = () => {
    setDashboardLayout(prev => prev === 'default' ? 'compact' : 'default');
  };

  if (loading) {
    return (
      <Box p={8} textAlign="center">
        <Spinner size="xl" />
        <Text mt={4}>Loading admin dashboard...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={8}>
        <Alert status="error">
          <AlertIcon />
          <AlertTitle>Error!</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={8} maxW="1400px" mx="auto">
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>Admin Dashboard</Heading>
          <Text color="gray.400">Manage users, monitor jobs, and view site statistics</Text>
        </Box>

        {/* Stats Cards */}
        {stats && (
          <HStack spacing={6} wrap="wrap">
            <Box bg="dark.800" p={6} borderRadius="lg" flex="1" minW="200px">
              <Text color="gray.400" fontSize="sm">Total Users</Text>
              <Text fontSize="2xl" fontWeight="bold" color="brand.400">{stats.user_count}</Text>
            </Box>
            <Box bg="dark.800" p={6} borderRadius="lg" flex="1" minW="200px">
              <Text color="gray.400" fontSize="sm">Total Jobs</Text>
              <Text fontSize="2xl" fontWeight="bold" color="brand.400">{stats.job_count}</Text>
            </Box>
            <Box bg="dark.800" p={6} borderRadius="lg" flex="1" minW="200px">
              <Text color="gray.400" fontSize="sm">Active Users Today</Text>
              <Text fontSize="2xl" fontWeight="bold" color="brand.400">{stats.active_users_today}</Text>
            </Box>
          </HStack>
        )}

        {/* Analytics Dashboard */}
        <Box bg="dark.800" p={6} borderRadius="lg">
          <HStack justify="space-between" mb={6}>
            <Heading size="md">Analytics Dashboard</Heading>
            <HStack spacing={2}>
              <Select
                value={analyticsPeriod}
                onChange={(e) => setAnalyticsPeriod(Number(e.target.value))}
                size="sm"
                maxW="150px"
                bg="dark.700"
                color="gray.200"
              >
                <option value={7}>Last 7 days</option>
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
              </Select>
              <Button
                size="sm"
                onClick={fetchAnalytics}
                colorScheme="brand"
                variant="outline"
                isLoading={analyticsLoading}
              >
                Refresh
              </Button>
            </HStack>
          </HStack>
          
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
            {renderUserGrowthChart()}
            {renderJobTrendsChart()}
            {renderPlanDistribution()}
            {renderActiveUsersChart()}
          </SimpleGrid>
        </Box>

        {/* User Management */}
        <Box bg="dark.800" p={6} borderRadius="lg">
          <HStack justify="space-between" mb={6}>
            <Heading size="md">User Management</Heading>
            <HStack spacing={2}>
              <Menu>
                <MenuButton
                  as={Button}
                  rightIcon={<ChevronDownIcon />}
                  leftIcon={<DownloadIcon />}
                  size="sm"
                  colorScheme="green"
                  variant="outline"
                >
                  Export
                </MenuButton>
                <MenuList bg="dark.700" border="1px solid" borderColor="gray.600">
                  <MenuItem
                    onClick={() => window.open(api.adminExportUsers('csv', { email: userEmailFilter, plan: userPlanFilter }), '_blank')}
                    bg="transparent"
                    _hover={{ bg: 'rgba(255, 255, 255, 0.1)' }}
                    color="gray.300"
                  >
                    Export as CSV
                  </MenuItem>
                  <MenuItem
                    onClick={() => window.open(api.adminExportUsers('json', { email: userEmailFilter, plan: userPlanFilter }), '_blank')}
                    bg="transparent"
                    _hover={{ bg: 'rgba(255, 255, 255, 0.1)' }}
                    color="gray.300"
                  >
                    Export as JSON
                  </MenuItem>
                </MenuList>
              </Menu>
              <Button
                size="sm"
                onClick={fetchUsers}
                colorScheme="brand"
                variant="outline"
                isLoading={userTableLoading}
              >
                Refresh
              </Button>
            </HStack>
          </HStack>
          <HStack mb={4} spacing={4}>
            <InputGroup maxW="250px">
              <InputLeftElement pointerEvents="none">
                <Icon as={SearchIcon} color="gray.400" />
              </InputLeftElement>
              <Input
                placeholder="Search email..."
                value={userEmailFilter}
                onChange={e => { setUserEmailFilter(e.target.value); setUserPage(1); }}
                size="sm"
                bg="dark.700"
                color="gray.200"
              />
            </InputGroup>
            <Select
              placeholder="All plans"
              value={userPlanFilter}
              onChange={e => { setUserPlanFilter(e.target.value); setUserPage(1); }}
              size="sm"
              maxW="150px"
              bg="dark.700"
              color="gray.200"
            >
              <option value="free">Free</option>
              <option value="pro">Pro</option>
              <option value="business">Business</option>
              <option value="banned">Banned</option>
            </Select>
            <Select
              value={userPageSize}
              onChange={e => { setUserPageSize(Number(e.target.value)); setUserPage(1); }}
              size="sm"
              maxW="100px"
              bg="dark.700"
              color="gray.200"
            >
              {[10, 20, 50, 100].map(size => (
                <option key={size} value={size}>{size} / page</option>
              ))}
            </Select>
            <Text color="gray.400" fontSize="sm">Total: {userTotal}</Text>
          </HStack>
          <Box overflowX="auto" position="relative">
            {userTableLoading && (
              <Box
                position="absolute"
                top={0}
                left={0}
                right={0}
                bottom={0}
                bg="rgba(0,0,0,0.7)"
                display="flex"
                alignItems="center"
                justifyContent="center"
                zIndex={1}
                borderRadius="md"
              >
                <Spinner size="lg" />
              </Box>
            )}
            <Table variant="simple" size="sm">
              <Thead>
                <Tr>
                  <Th color="gray.400">ID</Th>
                  <Th color="gray.400">Email</Th>
                  <Th color="gray.400">Plan</Th>
                  <Th color="gray.400">Created</Th>
                  <Th color="gray.400">Queries Today</Th>
                  <Th color="gray.400">Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {users.map((user) => (
                  <Tr key={user.id}>
                    <Td color="gray.300">{user.id}</Td>
                    <Td color="gray.300">{user.email}</Td>
                    <Td>
                      <Badge colorScheme={getPlanColor(user.plan)}>
                        {user.plan}
                      </Badge>
                    </Td>
                    <Td color="gray.300">{formatDate(user.created_at)}</Td>
                    <Td color="gray.300">{user.queries_today}</Td>
                    <Td>
                      <HStack spacing={2}>
                        {user.plan === 'banned' ? (
                          <Button
                            size="xs"
                            colorScheme="green"
                            onClick={() => openUnbanDialog(user)}
                          >
                            Unban
                          </Button>
                        ) : (
                          <Button
                            size="xs"
                            colorScheme="red"
                            onClick={() => openBanDialog(user)}
                          >
                            Ban
                          </Button>
                        )}
                        <Button
                          size="xs"
                          colorScheme="blue"
                          onClick={() => openResetDialog(user)}
                        >
                          Reset Password
                        </Button>
                      </HStack>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
          <HStack mt={4} justify="flex-end">
            <Button size="sm" onClick={() => setUserPage(1)} isDisabled={userPage === 1}>First</Button>
            <Button size="sm" onClick={() => setUserPage(p => Math.max(1, p-1))} isDisabled={userPage === 1}>Prev</Button>
            <Text color="gray.400" fontSize="sm">
              Page {userPage} of {Math.ceil(userTotal / userPageSize)}
            </Text>
            <Button size="sm" onClick={() => setUserPage(p => p+1)} isDisabled={userPage * userPageSize >= userTotal}>Next</Button>
            <Button size="sm" onClick={() => setUserPage(Math.ceil(userTotal / userPageSize))} isDisabled={userPage * userPageSize >= userTotal}>Last</Button>
          </HStack>
        </Box>

        {/* Job Monitoring */}
        <Box bg="dark.800" p={6} borderRadius="lg">
          <HStack justify="space-between" mb={6}>
            <Heading size="md">Job Monitoring</Heading>
            <HStack spacing={2}>
              <Menu>
                <MenuButton
                  as={Button}
                  rightIcon={<ChevronDownIcon />}
                  leftIcon={<DownloadIcon />}
                  size="sm"
                  colorScheme="green"
                  variant="outline"
                >
                  Export
                </MenuButton>
                <MenuList bg="dark.700" border="1px solid" borderColor="gray.600">
                  <MenuItem
                    onClick={() => window.open(api.adminExportJobs('csv', { userEmail: jobUserEmailFilter, status: jobStatusFilter }), '_blank')}
                    bg="transparent"
                    _hover={{ bg: 'rgba(255, 255, 255, 0.1)' }}
                    color="gray.300"
                  >
                    Export as CSV
                  </MenuItem>
                  <MenuItem
                    onClick={() => window.open(api.adminExportJobs('json', { userEmail: jobUserEmailFilter, status: jobStatusFilter }), '_blank')}
                    bg="transparent"
                    _hover={{ bg: 'rgba(255, 255, 255, 0.1)' }}
                    color="gray.300"
                  >
                    Export as JSON
                  </MenuItem>
                </MenuList>
              </Menu>
              <Button
                size="sm"
                onClick={fetchJobs}
                colorScheme="brand"
                variant="outline"
                isLoading={jobTableLoading}
              >
                Refresh
              </Button>
            </HStack>
          </HStack>
          <HStack mb={4} spacing={4}>
            <InputGroup maxW="250px">
              <InputLeftElement pointerEvents="none">
                <Icon as={SearchIcon} color="gray.400" />
              </InputLeftElement>
              <Input
                placeholder="Search user email..."
                value={jobUserEmailFilter}
                onChange={e => { setJobUserEmailFilter(e.target.value); setJobPage(1); }}
                size="sm"
                bg="dark.700"
                color="gray.200"
              />
            </InputGroup>
            <Select
              placeholder="All statuses"
              value={jobStatusFilter}
              onChange={e => { setJobStatusFilter(e.target.value); setJobPage(1); }}
              size="sm"
              maxW="150px"
              bg="dark.700"
              color="gray.200"
            >
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </Select>
            <Select
              value={jobPageSize}
              onChange={e => { setJobPageSize(Number(e.target.value)); setJobPage(1); }}
              size="sm"
              maxW="100px"
              bg="dark.700"
              color="gray.200"
            >
              {[10, 20, 50, 100].map(size => (
                <option key={size} value={size}>{size} / page</option>
              ))}
            </Select>
            <Text color="gray.400" fontSize="sm">Total: {jobTotal}</Text>
          </HStack>
          <Box overflowX="auto" position="relative">
            {jobTableLoading && (
              <Box
                position="absolute"
                top={0}
                left={0}
                right={0}
                bottom={0}
                bg="rgba(0,0,0,0.7)"
                display="flex"
                alignItems="center"
                justifyContent="center"
                zIndex={1}
                borderRadius="md"
              >
                <Spinner size="lg" />
              </Box>
            )}
            <Table variant="simple" size="sm">
              <Thead>
                <Tr>
                  <Th color="gray.400">ID</Th>
                  <Th color="gray.400">User</Th>
                  <Th color="gray.400">Queries</Th>
                  <Th color="gray.400">Status</Th>
                  <Th color="gray.400">Created</Th>
                  <Th color="gray.400">Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {jobs.map((job) => (
                  <Tr key={job.id}>
                    <Td color="gray.300">{job.id}</Td>
                    <Td color="gray.300">{job.user_email || 'Unknown'}</Td>
                    <Td color="gray.300" maxW="200px">
                      <Text noOfLines={2} fontSize="xs">
                        {JSON.parse(job.queries).join(', ')}
                      </Text>
                    </Td>
                    <Td>
                      <Badge 
                        colorScheme={
                          job.status === 'completed' ? 'green' : 
                          job.status === 'failed' ? 'red' : 
                          job.status === 'pending' ? 'yellow' : 'gray'
                        }
                      >
                        {job.status}
                      </Badge>
                    </Td>
                    <Td color="gray.300">{formatDate(job.created_at)}</Td>
                    <Td>
                      <HStack spacing={2}>
                        {job.status === 'completed' && job.result && (
                          <Button
                            size="xs"
                            colorScheme="blue"
                            onClick={() => window.open(`/api/scrape/${job.id}/results`, '_blank')}
                          >
                            View Results
                          </Button>
                        )}
                        {job.status === 'completed' && job.csv_path && (
                          <Button
                            size="xs"
                            colorScheme="green"
                            onClick={() => window.open(`/api/scrape/${job.id}/csv`, '_blank')}
                          >
                            Download CSV
                          </Button>
                        )}
                      </HStack>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
          <HStack mt={4} justify="flex-end">
            <Button size="sm" onClick={() => setJobPage(1)} isDisabled={jobPage === 1}>First</Button>
            <Button size="sm" onClick={() => setJobPage(p => Math.max(1, p-1))} isDisabled={jobPage === 1}>Prev</Button>
            <Text color="gray.400" fontSize="sm">
              Page {jobPage} of {Math.ceil(jobTotal / jobPageSize)}
            </Text>
            <Button size="sm" onClick={() => setJobPage(p => p+1)} isDisabled={jobPage * jobPageSize >= jobTotal}>Next</Button>
            <Button size="sm" onClick={() => setJobPage(Math.ceil(jobTotal / jobPageSize))} isDisabled={jobPage * jobPageSize >= jobTotal}>Last</Button>
          </HStack>
        </Box>

        {/* System Logs */}
        <Box bg="dark.800" p={6} borderRadius="lg">
          <HStack justify="space-between" mb={6}>
            <Heading size="md">System Logs</Heading>
            <Button
              size="sm"
              onClick={fetchData}
              colorScheme="brand"
              variant="outline"
            >
              Refresh
            </Button>
          </HStack>

          <Box 
            bg="dark.700" 
            p={4} 
            borderRadius="md" 
            maxH="400px" 
            overflowY="auto"
            border="1px solid"
            borderColor="gray.600"
          >
            {logs.length === 0 ? (
              <Text color="gray.400" textAlign="center" py={8}>
                No logs available
              </Text>
            ) : (
              <VStack align="stretch" spacing={2}>
                {logs.map((log, index) => (
                  <Box 
                    key={index} 
                    p={3} 
                    bg="dark.600" 
                    borderRadius="md"
                    borderLeft="4px solid"
                    borderLeftColor={
                      log.toLowerCase().includes('error') ? 'red.500' :
                      log.toLowerCase().includes('warning') ? 'yellow.500' :
                      log.toLowerCase().includes('info') ? 'blue.500' : 'gray.500'
                    }
                  >
                    <Text 
                      color="gray.300" 
                      fontSize="sm" 
                      fontFamily="mono"
                      whiteSpace="pre-wrap"
                    >
                      {log}
                    </Text>
                  </Box>
                ))}
              </VStack>
            )}
          </Box>
        </Box>

        {/* Audit Logs */}
        <Box bg="dark.800" p={6} borderRadius="lg">
          <HStack justify="space-between" mb={6}>
            <Heading size="md">Audit Logs</Heading>
            <Button
              size="sm"
              onClick={fetchAuditLogs}
              colorScheme="brand"
              variant="outline"
              isLoading={auditTableLoading}
            >
              Refresh
            </Button>
          </HStack>
          <HStack mb={4} spacing={4}>
            <InputGroup maxW="200px">
              <InputLeftElement pointerEvents="none">
                <Icon as={SearchIcon} color="gray.400" />
              </InputLeftElement>
              <Input
                placeholder="Search admin email..."
                value={auditAdminEmailFilter}
                onChange={e => { setAuditAdminEmailFilter(e.target.value); setAuditPage(1); }}
                size="sm"
                bg="dark.700"
                color="gray.200"
              />
            </InputGroup>
            <Select
              placeholder="All actions"
              value={auditActionFilter}
              onChange={e => { setAuditActionFilter(e.target.value); setAuditPage(1); }}
              size="sm"
              maxW="150px"
              bg="dark.700"
              color="gray.200"
            >
              <option value="ban_user">Ban User</option>
              <option value="unban_user">Unban User</option>
              <option value="reset_password">Reset Password</option>
            </Select>
            <Select
              placeholder="All types"
              value={auditTargetTypeFilter}
              onChange={e => { setAuditTargetTypeFilter(e.target.value); setAuditPage(1); }}
              size="sm"
              maxW="120px"
              bg="dark.700"
              color="gray.200"
            >
              <option value="user">User</option>
              <option value="job">Job</option>
            </Select>
            <Select
              value={auditPageSize}
              onChange={e => { setAuditPageSize(Number(e.target.value)); setAuditPage(1); }}
              size="sm"
              maxW="100px"
              bg="dark.700"
              color="gray.200"
            >
              {[10, 20, 50, 100].map(size => (
                <option key={size} value={size}>{size} / page</option>
              ))}
            </Select>
            <Text color="gray.400" fontSize="sm">Total: {auditTotal}</Text>
          </HStack>
          <Box overflowX="auto" position="relative">
            {auditTableLoading && (
              <Box
                position="absolute"
                top={0}
                left={0}
                right={0}
                bottom={0}
                bg="rgba(0,0,0,0.7)"
                display="flex"
                alignItems="center"
                justifyContent="center"
                zIndex={1}
                borderRadius="md"
              >
                <Spinner size="lg" />
              </Box>
            )}
            <Table variant="simple" size="sm">
              <Thead>
                <Tr>
                  <Th color="gray.400">Admin</Th>
                  <Th color="gray.400">Action</Th>
                  <Th color="gray.400">Target</Th>
                  <Th color="gray.400">Details</Th>
                  <Th color="gray.400">Date</Th>
                </Tr>
              </Thead>
              <Tbody>
                {auditLogs.map((log) => (
                  <Tr key={log.id}>
                    <Td color="gray.300">{log.admin_email}</Td>
                    <Td>
                      <Badge colorScheme={getActionColor(log.action)}>
                        {log.action.replace('_', ' ')}
                      </Badge>
                    </Td>
                    <Td color="gray.300">
                      {log.target_email || `ID: ${log.target_id}`}
                    </Td>
                    <Td color="gray.300" maxW="200px">
                      <Text noOfLines={2} fontSize="xs">
                        {formatAuditDetails(log.details)}
                      </Text>
                    </Td>
                    <Td color="gray.300">{formatDate(log.created_at)}</Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
          <HStack mt={4} justify="flex-end">
            <Button size="sm" onClick={() => setAuditPage(1)} isDisabled={auditPage === 1}>First</Button>
            <Button size="sm" onClick={() => setAuditPage(p => Math.max(1, p-1))} isDisabled={auditPage === 1}>Prev</Button>
            <Text color="gray.400" fontSize="sm">
              Page {auditPage} of {Math.ceil(auditTotal / auditPageSize)}
            </Text>
            <Button size="sm" onClick={() => setAuditPage(p => p+1)} isDisabled={auditPage * auditPageSize >= auditTotal}>Next</Button>
            <Button size="sm" onClick={() => setAuditPage(Math.ceil(auditTotal / auditPageSize))} isDisabled={auditPage * auditPageSize >= auditTotal}>Last</Button>
          </HStack>
        </Box>

        {/* Real-time Notifications */}
        <Box bg="dark.800" p={6} borderRadius="lg" mb={6}>
          <HStack justify="space-between" mb={4}>
            <Heading size="md">Real-time Notifications</Heading>
            <Button size="sm" onClick={testNotification} colorScheme="brand">
              Test Notification
            </Button>
          </HStack>
          
          <VStack spacing={2} align="stretch" maxH="200px" overflowY="auto">
            {notifications.length === 0 ? (
              <Text color="gray.500" textAlign="center" py={4}>
                No notifications yet
              </Text>
            ) : (
              notifications.map((notification, index) => (
                <Box key={index} bg="dark.700" p={3} borderRadius="md">
                  <HStack justify="space-between">
                    <VStack align="start" spacing={1}>
                      <Text color="gray.300" fontSize="sm">
                        {notification.type === 'system' ? t('adminDashboard.system', '🔔 System') : t('adminDashboard.notification', '📢 Notification')}
                      </Text>
                      <Text color="gray.200" fontSize="xs">
                        {notification.message}
                      </Text>
                    </VStack>
                    <Text color="gray.500" fontSize="xs">
                      {new Date(notification.timestamp).toLocaleTimeString()}
                    </Text>
                  </HStack>
                </Box>
              ))
            )}
          </VStack>
        </Box>

        {/* System Health Monitoring */}
        {renderSystemHealth()}

        {/* Dashboard Controls */}
        <Box bg="dark.800" p={4} borderRadius="lg" mb={6}>
          <HStack justify="space-between" wrap="wrap" spacing={4}>
            <HStack spacing={4}>
              <Button
                size="sm"
                onClick={toggleColorMode}
                colorScheme="brand"
                variant="outline"
                leftIcon={colorMode === 'dark' ? <span>☀️</span> : <span>🌙</span>}
              >
                {colorMode === 'dark' ? t('adminDashboard.lightMode', 'Light') : t('adminDashboard.darkMode', 'Dark')} {t('adminDashboard.mode', 'Mode')}
              </Button>
              <Button
                size="sm"
                onClick={toggleLayout}
                colorScheme="brand"
                variant="outline"
              >
                {dashboardLayout === 'default' ? t('adminDashboard.compactLayout', 'Compact') : t('adminDashboard.defaultLayout', 'Default')} {t('adminDashboard.layout', 'Layout')}
              </Button>
              <Button
                size="sm"
                onClick={() => setShowAdvancedCharts(!showAdvancedCharts)}
                colorScheme="brand"
                variant="outline"
              >
                {showAdvancedCharts ? t('adminDashboard.simpleCharts', 'Simple') : t('adminDashboard.advancedCharts', 'Advanced')} {t('adminDashboard.charts', 'Charts')}
              </Button>
            </HStack>
            <Button
              size="sm"
              onClick={exportDashboardAsPDF}
              colorScheme="green"
              variant="outline"
              leftIcon={<span>📊</span>}
            >
              {t('adminDashboard.exportDashboard', 'Export Dashboard')}
            </Button>
          </HStack>
        </Box>
      </VStack>

      {/* Reset Password Modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent bg="dark.800" border="1px solid" borderColor="gray.600">
          <ModalHeader color="gray.300">{t('adminDashboard.resetPassword', 'Reset Password')}</ModalHeader>
          <ModalCloseButton color="gray.400" />
          <ModalBody>
            <Text color="gray.400" mb={4}>
              {t('adminDashboard.resetPasswordForUser', 'Reset password for user:')} <strong>{selectedUser?.email}</strong>
            </Text>
            <FormControl>
              <FormLabel color="gray.400">{t('adminDashboard.newPassword', 'New Password')}</FormLabel>
              <Input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder={t('adminDashboard.enterNewPassword', 'Enter new password')}
                bg="dark.700"
                borderColor="gray.600"
                color="gray.300"
                _placeholder={{ color: 'gray.500' }}
              />
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose} color="gray.400">
              {t('adminDashboard.cancel', 'Cancel')}
            </Button>
            <Button
              colorScheme="blue"
              onClick={handleResetPassword}
              isDisabled={!newPassword.trim()}
            >
              {t('adminDashboard.resetPassword', 'Reset Password')}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Ban/Unban Confirmation Dialog */}
      <AlertDialog
        isOpen={isBanDialogOpen}
        leastDestructiveRef={banDialogCancelRef}
        onClose={() => setIsBanDialogOpen(false)}
      >
        <AlertDialogOverlay>
          <AlertDialogContent bg="dark.800" border="1px solid" borderColor="gray.600">
            <AlertDialogHeader color="gray.300">
              {banDialogUser?.plan === 'banned' ? t('adminDashboard.unbanUser', 'Unban User') : t('adminDashboard.banUser', 'Ban User')}
            </AlertDialogHeader>
            <AlertDialogBody color="gray.300">
              {t('adminDashboard.banConfirm', 'Are you sure you want to {{action}} user', { action: banDialogUser?.plan === 'banned' ? t('adminDashboard.unban', 'unban') : t('adminDashboard.ban', 'ban') })} <strong>{banDialogUser?.email}</strong>?
              {banDialogUser?.plan === 'banned' 
                ? t('adminDashboard.restoreAccess', ' This will restore their access to the platform.')
                : t('adminDashboard.preventAccess', ' This will prevent them from accessing the platform.')
              }
            </AlertDialogBody>
            <AlertDialogFooter>
              <Button ref={banDialogCancelRef} onClick={() => setIsBanDialogOpen(false)} color="gray.400">
                {t('adminDashboard.cancel', 'Cancel')}
              </Button>
              <Button 
                colorScheme={banDialogUser?.plan === 'banned' ? 'green' : 'red'} 
                onClick={confirmBan} 
                ml={3}
              >
                {banDialogUser?.plan === 'banned' ? t('adminDashboard.unban', 'Unban') : t('adminDashboard.ban', 'Ban')}
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>

      {/* Reset Password Confirmation Dialog */}
      <AlertDialog
        isOpen={isResetDialogOpen}
        leastDestructiveRef={resetDialogCancelRef}
        onClose={() => setIsResetDialogOpen(false)}
      >
        <AlertDialogOverlay>
          <AlertDialogContent bg="dark.800" border="1px solid" borderColor="gray.600">
            <AlertDialogHeader color="gray.300">{t('adminDashboard.resetPassword', 'Reset Password')}</AlertDialogHeader>
            <AlertDialogBody color="gray.300">
              <Text mb={4}>
                {t('adminDashboard.resetPasswordConfirm', 'Are you sure you want to reset the password for user')} <strong>{resetDialogUser?.email}</strong>?
              </Text>
              <FormControl>
                <FormLabel color="gray.400">{t('adminDashboard.newPassword', 'New Password')}</FormLabel>
                <Input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder={t('adminDashboard.enterNewPassword', 'Enter new password')}
                  bg="dark.700"
                  borderColor="gray.600"
                  color="gray.300"
                  _placeholder={{ color: 'gray.500' }}
                />
              </FormControl>
            </AlertDialogBody>
            <AlertDialogFooter>
              <Button ref={resetDialogCancelRef} onClick={() => setIsResetDialogOpen(false)} color="gray.400">
                {t('adminDashboard.cancel', 'Cancel')}
              </Button>
              <Button 
                colorScheme="blue" 
                onClick={confirmReset} 
                ml={3}
                isDisabled={!newPassword.trim()}
              >
                {t('adminDashboard.resetPassword', 'Reset Password')}
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Box>
  );
};

export default AdminDashboard; 