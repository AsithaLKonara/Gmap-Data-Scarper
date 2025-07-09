import React from 'react';
import { Box, Heading, Text, Container, VStack } from '@chakra-ui/react';
import PricingTable from '../components/PricingTable';

const Pricing = () => (
  <Box py={20} minH="calc(100vh - 64px)">
    <Container maxW="1200px">
      <VStack spacing={16}>
        <VStack spacing={6} textAlign="center">
          <Heading size="3xl" className="gradient-text">
            LeadTap Pricing
          </Heading>
          <Text color="gray.400" fontSize="xl" maxW="600px">
            Choose the perfect plan for your data extraction needs. 
            Start free and scale as you grow.
          </Text>
        </VStack>
        
        <PricingTable />
        
        <VStack spacing={4} textAlign="center" pt={8}>
          <Text color="gray.400" fontSize="md">
            All plans include our core features and 99.9% uptime guarantee
          </Text>
          <Text color="gray.500" fontSize="sm">
            Need a custom plan? Contact our sales team for enterprise solutions
          </Text>
        </VStack>
      </VStack>
    </Container>
  </Box>
);

export default Pricing; 