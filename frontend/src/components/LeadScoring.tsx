import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Badge,
  Button,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Select,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  useColorModeValue,
  Tooltip,
  IconButton,
  useToast,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import {
  FiTrendingUp,
  FiUsers,
  FiTarget,
  FiStar,
  FiFilter,
  FiEdit,
  FiEye,
} from 'react-icons/fi';

interface Lead {
  id: number;
  name: string;
  email: string;
  phone?: string;
  company?: string;
  website?: string;
  source: string;
  status: string;
  score: number;
  enriched: boolean;
  last_contacted?: string;
  engagement_level: 'high' | 'medium' | 'low';
  conversion_probability: number;
  tags: string[];
  notes?: string;
}

interface ScoringRule {
  id: string;
  field: string;
  label: string;
  points: number;
}

interface LeadScoringProps {
  leads: Lead[];
  onLeadUpdate: (leadId: number, updates: Partial<Lead>) => void;
}

const LeadScoring: React.FC<LeadScoringProps> = ({ leads, onLeadUpdate }) => {
  const { t } = useTranslation();
  const toast = useToast();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  const [filter, setFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [scoringRules, setScoringRules] = useState<ScoringRule[]>([
    { id: 'email', field: 'email', label: 'Has Email', points: 15 },
    { id: 'phone', field: 'phone', label: 'Has Phone', points: 10 },
    { id: 'website', field: 'website', label: 'Has Website', points: 5 },
    { id: 'company', field: 'company', label: 'Has Company', points: 10 },
    { id: 'enriched', field: 'enriched', label: 'Is Enriched', points: 15 },
  ]);

  const scoreBadge = (score: number) => {
    if (score >= 80) return <Badge colorScheme="green">Hot</Badge>;
    if (score >= 60) return <Badge colorScheme="blue">Warm</Badge>;
    if (score >= 40) return <Badge colorScheme="yellow">Cold</Badge>;
    return <Badge colorScheme="gray">Poor</Badge>;
  };

  // Calculate lead score based on user-defined rules
  const calculateLeadScore = (lead: Lead): number => {
    let score = 0;
    scoringRules.forEach((rule) => {
      if (rule.field === 'email' && lead.email) score += rule.points;
      if (rule.field === 'phone' && lead.phone) score += rule.points;
      if (rule.field === 'website' && lead.website) score += rule.points;
      if (rule.field === 'company' && lead.company) score += rule.points;
      if (rule.field === 'enriched' && lead.enriched) score += rule.points;
      if (rule.field === 'recent_contact' && lead.last_contacted) {
        const daysSince = Math.floor(
          (Date.now() - new Date(lead.last_contacted).getTime()) / (1000 * 60 * 60 * 24)
        );
        if (daysSince <= 7) score += rule.points;
      }
      if (rule.field === 'engagement_high' && lead.engagement_level === 'high') score += rule.points;
      if (rule.field === 'source_facebook' && lead.source === 'facebook') score += rule.points;
      if (rule.field === 'source_gmaps' && lead.source === 'google_maps') score += rule.points;
      if (rule.field === 'source_whatsapp' && lead.source === 'whatsapp') score += rule.points;
    });
    return Math.min(score, 100);
  };

  // Filter leads by score
  const filteredLeads = leads.filter((lead) => {
    const score = calculateLeadScore(lead);
    if (filter === 'high') return score >= 80;
    if (filter === 'medium') return score >= 60 && score < 80;
    if (filter === 'low') return score < 60;
    return true;
  });

  // Calculate statistics
  const totalLeads = leads.length;
  const highScoreLeads = leads.filter((lead) => calculateLeadScore(lead) >= 80).length;
  const mediumScoreLeads = leads.filter((lead) => {
    const score = calculateLeadScore(lead);
    return score >= 60 && score < 80;
  }).length;
  const lowScoreLeads = leads.filter((lead) => calculateLeadScore(lead) < 60).length;
  const averageScore =
    leads.length > 0
      ? leads.reduce((sum, lead) => sum + calculateLeadScore(lead), 0) / leads.length
      : 0;

  const handleUpdateScoringRules = (newRules: ScoringRule[]) => {
    setScoringRules(newRules);
    toast({
      title: 'Scoring rules updated',
      status: 'success',
      duration: 3000,
    });
  };

  return (
    <Box>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>Lead Scoring</Heading>
          <Text color={textColor}>
            Automatically score and prioritize your leads based on custom criteria
          </Text>
        </Box>

        {/* Statistics Cards */}
        <SimpleGrid columns={{ base: 1, md: 4 }} spacing={6}>
          <Stat>
            <StatLabel>Total Leads</StatLabel>
            <StatNumber>{totalLeads}</StatNumber>
            <StatHelpText>All leads in your CRM</StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>High Score Leads</StatLabel>
            <StatNumber color="green.500">{highScoreLeads}</StatNumber>
            <StatHelpText>Score ≥ 80</StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Medium Score Leads</StatLabel>
            <StatNumber color="blue.500">{mediumScoreLeads}</StatNumber>
            <StatHelpText>Score 60-79</StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Average Score</StatLabel>
            <StatNumber color="purple.500">{averageScore.toFixed(1)}</StatNumber>
            <StatHelpText>Overall lead quality</StatHelpText>
          </Stat>
        </SimpleGrid>

        {/* Scoring Rules */}
        <Box
          bg={bgColor}
          border="1px"
          borderColor={borderColor}
          borderRadius="lg"
          p={6}
        >
          <HStack justify="space-between" mb={4}>
            <Heading size="md">Scoring Rules</Heading>
            <Button size="sm" leftIcon={<FiEdit />}>
              Edit Rules
            </Button>
          </HStack>

          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
            {scoringRules.map((rule) => (
              <Box
                key={rule.id}
                p={4}
                border="1px"
                borderColor={borderColor}
                borderRadius="md"
              >
                <HStack justify="space-between">
                  <Text fontWeight="medium">{rule.label}</Text>
                  <Badge colorScheme="blue">{rule.points} pts</Badge>
                </HStack>
              </Box>
            ))}
          </SimpleGrid>
        </Box>

        {/* Filter Controls */}
        <HStack spacing={4}>
          <Text fontWeight="medium">Filter by Score:</Text>
          <Select
            value={filter}
            onChange={(e) => setFilter(e.target.value as 'all' | 'high' | 'medium' | 'low')}
            maxW="200px"
          >
            <option value="all">All Leads</option>
            <option value="high">High Score (≥80)</option>
            <option value="medium">Medium Score (60-79)</option>
            <option value="low">Low Score (&lt;60)</option>
          </Select>
        </HStack>

        {/* Leads Table */}
        <Box
          bg={bgColor}
          border="1px"
          borderColor={borderColor}
          borderRadius="lg"
          overflow="hidden"
        >
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Lead</Th>
                <Th>Company</Th>
                <Th>Source</Th>
                <Th>Score</Th>
                <Th>Status</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {filteredLeads.map((lead) => {
                const score = calculateLeadScore(lead);
                return (
                  <Tr key={lead.id}>
                    <Td>
                      <VStack align="start" spacing={1}>
                        <Text fontWeight="medium">{lead.name}</Text>
                        <Text fontSize="sm" color={textColor}>
                          {lead.email}
                        </Text>
                      </VStack>
                    </Td>
                    <Td>{lead.company || '-'}</Td>
                    <Td>
                      <Badge variant="outline">{lead.source}</Badge>
                    </Td>
                    <Td>
                      <HStack spacing={2}>
                        {scoreBadge(score)}
                        <Text fontSize="sm">{score}</Text>
                      </HStack>
                    </Td>
                    <Td>
                      <Badge colorScheme={getStatusColor(lead.status)}>
                        {lead.status}
                      </Badge>
                    </Td>
                    <Td>
                      <HStack spacing={1}>
                        <IconButton
                          size="sm"
                          variant="ghost"
                          icon={<FiEye />}
                          aria-label="View lead details"
                        />
                        <IconButton
                          size="sm"
                          variant="ghost"
                          icon={<FiEdit />}
                          aria-label="Edit lead"
                        />
                      </HStack>
                    </Td>
                  </Tr>
                );
              })}
            </Tbody>
          </Table>
        </Box>
      </VStack>
    </Box>
  );
};

// Helper function for status colors
const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case 'new':
      return 'blue';
    case 'contacted':
      return 'yellow';
    case 'qualified':
      return 'orange';
    case 'converted':
      return 'green';
    case 'lost':
      return 'red';
    default:
      return 'gray';
  }
};

export default LeadScoring;