import React, { useEffect } from 'react';
import { Box, Heading, Text, Button } from '@chakra-ui/react';
import { useAuth } from '../hooks/useAuth';
import { Link as RouterLink } from 'react-router-dom';

const PaymentSuccess = () => {
  const { user, loading } = useAuth();
  useEffect(() => {
    // Optionally, reload user info here if needed
    // (handled by AuthProvider on token change)
  }, []);
  return (
    <Box minH="60vh" display="flex" flexDirection="column" alignItems="center" justifyContent="center">
      <Heading as="h1" size="xl" mb={4}>Payment Successful!</Heading>
      <Text fontSize="lg" color="green.600" mb={6}>Your plan has been upgraded. Enjoy premium features!</Text>
      <Button as={RouterLink} to="/dashboard" colorScheme="teal">Go to Dashboard</Button>
    </Box>
  );
};

export default PaymentSuccess; 