import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Progress,
  Tooltip,
  Icon,
  useColorModeValue,
  Card,
  CardBody,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Button,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Divider,
} from '@chakra-ui/react';
import { 
  StarIcon, 
  InfoIcon, 
  CheckCircleIcon, 
  WarningIcon,
  ExternalLinkIcon,
  PhoneIcon,
  EmailIcon,
} from '@chakra-ui/icons';
import { FiGlobe } from 'react-icons/fi';
import * as api from '../api';
import { LeadScoringCriteriaBuilder, ScoringRule } from './LeadScoringCriteriaBuilder';

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

interface LeadScoringProps {
  leads: Lead[];
  onLeadUpdate: (leadId: number, updates: Partial<Lead>) => void;
}

const LeadScoring: React.FC<LeadScoringProps> = ({ leads, onLeadUpdate }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [enriching, setEnriching] = useState<number | null>(null);
  const [filter, setFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [scoringRules, setScoringRules] = useState<ScoringRule[]>([
    { id: 'email', field: 'email', label: 'Has Email', points: 15 },
    { id: 'phone', field: 'phone', label: 'Has Phone', points: 10 },
    { id: 'website', field: 'website', label: 'Has Website', points: 5 },
    { id: 'company', field: 'company', label: 'Has Company', points: 10 },
    { id: 'enriched', field: 'enriched', label: 'Is Enriched', points: 15 },
  ]);

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Calculate lead score based on user-defined rules
  const calculateLeadScore = (lead: Lead): number => {
    let score = 0;
    scoringRules.forEach(rule => {
      if (rule.field === 'email' && lead.email) score += rule.points;
      if (rule.field === 'phone' && lead.phone) score += rule.points;
      if (rule.field === 'website' && lead.website) score += rule.points;
      if (rule.field === 'company' && lead.company) score += rule.points;
      if (rule.field === 'enriched' && lead.enriched) score += rule.points;
      if (rule.field === 'recent_contact' && lead.last_contacted) {
        const daysSince = Math.floor((Date.now() - new Date(lead.last_contacted).getTime()) / (1000 * 60 * 60 * 24));
        if (daysSince <= 7) score += rule.points;
      }
      if (rule.field === 'engagement_high' && lead.engagement_level === 'high') score += rule.points;
      if (rule.field === 'source_facebook' && lead.source === 'facebook') score += rule.points;
      if (rule.field === 'source_gmaps' && lead.source === 'google_maps') score += rule.points;
      if (rule.field === 'source_whatsapp' && lead.source === 'whatsapp') score += rule.points;
    });
    return Math.min(score, 100);
  };

  // Get score color and label
  const getScoreInfo = (score: number) => {
    if (score >= 80) return { color: 'green', label: 'Hot Lead', icon: StarIcon };
    if (score >= 60) return { color: 'blue', label: 'Warm Lead', icon: CheckCircleIcon };
    if (score >= 40) return { color: 'yellow', label: 'Cold Lead', icon: WarningIcon };
    return { color: 'gray', label: 'Poor Lead', icon: InfoIcon };
  };

  // Enrich lead with additional data
  const enrichLead = async (leadId: number) => {
    setEnriching(leadId);
    try {
      const enriched = await api.enrichLead(leadId);
      onLeadUpdate(leadId, {
        enriched: true,
        score: calculateLeadScore({ ...leads.find(l => l.id === leadId)!, enriched: true }),
        tags: [...(leads.find(l => l.id === leadId)?.tags || []), 'enriched', 'verified'],
        ...enriched
      });
    } catch (error) {
      console.error('Lead enrichment failed:', error);
    } finally {
      setEnriching(null);
    }
  };

  // Filter leads by score
  const filteredLeads = leads.filter(lead => {
    const score = calculateLeadScore(lead);
    if (filter === 'high') return score >= 80;
    if (filter === 'medium') return score >= 60 && score < 80;
    if (filter === 'low') return score < 60;
    return true;
  });

  // Calculate statistics
  const totalLeads = leads.length;
  const highScoreLeads = leads.filter(lead => calculateLeadScore(lead) >= 80).length;
  const mediumScoreLeads = leads.filter(lead => {
    const score = calculateLeadScore(lead);
    return score >= 60 && score < 80;
  }).length;
  const lowScoreLeads = leads.filter(lead => calculateLeadScore(lead) < 60).length;

  const averageScore = leads.length > 0 
    ? leads.reduce((sum, lead) => sum + calculateLeadScore(lead), 0) / leads.length 
    : 0;

  return (
    <Box>
      <LeadScoringCriteriaBuilder rules={scoringRules} onChange={setScoringRules} />
      {/* Statistics Cards */}
      <SimpleGrid columns={{ base: 1, md: 4 }} spacing={4} mb={6}>
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Stat>
              <StatLabel>Total Leads</StatLabel>
              <StatNumber>{totalLeads}</StatNumber>
              <StatHelpText>All leads in your CRM</StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Stat>
              <StatLabel>Hot Leads</StatLabel>
              <StatNumber color="green.500">{highScoreLeads}</StatNumber>
              <StatHelpText>Score ≥ 80</StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Stat>
              <StatLabel>Warm Leads</StatLabel>
              <StatNumber color="blue.500">{mediumScoreLeads}</StatNumber>
              <StatHelpText>Score 60-79</StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Stat>
              <StatLabel>Average Score</StatLabel>
              <StatNumber>{averageScore.toFixed(0)}</StatNumber>
              <StatHelpText>Overall lead quality</StatHelpText>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Filter Controls */}
      <HStack spacing={4} mb={4}>
        <Text fontSize="sm" fontWeight="medium">Filter by Score:</Text>
        <Button
          size="sm"
          variant={filter === 'all' ? 'solid' : 'outline'}
          onClick={() => setFilter('all')}
        >
          All ({totalLeads})
        </Button>
        <Button
          size="sm"
          variant={filter === 'high' ? 'solid' : 'outline'}
          colorScheme="green"
          onClick={() => setFilter('high')}
        >
          Hot ({highScoreLeads})
        </Button>
        <Button
          size="sm"
          variant={filter === 'medium' ? 'solid' : 'outline'}
          colorScheme="blue"
          onClick={() => setFilter('medium')}
        >
          Warm ({mediumScoreLeads})
        </Button>
        <Button
          size="sm"
          variant={filter === 'low' ? 'solid' : 'outline'}
          colorScheme="yellow"
          onClick={() => setFilter('low')}
        >
          Cold ({lowScoreLeads})
        </Button>
      </HStack>

      {/* Leads Table */}
      <Card bg={bgColor} border="1px" borderColor={borderColor}>
        <CardBody>
          <Table variant="simple" size="sm">
            <Thead>
              <Tr>
                <Th>Lead</Th>
                <Th>Source</Th>
                <Th>Score</Th>
                <Th>Status</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {filteredLeads.map((lead) => {
                const score = calculateLeadScore(lead);
                const scoreInfo = getScoreInfo(score);
                const ScoreIcon = scoreInfo.icon;

                return (
                  <Tr key={lead.id} _hover={{ bg: 'gray.50' }}>
                    <Td>
                      <VStack align="start" spacing={1}>
                        <Text fontWeight="medium">{lead.name}</Text>
                        <Text fontSize="sm" color="gray.600">{lead.company}</Text>
                        <HStack spacing={2}>
                          {lead.email && <Icon as={EmailIcon} color="blue.500" />}
                          {lead.phone && <Icon as={PhoneIcon} color="green.500" />}
                          {lead.website && <Icon as={FiGlobe} color="purple.500" />}
                        </HStack>
                      </VStack>
                    </Td>
                    <Td>
                      <Badge colorScheme="purple" variant="subtle">
                        {lead.source.replace('_', ' ')}
                      </Badge>
                    </Td>
                    <Td>
                      <VStack align="start" spacing={1}>
                        <HStack spacing={2}>
                          <Icon as={ScoreIcon} color={`${scoreInfo.color}.500`} />
                          <Text fontWeight="medium">{score}</Text>
                        </HStack>
                        <Progress 
                          value={score} 
                          size="sm" 
                          colorScheme={scoreInfo.color}
                          width="60px"
                        />
                        <Text fontSize="xs" color="gray.500">
                          {scoreInfo.label}
                        </Text>
                      </VStack>
                    </Td>
                    <Td>
                      <Badge 
                        colorScheme={lead.status === 'new' ? 'blue' : 'green'}
                        variant="subtle"
                      >
                        {lead.status}
                      </Badge>
                    </Td>
                    <Td>
                      <HStack spacing={2}>
                        <Button
                          size="xs"
                          colorScheme="blue"
                          onClick={() => {
                            setSelectedLead(lead);
                            onOpen();
                          }}
                        >
                          View
                        </Button>
                        {!lead.enriched && (
                          <Button
                            size="xs"
                            colorScheme="green"
                            isLoading={enriching === lead.id}
                            onClick={() => enrichLead(lead.id)}
                          >
                            Enrich
                          </Button>
                        )}
                      </HStack>
                    </Td>
                  </Tr>
                );
              })}
            </Tbody>
          </Table>
        </CardBody>
      </Card>

      {/* Lead Detail Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Lead Details</ModalHeader>
          <ModalBody>
            {selectedLead && (
              <VStack spacing={4} align="stretch">
                <Box>
                  <Text fontSize="lg" fontWeight="bold">{selectedLead.name}</Text>
                  <Text color="gray.600">{selectedLead.company}</Text>
                </Box>

                <SimpleGrid columns={2} spacing={4}>
                  <Box>
                    <Text fontSize="sm" fontWeight="medium" color="gray.600">Email</Text>
                    <Text>{selectedLead.email}</Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" fontWeight="medium" color="gray.600">Phone</Text>
                    <Text>{selectedLead.phone || 'Not provided'}</Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" fontWeight="medium" color="gray.600">Website</Text>
                    <Text>{selectedLead.website || 'Not provided'}</Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" fontWeight="medium" color="gray.600">Source</Text>
                    <Badge colorScheme="purple">{selectedLead.source}</Badge>
                  </Box>
                </SimpleGrid>

                <Divider />

                <Box>
                  <Text fontSize="sm" fontWeight="medium" color="gray.600" mb={2}>Tags</Text>
                  <HStack spacing={2} flexWrap="wrap">
                    {selectedLead.tags.map((tag, index) => (
                      <Badge key={index} colorScheme="blue" variant="subtle">
                        {tag}
                      </Badge>
                    ))}
                  </HStack>
                </Box>

                {selectedLead.notes && (
                  <Box>
                    <Text fontSize="sm" fontWeight="medium" color="gray.600" mb={2}>Notes</Text>
                    <Text fontSize="sm">{selectedLead.notes}</Text>
                  </Box>
                )}
              </VStack>
            )}
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Close
            </Button>
            <Button colorScheme="blue">
              Edit Lead
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default LeadScoring;