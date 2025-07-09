import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Heading, Text, Spinner, Table, Thead, Tr, Th, Tbody, Td, Alert, AlertIcon, Container } from '@chakra-ui/react';
import { getSharedJob } from '../api';

const SharedJob: React.FC = () => {
  const { token } = useParams<{ token: string }>();
  const [job, setJob] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    getSharedJob(token)
      .then(setJob)
      .catch(e => setError(e.message || 'Not found'))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) return <Spinner />;
  if (error) return <Alert status="error"><AlertIcon />{error}</Alert>;
  if (!job) return <Text>Job not found.</Text>;

  let results: any[] = [];
  try {
    results = job.result ? JSON.parse(job.result) : [];
  } catch {
    results = [];
  }

  return (
    <Container maxW="container.md" py={8}>
      <Box bg="white" p={8} borderRadius="lg" boxShadow="md">
        <Heading size="lg" mb={4}>Shared Job Results</Heading>
        <Text mb={2}><b>Queries:</b> {job.queries}</Text>
        <Text mb={2}><b>Status:</b> {job.status}</Text>
        <Text mb={4}><b>Created:</b> {new Date(job.created_at).toLocaleString()}</Text>
        <Heading size="md" mb={2}>Results</Heading>
        {results.length === 0 ? (
          <Text color="gray.500">No results to display.</Text>
        ) : (
          <Table size="sm">
            <Thead>
              <Tr>
                {Object.keys(results[0]).map((key) => (
                  <Th key={key}>{key}</Th>
                ))}
              </Tr>
            </Thead>
            <Tbody>
              {results.map((row, idx) => (
                <Tr key={idx}>
                  {Object.values(row).map((val, i) => (
                    <Td key={i}>{String(val)}</Td>
                  ))}
                </Tr>
              ))}
            </Tbody>
          </Table>
        )}
      </Box>
    </Container>
  );
};

export default SharedJob; 