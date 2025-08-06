import React, { useState, useMemo } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Input,
  Select,
  Button,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Badge,
  Divider,
  useColorModeValue,
} from '@chakra-ui/react';

interface ROICalculatorProps {
  planType?: 'free' | 'pro' | 'business';
}

const ROICalculator: React.FC<ROICalculatorProps> = ({ planType = 'pro' }) => {
  const [queriesPerDay, setQueriesPerDay] = useState(10);
  const [leadsPerQuery, setLeadsPerQuery] = useState(20);
  const [conversionRate, setConversionRate] = useState(2);
  const [averageDealValue, setAverageDealValue] = useState(500);

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const plans = {
    free: { name: 'Free', cost: 0, queries: 5 },
    pro: { name: 'Pro', cost: 29, queries: 50 },
    business: { name: 'Business', cost: 99, queries: 200 },
  };

  const currentPlan = plans[planType];

  const calculations = useMemo(() => {
    const monthlyLeads = queriesPerDay * leadsPerQuery * 30;
    const monthlyConversions = monthlyLeads * (conversionRate / 100);
    const monthlyRevenue = monthlyConversions * averageDealValue;
    const monthlyProfit = monthlyRevenue - currentPlan.cost;
    const roi = currentPlan.cost > 0 ? (monthlyProfit / currentPlan.cost) * 100 : 0;
    const paybackDays = currentPlan.cost > 0 ? (currentPlan.cost / (monthlyProfit / 30)) : 0;
    const isOverLimit = queriesPerDay > currentPlan.queries;

    return {
      monthlyLeads,
      monthlyConversions,
      monthlyRevenue,
      monthlyProfit,
      roi,
      paybackDays,
      isOverLimit,
    };
  }, [queriesPerDay, leadsPerQuery, conversionRate, averageDealValue, currentPlan]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const {
    monthlyLeads,
    monthlyConversions,
    monthlyRevenue,
    monthlyProfit,
    roi,
    paybackDays,
    isOverLimit,
  } = calculations;

  return (
    <Box
      bg={bgColor}
      border="1px"
      borderColor={borderColor}
      borderRadius="lg"
      p={6}
      shadow="md"
    >
      <VStack spacing={6} align="stretch">
        <Heading size="lg" textAlign="center">
          ROI Calculator
        </Heading>

        <Text fontSize="sm" color="gray.600" textAlign="center">
          Calculate your potential return on investment with LeadTap
        </Text>

        {/* Input Controls */}
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
          <Box>
            <Text fontSize="sm" fontWeight="medium" mb={2}>
              Queries per Day
            </Text>
            <Input
              type="number"
              value={queriesPerDay}
              onChange={(e) => setQueriesPerDay(Number(e.target.value))}
              min={1}
              max={currentPlan.queries}
            />
            <Text fontSize="xs" color="gray.500" mt={1}>
              Max: {currentPlan.queries} (Free plan: 5, Pro: 50, Business: 200)
            </Text>
          </Box>

          <Box>
            <Text fontSize="sm" fontWeight="medium" mb={2}>
              Leads per Query
            </Text>
            <Input
              type="number"
              value={leadsPerQuery}
              onChange={(e) => setLeadsPerQuery(Number(e.target.value))}
              min={1}
              max={100}
            />
            <Text fontSize="xs" color="gray.500" mt={1}>
              Average leads found per search
            </Text>
          </Box>

          <Box>
            <Text fontSize="sm" fontWeight="medium" mb={2}>
              Conversion Rate (%)
            </Text>
            <Input
              type="number"
              value={conversionRate}
              onChange={(e) => setConversionRate(Number(e.target.value))}
              min={0.1}
              max={10}
              step={0.1}
            />
            <Text fontSize="xs" color="gray.500" mt={1}>
              Percentage of leads that convert to customers
            </Text>
          </Box>

          <Box>
            <Text fontSize="sm" fontWeight="medium" mb={2}>
              Average Deal Value ($)
            </Text>
            <Input
              type="number"
              value={averageDealValue}
              onChange={(e) => setAverageDealValue(Number(e.target.value))}
              min={10}
              max={10000}
            />
            <Text fontSize="xs" color="gray.500" mt={1}>
              Average revenue per customer
            </Text>
          </Box>
        </SimpleGrid>

        {/* Over Limit Warning */}
        {isOverLimit && (
          <Alert status="warning" borderRadius="md">
            <AlertIcon />
            <Box>
              <AlertTitle>Plan Limit Exceeded</AlertTitle>
              <AlertDescription>
                Your queries exceed the {currentPlan.name} plan limit. Consider upgrading for more capacity.
              </AlertDescription>
            </Box>
          </Alert>
        )}

        <Divider />

        {/* Results */}
        <Box>
          <Text fontSize="lg" fontWeight="bold" mb={4}>
            Your Monthly Results
          </Text>
          
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
            <Stat>
              <StatLabel>Monthly Leads</StatLabel>
              <StatNumber fontSize="2xl" color="blue.500">
                {monthlyLeads.toLocaleString()}
              </StatNumber>
              <StatHelpText>
                {queriesPerDay} queries/day × {leadsPerQuery} leads/query × 30 days
              </StatHelpText>
            </Stat>

            <Stat>
              <StatLabel>Monthly Revenue</StatLabel>
              <StatNumber fontSize="2xl" color="green.500">
                {formatCurrency(monthlyRevenue)}
              </StatNumber>
              <StatHelpText>
                {monthlyConversions.toFixed(0)} conversions × ${averageDealValue}
              </StatHelpText>
            </Stat>

            <Stat>
              <StatLabel>Monthly Profit</StatLabel>
              <StatNumber fontSize="2xl" color={monthlyProfit > 0 ? 'green.500' : 'red.500'}>
                {formatCurrency(monthlyProfit)}
              </StatNumber>
              <StatHelpText>
                Revenue - ${currentPlan.cost}/month plan cost
              </StatHelpText>
            </Stat>

            <Stat>
              <StatLabel>ROI</StatLabel>
              <StatNumber fontSize="2xl" color={roi > 0 ? 'green.500' : 'red.500'}>
                {roi > 0 ? '+' : ''}{roi.toFixed(0)}%
              </StatNumber>
              <StatHelpText>
                {roi > 0 ? 'Excellent return on investment!' : 'Consider adjusting your strategy'}
              </StatHelpText>
            </Stat>
          </SimpleGrid>

          {monthlyProfit > 0 && (
            <Alert status="success" mt={4} borderRadius="md">
              <AlertIcon />
              <Box>
                <AlertTitle>Great Investment!</AlertTitle>
                <AlertDescription>
                  You'll break even in {paybackDays.toFixed(1)} days and generate {formatCurrency(monthlyProfit)} in monthly profit.
                </AlertDescription>
              </Box>
            </Alert>
          )}
        </Box>

        {/* Plan Features */}
        <Box>
          <Text fontSize="sm" fontWeight="medium" mb={2}>
            {currentPlan.name} Plan Features:
          </Text>
          <VStack spacing={1} align="stretch">
            <HStack spacing={2}>
              <Badge colorScheme="green" size="sm">✓</Badge>
              <Text fontSize="sm">Google Maps scraping</Text>
            </HStack>
            <HStack spacing={2}>
              <Badge colorScheme="green" size="sm">✓</Badge>
              <Text fontSize="sm">Lead scoring & filtering</Text>
            </HStack>
            <HStack spacing={2}>
              <Badge colorScheme="green" size="sm">✓</Badge>
              <Text fontSize="sm">Export to CSV/Excel</Text>
            </HStack>
            <HStack spacing={2}>
              <Badge colorScheme="green" size="sm">✓</Badge>
              <Text fontSize="sm">Analytics dashboard</Text>
            </HStack>
          </VStack>
        </Box>
      </VStack>
    </Box>
  );
};

export default ROICalculator; 