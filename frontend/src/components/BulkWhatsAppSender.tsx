import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Button,
  VStack,
  HStack,
  Heading,
  Text,
  Input,
  Textarea,
  Select,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  useToast,
  useColorModeValue,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  IconButton,
  Tooltip,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
  Switch,
  FormControl,
  FormLabel,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  Card,
  CardBody,
  CardHeader,
  Flex,
  Spacer,
  Divider,
  List,
  ListItem,
  ListIcon,
  useDisclosure as useChakraDisclosure,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import {
  FiUpload,
  FiSend,
  FiPlay,
  FiPause,
  FiSquare,
  FiPlus,
  FiEdit,
  FiTrash2,
  FiCopy,
  FiEye,
  FiCheck,
  FiX,
  FiClock,
  FiMessageSquare,
  FiFilter,
  FiSettings,
  FiTrendingUp,
  FiUsers,
  FiMail,
  FiPhone,
  FiGlobe,
  FiCheckCircle,
  FiAlertTriangle,
  FiInfo,
  FiFileText,
  FiDownload,
  FiPieChart,
  FiBarChart2,
  FiCalendar,
  FiUser,
  FiSmartphone,
} from 'react-icons/fi';

interface Contact {
  phone_number: string;
  name?: string;
  email?: string;
  company?: string;
  custom_fields?: Record<string, string>;
}

interface MessageTemplate {
  id: number;
  name: string;
  content: string;
  variables: string[];
  media_url?: string;
  media_type?: string;
}

interface Campaign {
  id: number;
  name: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused';
  total_contacts: number;
  sent_messages: number;
  created_at: string;
  start_time?: string;
  end_time?: string;
}

interface CampaignStatus {
  campaign_id: number;
  status: string;
  total_messages: number;
  sent_messages: number;
  failed_messages: number;
  pending_messages: number;
  success_rate: number;
  start_time?: string;
  end_time?: string;
}

interface BulkAnalytics {
  total_campaigns: number;
  total_messages: number;
  sent_messages: number;
  success_rate: number;
  recent_campaigns: Campaign[];
}

