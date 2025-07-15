import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  useToast,
  Spinner,
  Badge,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Input,
  Select,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  FormControl,
  FormLabel,
  Textarea,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Grid,
  GridItem,
  IconButton,
  Tooltip,
  Alert,
  AlertIcon,
  Flex,
  useColorModeValue,
} from '@chakra-ui/react';
import { AddIcon, EditIcon, DeleteIcon, ViewIcon } from '@chakra-ui/icons';
import * as api from '../api';
import { LeadKanban, KanbanLead, LeadStage } from '../components/LeadKanban';

interface Lead {
  id: number;
  name: string;
  email: string;
  phone?: string;
  company?: string;
  tag?: string;
  notes?: string;
  status: string;
  source?: string;
  created_at: string;
  updated_at: string;
}

interface LeadStats {
  total_leads: number;
  new_leads: number;
  contacted_leads: number;
  qualified_leads: number;
  converted_leads: number;
  conversion_rate: number;
}

const CRM: React.FC = () => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [stats, setStats] = useState<LeadStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(false);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [filterStatus, setFilterStatus] = useState('');
  const [filterTag, setFilterTag] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    loadLeads();
    loadStats();
  }, []);

  const loadLeads = async () => {
    setLoading(true);
    try {
      const response = await api.getCRMLeads();
      setLeads(response || []);
    } catch (error: any) {
      console.error(error);
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    setStatsLoading(true);
    try {
      const response = await api.getCRMLeads();
      // Calculate stats from leads data
      const total = response?.length || 0;
      const new_leads = response?.filter((l: Lead) => l.status === 'new').length || 0;
      const contacted = response?.filter((l: Lead) => l.status === 'contacted').length || 0;
      const qualified = response?.filter((l: Lead) => l.status === 'qualified').length || 0;
      const converted = response?.filter((l: Lead) => l.status === 'converted').length || 0;
      
      setStats({
        total_leads: total,
        new_leads,
        contacted_leads: contacted,
        qualified_leads: qualified,
        converted_leads: converted,
        conversion_rate: total > 0 ? (converted / total) * 100 : 0
      });
    } catch (error: any) {
      console.error(error);
    } finally {
      setStatsLoading(false);
    }
  };

  const addLead = async (leadData: Partial<Lead>) => {
    try {
      await api.addLeadToCRM(leadData);
      toast({
        title: 'Success',
        description: 'Lead added successfully',
        status: 'success',
        duration: 3000,
      });
      loadLeads();
      loadStats();
      onClose();
    } catch (error: any) {
      console.error(error);
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  const updateLead = async (leadId: number, leadData: Partial<Lead>) => {
    try {
      await api.updateCRMLead(leadId, leadData);
      toast({
        title: 'Success',
        description: 'Lead updated successfully',
        status: 'success',
        duration: 3000,
      });
      loadLeads();
      loadStats();
      onClose();
    } catch (error: any) {
      console.error(error);
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  const deleteLead = async (leadId: number) => {
    if (!confirm('Are you sure you want to delete this lead?')) return;
    
    try {
      await api.deleteCRMLead(leadId);
      toast({
        title: 'Success',
        description: 'Lead deleted successfully',
        status: 'success',
        duration: 3000,
      });
      loadLeads();
      loadStats();
    } catch (error: any) {
      console.error(error);
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new': return 'blue';
      case 'contacted': return 'yellow';
      case 'qualified': return 'orange';
      case 'converted': return 'green';
      default: return 'gray';
    }
  };

  const filteredLeads = leads.filter(lead => {
    const matchesStatus = !filterStatus || lead.status === filterStatus;
    const matchesTag = !filterTag || lead.tag === filterTag;
    const matchesSearch = !searchTerm || 
      lead.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (lead.company && lead.company.toLowerCase().includes(searchTerm.toLowerCase()));
    
    return matchesStatus && matchesTag && matchesSearch;
  });

  const uniqueTags = [...new Set(leads.map(lead => lead.tag).filter(Boolean))];

  // Map CRM lead status to Kanban stage
  const statusToStage = (status: string): LeadStage => {
    if (status === 'converted') return 'converted';
    if (status === 'contacted' || status === 'qualified') return 'in_progress';
    return 'to_contact';
  };
  const stageToStatus = (stage: LeadStage): string => {
    if (stage === 'converted') return 'converted';
    if (stage === 'in_progress') return 'contacted';
    return 'new';
  };
  const kanbanLeads: KanbanLead[] = leads.map(l => ({
    id: l.id.toString(),
    name: l.name,
    email: l.email,
    company: l.company,
    stage: statusToStage(l.status),
  }));
  const handleStageChange = (leadId: string, newStage: LeadStage) => {
    const lead = leads.find(l => l.id.toString() === leadId);
    if (lead) {
      updateLead(lead.id, { status: stageToStatus(newStage) });
    }
  };

  return (
    <Box minH="100vh" bg={useColorModeValue('gray.100', 'gray.800')} data-tour="crm-main">
      <Container maxW="container.xl" py={8} data-tour="crm-content">
        <Heading size="lg" mb={6} className="gradient-text" data-tour="crm-title">CRM Leads</Heading>
        <HStack justify="space-between" mb={4} data-tour="crm-actions">
          <Button colorScheme="blue" onClick={onOpen} data-tour="crm-add-lead">Add Lead</Button>
          <Button colorScheme="green" onClick={handleExportLeads} data-tour="crm-export">Export Leads</Button>
        </HStack>

        {/* Statistics */}
        {stats && (
          <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={6}>
            <GridItem>
              <Stat>
                <StatLabel>Total Leads</StatLabel>
                <StatNumber>{stats.total_leads}</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  23.36%
                </StatHelpText>
              </Stat>
            </GridItem>
            <GridItem>
              <Stat>
                <StatLabel>New Leads</StatLabel>
                <StatNumber>{stats.new_leads}</StatNumber>
                <StatHelpText>This month</StatHelpText>
              </Stat>
            </GridItem>
            <GridItem>
              <Stat>
                <StatLabel>Conversion Rate</StatLabel>
                <StatNumber>{stats.conversion_rate.toFixed(1)}%</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  12.5%
                </StatHelpText>
              </Stat>
            </GridItem>
            <GridItem>
              <Stat>
                <StatLabel>Converted</StatLabel>
                <StatNumber>{stats.converted_leads}</StatNumber>
                <StatHelpText>This month</StatHelpText>
              </Stat>
            </GridItem>
          </Grid>
        )}

        {/* Filters and Actions */}
        <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor}>
          <HStack spacing={4} mb={4}>
            <Input
              placeholder="Search leads..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              maxW="300px"
            />
            <Select
              placeholder="Filter by status"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              maxW="200px"
            >
              <option value="new">New</option>
              <option value="contacted">Contacted</option>
              <option value="qualified">Qualified</option>
              <option value="converted">Converted</option>
            </Select>
            <Select
              placeholder="Filter by tag"
              value={filterTag}
              onChange={(e) => setFilterTag(e.target.value)}
              maxW="200px"
            >
              {uniqueTags.map(tag => (
                <option key={tag} value={tag}>{tag}</option>
              ))}
            </Select>
            <Button
              leftIcon={<AddIcon />}
              colorScheme="blue"
              onClick={() => {
                setSelectedLead(null);
                onOpen();
              }}
            >
              Add Lead
            </Button>
          </HStack>
        </Box>

        {/* Leads Table */}
        <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor}>
          <Heading size="md" mb={4}>Leads</Heading>
          {loading ? (
            <Flex justify="center" py={8}>
              <Spinner size="lg" />
            </Flex>
          ) : filteredLeads.length === 0 ? (
            <Alert status="info">
              <AlertIcon />
              No leads found. Add your first lead to get started!
            </Alert>
          ) : (
            <Table variant="simple">
              <Thead>
                <Tr>
                  <Th>Name</Th>
                  <Th>Email</Th>
                  <Th>Company</Th>
                  <Th>Status</Th>
                  <Th>Tag</Th>
                  <Th>Created</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {filteredLeads.map((lead) => (
                  <Tr key={lead.id}>
                    <Td fontWeight="bold">{lead.name}</Td>
                    <Td>{lead.email}</Td>
                    <Td>{lead.company || '-'}</Td>
                    <Td>
                      <Badge colorScheme={getStatusColor(lead.status)}>
                        {lead.status}
                      </Badge>
                    </Td>
                    <Td>{lead.tag || '-'}</Td>
                    <Td>{new Date(lead.created_at).toLocaleDateString()}</Td>
                    <Td>
                      <HStack spacing={2}>
                        <Tooltip label="View Details">
                          <IconButton
                            aria-label="View lead"
                            icon={<ViewIcon />}
                            size="sm"
                            variant="ghost"
                            onClick={() => {
                              setSelectedLead(lead);
                              onOpen();
                            }}
                          />
                        </Tooltip>
                        <Tooltip label="Edit Lead">
                          <IconButton
                            aria-label="Edit lead"
                            icon={<EditIcon />}
                            size="sm"
                            variant="ghost"
                            onClick={() => {
                              setSelectedLead(lead);
                              onOpen();
                            }}
                          />
                        </Tooltip>
                        <Tooltip label="Delete Lead">
                          <IconButton
                            aria-label="Delete lead"
                            icon={<DeleteIcon />}
                            size="sm"
                            variant="ghost"
                            colorScheme="red"
                            onClick={() => deleteLead(lead.id)}
                          />
                        </Tooltip>
                      </HStack>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          )}
        </Box>
      </Container>

      {/* Add/Edit Lead Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            {selectedLead ? 'Edit Lead' : 'Add New Lead'}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <LeadForm
              lead={selectedLead}
              onSubmit={selectedLead ? updateLead : addLead}
              onCancel={onClose}
            />
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
};

// Lead Form Component
interface LeadFormProps {
  lead?: Lead | null;
  onSubmit: (data: Partial<Lead>) => void;
  onCancel: () => void;
}

const LeadForm: React.FC<LeadFormProps> = ({ lead, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: lead?.name || '',
    email: lead?.email || '',
    phone: lead?.phone || '',
    company: lead?.company || '',
    tag: lead?.tag || '',
    notes: lead?.notes || '',
    status: lead?.status || 'new',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (lead) {
      onSubmit(lead.id, formData);
    } else {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <VStack spacing={4}>
        <FormControl isRequired>
          <FormLabel>Name</FormLabel>
          <Input
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="Enter lead name"
          />
        </FormControl>
        
        <FormControl isRequired>
          <FormLabel>Email</FormLabel>
          <Input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            placeholder="Enter email address"
          />
        </FormControl>
        
        <FormControl>
          <FormLabel>Phone</FormLabel>
          <Input
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            placeholder="Enter phone number"
          />
        </FormControl>
        
        <FormControl>
          <FormLabel>Company</FormLabel>
          <Input
            value={formData.company}
            onChange={(e) => setFormData({ ...formData, company: e.target.value })}
            placeholder="Enter company name"
          />
        </FormControl>
        
        <FormControl>
          <FormLabel>Tag</FormLabel>
          <Input
            value={formData.tag}
            onChange={(e) => setFormData({ ...formData, tag: e.target.value })}
            placeholder="Enter tag"
          />
        </FormControl>
        
        <FormControl>
          <FormLabel>Status</FormLabel>
          <Select
            value={formData.status}
            onChange={(e) => setFormData({ ...formData, status: e.target.value })}
          >
            <option value="new">New</option>
            <option value="contacted">Contacted</option>
            <option value="qualified">Qualified</option>
            <option value="converted">Converted</option>
          </Select>
        </FormControl>
        
        <FormControl>
          <FormLabel>Notes</FormLabel>
          <Textarea
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            placeholder="Enter notes about this lead"
            rows={3}
          />
        </FormControl>
        
        <HStack spacing={4} w="full">
          <Button type="submit" colorScheme="blue" flex={1}>
            {lead ? 'Update Lead' : 'Add Lead'}
          </Button>
          <Button onClick={onCancel} variant="outline" flex={1}>
            Cancel
          </Button>
        </HStack>
      </VStack>
    </form>
  );
};

export default CRM; 