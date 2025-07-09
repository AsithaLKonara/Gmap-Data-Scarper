import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  Input,
  VStack,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Text,
  useColorModeValue,
} from '@chakra-ui/react';
import * as api from '../api';

const KnowledgeBase: React.FC = () => {
  const [faqs, setFaqs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadFaqs();
  }, []);

  const loadFaqs = async () => {
    setLoading(true);
    setError(null);
    try {
      // TODO: Replace with real API call when backend is ready
      const response = await api.getFaqs();
      setFaqs(response);
    } catch (err: any) {
      setError('Failed to load FAQs');
    } finally {
      setLoading(false);
    }
  };

  const filteredFaqs = faqs.filter(faq =>
    faq.question.toLowerCase().includes(search.toLowerCase()) ||
    faq.answer.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <Box p={8}><Text>Loading FAQs...</Text></Box>;
  if (error) return <Box p={8}><Text color="red.500">{error}</Text></Box>;

  return (
    <Box minH="100vh" bg={useColorModeValue('gray.100', 'gray.800')} data-tour="knowledge-base-main">
      <Container maxW="container.md" py={8} data-tour="knowledge-base-content">
        <Heading size="lg" mb={6} className="gradient-text" data-tour="knowledge-base-title">Knowledge Base & FAQ</Heading>
        <Input
          placeholder="Search FAQs..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          mb={6}
        />
        <VStack align="stretch" spacing={4}>
          <Accordion allowToggle>
            {filteredFaqs.map((faq, idx) => (
              <AccordionItem key={idx}>
                <AccordionButton>
                  <Box flex="1" textAlign="left">{faq.question}</Box>
                  <AccordionIcon />
                </AccordionButton>
                <AccordionPanel pb={4}>{faq.answer}</AccordionPanel>
              </AccordionItem>
            ))}
          </Accordion>
        </VStack>
      </Container>
    </Box>
  );
};

export default KnowledgeBase; 