const BulkWhatsAppSender: React.FC = () => {
  const { t } = useTranslation();
  const toast = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // State management
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [templates, setTemplates] = useState<MessageTemplate[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [analytics, setAnalytics] = useState<BulkAnalytics | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null);
  const [messageContent, setMessageContent] = useState('');
  const [campaignName, setCampaignName] = useState('');
  const [campaignDescription, setCampaignDescription] = useState('');
  const [delayBetweenMessages, setDelayBetweenMessages] = useState(30);
  const [maxMessagesPerHour, setMaxMessagesPerHour] = useState(50);
  const [maxMessagesPerDay, setMaxMessagesPerDay] = useState(500);
  const [retryFailed, setRetryFailed] = useState(true);
  const [maxRetries, setMaxRetries] = useState(3);
  const [scheduleType, setScheduleType] = useState('immediate');
  const [scheduleTime, setScheduleTime] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  
  // Modals
  const { isOpen: isCreateOpen, onOpen: onCreateOpen, onClose: onCreateClose } = useDisclosure();
  const { isOpen: isPreviewOpen, onOpen: onPreviewOpen, onClose: onPreviewClose } = useDisclosure();
  const { isOpen: isAnalyticsOpen, onOpen: onAnalyticsOpen, onClose: onAnalyticsClose } = useDisclosure();

  // Color mode
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    loadTemplates();
    loadCampaigns();
    loadAnalytics();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await fetch('/api/bulk-whatsapp/templates', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const loadCampaigns = async () => {
    try {
      const response = await fetch('/api/bulk-whatsapp/campaigns', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setCampaigns(data);
      }
    } catch (error) {
      console.error('Error loading campaigns:', error);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await fetch('/api/bulk-whatsapp/analytics', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setIsLoading(true);
      const response = await fetch('/api/bulk-whatsapp/import-contacts', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        setContacts(data.contacts);
        toast({
          title: 'Contacts imported',
          description: `Successfully imported ${data.total_contacts} contacts`,
          status: 'success',
          duration: 3000,
        });
      } else {
        throw new Error('Failed to import contacts');
      }
    } catch (error) {
      toast({
        title: 'Import failed',
        description: 'Failed to import contacts. Please check your file format.',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleTemplateSelect = (templateId: number) => {
    const template = templates.find(t => t.id === templateId);
    if (template) {
      setSelectedTemplate(templateId);
      setMessageContent(template.content);
    }
  };

  const handleCreateCampaign = async () => {
    if (!campaignName || !messageContent || contacts.length === 0) {
      toast({
        title: 'Missing information',
        description: 'Please fill in all required fields and import contacts.',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    try {
      setIsLoading(true);
      const campaignData = {
        name: campaignName,
        description: campaignDescription,
        template_id: selectedTemplate,
        message_content: messageContent,
        contacts: contacts,
        schedule_type: scheduleType,
        schedule_time: scheduleType === 'scheduled' ? scheduleTime : null,
        delay_between_messages: delayBetweenMessages,
        max_messages_per_hour: maxMessagesPerHour,
        max_messages_per_day: maxMessagesPerDay,
        retry_failed: retryFailed,
        max_retries: maxRetries
      };

      const response = await fetch('/api/bulk-whatsapp/campaigns', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(campaignData)
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: 'Campaign created',
          description: `Campaign "${campaignName}" created successfully`,
          status: 'success',
          duration: 3000,
        });
        onCreateClose();
        loadCampaigns();
        resetForm();
      } else {
        throw new Error('Failed to create campaign');
      }
    } catch (error) {
      toast({
        title: 'Creation failed',
        description: 'Failed to create campaign. Please try again.',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartCampaign = async (campaignId: number) => {
    try {
      const response = await fetch(`/api/bulk-whatsapp/campaigns/${campaignId}/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        toast({
          title: 'Campaign started',
          description: 'Campaign is now running',
          status: 'success',
          duration: 3000,
        });
        loadCampaigns();
      } else {
        throw new Error('Failed to start campaign');
      }
    } catch (error) {
      toast({
        title: 'Start failed',
        description: 'Failed to start campaign. Please try again.',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const resetForm = () => {
    setCampaignName('');
    setCampaignDescription('');
    setMessageContent('');
    setSelectedTemplate(null);
    setContacts([]);
    setDelayBetweenMessages(30);
    setMaxMessagesPerHour(50);
    setMaxMessagesPerDay(500);
    setRetryFailed(true);
    setMaxRetries(3);
    setScheduleType('immediate');
    setScheduleTime('');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'yellow';
      case 'running': return 'blue';
      case 'completed': return 'green';
      case 'failed': return 'red';
      case 'paused': return 'orange';
      default: return 'gray';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return FiClock;
      case 'running': return FiPlay;
      case 'completed': return FiCheckCircle;
      case 'failed': return FiAlertTriangle;
      case 'paused': return FiPause;
      default: return FiInfo;
    }
  };

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Flex align="center" justify="space-between">
          <VStack align="start" spacing={2}>
            <Heading size="lg" display="flex" alignItems="center" gap={2}>
              <FiSend />
              Bulk WhatsApp Sender
            </Heading>
            <Text color="gray.600">
              Send personalized WhatsApp messages to multiple contacts at scale
            </Text>
          </VStack>
          <HStack spacing={3}>
            <Button
              leftIcon={<FiPieChart />}
              variant="outline"
              onClick={onAnalyticsOpen}
            >
              Analytics
            </Button>
            <Button
              leftIcon={<FiPlus />}
              colorScheme="blue"
              onClick={onCreateOpen}
            >
              Create Campaign
            </Button>
          </HStack>
        </Flex>

        {/* Main Content */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <TabList>
            <Tab>Campaigns</Tab>
            <Tab>Contacts</Tab>
            <Tab>Templates</Tab>
          </TabList>

          <TabPanels>
            {/* Campaigns Tab */}
            <TabPanel>
              <VStack spacing={4} align="stretch">
                <HStack justify="space-between">
                  <Heading size="md">Active Campaigns</Heading>
                  <Button size="sm" onClick={loadCampaigns}>
                    Refresh
                  </Button>
                </HStack>

                {campaigns.length === 0 ? (
                  <Card>
                    <CardBody textAlign="center" py={10}>
                      <FiMessageSquare size={48} color="gray" />
                      <Text mt={4} color="gray.600">
                        No campaigns yet. Create your first campaign to get started.
                      </Text>
                    </CardBody>
                  </Card>
                ) : (
                  <Table variant="simple">
                    <Thead>
                      <Tr>
                        <Th>Campaign</Th>
                        <Th>Status</Th>
                        <Th>Contacts</Th>
                        <Th>Sent</Th>
                        <Th>Created</Th>
                        <Th>Actions</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {campaigns.map((campaign) => {
                        const StatusIcon = getStatusIcon(campaign.status);
                        return (
                          <Tr key={campaign.id}>
                            <Td>
                              <VStack align="start" spacing={1}>
                                <Text fontWeight="medium">{campaign.name}</Text>
                                {campaign.description && (
                                  <Text fontSize="sm" color="gray.600">
                                    {campaign.description}
                                  </Text>
                                )}
                              </VStack>
                            </Td>
                            <Td>
                              <Badge colorScheme={getStatusColor(campaign.status)}>
                                <HStack spacing={1}>
                                  <StatusIcon size={12} />
                                  <Text>{campaign.status}</Text>
                                </HStack>
                              </Badge>
                            </Td>
                            <Td>{campaign.total_contacts}</Td>
                            <Td>{campaign.sent_messages}</Td>
                            <Td>{new Date(campaign.created_at).toLocaleDateString()}</Td>
                            <Td>
                              <HStack spacing={2}>
                                {campaign.status === 'pending' && (
                                  <Button
                                    size="sm"
                                    leftIcon={<FiPlay />}
                                    colorScheme="green"
                                    onClick={() => handleStartCampaign(campaign.id)}
                                  >
                                    Start
                                  </Button>
                                )}
                                <Button size="sm" variant="outline" leftIcon={<FiEye />}>
                                  View
                                </Button>
                              </HStack>
                            </Td>
                          </Tr>
                        );
                      })}
                    </Tbody>
                  </Table>
                )}
              </VStack>
            </TabPanel>

            {/* Contacts Tab */}
            <TabPanel>
              <VStack spacing={4} align="stretch">
                <HStack justify="space-between">
                  <Heading size="md">Contact Management</Heading>
                  <Button
                    leftIcon={<FiUpload />}
                    onClick={() => fileInputRef.current?.click()}
                    isLoading={isLoading}
                  >
                    Import Contacts
                  </Button>
                </HStack>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                />

                {contacts.length === 0 ? (
                  <Card>
                    <CardBody textAlign="center" py={10}>
                      <FiUsers size={48} color="gray" />
                      <Text mt={4} color="gray.600">
                        No contacts imported yet. Upload a CSV or Excel file to get started.
                      </Text>
                      <Text fontSize="sm" color="gray.500" mt={2}>
                        Supported formats: CSV, Excel (.xlsx, .xls)
                      </Text>
                    </CardBody>
                  </Card>
                ) : (
                  <Box>
                    <HStack justify="space-between" mb={4}>
                      <Text fontWeight="medium">
                        {contacts.length} contacts imported
                      </Text>
                      <Button size="sm" variant="outline" leftIcon={<FiDownload />}>
                        Export
                      </Button>
                    </HStack>

                    <Table variant="simple" size="sm">
                      <Thead>
                        <Tr>
                          <Th>Name</Th>
                          <Th>Phone</Th>
                          <Th>Email</Th>
                          <Th>Company</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {contacts.slice(0, 10).map((contact, index) => (
                          <Tr key={index}>
                            <Td>{contact.name || '-'}</Td>
                            <Td>{contact.phone_number}</Td>
                            <Td>{contact.email || '-'}</Td>
                            <Td>{contact.company || '-'}</Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>

                    {contacts.length > 10 && (
                      <Text fontSize="sm" color="gray.600" mt={2}>
                        Showing first 10 contacts. Total: {contacts.length}
                      </Text>
                    )}
                  </Box>
                )}
              </VStack>
            </TabPanel>

            {/* Templates Tab */}
            <TabPanel>
              <VStack spacing={4} align="stretch">
                <HStack justify="space-between">
                  <Heading size="md">Message Templates</Heading>
                  <Button leftIcon={<FiPlus />} colorScheme="blue">
                    Create Template
                  </Button>
                </HStack>

                {templates.length === 0 ? (
                  <Card>
                    <CardBody textAlign="center" py={10}>
                      <FiFileText size={48} color="gray" />
                      <Text mt={4} color="gray.600">
                        No templates created yet. Create your first template to get started.
                      </Text>
                    </CardBody>
                  </Card>
                ) : (
                  <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                    {templates.map((template) => (
                      <Card key={template.id} cursor="pointer" _hover={{ shadow: 'md' }}>
                        <CardHeader>
                          <Heading size="sm">{template.name}</Heading>
                        </CardHeader>
                        <CardBody>
                          <Text fontSize="sm" color="gray.600" noOfLines={3}>
                            {template.content}
                          </Text>
                          {template.variables.length > 0 && (
                            <HStack mt={2} flexWrap="wrap">
                              {template.variables.map((variable) => (
                                <Badge key={variable} size="sm" colorScheme="blue">
                                  {variable}
                                </Badge>
                              ))}
                            </HStack>
                          )}
                        </CardBody>
                      </Card>
                    ))}
                  </SimpleGrid>
                )}
              </VStack>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </VStack>

      {/* Create Campaign Modal */}
      <Modal isOpen={isCreateOpen} onClose={onCreateClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Create Bulk Campaign</ModalHeader>
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Campaign Name</FormLabel>
                <Input
                  value={campaignName}
                  onChange={(e) => setCampaignName(e.target.value)}
                  placeholder="Enter campaign name"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Description</FormLabel>
                <Textarea
                  value={campaignDescription}
                  onChange={(e) => setCampaignDescription(e.target.value)}
                  placeholder="Enter campaign description"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Message Template</FormLabel>
                <Select
                  value={selectedTemplate || ''}
                  onChange={(e) => handleTemplateSelect(Number(e.target.value))}
                  placeholder="Select a template"
                >
                  {templates.map((template) => (
                    <option key={template.id} value={template.id}>
                      {template.name}
                    </option>
                  ))}
                </Select>
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Message Content</FormLabel>
                <Textarea
                  value={messageContent}
                  onChange={(e) => setMessageContent(e.target.value)}
                  placeholder="Enter your message content. Use {{name}}, {{phone}}, {{email}} for personalization."
                  rows={4}
                />
              </FormControl>

              <HStack spacing={4} w="full">
                <FormControl>
                  <FormLabel>Delay Between Messages (seconds)</FormLabel>
                  <NumberInput
                    value={delayBetweenMessages}
                    onChange={(_, value) => setDelayBetweenMessages(value)}
                    min={1}
                    max={3600}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>

                <FormControl>
                  <FormLabel>Max Messages/Hour</FormLabel>
                  <NumberInput
                    value={maxMessagesPerHour}
                    onChange={(_, value) => setMaxMessagesPerHour(value)}
                    min={1}
                    max={100}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
              </HStack>

              <HStack spacing={4} w="full">
                <FormControl>
                  <FormLabel>Max Messages/Day</FormLabel>
                  <NumberInput
                    value={maxMessagesPerDay}
                    onChange={(_, value) => setMaxMessagesPerDay(value)}
                    min={1}
                    max={1000}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>

                <FormControl>
                  <FormLabel>Max Retries</FormLabel>
                  <NumberInput
                    value={maxRetries}
                    onChange={(_, value) => setMaxRetries(value)}
                    min={0}
                    max={5}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
              </HStack>

              <FormControl>
                <FormLabel>Retry Failed Messages</FormLabel>
                <Switch
                  isChecked={retryFailed}
                  onChange={(e) => setRetryFailed(e.target.checked)}
                />
              </FormControl>

              <Alert status="info">
                <AlertIcon />
                <Box>
                  <AlertTitle>Ready to send!</AlertTitle>
                  <AlertDescription>
                    This campaign will send messages to {contacts.length} contacts.
                    Make sure to review your message content before starting.
                  </AlertDescription>
                </Box>
              </Alert>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onCreateClose}>
              Cancel
            </Button>
            <Button
              colorScheme="blue"
              onClick={handleCreateCampaign}
              isLoading={isLoading}
              leftIcon={<FiSend />}
            >
              Create Campaign
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Analytics Modal */}
      <Modal isOpen={isAnalyticsOpen} onClose={onAnalyticsClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Bulk Messaging Analytics</ModalHeader>
          <ModalBody>
            {analytics && (
              <VStack spacing={6}>
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
                  <Stat>
                    <StatLabel>Total Campaigns</StatLabel>
                    <StatNumber>{analytics.total_campaigns}</StatNumber>
                    <StatHelpText>All time campaigns</StatHelpText>
                  </Stat>
                  <Stat>
                    <StatLabel>Total Messages</StatLabel>
                    <StatNumber>{analytics.total_messages}</StatNumber>
                    <StatHelpText>Messages sent</StatHelpText>
                  </Stat>
                  <Stat>
                    <StatLabel>Success Rate</StatLabel>
                    <StatNumber>{analytics.success_rate.toFixed(1)}%</StatNumber>
                    <StatHelpText>Delivery success</StatHelpText>
                  </Stat>
                  <Stat>
                    <StatLabel>Sent Messages</StatLabel>
                    <StatNumber>{analytics.sent_messages}</StatNumber>
                    <StatHelpText>Successfully delivered</StatHelpText>
                  </Stat>
                </SimpleGrid>

                <Divider />

                <Box w="full">
                  <Heading size="md" mb={4}>Recent Campaigns</Heading>
                  <VStack spacing={3} align="stretch">
                    {analytics.recent_campaigns.map((campaign) => (
                      <Card key={campaign.id}>
                        <CardBody>
                          <HStack justify="space-between">
                            <VStack align="start" spacing={1}>
                              <Text fontWeight="medium">{campaign.name}</Text>
                              <Text fontSize="sm" color="gray.600">
                                {new Date(campaign.created_at).toLocaleDateString()}
                              </Text>
                            </VStack>
                            <VStack align="end" spacing={1}>
                              <Badge colorScheme={getStatusColor(campaign.status)}>
                                {campaign.status}
                              </Badge>
                              <Text fontSize="sm">
                                {campaign.sent_messages}/{campaign.total_contacts}
                              </Text>
                            </VStack>
                          </HStack>
                        </CardBody>
                      </Card>
                    ))}
                  </VStack>
                </Box>
              </VStack>
            )}
          </ModalBody>
          <ModalFooter>
            <Button onClick={onAnalyticsClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default BulkWhatsAppSender; 