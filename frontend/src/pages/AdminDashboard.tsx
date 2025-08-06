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
  Badge,
  IconButton,
  Divider,
  useColorModeValue,
  Table,
  Thead,
  Tr,
  Th,
  Tbody,
  Td,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Select,
  Input,
  useToast,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import {
  FiUsers,
  FiTrendingUp,
  FiActivity,
  FiDollarSign,
  FiSearch,
  FiDownload,
  FiMoreVertical,
  FiEye,
  FiEdit,
  FiTrash2,
} from 'react-icons/fi';

const AdminDashboard: React.FC = () => {
  const { t } = useTranslation();
  const toast = useToast();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  // State management
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

  // Mock data - replace with actual API calls
  useEffect(() => {
    const mockAnalyticsData = {
      userGrowth: {
        totalUsers: 1250,
        newUsers: 45,
        growthRate: 12.5,
      },
      jobTrends: {
        totalJobs: 3420,
        completedJobs: 3156,
        successRate: 92.3,
      },
      planDistribution: {
        free: 650,
        pro: 450,
        business: 150,
      },
      activeUsers: {
        daily: 234,
        weekly: 892,
        monthly: 1156,
      },
    };

    const mockUsers = [
      {
        id: 1,
        email: 'john@example.com',
        name: 'John Doe',
        plan: 'Pro',
        status: 'active',
        created_at: '2024-01-01',
        last_login: '2024-01-15',
      },
      {
        id: 2,
        email: 'jane@example.com',
        name: 'Jane Smith',
        plan: 'Business',
        status: 'active',
        created_at: '2024-01-05',
        last_login: '2024-01-14',
      },
    ];

    const mockJobs = [
      {
        id: 1,
        user_email: 'john@example.com',
        type: 'Google Maps',
        status: 'completed',
        created_at: '2024-01-15',
        leads_found: 45,
      },
      {
        id: 2,
        user_email: 'jane@example.com',
        type: 'Facebook',
        status: 'running',
        created_at: '2024-01-15',
        leads_found: 0,
      },
    ];

    setAnalyticsData(mockAnalyticsData);
    setUsers(mockUsers);
    setJobs(mockJobs);
    setUserTotal(1250);
    setJobTotal(3420);
  }, []);

  const fetchAnalytics = async () => {
    setAnalyticsLoading(true);
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
    } catch (error) {
      toast({
        title: 'Error fetching analytics',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setAnalyticsLoading(false);
    }
  };

  const fetchUsers = async () => {
    setUserTableLoading(true);
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 500));
    } catch (error) {
      toast({
        title: 'Error fetching users',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setUserTableLoading(false);
    }
  };

  const fetchJobs = async () => {
    setJobTableLoading(true);
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 500));
    } catch (error) {
      toast({
        title: 'Error fetching jobs',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setJobTableLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'completed':
        return 'green';
      case 'running':
        return 'blue';
      case 'failed':
        return 'red';
      case 'pending':
        return 'yellow';
      default:
        return 'gray';
    }
  };

  const getPlanColor = (plan: string) => {
    switch (plan.toLowerCase()) {
      case 'pro':
        return 'blue';
      case 'business':
        return 'purple';
      case 'enterprise':
        return 'green';
      default:
        return 'gray';
    }
  };

  if (analyticsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minH="400px">
        <Spinner size="xl" />
      </Box>
    );
  }

  return (
    <Box>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>Admin Dashboard</Heading>
          <Text color={textColor}>Monitor system performance and user activity</Text>
        </Box>

        {/* Analytics Overview */}
        {analyticsData && (
          <SimpleGrid columns={{ base: 1, md: 4 }} spacing={6}>
            <Stat>
              <StatLabel>Total Users</StatLabel>
              <StatNumber>{analyticsData.userGrowth.totalUsers.toLocaleString()}</StatNumber>
              <StatHelpText>
                +{analyticsData.userGrowth.newUsers} this month
              </StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Total Jobs</StatLabel>
              <StatNumber>{analyticsData.jobTrends.totalJobs.toLocaleString()}</StatNumber>
              <StatHelpText>
                {analyticsData.jobTrends.successRate}% success rate
              </StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Active Users</StatLabel>
              <StatNumber>{analyticsData.activeUsers.daily}</StatNumber>
              <StatHelpText>Today</StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Revenue</StatLabel>
              <StatNumber color="green.500">$12,450</StatNumber>
              <StatHelpText>This month</StatHelpText>
            </Stat>
          </SimpleGrid>
        )}

        {/* Plan Distribution */}
        {analyticsData && (
          <Box
            bg={bgColor}
            border="1px"
            borderColor={borderColor}
            borderRadius="lg"
            p={6}
          >
            <Heading size="md" mb={4}>Plan Distribution</Heading>
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
              <Box textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color="gray.500">
                  {analyticsData.planDistribution.free}
                </Text>
                <Text fontSize="sm" color={textColor}>Free Plan</Text>
              </Box>
              <Box textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                  {analyticsData.planDistribution.pro}
                </Text>
                <Text fontSize="sm" color={textColor}>Pro Plan</Text>
              </Box>
              <Box textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color="purple.500">
                  {analyticsData.planDistribution.business}
                </Text>
                <Text fontSize="sm" color={textColor}>Business Plan</Text>
              </Box>
            </SimpleGrid>
          </Box>
        )}

        {/* Users Table */}
        <Box
          bg={bgColor}
          border="1px"
          borderColor={borderColor}
          borderRadius="lg"
          p={6}
        >
          <HStack justify="space-between" mb={4}>
            <Heading size="md">Recent Users</Heading>
            <HStack spacing={2}>
              <Input
                placeholder="Filter by email"
                value={userEmailFilter}
                onChange={(e) => setUserEmailFilter(e.target.value)}
                size="sm"
                maxW="200px"
              />
              <Select
                value={userPlanFilter}
                onChange={(e) => setUserPlanFilter(e.target.value)}
                size="sm"
                maxW="150px"
              >
                <option value="">All Plans</option>
                <option value="free">Free</option>
                <option value="pro">Pro</option>
                <option value="business">Business</option>
              </Select>
            </HStack>
          </HStack>

          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>User</Th>
                <Th>Plan</Th>
                <Th>Status</Th>
                <Th>Created</Th>
                <Th>Last Login</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {users.map((user) => (
                <Tr key={user.id}>
                  <Td>
                    <HStack spacing={3}>
                      <Avatar size="sm" name={user.name} />
                      <VStack align="start" spacing={0}>
                        <Text fontWeight="medium">{user.name}</Text>
                        <Text fontSize="sm" color={textColor}>
                          {user.email}
                        </Text>
                      </VStack>
                    </HStack>
                  </Td>
                  <Td>
                    <Badge colorScheme={getPlanColor(user.plan)}>
                      {user.plan}
                    </Badge>
                  </Td>
                  <Td>
                    <Badge colorScheme={getStatusColor(user.status)}>
                      {user.status}
                    </Badge>
                  </Td>
                  <Td>{new Date(user.created_at).toLocaleDateString()}</Td>
                  <Td>{new Date(user.last_login).toLocaleDateString()}</Td>
                  <Td>
                    <Menu>
                      <MenuButton
                        as={IconButton}
                        icon={<FiMoreVertical />}
                        variant="ghost"
                        size="sm"
                      />
                      <MenuList>
                        <MenuItem icon={<FiEye />}>View Details</MenuItem>
                        <MenuItem icon={<FiEdit />}>Edit User</MenuItem>
                        <MenuItem icon={<FiTrash2 />} color="red.500">
                          Delete User
                        </MenuItem>
                      </MenuList>
                    </Menu>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>

        {/* Jobs Table */}
        <Box
          bg={bgColor}
          border="1px"
          borderColor={borderColor}
          borderRadius="lg"
          p={6}
        >
          <HStack justify="space-between" mb={4}>
            <Heading size="md">Recent Jobs</Heading>
            <HStack spacing={2}>
              <Input
                placeholder="Filter by user email"
                value={jobUserEmailFilter}
                onChange={(e) => setJobUserEmailFilter(e.target.value)}
                size="sm"
                maxW="200px"
              />
              <Select
                value={jobStatusFilter}
                onChange={(e) => setJobStatusFilter(e.target.value)}
                size="sm"
                maxW="150px"
              >
                <option value="">All Status</option>
                <option value="completed">Completed</option>
                <option value="running">Running</option>
                <option value="failed">Failed</option>
                <option value="pending">Pending</option>
              </Select>
            </HStack>
          </HStack>

          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>User</Th>
                <Th>Type</Th>
                <Th>Status</Th>
                <Th>Leads Found</Th>
                <Th>Created</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {jobs.map((job) => (
                <Tr key={job.id}>
                  <Td>{job.user_email}</Td>
                  <Td>
                    <Badge variant="outline">{job.type}</Badge>
                  </Td>
                  <Td>
                    <Badge colorScheme={getStatusColor(job.status)}>
                      {job.status}
                    </Badge>
                  </Td>
                  <Td>{job.leads_found}</Td>
                  <Td>{new Date(job.created_at).toLocaleDateString()}</Td>
                  <Td>
                    <Menu>
                      <MenuButton
                        as={IconButton}
                        icon={<FiMoreVertical />}
                        variant="ghost"
                        size="sm"
                      />
                      <MenuList>
                        <MenuItem icon={<FiEye />}>View Details</MenuItem>
                        <MenuItem icon={<FiDownload />}>Download Results</MenuItem>
                        <MenuItem icon={<FiTrash2 />} color="red.500">
                          Delete Job
                        </MenuItem>
                      </MenuList>
                    </Menu>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      </VStack>
    </Box>
  );
};

export default AdminDashboard; 