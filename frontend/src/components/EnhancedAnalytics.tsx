import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Card,
  CardBody,
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
  Input,
  FormControl,
  FormLabel,
} from '@chakra-ui/react';
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
import { 
  TrendingUpIcon, 
  TargetIcon, 
  FunnelIcon,
  CalendarIcon,
  DownloadIcon,
  SettingsIcon,
} from '@chakra-ui/icons';
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
    <Box>
      {/* Header with Period Selector */}
      <HStack justify="space-between" mb={6}>
        <Box>
          <Text fontSize="2xl" fontWeight="bold">Analytics Dashboard</Text>
          <Text color="gray.600">Track your lead generation performance</Text>
        </Box>
        <HStack spacing={4}>
          <Select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            size="sm"
            width="120px"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="365">Last year</option>
          </Select>
          <Button size="sm" leftIcon={<DownloadIcon />}>
            Export Report
          </Button>
        </HStack>
      </HStack>

      {/* Key Metrics */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mb={8}>
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Stat>
              <StatLabel>Jobs Created</StatLabel>
              <StatNumber>{currentMonth?.jobsCreated || 0}</StatNumber>
              <StatHelpText>
                <StatArrow type={currentMonth?.jobsCreated > previousMonth?.jobsCreated ? 'increase' : 'decrease'} />
                {Math.abs(calculateGrowth(currentMonth?.jobsCreated || 0, previousMonth?.jobsCreated || 0)).toFixed(1)}%
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Stat>
              <StatLabel>Leads Generated</StatLabel>
              <StatNumber>{currentMonth?.leadsGenerated?.toLocaleString() || 0}</StatNumber>
              <StatHelpText>
                <StatArrow type={currentMonth?.leadsGenerated > previousMonth?.leadsGenerated ? 'increase' : 'decrease'} />
                {Math.abs(calculateGrowth(currentMonth?.leadsGenerated || 0, previousMonth?.leadsGenerated || 0)).toFixed(1)}%
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Stat>
              <StatLabel>Conversion Rate</StatLabel>
              <StatNumber>{(currentMonth?.conversionRate * 100).toFixed(1)}%</StatNumber>
              <StatHelpText>
                <StatArrow type={currentMonth?.conversionRate > previousMonth?.conversionRate ? 'increase' : 'decrease'} />
                {Math.abs(calculateGrowth(currentMonth?.conversionRate || 0, previousMonth?.conversionRate || 0)).toFixed(1)}%
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Stat>
              <StatLabel>Revenue</StatLabel>
              <StatNumber>${currentMonth?.revenue?.toLocaleString() || 0}</StatNumber>
              <StatHelpText>
                <StatArrow type={currentMonth?.revenue > previousMonth?.revenue ? 'increase' : 'decrease'} />
                {Math.abs(calculateGrowth(currentMonth?.revenue || 0, previousMonth?.revenue || 0)).toFixed(1)}%
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Goals Section */}
      <Card bg={bgColor} border="1px" borderColor={borderColor} mb={6}>
        <CardBody>
          <HStack justify="space-between" mb={4}>
            <Text fontSize="lg" fontWeight="bold">Goals & Targets</Text>
            <Button size="sm" onClick={() => setShowGoalModal(true)}>
              Add Goal
            </Button>
          </HStack>
          
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
            {goals.map((goal) => (
              <Box key={goal.id} p={4} border="1px" borderColor={borderColor} borderRadius="md">
                <HStack justify="space-between" mb={2}>
                  <Text fontWeight="medium" fontSize="sm">{goal.name}</Text>
                  <Badge colorScheme={getGoalColor(goal)}>
                    {getGoalProgress(goal).toFixed(0)}%
                  </Badge>
                </HStack>
                <Progress 
                  value={getGoalProgress(goal)} 
                  colorScheme={getGoalColor(goal)}
                  size="sm"
                  mb={2}
                />
                <Text fontSize="sm" color="gray.600">
                  {goal.current.toLocaleString()} / {goal.target.toLocaleString()} {goal.type}
                </Text>
                <Text fontSize="xs" color="gray.500">
                  Due: {new Date(goal.deadline).toLocaleDateString()}
                </Text>
              </Box>
            ))}
          </SimpleGrid>
        </CardBody>
      </Card>

      {/* Charts Section */}
      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6} mb={6}>
        {/* Trend Chart */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Text fontSize="lg" fontWeight="bold" mb={4}>Performance Trends</Text>
            <ResponsiveContainer width="100%" height={300}>
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
          </CardBody>
        </Card>

        {/* Funnel Chart */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Text fontSize="lg" fontWeight="bold" mb={4}>Conversion Funnel</Text>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={funnelData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="stage" />
                <YAxis />
                <RechartsTooltip />
                <Bar dataKey="count" fill="#3182CE" />
              </BarChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Funnel Details Table */}
      <Card bg={bgColor} border="1px" borderColor={borderColor} mb={6}>
        <CardBody>
          <Text fontSize="lg" fontWeight="bold" mb={4}>Funnel Analysis</Text>
          <Table variant="simple" size="sm">
            <Thead>
              <Tr>
                <Th>Stage</Th>
                <Th>Count</Th>
                <Th>Conversion Rate</Th>
                <Th>Drop-off</Th>
              </Tr>
            </Thead>
            <Tbody>
              {funnelData.map((stage, index) => (
                <Tr key={stage.stage}>
                  <Td>
                    <HStack>
                      <Box w={3} h={3} bg={stage.color} borderRadius="full" />
                      <Text>{stage.stage}</Text>
                    </HStack>
                  </Td>
                  <Td>{stage.count.toLocaleString()}</Td>
                  <Td>{stage.conversionRate.toFixed(1)}%</Td>
                  <Td>
                    {index < funnelData.length - 1 
                      ? `${((1 - funnelData[index + 1].count / stage.count) * 100).toFixed(1)}%`
                      : '-'
                    }
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </CardBody>
      </Card>

      {/* Insights & Recommendations */}
      <Card bg={bgColor} border="1px" borderColor={borderColor}>
        <CardBody>
          <Text fontSize="lg" fontWeight="bold" mb={4}>Insights & Recommendations</Text>
          
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
            <Alert status="success" borderRadius="md">
              <AlertIcon />
              <Box>
                <AlertTitle>Strong Performance</AlertTitle>
                <AlertDescription>
                  Your conversion rate is 20% above industry average. Keep up the great work!
                </AlertDescription>
              </Box>
            </Alert>

            <Alert status="info" borderRadius="md">
              <AlertIcon />
              <Box>
                <AlertTitle>Optimization Opportunity</AlertTitle>
                <AlertDescription>
                  Consider adding more specific queries to improve lead quality and conversion rates.
                </AlertDescription>
              </Box>
            </Alert>

            <Alert status="warning" borderRadius="md">
              <AlertIcon />
              <Box>
                <AlertTitle>Goal Alert</AlertTitle>
                <AlertDescription>
                  You're 15% behind your monthly lead generation goal. Consider increasing your daily query volume.
                </AlertDescription>
              </Box>
            </Alert>

            <Alert status="info" borderRadius="md">
              <AlertIcon />
              <Box>
                <AlertTitle>Feature Suggestion</AlertTitle>
                <AlertDescription>
                  Upgrade to Pro plan to access advanced analytics and team collaboration features.
                </AlertDescription>
              </Box>
            </Alert>
          </SimpleGrid>
        </CardBody>
      </Card>

      {/* Add Goal Modal */}
      <Modal isOpen={showGoalModal} onClose={() => setShowGoalModal(false)}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Add New Goal</ModalHeader>
          <ModalBody>
            <VStack spacing={4}>
              <FormControl>
                <FormLabel>Goal Name</FormLabel>
                <Input
                  value={newGoal.name}
                  onChange={(e) => setNewGoal({ ...newGoal, name: e.target.value })}
                  placeholder="e.g., Generate 1000 leads this month"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Target Value</FormLabel>
                <Input
                  type="number"
                  value={newGoal.target}
                  onChange={(e) => setNewGoal({ ...newGoal, target: Number(e.target.value) })}
                  placeholder="1000"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Goal Type</FormLabel>
                <Select
                  value={newGoal.type}
                  onChange={(e) => setNewGoal({ ...newGoal, type: e.target.value as any })}
                >
                  <option value="leads">Leads Generated</option>
                  <option value="revenue">Revenue</option>
                  <option value="jobs">Jobs Created</option>
                  <option value="exports">Exports Completed</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Period</FormLabel>
                <Select
                  value={newGoal.period}
                  onChange={(e) => setNewGoal({ ...newGoal, period: e.target.value as any })}
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Deadline</FormLabel>
                <Input
                  type="date"
                  value={newGoal.deadline}
                  onChange={(e) => setNewGoal({ ...newGoal, deadline: e.target.value })}
                />
              </FormControl>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => setShowGoalModal(false)}>
              Cancel
            </Button>
            <Button colorScheme="blue" onClick={handleAddGoal}>
              Add Goal
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default EnhancedAnalytics; 