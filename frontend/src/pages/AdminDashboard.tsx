import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  VStack,
  HStack,
  Text,
  Spinner,
  Alert,
  AlertIcon,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Button,
  Flex,
  Tag,
  IconButton,
  Divider,
  useColorModeValue,
  Table,
  Thead,
  Tr,
  Th,
  Tbody,
  Td,
} from '@chakra-ui/react';
import { HamburgerIcon, ChevronDownIcon, SearchIcon, DownloadIcon } from '@chakra-ui/icons';
import { useAuth } from '../hooks/useAuth';
import { Navigate } from 'react-router-dom';
import * as api from '../api';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';
import { Button as ShadCNButton } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  Table as ShadCNTable,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from '../components/ui/table';

const AdminDashboard: React.FC = () => {
  const { user, loading } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  // State for analytics, users, jobs, CRM
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [analyticsPeriod, setAnalyticsPeriod] = useState(30);
  const [users, setUsers] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [userTableLoading, setUserTableLoading] = useState(false);
  const [jobTableLoading, setJobTableLoading] = useState(false);
  const [userEmailFilter, setUserEmailFilter] = useState('');
  const [userPlanFilter, setUserPlanFilter] = useState('');
  const [userPage, setUserPage] = useState(1);
  const [userPageSize, setUserPageSize] = useState(20);
  const [userTotal, setUserTotal] = useState(0);
  const [jobUserEmailFilter, setJobUserEmailFilter] = useState('');
  const [jobStatusFilter, setJobStatusFilter] = useState('');
  const [jobPage, setJobPage] = useState(1);
  const [jobPageSize, setJobPageSize] = useState(20);
  const [jobTotal, setJobTotal] = useState(0);
  const [crmLeads, setCrmLeads] = useState<any[]>([]);
  const [crmLoading, setCrmLoading] = useState(false);

  // Fetch analytics
  useEffect(() => { fetchAnalytics(); }, [analyticsPeriod]);
  const fetchAnalytics = async () => {
    setAnalyticsLoading(true);
    try {
      const [userGrowth, jobTrends, planDistribution, activeUsers] = await Promise.all([
        api.adminGetUserGrowth(analyticsPeriod),
        api.adminGetJobTrends(analyticsPeriod),
        api.adminGetPlanDistribution(),
        api.adminGetActiveUsers(Math.min(analyticsPeriod, 7)),
      ]);
      setAnalyticsData({ userGrowth, jobTrends, planDistribution, activeUsers });
    } finally { setAnalyticsLoading(false); }
  };

  // Fetch users
  useEffect(() => { fetchUsers(); }, [userPage, userPageSize, userEmailFilter, userPlanFilter]);
  const fetchUsers = async () => {
    setUserTableLoading(true);
    try {
      const data = await api.adminGetUsers({ page: userPage, pageSize: userPageSize, email: userEmailFilter, plan: userPlanFilter });
      setUsers(data.results);
      setUserTotal(data.total);
    } finally { setUserTableLoading(false); }
  };

  // Fetch jobs
  useEffect(() => { fetchJobs(); }, [jobPage, jobPageSize, jobUserEmailFilter, jobStatusFilter]);
  const fetchJobs = async () => {
    setJobTableLoading(true);
    try {
      const data = await api.adminGetJobs({ page: jobPage, pageSize: jobPageSize, userEmail: jobUserEmailFilter, status: jobStatusFilter });
      setJobs(data.results);
      setJobTotal(data.total);
    } finally { setJobTableLoading(false); }
  };

  // Fetch CRM leads (admin view)
  useEffect(() => { fetchCrmLeads(); }, []);
  const fetchCrmLeads = async () => {
    setCrmLoading(true);
    try {
      const data = await api.getCRMLeads();
      setCrmLeads(data || []);
    } finally { setCrmLoading(false); }
  };

  if (loading) return <Spinner size="xl" mt={20} />;
  if (!user) return <Navigate to="/login" replace />;
  if (user.plan !== 'business') return (
    <Box maxW="600px" mx="auto" mt={20}><Alert status="error"><AlertIcon />Admin access required.</Alert></Box>
  );

  // Sidebar animation styles
  const sidebarStyles = {
    transition: 'width 0.3s cubic-bezier(.4,0,.2,1)',
    width: sidebarOpen ? 280 : 64,
    minWidth: sidebarOpen ? 280 : 64,
    bg: useColorModeValue('gray.50', 'gray.900'),
    borderRight: '1px solid',
    borderColor: useColorModeValue('gray.200', 'gray.700'),
    height: '100vh',
    position: 'fixed' as const,
    top: 0,
    left: 0,
    zIndex: 100,
    overflow: 'hidden',
    boxShadow: 'md',
  };

  // Header
  const header = (
    <Flex as="header" align="center" justify="space-between" px={6} py={4} bg={useColorModeValue('white', 'gray.800')} borderBottom="1px solid" borderColor={useColorModeValue('gray.200', 'gray.700')} position="sticky" top={0} zIndex={101} boxShadow="sm">
      <HStack spacing={4}>
        <IconButton
          icon={<HamburgerIcon />}
          aria-label="Toggle sidebar"
          variant="ghost"
          onClick={() => setSidebarOpen((v) => !v)}
        />
        <Heading size="md" fontWeight="bold" color="blue.500">LeadTap Admin</Heading>
      </HStack>
      <HStack spacing={4}>
        <Badge variant="outline">{user.plan.toUpperCase()}</Badge>
        <Menu>
          <MenuButton as={ShadCNButton} rightIcon={<ChevronDownIcon />} variant="ghost">
            <HStack>
              <Avatar size="sm" name={user.email} />
              <Text fontSize="sm">{user.email}</Text>
            </HStack>
          </MenuButton>
          <MenuList>
            <MenuItem>Profile</MenuItem>
            <MenuItem>Settings</MenuItem>
            <MenuItem>Logout</MenuItem>
          </MenuList>
        </Menu>
      </HStack>
    </Flex>
  );

  // Sidebar
  const sidebar = (
    <Box {...sidebarStyles}>
      <VStack align="stretch" spacing={2} pt={6} px={sidebarOpen ? 4 : 1}>
        <ShadCNButton variant="ghost" justifyContent={sidebarOpen ? 'flex-start' : 'center'} leftIcon={<span>📊</span>} size="lg">{sidebarOpen && 'Dashboard'}</ShadCNButton>
        <ShadCNButton variant="ghost" justifyContent={sidebarOpen ? 'flex-start' : 'center'} leftIcon={<span>👥</span>} size="lg">{sidebarOpen && 'Users'}</ShadCNButton>
        <ShadCNButton variant="ghost" justifyContent={sidebarOpen ? 'flex-start' : 'center'} leftIcon={<span>🗂️</span>} size="lg">{sidebarOpen && 'Jobs'}</ShadCNButton>
        <ShadCNButton variant="ghost" justifyContent={sidebarOpen ? 'flex-start' : 'center'} leftIcon={<span>📈</span>} size="lg">{sidebarOpen && 'Analytics'}</ShadCNButton>
        <ShadCNButton variant="ghost" justifyContent={sidebarOpen ? 'flex-start' : 'center'} leftIcon={<span>📝</span>} size="lg" onClick={() => window.location.href = '/admin/audit-log'}>{sidebarOpen && 'Audit Log'}</ShadCNButton>
        <ShadCNButton variant="ghost" justifyContent={sidebarOpen ? 'flex-start' : 'center'} leftIcon={<span>📝</span>} size="lg">{sidebarOpen && 'CRM'}</ShadCNButton>
        <ShadCNButton variant="ghost" justifyContent={sidebarOpen ? 'flex-start' : 'center'} leftIcon={<span>⚙️</span>} size="lg">{sidebarOpen && 'Settings'}</ShadCNButton>
      </VStack>
    </Box>
  );

  // Main content (scaffold for analytics, user/job management, CRM, etc.)
  return (
    <Box minH="100vh" bg={useColorModeValue('gray.100', 'gray.800')}>
      {header}
      <Box pl={sidebarOpen ? 280 : 64} transition="pl 0.3s cubic-bezier(.4,0,.2,1)">
        <VStack align="stretch" spacing={8} py={8} px={4}>
          <HStack align="start" spacing={8}>
            {/* Left: Admin Actions */}
            <Box flex="1" minW="320px">
              <VStack spacing={8} align="stretch">
                <Box>
                  <Heading size="lg" mb={4}>Admin Dashboard</Heading>
                  <Text color="gray.600">Manage users, jobs, analytics, and CRM</Text>
                </Box>
                {/* Add user/job management, filters, etc. here */}
                <Box bg={useColorModeValue('white', 'gray.900')} p={6} borderRadius="lg" border="1px" borderColor={useColorModeValue('gray.200', 'gray.700')} boxShadow="md">
                  <Heading size="md" mb={4}>User Management</Heading>
                  <ShadCNTable size="sm">
                    <TableHeader>
                      <TableRow>
                        <TableHead>ID</TableHead>
                        <TableHead>Email</TableHead>
                        <TableHead>Plan</TableHead>
                        <TableHead>Created</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {users.map((u) => (
                        <TableRow key={u.id}>
                          <TableCell>{u.id}</TableCell>
                          <TableCell>{u.email}</TableCell>
                          <TableCell>{u.plan}</TableCell>
                          <TableCell>{new Date(u.created_at).toLocaleDateString()}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </ShadCNTable>
                </Box>
                <Box bg={useColorModeValue('white', 'gray.900')} p={6} borderRadius="lg" border="1px" borderColor={useColorModeValue('gray.200', 'gray.700')} boxShadow="md">
                  <Heading size="md" mb={4}>Job Management</Heading>
                  <ShadCNTable size="sm">
                    <TableHeader>
                      <TableRow>
                        <TableHead>ID</TableHead>
                        <TableHead>User</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Created</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {jobs.map((j) => (
                        <TableRow key={j.id}>
                          <TableCell>{j.id}</TableCell>
                          <TableCell>{j.user_email || '-'}</TableCell>
                          <TableCell>{j.status}</TableCell>
                          <TableCell>{new Date(j.created_at).toLocaleDateString()}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </ShadCNTable>
                </Box>
              </VStack>
            </Box>
            {/* Right: Analytics, Map, CRM, etc. */}
            <Box flex="2" minW="400px">
              <VStack spacing={6} align="stretch">
                <Box bg={useColorModeValue('white', 'gray.900')} p={6} borderRadius="lg" border="1px" borderColor={useColorModeValue('gray.200', 'gray.700')} boxShadow="md">
                  <Heading size="md" mb={4}>Analytics</Heading>
                  {analyticsLoading ? <Spinner /> : (
                    analyticsData && (
                      <VStack spacing={6} align="stretch">
                        <Box h="300px">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={analyticsData.userGrowth?.data || []}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="date" />
                              <YAxis />
                              <RechartsTooltip />
                              <Legend />
                              <Line type="monotone" dataKey="new_users" stroke="#3182ce" name="New Users" />
                              <Line type="monotone" dataKey="total_users" stroke="#38a169" name="Total Users" />
                            </LineChart>
                          </ResponsiveContainer>
                        </Box>
                        <Box h="300px">
                          <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={analyticsData.jobTrends?.data || []}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="date" />
                              <YAxis />
                              <RechartsTooltip />
                              <Legend />
                              <Area type="monotone" dataKey="completed" stackId="1" stroke="#38a169" fill="#38a169" name="Completed" />
                              <Area type="monotone" dataKey="pending" stackId="1" stroke="#ecc94b" fill="#ecc94b" name="Pending" />
                              <Area type="monotone" dataKey="failed" stackId="1" stroke="#e53e3e" fill="#e53e3e" name="Failed" />
                            </AreaChart>
                          </ResponsiveContainer>
                        </Box>
                        <Box h="300px">
                          <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                              <Pie data={analyticsData.planDistribution?.plans || []} dataKey="count" nameKey="name" cx="50%" cy="50%" outerRadius={80} label />
                              <RechartsTooltip />
                            </PieChart>
                          </ResponsiveContainer>
                        </Box>
                        <Box h="300px">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={analyticsData.activeUsers?.data || []}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="date" />
                              <YAxis />
                              <RechartsTooltip />
                              <Legend />
                              <Bar dataKey="active_users" fill="#3182ce" name="Active Users" />
                            </BarChart>
                          </ResponsiveContainer>
                        </Box>
                      </VStack>
                    )
                  )}
                </Box>
                <Box borderRadius="lg" overflow="hidden" border="1px" borderColor={useColorModeValue('gray.200', 'gray.700')} minH="320px" boxShadow="md">
                  {/* Map view (iframe or map component) */}
                  <Text color="gray.500" p={8} textAlign="center">(Map view goes here)</Text>
                </Box>
                <Box bg={useColorModeValue('white', 'gray.900')} p={6} borderRadius="lg" border="1px" borderColor={useColorModeValue('gray.200', 'gray.700')} boxShadow="md">
                  <Heading size="md" mb={4}>CRM Leads</Heading>
                  <ShadCNTable size="sm">
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Email</TableHead>
                        <TableHead>Company</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Source</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {crmLeads.map((lead) => (
                        <TableRow key={lead.id}>
                          <TableCell>{lead.name}</TableCell>
                          <TableCell>{lead.email}</TableCell>
                          <TableCell>{lead.company || '-'}</TableCell>
                          <TableCell>{lead.status}</TableCell>
                          <TableCell>{lead.source}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </ShadCNTable>
                </Box>
              </VStack>
            </Box>
          </HStack>
        </VStack>
      </Box>
    </Box>
  );
};

export default AdminDashboard; 