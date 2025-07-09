import React, { useEffect, useState } from 'react';
import { Box, Heading, Table, Thead, Tr, Th, Tbody, Td, Spinner, Alert, AlertIcon, Container, Text } from '@chakra-ui/react';
import { getMyAuditLogs } from '../api';

const AuditLog: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getMyAuditLogs()
      .then(setLogs)
      .catch(e => setError(e.message || 'Failed to load logs'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Container maxW="container.lg" py={8}>
      <Box bg="white" p={8} borderRadius="lg" boxShadow="md">
        <Heading size="lg" mb={4}>Activity History</Heading>
        {loading ? <Spinner /> : error ? <Alert status="error"><AlertIcon />{error}</Alert> : logs.length === 0 ? <Text color="gray.500">No activity found.</Text> : (
          <Table size="sm">
            <Thead>
              <Tr>
                <Th>Action</Th>
                <Th>Target</Th>
                <Th>Details</Th>
                <Th>Timestamp</Th>
              </Tr>
            </Thead>
            <Tbody>
              {logs.map(log => (
                <Tr key={log.id}>
                  <Td>{log.action}</Td>
                  <Td>{log.target_type}{log.target_id ? ` #${log.target_id}` : ''}</Td>
                  <Td><pre style={{ whiteSpace: 'pre-wrap', fontSize: 12 }}>{log.details}</pre></Td>
                  <Td>{new Date(log.timestamp).toLocaleString()}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        )}
      </Box>
    </Container>
  );
};

export default AuditLog; 