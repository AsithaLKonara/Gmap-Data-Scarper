import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  HStack,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Card,
  CardBody,
  CardHeader,
  Button,
  useColorModeValue,
  Icon,
  Badge,
  Progress,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Avatar,
  Flex,
  Spacer,
  Divider,
  Grid,
  GridItem,
  IconButton,
  Tooltip,
} from '@chakra-ui/react';
import { keyframes } from '@emotion/react';
import {
  FiUsers,
  FiTrendingUp,
  FiSearch,
  FiSend,
  FiDollarSign,
  FiActivity,
  FiArrowUp,
  FiArrowDown,
  FiEye,
  FiMessageSquare,
  FiBarChart2,
  FiTarget,
  FiZap,
  FiGlobe,
  FiShield,
  FiPlus,
  FiMoreVertical,
  FiRefreshCw,
  FiDownload,
  FiFilter,
} from 'react-icons/fi';
import { useTranslation } from 'react-i18next';

// Animations
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;

const slideIn = keyframes`
  from { transform: translateX(-100px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
`;

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
`;

const float = keyframes`
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-5px); }
`;

interface DashboardStats {
  totalLeads: number;
  activeCampaigns: number;
  messagesSent: number;
  conversionRate: number;
  revenue: number;
  growthRate: number;
}

interface RecentActivity {
  id: string;
  type: 'lead_added' | 'campaign_started' | 'message_sent' | 'conversion';
  title: string;
  description: string;
  timestamp: string;
  value?: string;
  avatar?: string;
}

const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const [stats, setStats] = useState<DashboardStats>({
    totalLeads: 0,
    activeCampaigns: 0,
    messagesSent: 0,
    conversionRate: 0,
    revenue: 0,
    growthRate: 0,
  });
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const bgColor = useColorModeValue('white', 'gray.800');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const headingColor = useColorModeValue('gray.800', 'white');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const gradientBg = useColorModeValue(
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #4c1d95 0%, #7c3aed 100%)'
  );
  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    const loadDashboardData = async () => {
      setIsLoading(true);
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setStats({
        totalLeads: 1247,
        activeCampaigns: 8,
        messagesSent: 3456,
        conversionRate: 12.5,
        revenue: 45600,
        growthRate: 23.4,
      });

      setRecentActivity([
        {
          id: '1',
          type: 'lead_added',
          title: 'New Lead Added',
          description: 'John Smith from TechCorp added to CRM',
          timestamp: '2 minutes ago',
          value: '+1',
          avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=40&h=40&fit=crop&crop=face'
        },
        {
          id: '2',
          type: 'campaign_started',
          title: 'Campaign Started',
          description: 'Welcome sequence campaign activated',
          timestamp: '15 minutes ago',
          value: 'Active',
          avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=40&h=40&fit=crop&crop=face'
        },
        {
          id: '3',
          type: 'message_sent',
          title: 'Bulk Messages Sent',
          description: '500 WhatsApp messages delivered',
          timestamp: '1 hour ago',
          value: '500',
          avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=40&h=40&fit=crop&crop=face'
        },
        {
          id: '4',
          type: 'conversion',
          title: 'Lead Converted',
          description: 'Sarah Johnson converted to customer',
          timestamp: '2 hours ago',
          value: '+$2,400',
          avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=40&h=40&fit=crop&crop=face'
        },
        {
          id: '5',
          type: 'lead_added',
          title: 'New Lead Added',
          description: 'Mike Chen from GrowthCo added to CRM',
          timestamp: '3 hours ago',
          value: '+1',
          avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=40&h=40&fit=crop&crop=face'
        }
      ]);

      setIsLoading(false);
    };

    loadDashboardData();
  }, []);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'lead_added':
        return FiUsers;
      case 'campaign_started':
        return FiActivity;
      case 'message_sent':
        return FiSend;
      case 'conversion':
        return FiDollarSign;
      default:
        return FiActivity;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'lead_added':
        return 'blue';
      case 'campaign_started':
        return 'green';
      case 'message_sent':
        return 'purple';
      case 'conversion':
        return 'orange';
      default:
        return 'gray';
    }
  };

  const statCards = [
    {
      label: 'Total Leads',
      value: stats.totalLeads.toLocaleString(),
      help: '+23.4% from last month',
      icon: FiUsers,
      color: 'blue.500',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      trend: 'up'
    },
    {
      label: 'Active Campaigns',
      value: stats.activeCampaigns.toString(),
      help: 'Running WhatsApp campaigns',
      icon: FiSend,
      color: 'green.500',
      gradient: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
      trend: 'up'
    },
    {
      label: 'Messages Sent',
      value: stats.messagesSent.toLocaleString(),
      help: 'This month via WhatsApp',
      icon: FiMessageSquare,
      color: 'purple.500',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      trend: 'up'
    },
    {
      label: 'Conversion Rate',
      value: `${stats.conversionRate}%`,
      help: '+2.1% from last month',
      icon: FiTarget,
      color: 'orange.500',
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      trend: 'up'
    },
    {
      label: 'Revenue Generated',
      value: `$${stats.revenue.toLocaleString()}`,
      help: 'From converted leads',
      icon: FiDollarSign,
      color: 'teal.500',
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      trend: 'up'
    },
    {
      label: 'Success Rate',
      value: '94.2%',
      help: 'Message delivery success',
      icon: FiShield,
      color: 'pink.500',
      gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
      trend: 'up'
    }
  ];

  if (isLoading) {
    return (
      <Box p={6}>
        <VStack spacing={4}>
          <Text>Loading dashboard...</Text>
        </VStack>
      </Box>
    );
  }

  return (
    <Box p={6} bg={useColorModeValue('gray.50', 'gray.900')} minH="100vh">
      <Container maxW="7xl">
        <VStack spacing={8} align="stretch">
          {/* Header */}
          <Box
            bg={cardBg}
            p={6}
            borderRadius="2xl"
            border="1px"
            borderColor={cardBorder}
            boxShadow="lg"
            animation={`${fadeIn} 1s ease-out`}
          >
            <Flex align="center" justify="space-between">
              <VStack align="start" spacing={2}>
                <HStack spacing={3}>
                  <Box
                    p={2}
                    borderRadius="xl"
                    bg={gradientBg}
                    boxShadow="lg"
                    animation={`${float} 3s ease-in-out infinite`}
                  >
                    <Icon as={FiBarChart2} boxSize={6} color="white" />
                  </Box>
                  <Heading size="lg" color={headingColor}>
                    Welcome back! 👋
                  </Heading>
                </HStack>
                <Text color={textColor}>
                  Here's what's happening with your lead generation today
                </Text>
              </VStack>
              <HStack spacing={3}>
                <Tooltip label="Refresh Data">
                  <IconButton
                    aria-label="Refresh"
                    icon={<Icon as={FiRefreshCw} />}
                    variant="outline"
                    size="md"
                  />
                </Tooltip>
                <Button variant="outline" leftIcon={<FiEye />}>
                  View Reports
                </Button>
                <Button bg={gradientBg} color="white" leftIcon={<FiSearch />} _hover={{ transform: 'translateY(-2px)', boxShadow: 'xl' }} transition="all 0.3s">
                  Find Leads
                </Button>
              </HStack>
            </Flex>
          </Box>

          {/* Stats Grid */}
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
            {statCards.map((stat, index) => (
              <Card
                key={index}
                bg={cardBg}
                border="1px"
                borderColor={cardBorder}
                borderRadius="xl"
                overflow="hidden"
                _hover={{ transform: 'translateY(-5px)', boxShadow: 'xl' }}
                transition="all 0.3s"
                animation={`${fadeIn} 1s ease-out ${index * 0.1}s both`}
              >
                <Box
                  h="4px"
                  bg={stat.gradient}
                />
                <CardBody p={6}>
                  <HStack justify="space-between" mb={4}>
                    <Box
                      p={3}
                      borderRadius="xl"
                      bg={stat.gradient}
                      boxShadow="lg"
                    >
                      <Icon as={stat.icon} boxSize={5} color="white" />
                    </Box>
                    <HStack spacing={1}>
                      <Icon as={stat.trend === 'up' ? FiArrowUp : FiArrowDown} color={stat.trend === 'up' ? 'green.500' : 'red.500'} boxSize={4} />
                    </HStack>
                  </HStack>
                  <Stat>
                    <StatNumber fontSize="2xl" color={headingColor} fontWeight="bold">
                      {stat.value}
                    </StatNumber>
                    <StatLabel fontSize="md" color={headingColor} fontWeight="medium">
                      {stat.label}
                    </StatLabel>
                    <StatHelpText>
                      <Text color={textColor} fontSize="sm">
                        {stat.help}
                      </Text>
                    </StatHelpText>
                  </Stat>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>

          {/* Main Content Grid */}
          <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={6}>
            {/* Recent Activity */}
            <GridItem>
              <Card
                bg={cardBg}
                border="1px"
                borderColor={cardBorder}
                borderRadius="xl"
                overflow="hidden"
                animation={`${slideIn} 1s ease-out 0.5s both`}
              >
                <CardHeader pb={4}>
                  <Flex align="center" justify="space-between">
                    <Heading size="md" color={headingColor}>
                      Recent Activity
                    </Heading>
                    <HStack spacing={2}>
                      <Tooltip label="Filter">
                        <IconButton
                          aria-label="Filter"
                          icon={<Icon as={FiFilter} />}
                          variant="ghost"
                          size="sm"
                        />
                      </Tooltip>
                      <Button variant="ghost" size="sm">
                        View All
                      </Button>
                    </HStack>
                  </Flex>
                </CardHeader>
                <CardBody pt={0}>
                  <VStack spacing={4} align="stretch">
                    {recentActivity.map((activity) => {
                      const ActivityIcon = getActivityIcon(activity.type);
                      return (
                        <Box
                          key={activity.id}
                          p={4}
                          border="1px"
                          borderColor={borderColor}
                          borderRadius="lg"
                          _hover={{ bg: useColorModeValue('gray.50', 'gray.700'), transform: 'translateX(5px)' }}
                          transition="all 0.3s"
                        >
                          <HStack spacing={4}>
                            <Avatar src={activity.avatar} size="sm" />
                            <Box flex="1">
                              <HStack justify="space-between" mb={2}>
                                <Text fontWeight="medium" color={headingColor}>
                                  {activity.title}
                                </Text>
                                {activity.value && (
                                  <Badge
                                    colorScheme={getActivityColor(activity.type)}
                                    variant="subtle"
                                    fontSize="xs"
                                  >
                                    {activity.value}
                                  </Badge>
                                )}
                              </HStack>
                              <Text fontSize="sm" color={textColor} mb={1}>
                                {activity.description}
                              </Text>
                              <Text fontSize="xs" color={textColor}>
                                {activity.timestamp}
                              </Text>
                            </Box>
                            <Icon
                              as={ActivityIcon}
                              boxSize={5}
                              color={`${getActivityColor(activity.type)}.500`}
                            />
                          </HStack>
                        </Box>
                      );
                    })}
                  </VStack>
                </CardBody>
              </Card>
            </GridItem>

            {/* Quick Actions & Performance */}
            <GridItem>
              <VStack spacing={6} align="stretch">
                {/* Quick Actions */}
                <Card
                  bg={cardBg}
                  border="1px"
                  borderColor={cardBorder}
                  borderRadius="xl"
                  overflow="hidden"
                >
                  <CardHeader pb={4}>
                    <Heading size="md" color={headingColor}>
                      Quick Actions
                    </Heading>
                  </CardHeader>
                  <CardBody pt={0}>
                    <VStack spacing={3} align="stretch">
                      <Button
                        variant="outline"
                        leftIcon={<FiSearch />}
                        justifyContent="start"
                        size="lg"
                        borderRadius="lg"
                        _hover={{ bg: useColorModeValue('blue.50', 'blue.900'), borderColor: 'blue.500' }}
                      >
                        Search for New Leads
                      </Button>
                      <Button
                        variant="outline"
                        leftIcon={<FiSend />}
                        justifyContent="start"
                        size="lg"
                        borderRadius="lg"
                        _hover={{ bg: useColorModeValue('green.50', 'green.900'), borderColor: 'green.500' }}
                      >
                        Create WhatsApp Campaign
                      </Button>
                      <Button
                        variant="outline"
                        leftIcon={<FiUsers />}
                        justifyContent="start"
                        size="lg"
                        borderRadius="lg"
                        _hover={{ bg: useColorModeValue('purple.50', 'purple.900'), borderColor: 'purple.500' }}
                      >
                        Import Contacts
                      </Button>
                      <Button
                        variant="outline"
                        leftIcon={<FiTrendingUp />}
                        justifyContent="start"
                        size="lg"
                        borderRadius="lg"
                        _hover={{ bg: useColorModeValue('orange.50', 'orange.900'), borderColor: 'orange.500' }}
                      >
                        View Analytics
                      </Button>
                    </VStack>
                  </CardBody>
                </Card>

                {/* Performance Overview */}
                <Card
                  bg={cardBg}
                  border="1px"
                  borderColor={cardBorder}
                  borderRadius="xl"
                  overflow="hidden"
                >
                  <CardHeader pb={4}>
                    <Heading size="md" color={headingColor}>
                      Performance Overview
                    </Heading>
                  </CardHeader>
                  <CardBody pt={0}>
                    <VStack spacing={4} align="stretch">
                      <Box>
                        <Flex justify="space-between" mb={2}>
                          <Text fontSize="sm" color={textColor}>Lead Generation</Text>
                          <Text fontSize="sm" fontWeight="medium" color={headingColor}>85%</Text>
                        </Flex>
                        <Progress value={85} colorScheme="blue" size="sm" borderRadius="full" />
                      </Box>
                      
                      <Box>
                        <Flex justify="space-between" mb={2}>
                          <Text fontSize="sm" color={textColor}>Message Delivery</Text>
                          <Text fontSize="sm" fontWeight="medium" color={headingColor}>94%</Text>
                        </Flex>
                        <Progress value={94} colorScheme="green" size="sm" borderRadius="full" />
                      </Box>
                      
                      <Box>
                        <Flex justify="space-between" mb={2}>
                          <Text fontSize="sm" color={textColor}>Conversion Rate</Text>
                          <Text fontSize="sm" fontWeight="medium" color={headingColor}>12.5%</Text>
                        </Flex>
                        <Progress value={12.5} colorScheme="orange" size="sm" borderRadius="full" />
                      </Box>
                      
                      <Box>
                        <Flex justify="space-between" mb={2}>
                          <Text fontSize="sm" color={textColor}>Revenue Growth</Text>
                          <Text fontSize="sm" fontWeight="medium" color={headingColor}>23%</Text>
                        </Flex>
                        <Progress value={23} colorScheme="purple" size="sm" borderRadius="full" />
                      </Box>
                    </VStack>
                  </CardBody>
                </Card>
              </VStack>
            </GridItem>
          </Grid>
        </VStack>
      </Container>
    </Box>
  );
};

export default Dashboard;
