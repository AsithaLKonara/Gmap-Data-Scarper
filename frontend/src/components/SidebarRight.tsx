import React, { useEffect, useState } from 'react';
import { Box, Heading, Button, Text, Spinner, Table, Thead, Tbody, Tr, Th, Td } from '@chakra-ui/react';
import * as api from '../api';

const SidebarRight = ({ jobId }: { jobId: number | null }) => {
  const [status, setStatus] = useState<string>('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [csvReady, setCsvReady] = useState(false);

  useEffect(() => {
    if (!jobId) return;
    setLoading(true);
    setStatus('pending');
    setResults([]);
    setCsvReady(false);
    const interval = setInterval(async () => {
      try {
        const s = await api.getJobStatus(jobId);
        setStatus(s.status);
        if (s.status === 'completed') {
          const r = await api.getJobResults(jobId);
          setResults(r.result);
          setCsvReady(true);
          setLoading(false);
          clearInterval(interval);
        } else if (s.status === 'failed') {
          setStatus('failed');
          setLoading(false);
          clearInterval(interval);
        }
      } catch {
        setStatus('error');
        setLoading(false);
        clearInterval(interval);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [jobId]);

  return (
    <Box w={['100%', '350px']} p={4} bg="gray.100" minH="100vh" borderLeftWidth={1}>
      <Heading as="h3" size="md" mb={4}>Collected Data</Heading>
      {loading && <Spinner />}
      {status === 'completed' && results.length > 0 && (
        <Table size="sm" bg="white" borderRadius="md" boxShadow="sm" mb={2}>
          <Thead>
            <Tr>
              {Object.keys(results[0]).map(key => <Th key={key}>{key}</Th>)}
            </Tr>
          </Thead>
          <Tbody>
            {results.map((row, i) => (
              <Tr key={i}>
                {Object.values(row).map((val, j) => <Td key={j}>{val}</Td>)}
              </Tr>
            ))}
          </Tbody>
        </Table>
      )}
      {status === 'pending' && <Text>Scraping in progress...</Text>}
      {status === 'failed' && <Text color="red.500">Scraping failed.</Text>}
      <Button colorScheme="teal" mt={4} width="100%" as="a" href={jobId && csvReady ? api.getJobCSV(jobId) : undefined} isDisabled={!csvReady} download>
        Download CSV
      </Button>
    </Box>
  );
};

export default SidebarRight; 