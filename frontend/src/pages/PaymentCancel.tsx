import React from 'react';
import { Box, Heading, Text, Button } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

const PaymentCancel = () => (
  <Box minH="60vh" display="flex" flexDirection="column" alignItems="center" justifyContent="center">
    <Heading as="h1" size="xl" mb={4}>Payment Cancelled</Heading>
    <Text fontSize="lg" color="red.600" mb={6}>Your payment was cancelled. You can try upgrading again anytime.</Text>
    <Button as={RouterLink} to="/dashboard" colorScheme="teal">Back to Dashboard</Button>
  </Box>
);

export default PaymentCancel; 