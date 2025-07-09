import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Input,
  InputGroup,
  InputLeftAddon,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  SliderMark,
  Button,
  Card,
  CardBody,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Badge,
  useColorModeValue,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Divider,
  SimpleGrid,
} from '@chakra-ui/react';

interface ROICalculatorProps {
  planType?: 'free' | 'pro' | 'business';
}

const ROICalculator: React.FC<ROICalculatorProps> = ({ planType = 'pro' }) => {
  const [queriesPerDay, setQueriesPerDay] = useState(10);
  const [leadsPerQuery, setLeadsPerQuery] = useState(20);
  const [conversionRate, setConversionRate] = useState(0.05);
  const [averageDealValue, setAverageDealValue] = useState(100);
  const [planCost, setPlanCost] = useState(29);

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Plan configurations
  const planConfigs = {
    free: {
      name: 'Free',
      cost: 0,
      maxQueries: 10,
      features: ['Basic CRM', 'CSV Export', 'Email Support']
    },
    pro: {
      name: 'Pro',
      cost: 29,
      maxQueries: 100,
      features: ['Advanced CRM', 'All Export Formats', 'Priority Support', 'Analytics', 'Team Management']
    },
    business: {
      name: 'Business',
      cost: 99,
      maxQueries: 1000,
      features: ['Enterprise CRM', 'White-label', 'API Access', '24/7 Support', 'Admin Dashboard']
    }
  };

  const currentPlan = planConfigs[planType];

  // Calculate metrics
  const monthlyQueries = queriesPerDay * 30;
  const monthlyLeads = monthlyQueries * leadsPerQuery;
  const monthlyConversions = monthlyLeads * conversionRate;
  const monthlyRevenue = monthlyConversions * averageDealValue;
  const monthlyProfit = monthlyRevenue - currentPlan.cost;
  const roi = monthlyProfit > 0 ? (monthlyProfit / currentPlan.cost) * 100 : 0;
  const paybackDays = monthlyProfit > 0 ? currentPlan.cost / (monthlyProfit / 30) : 0;

  // Check if queries exceed plan limit
  const isOverLimit = monthlyQueries > currentPlan.maxQueries;

  useEffect(() => {
    setPlanCost(currentPlan.cost);
  }, [planType, currentPlan.cost]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <Card bg={bgColor} border="1px" borderColor={borderColor} shadow="md">
      <CardBody>
        <VStack spacing={6} align="stretch">
          <Box>
            <Text fontSize="lg" fontWeight="bold" mb={2}>
              ROI Calculator
            </Text>
            <Text fontSize="sm" color="gray.600">
              See how much revenue you can generate with LeadTap
            </Text>
          </Box>

          {/* Input Controls */}
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
            <Box>
              <Text fontSize="sm" fontWeight="medium" mb={2}>
                Queries per Day
              </Text>
              <InputGroup>
                <InputLeftAddon>🔍</InputLeftAddon>
                <Input
                  type="number"
                  value={queriesPerDay}
                  onChange={(e) => setQueriesPerDay(Number(e.target.value))}
                  min={1}
                  max={currentPlan.maxQueries / 30}
                />
              </InputGroup>
              <Text fontSize="xs" color="gray.500" mt={1}>
                Max: {currentPlan.maxQueries / 30} per day
              </Text>
            </Box>

            <Box>
              <Text fontSize="sm" fontWeight="medium" mb={2}>
                Leads per Query
              </Text>
              <InputGroup>
                <InputLeftAddon>📊</InputLeftAddon>
                <Input
                  type="number"
                  value={leadsPerQuery}
                  onChange={(e) => setLeadsPerQuery(Number(e.target.value))}
                  min={1}
                  max={100}
                />
              </InputGroup>
              <Text fontSize="xs" color="gray.500" mt={1}>
                Average: 15-25 leads per query
              </Text>
            </Box>
          </SimpleGrid>

          <Box>
            <Text fontSize="sm" fontWeight="medium" mb={2}>
              Conversion Rate
            </Text>
            <Slider
              value={conversionRate}
              onChange={setConversionRate}
              min={0.01}
              max={0.20}
              step={0.01}
              colorScheme="blue"
            >
              <SliderMark value={0.01} mt={2} fontSize="xs">1%</SliderMark>
              <SliderMark value={0.05} mt={2} fontSize="xs">5%</SliderMark>
              <SliderMark value={0.10} mt={2} fontSize="xs">10%</SliderMark>
              <SliderMark value={0.20} mt={2} fontSize="xs">20%</SliderMark>
              <SliderTrack>
                <SliderFilledTrack />
              </SliderTrack>
              <SliderThumb />
            </Slider>
            <Text fontSize="sm" color="gray.600" mt={1}>
              {formatPercentage(conversionRate)} of leads convert to customers
            </Text>
          </Box>

          <Box>
            <Text fontSize="sm" fontWeight="medium" mb={2}>
              Average Deal Value
            </Text>
            <InputGroup>
              <InputLeftAddon>$</InputLeftAddon>
              <Input
                type="number"
                value={averageDealValue}
                onChange={(e) => setAverageDealValue(Number(e.target.value))}
                min={10}
                max={10000}
              />
            </InputGroup>
            <Text fontSize="xs" color="gray.500" mt={1}>
              Average revenue per customer
            </Text>
          </Box>

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
              {currentPlan.features.map((feature, index) => (
                <HStack key={index} spacing={2}>
                  <Badge colorScheme="green" size="sm">✓</Badge>
                  <Text fontSize="sm">{feature}</Text>
                </HStack>
              ))}
            </VStack>
          </Box>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default ROICalculator; 