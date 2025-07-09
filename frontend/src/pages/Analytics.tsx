import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  HStack,
  useToast,
  Spinner,
  Grid,
  GridItem,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Badge,
  Select,
  Button,
  useColorModeValue,
  Card,
  CardBody,
  CardHeader,
  Progress,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Flex,
  IconButton,
  Tooltip,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Input,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import { DownloadIcon, RepeatIcon } from '@chakra-ui/icons';
import * as api from '../api';

interface AnalyticsData {
  totalJobs: number;
  completedJobs: number;
  failedJobs: number;
  successRate: number;
  totalLeads: number;
  conversionRate: number;
  averageResponseTime: number;
  dailyQueries: number;
  monthlyGrowth: number;
  topQueries: Array<{ query: string; count: number }>;
  leadSources: Array<{ source: string; count: number }>;
  jobTrends: Array<{ date: string; count: number }>;
}

const Analytics: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState('30');
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    loadAnalytics();
  }, [timeRange]);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      // TODO: Replace with real API call when backend is ready
      const response = await api.getAnalytics();
      setData(response);
    } catch (error: any) {
      console.error(error);
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const exportAnalytics = async () => {
    try {
      // Mock export functionality
      toast({
        title: 'Export Started',
        description: 'Analytics data is being exported...',
        status: 'info',
        duration: 3000,
      });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  if (loading) {
    return (
      <Container maxW="container.xl" py={8}>
        <Flex justify="center" py={8}>
          <Spinner size="lg" />
        </Flex>
      </Container>
    );
  }

  return (
    <Box minH="100vh" bg={useColorModeValue('gray.100', 'gray.800')} data-tour="analytics-main">
      <Container maxW="container.xl" py={8} data-tour="analytics-content">
        <Heading size="lg" mb={6} className="gradient-text" data-tour="analytics-title">Analytics</Heading>
        <HStack justify="space-between" mb={4} data-tour="analytics-actions">
          <Button colorScheme="blue" onClick={loadAnalytics} data-tour="analytics-refresh">Refresh</Button>
          <Button colorScheme="green" onClick={exportAnalytics} data-tour="analytics-export">Export Analytics</Button>
        </HStack>

        {/* Key Metrics */}
        {data && (
          <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={6}>
            <GridItem data-tour="total-jobs-card">
              <Card bg={bgColor} border="1px" borderColor={borderColor}>
                <CardBody>
                  <Stat>
                    <StatLabel>Total Jobs</StatLabel>
                    <StatNumber>{data.totalJobs}</StatNumber>
                    <StatHelpText>
                      <StatArrow type="increase" />
                      {data.monthlyGrowth}%
                    </StatHelpText>
                  </Stat>
                </CardBody>
              </Card>
            </GridItem>
            
            <GridItem data-tour="success-rate-card">
              <Card bg={bgColor} border="1px" borderColor={borderColor}>
                <CardBody>
                  <Stat>
                    <StatLabel>Success Rate</StatLabel>
                    <StatNumber>{data.successRate}%</StatNumber>
                    <StatHelpText>
                      {data.completedJobs} completed, {data.failedJobs} failed
                    </StatHelpText>
                  </Stat>
                </CardBody>
              </Card>
            </GridItem>
            
            <GridItem data-tour="total-leads-card">
              <Card bg={bgColor} border="1px" borderColor={borderColor}>
                <CardBody>
                  <Stat>
                    <StatLabel>Total Leads</StatLabel>
                    <StatNumber>{data.totalLeads}</StatNumber>
                    <StatHelpText>
                      Conversion rate: {data.conversionRate}%
                    </StatHelpText>
                  </Stat>
                </CardBody>
              </Card>
            </GridItem>
            
            <GridItem data-tour="avg-response-time-card">
              <Card bg={bgColor} border="1px" borderColor={borderColor}>
                <CardBody>
                  <Stat>
                    <StatLabel>Avg Response Time</StatLabel>
                    <StatNumber>{data.averageResponseTime}s</StatNumber>
                    <StatHelpText>
                      Daily queries: {data.dailyQueries}
                    </StatHelpText>
                  </Stat>
                </CardBody>
              </Card>
            </GridItem>
          </Grid>
        )}

        {/* Detailed Analytics */}
        <Grid templateColumns="repeat(auto-fit, minmax(400px, 1fr))" gap={6}>
          {/* Top Queries */}
          <GridItem data-tour="top-queries-card">
            <Card bg={bgColor} border="1px" borderColor={borderColor}>
              <CardHeader>
                <Heading size="md">Top Search Queries</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={3} align="stretch">
                  {data?.topQueries.map((query, index) => (
                    <Box key={index}>
                      <HStack justify="space-between" mb={2}>
                        <Text fontSize="sm" fontWeight="medium">
                          {query.query}
                        </Text>
                        <Badge colorScheme="blue">{query.count}</Badge>
                      </HStack>
                      <Progress
                        value={(query.count / (data?.topQueries[0]?.count || 1)) * 100}
                        size="sm"
                        colorScheme="blue"
                      />
                    </Box>
                  ))}
                </VStack>
              </CardBody>
            </Card>
          </GridItem>

          {/* Lead Sources */}
          <GridItem data-tour="lead-sources-card">
            <Card bg={bgColor} border="1px" borderColor={borderColor}>
              <CardHeader>
                <Heading size="md">Lead Sources</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={3} align="stretch">
                  {data?.leadSources.map((source, index) => (
                    <Box key={index}>
                      <HStack justify="space-between" mb={2}>
                        <Text fontSize="sm" fontWeight="medium">
                          {source.source}
                        </Text>
                        <Badge colorScheme="green">{source.count}</Badge>
                      </HStack>
                      <Progress
                        value={(source.count / (data?.leadSources[0]?.count || 1)) * 100}
                        size="sm"
                        colorScheme="green"
                      />
                    </Box>
                  ))}
                </VStack>
              </CardBody>
            </Card>
          </GridItem>
        </Grid>

        {/* Job Trends Table */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardHeader>
            <Heading size="md">Job Trends</Heading>
          </CardHeader>
          <CardBody>
            <Table size="sm">
              <Thead>
                <Tr>
                  <Th>Date</Th>
                  <Th>Jobs Created</Th>
                  <Th>Status</Th>
                </Tr>
              </Thead>
              <Tbody>
                {data?.jobTrends.map((trend, index) => (
                  <Tr key={index}>
                    <Td>{new Date(trend.date).toLocaleDateString()}</Td>
                    <Td>{trend.count}</Td>
                    <Td>
                      <Badge colorScheme="blue">Active</Badge>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </CardBody>
        </Card>
      </Container>
    </Box>
  );
};

export default Analytics; 