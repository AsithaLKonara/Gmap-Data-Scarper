import React from 'react';
import { Box, Heading, Text, Button } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

const NotFound = () => (
  <Box minH="60vh" display="flex" flexDirection="column" alignItems="center" justifyContent="center">
    <Heading as="h1" size="2xl" mb={4}>404</Heading>
    <Text fontSize="xl" color="gray.600" mb={6}>Page Not Found</Text>
    <Button as={RouterLink} to="/" colorScheme="teal">Go Home</Button>
  </Box>
);

export default NotFound; 