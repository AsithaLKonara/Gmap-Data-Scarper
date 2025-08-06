import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Badge,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Input,
  VStack,
  HStack,
  Heading,
  Text,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  FormControl,
  FormLabel,
  Select,
  Textarea,
  useToast,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  useColorModeValue,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import {
  FiPlus,
  FiEdit,
  FiTrash2,
  FiEye,
  FiUsers,
  FiTrendingUp,
  FiCheckCircle,
} from 'react-icons/fi';

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
  const { t } = useTranslation();
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [stats, setStats] = useState<LeadStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Mock data - replace with actual API calls
  useEffect(() => {
    const mockLeads: Lead[] = [
      {
        id: 1,
        name: 'John Doe',
        email: 'john@example.com',
        phone: '+1234567890',
        company: 'Tech Corp',
        status: 'new',
        source: 'Google Maps',
        created_at: '2024-01-15',
        updated_at: '2024-01-15',
      },
      {
        id: 2,
        name: 'Jane Smith',
        email: 'jane@example.com',
        phone: '+1234567891',
        company: 'Design Studio',
        status: 'contacted',
        source: 'Facebook',
        created_at: '2024-01-14',
        updated_at: '2024-01-15',
      },
    ];

    const mockStats: LeadStats = {
      total_leads: 150,
      new_leads: 45,
      contacted_leads: 60,
      qualified_leads: 30,
      converted_leads: 15,
      conversion_rate: 10,
    };

    setLeads(mockLeads);
    setStats(mockStats);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
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

  const handleAddLead = () => {
    setSelectedLead(null);
    setIsEditing(false);
    onOpen();
  };

  const handleEditLead = (lead: Lead) => {
    setSelectedLead(lead);
    setIsEditing(true);
    onOpen();
  };

  const handleDeleteLead = async (leadId: number) => {
    try {
      // Mock API call
      setLeads(leads.filter(lead => lead.id !== leadId));
      toast({
        title: 'Lead deleted',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error deleting lead',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleSubmit = async (formData: Partial<Lead>) => {
    try {
      if (isEditing && selectedLead) {
        // Update existing lead
        setLeads(leads.map(lead => 
          lead.id === selectedLead.id ? { ...lead, ...formData } : lead
        ));
        toast({
          title: 'Lead updated',
          status: 'success',
          duration: 3000,
        });
      } else {
        // Add new lead
        const newLead: Lead = {
          id: Date.now(),
          name: formData.name || '',
          email: formData.email || '',
          phone: formData.phone || '',
          company: formData.company || '',
          status: formData.status || 'new',
          source: formData.source || 'Manual',
          created_at: new Date().toISOString().split('T')[0],
          updated_at: new Date().toISOString().split('T')[0],
        };
        setLeads([...leads, newLead]);
        toast({
          title: 'Lead added',
          status: 'success',
          duration: 3000,
        });
      }
      onClose();
    } catch (error) {
      toast({
        title: 'Error saving lead',
        status: 'error',
        duration: 3000,
      });
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box mb={6}>
        <HStack justify="space-between" align="center">
          <VStack align="start" spacing={1}>
            <Heading size="lg">CRM - Lead Management</Heading>
            <Text color="gray.600">Manage and track your leads</Text>
          </VStack>
          <Button
            leftIcon={<FiPlus />}
            colorScheme="blue"
            onClick={handleAddLead}
          >
            Add Lead
          </Button>
        </HStack>
      </Box>

      {/* Stats */}
      {stats && (
        <SimpleGrid columns={{ base: 1, md: 4 }} spacing={6} mb={8}>
          <Stat>
            <StatLabel>Total Leads</StatLabel>
            <StatNumber>{stats.total_leads}</StatNumber>
            <StatHelpText>All time</StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>New Leads</StatLabel>
            <StatNumber color="blue.500">{stats.new_leads}</StatNumber>
            <StatHelpText>This month</StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Conversion Rate</StatLabel>
            <StatNumber color="green.500">{stats.conversion_rate}%</StatNumber>
            <StatHelpText>Last 30 days</StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Converted</StatLabel>
            <StatNumber color="purple.500">{stats.converted_leads}</StatNumber>
            <StatHelpText>This month</StatHelpText>
          </Stat>
        </SimpleGrid>
      )}

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
              <Th>Name</Th>
              <Th>Email</Th>
              <Th>Company</Th>
              <Th>Status</Th>
              <Th>Source</Th>
              <Th>Created</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          <Tbody>
            {leads.map((lead) => (
              <Tr key={lead.id}>
                <Td fontWeight="medium">{lead.name}</Td>
                <Td>{lead.email}</Td>
                <Td>{lead.company || '-'}</Td>
                <Td>
                  <Badge colorScheme={getStatusColor(lead.status)}>
                    {lead.status}
                  </Badge>
                </Td>
                <Td>{lead.source || '-'}</Td>
                <Td>{lead.created_at}</Td>
                <Td>
                  <HStack spacing={2}>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleEditLead(lead)}
                    >
                      <FiEdit />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      colorScheme="red"
                      onClick={() => handleDeleteLead(lead.id)}
                    >
                      <FiTrash2 />
                    </Button>
                  </HStack>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>

      {/* Lead Form Modal */}
      <LeadFormModal
        isOpen={isOpen}
        onClose={onClose}
        lead={selectedLead}
        isEditing={isEditing}
        onSubmit={handleSubmit}
      />
    </Box>
  );
};

interface LeadFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  lead: Lead | null;
  isEditing: boolean;
  onSubmit: (data: Partial<Lead>) => void;
}

const LeadFormModal: React.FC<LeadFormModalProps> = ({
  isOpen,
  onClose,
  lead,
  isEditing,
  onSubmit,
}) => {
  const [formData, setFormData] = useState<Partial<Lead>>({
    name: '',
    email: '',
    phone: '',
    company: '',
    status: 'new',
    source: '',
    notes: '',
  });

  useEffect(() => {
    if (lead) {
      setFormData(lead);
    } else {
      setFormData({
        name: '',
        email: '',
        phone: '',
        company: '',
        status: 'new',
        source: '',
        notes: '',
      });
    }
  }, [lead]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          {isEditing ? 'Edit Lead' : 'Add New Lead'}
        </ModalHeader>
        <form onSubmit={handleSubmit}>
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Name</FormLabel>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Email</FormLabel>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Phone</FormLabel>
                <Input
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Company</FormLabel>
                <Input
                  value={formData.company}
                  onChange={(e) => setFormData({ ...formData, company: e.target.value })}
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
                  <option value="lost">Lost</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Source</FormLabel>
                <Input
                  value={formData.source}
                  onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Notes</FormLabel>
                <Textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                />
              </FormControl>
            </VStack>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" colorScheme="blue">
              {isEditing ? 'Update' : 'Add'} Lead
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  );
};

export default CRM; 