import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Heading, Text, Spinner, Alert, AlertIcon, Container, VStack } from '@chakra-ui/react';
import { getSharedLead } from '../api';

const SharedLead: React.FC = () => {
  const { token } = useParams<{ token: string }>();
  const [lead, setLead] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    getSharedLead(token)
      .then(setLead)
      .catch(e => setError(e.message || 'Not found'))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) return <Spinner />;
  if (error) return <Alert status="error"><AlertIcon />{error}</Alert>;
  if (!lead) return <Text>Lead not found.</Text>;

  return (
    <Container maxW="container.sm" py={8}>
      <Box bg="white" p={8} borderRadius="lg" boxShadow="md">
        <Heading size="lg" mb={4}>Shared Lead</Heading>
        <VStack align="start" spacing={2}>
          <Text><b>Name:</b> {lead.name}</Text>
          <Text><b>Email:</b> {lead.email}</Text>
          <Text><b>Phone:</b> {lead.phone || '-'}</Text>
          <Text><b>Company:</b> {lead.company || '-'}</Text>
          <Text><b>Status:</b> {lead.status}</Text>
          <Text><b>Source:</b> {lead.source}</Text>
          <Text><b>Notes:</b> {lead.notes || '-'}</Text>
          <Text><b>Created:</b> {new Date(lead.created_at).toLocaleString()}</Text>
          <Text><b>Updated:</b> {new Date(lead.updated_at).toLocaleString()}</Text>
        </VStack>
      </Box>
    </Container>
  );
};

export default SharedLead; 