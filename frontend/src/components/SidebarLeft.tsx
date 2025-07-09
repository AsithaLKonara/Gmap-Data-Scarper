import React, { useState } from 'react';
import { Box, VStack, Input, Button, List, ListItem, IconButton, HStack, Heading, Spinner, Text } from '@chakra-ui/react';
import { CloseIcon } from '@chakra-ui/icons';
import * as api from '../api';

const SidebarLeft = ({ onJobCreated }: { onJobCreated: (jobId: number) => void }) => {
  const [query, setQuery] = useState('');
  const [queries, setQueries] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addQuery = () => {
    if (query.trim() && !queries.includes(query.trim())) {
      setQueries([query.trim(), ...queries]);
      setQuery('');
    }
  };

  const removeQuery = (q: string) => {
    setQueries(queries.filter(item => item !== q));
  };

  const handleSubmit = async () => {
    if (!queries.length) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.createJob(queries);
      onJobCreated(res.job_id);
    } catch (e: any) {
      setError(e.message);
    }
    setLoading(false);
  };

  return (
    <Box w={['100%', '300px']} p={4} bg="gray.100" minH="100vh" borderRightWidth={1}>
      <Heading as="h3" size="md" mb={4}>Search Queries</Heading>
      <HStack mb={4}>
        <Input
          placeholder="Enter search query"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && addQuery()}
        />
        <Button onClick={addQuery} colorScheme="teal">Add</Button>
      </HStack>
      <List spacing={2} mb={4}>
        {queries.map(q => (
          <ListItem key={q} display="flex" alignItems="center" justifyContent="space-between" bg="white" p={2} borderRadius="md" boxShadow="sm">
            <span>{q}</span>
            <IconButton aria-label="Remove" icon={<CloseIcon />} size="xs" onClick={() => removeQuery(q)} />
          </ListItem>
        ))}
      </List>
      <Button colorScheme="teal" width="100%" onClick={handleSubmit} isLoading={loading} isDisabled={!queries.length} mb={2}>
        Start Scraping
      </Button>
      {error && <Text color="red.500">{error}</Text>}
    </Box>
  );
};

export default SidebarLeft; 