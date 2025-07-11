import React from 'react';
import { 
  Box, 
  Table, 
  Thead, 
  Tbody, 
  Tr, 
  Th, 
  Td, 
  Button, 
  VStack, 
  Text,
  Badge,
  HStack,
  Icon,
  useColorModeValue
} from '@chakra-ui/react';
import { CheckIcon, StarIcon } from '@chakra-ui/icons';

const PricingTable = () => {
  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: 'forever',
      queries: '10 queries/day',
      features: [
        'Basic Google Maps scraping',
        'CSV export format',
        'Email support',
        'Basic search filters'
      ],
      popular: false,
      color: 'gray'
    },
    {
      name: 'Pro',
      price: '$9',
      period: 'month',
      queries: '100 queries/day',
      features: [
        'Advanced scraping capabilities',
        'CSV, JSON, Excel export',
        'Priority email support',
        'Advanced search filters',
        'API access',
        'Data validation'
      ],
      popular: true,
      color: 'purple'
    },
    {
      name: 'Business',
      price: '$49',
      period: 'month',
      queries: 'Unlimited queries',
      features: [
        'Enterprise-level scraping',
        'All export formats',
        '24/7 phone support',
        'Custom integrations',
        'White-label options',
        'Dedicated account manager'
      ],
      popular: false,
      color: 'blue'
    }
  ];

  return (
    <Box overflowX="auto" className="fade-in-up">
      <Table variant="simple" size="lg">
        <Thead>
          <Tr>
            <Th border="none" color="gray.400" fontSize="md">Plan</Th>
            <Th border="none" color="gray.400" fontSize="md">Price</Th>
            <Th border="none" color="gray.400" fontSize="md">Queries</Th>
            <Th border="none" color="gray.400" fontSize="md">Features</Th>
            <Th border="none" color="gray.400" fontSize="md">Action</Th>
          </Tr>
          <Tr>
            <Th border="none"></Th>
            <Th border="none" colSpan={4}>
              <HStack spacing={8} justify="center">
                <HStack spacing={2}><Text fontWeight="bold">Google Maps</Text></HStack>
                <HStack spacing={2}><Text fontWeight="bold">Facebook</Text></HStack>
                <HStack spacing={2}><Text fontWeight="bold">Instagram</Text></HStack>
                <HStack spacing={2}><Text fontWeight="bold">WhatsApp</Text></HStack>
              </HStack>
            </Th>
          </Tr>
          <Tr>
            <Th border="none"></Th>
            <Td border="none" colSpan={4}>
              <HStack spacing={8} justify="center">
                {/* Free */}
                <HStack spacing={2}>
                  <Icon as={CheckIcon} color="green.400" />
                  <Text color="gray.400" fontSize="sm">Included</Text>
                </HStack>
                <HStack spacing={2}>
                  <Text color="gray.400" fontSize="sm">-</Text>
                </HStack>
                <HStack spacing={2}>
                  <Text color="gray.400" fontSize="sm">-</Text>
                </HStack>
                <HStack spacing={2}>
                  <Text color="gray.400" fontSize="sm">-</Text>
                </HStack>
              </HStack>
            </Td>
          </Tr>
          <Tr>
            <Th border="none"></Th>
            <Td border="none" colSpan={4}>
              <HStack spacing={8} justify="center">
                {/* Pro */}
                <HStack spacing={2}>
                  <Icon as={CheckIcon} color="green.400" />
                  <Text color="gray.400" fontSize="sm">Included</Text>
                </HStack>
                <HStack spacing={2}>
                  <Icon as={CheckIcon} color="green.400" />
                  <Text color="gray.400" fontSize="sm">Included</Text>
                </HStack>
                <HStack spacing={2}>
                  <Icon as={CheckIcon} color="green.400" />
                  <Text color="gray.400" fontSize="sm">Included</Text>
                </HStack>
                <HStack spacing={2}>
                  <Text color="gray.400" fontSize="sm">-</Text>
                </HStack>
              </HStack>
            </Td>
          </Tr>
          <Tr>
            <Th border="none"></Th>
            <Td border="none" colSpan={4}>
              <HStack spacing={8} justify="center">
                {/* Business */}
                <HStack spacing={2}>
                  <Icon as={CheckIcon} color="green.400" />
                  <Text color="gray.400" fontSize="sm">Included</Text>
                </HStack>
                <HStack spacing={2}>
                  <Icon as={CheckIcon} color="green.400" />
                  <Text color="gray.400" fontSize="sm">Included</Text>
                </HStack>
                <HStack spacing={2}>
                  <Icon as={CheckIcon} color="green.400" />
                  <Text color="gray.400" fontSize="sm">Included</Text>
                </HStack>
                <HStack spacing={2}>
                  <Icon as={CheckIcon} color="green.400" />
                  <Text color="gray.400" fontSize="sm">Included</Text>
                </HStack>
              </HStack>
            </Td>
          </Tr>
        </Thead>
        <Tbody>
          {plans.map((plan, index) => (
            <Tr 
              key={plan.name}
              _hover={{ bg: 'rgba(255, 255, 255, 0.02)' }}
              transition="all 0.3s ease"
            >
              <Td border="none">
                <VStack align="start" spacing={2}>
                  <HStack spacing={2}>
                    <Text fontWeight="bold" fontSize="lg">
                      {plan.name}
                    </Text>
                    {plan.popular && (
                      <Badge colorScheme="purple" size="sm">
                        <StarIcon mr={1} />
                        Popular
                      </Badge>
                    )}
                  </HStack>
                </VStack>
              </Td>
              <Td border="none">
                <VStack align="start" spacing={1}>
                  <Text fontSize="2xl" fontWeight="bold" className="gradient-text">
                    {plan.price}
                  </Text>
                  <Text color="gray.400" fontSize="sm">
                    per {plan.period}
                  </Text>
                </VStack>
              </Td>
              <Td border="none">
                <Text color="gray.300" fontWeight="medium">
                  {plan.queries}
                </Text>
              </Td>
              <Td border="none">
                <VStack align="start" spacing={2}>
                  {plan.features.map((feature, featureIndex) => (
                    <HStack key={featureIndex} spacing={2}>
                      <Icon as={CheckIcon} color="success.green" boxSize={4} />
                      <Text color="gray.400" fontSize="sm">
                        {feature}
                      </Text>
                    </HStack>
                  ))}
                </VStack>
              </Td>
              <Td border="none">
                <Button 
                  colorScheme={plan.color}
                  variant={plan.popular ? "solid" : "outline"}
                  size="sm"
                  bg={plan.popular ? "linear-gradient(135deg, brand.500 0%, brand.600 100%)" : "transparent"}
                  _hover={{
                    bg: plan.popular 
                      ? "linear-gradient(135deg, brand.600 0%, brand.700 100%)"
                      : "brand.500",
                    color: "white",
                    transform: "translateY(-2px)",
                    boxShadow: "0 8px 25px rgba(99, 102, 241, 0.4)"
                  }}
                  transition="all 0.3s ease"
                >
                  {plan.name === 'Free' ? 'Current' : 'Upgrade'}
                </Button>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
};

export default PricingTable; 