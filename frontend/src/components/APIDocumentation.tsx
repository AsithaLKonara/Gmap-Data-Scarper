import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Card,
  CardBody,
  Button,
  Badge,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  Input,
  FormControl,
  FormLabel,
  Select,
  Textarea,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Code,
  useColorModeValue,
  Divider,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  IconButton,
  Tooltip,
  Link,
  List,
  ListItem,
  ListIcon,
  SimpleGrid,
} from '@chakra-ui/react';
import {
  CodeIcon,
  LinkIcon,
  DownloadIcon,
  PlayIcon,
  CopyIcon,
  CheckIcon,
  ExternalLinkIcon,
  SettingsIcon,
  CloseIcon,
} from '@chakra-ui/icons';

interface APIEndpoint {
  method: string;
  path: string;
  description: string;
  parameters: any[];
  responses: any[];
  examples: any[];
}

interface Webhook {
  id: string;
  name: string;
  url: string;
  events: string[];
  status: 'active' | 'inactive' | 'error';
  lastTriggered?: string;
  successRate: number;
}

interface Integration {
  name: string;
  description: string;
  status: 'available' | 'coming_soon' | 'beta';
  category: string;
  logo: string;
  setupUrl?: string;
}

const APIDocumentation: React.FC = () => {
  const [apiKey, setApiKey] = useState('sk_live_...');
  const [showWebhookModal, setShowWebhookModal] = useState(false);
  const [showTestModal, setShowTestModal] = useState(false);
  const [selectedEndpoint, setSelectedEndpoint] = useState<APIEndpoint | null>(null);
  const [testResponse, setTestResponse] = useState('');
  const [webhooks, setWebhooks] = useState<Webhook[]>([]);
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [loading, setLoading] = useState(false);

  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Mock API endpoints
  const apiEndpoints: APIEndpoint[] = [
    {
      method: 'GET',
      path: '/api/v1/jobs',
      description: 'Retrieve all jobs for the authenticated user',
      parameters: [
        { name: 'page', type: 'integer', required: false, description: 'Page number for pagination' },
        { name: 'limit', type: 'integer', required: false, description: 'Number of items per page' },
        { name: 'status', type: 'string', required: false, description: 'Filter by job status' }
      ],
      responses: [
        { code: 200, description: 'Success', example: '{ "jobs": [...], "total": 100 }' },
        { code: 401, description: 'Unauthorized', example: '{ "error": "Invalid API key" }' }
      ],
      examples: [
        {
          language: 'curl',
          code: 'curl -X GET "https://api.leadtap.com/api/v1/jobs" \\\n  -H "Authorization: Bearer YOUR_API_KEY"'
        },
        {
          language: 'javascript',
          code: 'const response = await fetch("https://api.leadtap.com/api/v1/jobs", {\n  headers: {\n    "Authorization": "Bearer YOUR_API_KEY"\n  }\n});\nconst data = await response.json();'
        }
      ]
    },
    {
      method: 'POST',
      path: '/api/v1/jobs',
      description: 'Create a new scraping job',
      parameters: [
        { name: 'queries', type: 'array', required: true, description: 'Array of search queries' },
        { name: 'filters', type: 'object', required: false, description: 'Optional filters for results' }
      ],
      responses: [
        { code: 201, description: 'Job created', example: '{ "job_id": 123, "status": "pending" }' },
        { code: 400, description: 'Bad request', example: '{ "error": "Invalid queries format" }' }
      ],
      examples: [
        {
          language: 'curl',
          code: 'curl -X POST "https://api.leadtap.com/api/v1/jobs" \\\n  -H "Authorization: Bearer YOUR_API_KEY" \\\n  -H "Content-Type: application/json" \\\n  -d \'{"queries": ["restaurants in NYC"]}\''
        }
      ]
    },
    {
      method: 'GET',
      path: '/api/v1/jobs/{id}/results',
      description: 'Get results for a specific job',
      parameters: [
        { name: 'id', type: 'integer', required: true, description: 'Job ID' },
        { name: 'format', type: 'string', required: false, description: 'Export format (csv, json, xlsx)' }
      ],
      responses: [
        { code: 200, description: 'Job results', example: '{ "results": [...], "total": 150 }' },
        { code: 404, description: 'Job not found', example: '{ "error": "Job not found" }' }
      ],
      examples: [
        {
          language: 'curl',
          code: 'curl -X GET "https://api.leadtap.com/api/v1/jobs/123/results" \\\n  -H "Authorization: Bearer YOUR_API_KEY"'
        }
      ]
    }
  ];

  // Mock webhooks
  useEffect(() => {
    const mockWebhooks: Webhook[] = [
      {
        id: '1',
        name: 'Job Completion',
        url: 'https://myapp.com/webhooks/job-complete',
        events: ['job.completed'],
        status: 'active',
        lastTriggered: '2024-07-10T10:30:00Z',
        successRate: 98.5
      },
      {
        id: '2',
        name: 'Lead Export',
        url: 'https://myapp.com/webhooks/lead-export',
        events: ['lead.exported', 'lead.added_to_crm'],
        status: 'active',
        lastTriggered: '2024-07-10T09:15:00Z',
        successRate: 100
      }
    ];

    const mockIntegrations: Integration[] = [
      {
        name: 'Zapier',
        description: 'Connect LeadTap with 5000+ apps',
        status: 'available',
        category: 'Automation',
        logo: '🔗',
        setupUrl: 'https://zapier.com/apps/leadtap'
      },
      {
        name: 'Make (Integromat)',
        description: 'Advanced automation workflows',
        status: 'available',
        category: 'Automation',
        logo: '⚙️',
        setupUrl: 'https://make.com/integrations/leadtap'
      },
      {
        name: 'HubSpot',
        description: 'CRM integration for lead management',
        status: 'available',
        category: 'CRM',
        logo: '📊'
      },
      {
        name: 'Salesforce',
        description: 'Enterprise CRM integration',
        status: 'coming_soon',
        category: 'CRM',
        logo: '☁️'
      },
      {
        name: 'Slack',
        description: 'Get notifications in Slack',
        status: 'available',
        category: 'Communication',
        logo: '💬'
      },
      {
        name: 'Discord',
        description: 'Discord bot integration',
        status: 'beta',
        category: 'Communication',
        logo: '🎮'
      }
    ];

    setWebhooks(mockWebhooks);
    setIntegrations(mockIntegrations);
  }, []);

  const handleTestEndpoint = async (endpoint: APIEndpoint) => {
    setSelectedEndpoint(endpoint);
    setShowTestModal(true);
  };

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code);
    toast({
      title: 'Copied',
      description: 'Code copied to clipboard',
      status: 'success',
      duration: 2000,
    });
  };

  const handleCreateWebhook = async (webhookData: any) => {
    setLoading(true);
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const newWebhook: Webhook = {
        id: Date.now().toString(),
        name: webhookData.name,
        url: webhookData.url,
        events: webhookData.events,
        status: 'active',
        successRate: 100
      };

      setWebhooks([...webhooks, newWebhook]);
      setShowWebhookModal(false);
      toast({
        title: 'Webhook Created',
        description: 'Webhook has been created successfully',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create webhook',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const getMethodColor = (method: string) => {
    switch (method) {
      case 'GET': return 'green';
      case 'POST': return 'blue';
      case 'PUT': return 'yellow';
      case 'DELETE': return 'red';
      default: return 'gray';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'green';
      case 'inactive': return 'gray';
      case 'error': return 'red';
      default: return 'gray';
    }
  };

  return (
    <Box>
      <VStack spacing={6} align="stretch">
        {/* API Key Section */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <HStack justify="space-between" mb={4}>
              <Text fontSize="lg" fontWeight="bold">API Key</Text>
              <Button size="sm" leftIcon={<CopyIcon />} onClick={() => handleCopyCode(apiKey)}>
                Copy Key
              </Button>
            </HStack>
            
            <Box p={4} bg="gray.50" borderRadius="md" fontFamily="mono" fontSize="sm">
              {apiKey}
            </Box>
            
            <Text fontSize="sm" color="gray.600" mt={2}>
              Use this API key in the Authorization header: <Code>Authorization: Bearer YOUR_API_KEY</Code>
            </Text>
          </CardBody>
        </Card>

        {/* API Documentation */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Text fontSize="lg" fontWeight="bold" mb={4}>API Endpoints</Text>
            
            <Tabs>
              <TabList>
                <Tab>Jobs</Tab>
                <Tab>Leads</Tab>
                <Tab>Exports</Tab>
                <Tab>Webhooks</Tab>
              </TabList>

              <TabPanels>
                <TabPanel>
                  <VStack spacing={4} align="stretch">
                    {apiEndpoints.map((endpoint, index) => (
                      <Box key={index} p={4} border="1px" borderColor={borderColor} borderRadius="md">
                        <HStack justify="space-between" mb={2}>
                          <HStack>
                            <Badge colorScheme={getMethodColor(endpoint.method)}>
                              {endpoint.method}
                            </Badge>
                            <Code fontSize="sm">{endpoint.path}</Code>
                          </HStack>
                          <Button size="sm" onClick={() => handleTestEndpoint(endpoint)}>
                            Test
                          </Button>
                        </HStack>
                        
                        <Text fontSize="sm" color="gray.600" mb={3}>
                          {endpoint.description}
                        </Text>

                        <Accordion allowToggle>
                          <AccordionItem>
                            <AccordionButton>
                              <Text fontSize="sm" fontWeight="medium">Parameters</Text>
                              <AccordionIcon />
                            </AccordionButton>
                            <AccordionPanel>
                              <Table size="sm">
                                <Thead>
                                  <Tr>
                                    <Th>Name</Th>
                                    <Th>Type</Th>
                                    <Th>Required</Th>
                                    <Th>Description</Th>
                                  </Tr>
                                </Thead>
                                <Tbody>
                                  {endpoint.parameters.map((param, idx) => (
                                    <Tr key={idx}>
                                      <Td>{param.name}</Td>
                                      <Td>{param.type}</Td>
                                      <Td>{param.required ? 'Yes' : 'No'}</Td>
                                      <Td>{param.description}</Td>
                                    </Tr>
                                  ))}
                                </Tbody>
                              </Table>
                            </AccordionPanel>
                          </AccordionItem>

                          <AccordionItem>
                            <AccordionButton>
                              <Text fontSize="sm" fontWeight="medium">Examples</Text>
                              <AccordionIcon />
                            </AccordionButton>
                            <AccordionPanel>
                              <VStack spacing={3} align="stretch">
                                {endpoint.examples.map((example, idx) => (
                                  <Box key={idx}>
                                    <HStack justify="space-between" mb={2}>
                                      <Badge>{example.language}</Badge>
                                      <Button size="xs" onClick={() => handleCopyCode(example.code)}>
                                        Copy
                                      </Button>
                                    </HStack>
                                    <Box
                                      p={3}
                                      bg="gray.50"
                                      borderRadius="md"
                                      fontFamily="mono"
                                      fontSize="xs"
                                      overflowX="auto"
                                    >
                                      <pre>{example.code}</pre>
                                    </Box>
                                  </Box>
                                ))}
                              </VStack>
                            </AccordionPanel>
                          </AccordionItem>
                        </Accordion>
                      </Box>
                    ))}
                  </VStack>
                </TabPanel>

                <TabPanel>
                  <Text>Lead management endpoints coming soon...</Text>
                </TabPanel>

                <TabPanel>
                  <Text>Export endpoints coming soon...</Text>
                </TabPanel>

                <TabPanel>
                  <Text>Webhook endpoints coming soon...</Text>
                </TabPanel>
              </TabPanels>
            </Tabs>
          </CardBody>
        </Card>

        {/* Webhooks */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <HStack justify="space-between" mb={4}>
              <Text fontSize="lg" fontWeight="bold">Webhooks</Text>
              <Button size="sm" onClick={() => setShowWebhookModal(true)}>
                Create Webhook
              </Button>
            </HStack>
            
            {webhooks.length === 0 ? (
              <Text color="gray.500">No webhooks configured yet.</Text>
            ) : (
              <Table variant="simple" size="sm">
                <Thead>
                  <Tr>
                    <Th>Name</Th>
                    <Th>URL</Th>
                    <Th>Events</Th>
                    <Th>Status</Th>
                    <Th>Success Rate</Th>
                    <Th>Last Triggered</Th>
                    <Th>Actions</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {webhooks.map((webhook) => (
                    <Tr key={webhook.id}>
                      <Td>{webhook.name}</Td>
                      <Td>
                        <Text fontSize="xs" maxW="200px" isTruncated>
                          {webhook.url}
                        </Text>
                      </Td>
                      <Td>
                        <HStack spacing={1}>
                          {webhook.events.map((event) => (
                            <Badge key={event} size="sm" colorScheme="blue">
                              {event}
                            </Badge>
                          ))}
                        </HStack>
                      </Td>
                      <Td>
                        <Badge colorScheme={getStatusColor(webhook.status)}>
                          {webhook.status}
                        </Badge>
                      </Td>
                      <Td>{webhook.successRate}%</Td>
                      <Td fontSize="xs">
                        {webhook.lastTriggered ? new Date(webhook.lastTriggered).toLocaleString() : 'Never'}
                      </Td>
                      <Td>
                        <HStack spacing={1}>
                          <Tooltip label="Edit">
                            <IconButton size="xs" aria-label="Edit" icon={<SettingsIcon />} />
                          </Tooltip>
                          <Tooltip label="Delete">
                            <IconButton size="xs" aria-label="Delete" icon={<CloseIcon />} />
                          </Tooltip>
                        </HStack>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            )}
          </CardBody>
        </Card>

        {/* Integrations */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Text fontSize="lg" fontWeight="bold" mb={4}>Integrations</Text>
            
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
              {integrations.map((integration) => (
                <Box
                  key={integration.name}
                  p={4}
                  border="1px"
                  borderColor={borderColor}
                  borderRadius="md"
                  _hover={{ shadow: 'md' }}
                  transition="all 0.2s"
                >
                  <HStack justify="space-between" mb={2}>
                    <Text fontSize="lg">{integration.logo}</Text>
                    <Badge
                      colorScheme={
                        integration.status === 'available' ? 'green' :
                        integration.status === 'coming_soon' ? 'yellow' : 'blue'
                      }
                    >
                      {integration.status}
                    </Badge>
                  </HStack>
                  
                  <Text fontWeight="medium" mb={1}>{integration.name}</Text>
                  <Text fontSize="sm" color="gray.600" mb={3}>
                    {integration.description}
                  </Text>
                  
                  <Badge size="sm" colorScheme="gray" mb={3}>
                    {integration.category}
                  </Badge>
                  
                  {integration.setupUrl && integration.status === 'available' && (
                    <Button
                      size="sm"
                      rightIcon={<ExternalLinkIcon />}
                      onClick={() => window.open(integration.setupUrl, '_blank')}
                    >
                      Setup
                    </Button>
                  )}
                </Box>
              ))}
            </SimpleGrid>
          </CardBody>
        </Card>

        {/* SDKs & Libraries */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Text fontSize="lg" fontWeight="bold" mb={4}>SDKs & Libraries</Text>
            
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
              <Box p={4} border="1px" borderColor={borderColor} borderRadius="md">
                <Text fontWeight="medium" mb={2}>JavaScript/Node.js</Text>
                <Code fontSize="sm">npm install leadtap-sdk</Code>
                <Button size="sm" mt={2} onClick={() => handleCopyCode('npm install leadtap-sdk')}>
                  Copy
                </Button>
              </Box>
              
              <Box p={4} border="1px" borderColor={borderColor} borderRadius="md">
                <Text fontWeight="medium" mb={2}>Python</Text>
                <Code fontSize="sm">pip install leadtap-python</Code>
                <Button size="sm" mt={2} onClick={() => handleCopyCode('pip install leadtap-python')}>
                  Copy
                </Button>
              </Box>
              
              <Box p={4} border="1px" borderColor={borderColor} borderRadius="md">
                <Text fontWeight="medium" mb={2}>PHP</Text>
                <Code fontSize="sm">composer require leadtap/php-sdk</Code>
                <Button size="sm" mt={2} onClick={() => handleCopyCode('composer require leadtap/php-sdk')}>
                  Copy
                </Button>
              </Box>
              
              <Box p={4} border="1px" borderColor={borderColor} borderRadius="md">
                <Text fontWeight="medium" mb={2}>Postman Collection</Text>
                <Button size="sm" rightIcon={<DownloadIcon />}>
                  Download
                </Button>
              </Box>
            </SimpleGrid>
          </CardBody>
        </Card>
      </VStack>

      {/* Test Endpoint Modal */}
      <Modal isOpen={showTestModal} onClose={() => setShowTestModal(false)} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Test API Endpoint</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {selectedEndpoint && (
              <VStack spacing={4}>
                <HStack>
                  <Badge colorScheme={getMethodColor(selectedEndpoint.method)}>
                    {selectedEndpoint.method}
                  </Badge>
                  <Code>{selectedEndpoint.path}</Code>
                </HStack>
                
                <Text fontSize="sm" color="gray.600">
                  {selectedEndpoint.description}
                </Text>

                <FormControl>
                  <FormLabel>Request URL</FormLabel>
                  <Input
                    value={`https://api.leadtap.com${selectedEndpoint.path}`}
                    isReadOnly
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Headers</FormLabel>
                  <Textarea
                    value={`Authorization: Bearer ${apiKey}\nContent-Type: application/json`}
                    isReadOnly
                    rows={3}
                  />
                </FormControl>

                {selectedEndpoint.method === 'POST' && (
                  <FormControl>
                    <FormLabel>Request Body</FormLabel>
                    <Textarea
                      placeholder="Enter JSON payload..."
                      rows={5}
                    />
                  </FormControl>
                )}

                <Button
                  colorScheme="blue"
                  leftIcon={<PlayIcon />}
                  onClick={() => {
                    setTestResponse('{"status": "success", "message": "Test completed successfully"}');
                    toast({
                      title: 'Test Completed',
                      description: 'API call was successful',
                      status: 'success',
                      duration: 3000,
                    });
                  }}
                >
                  Send Test Request
                </Button>

                {testResponse && (
                  <FormControl>
                    <FormLabel>Response</FormLabel>
                    <Textarea
                      value={testResponse}
                      isReadOnly
                      rows={5}
                      fontFamily="mono"
                    />
                  </FormControl>
                )}
              </VStack>
            )}
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => setShowTestModal(false)}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Create Webhook Modal */}
      <Modal isOpen={showWebhookModal} onClose={() => setShowWebhookModal(false)}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Create Webhook</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl>
                <FormLabel>Webhook Name</FormLabel>
                <Input placeholder="e.g., Job Completion Notifications" />
              </FormControl>

              <FormControl>
                <FormLabel>Webhook URL</FormLabel>
                <Input placeholder="https://your-app.com/webhooks/leadtap" />
              </FormControl>

              <FormControl>
                <FormLabel>Events</FormLabel>
                <Select placeholder="Select events">
                  <option value="job.completed">Job Completed</option>
                  <option value="job.failed">Job Failed</option>
                  <option value="lead.exported">Lead Exported</option>
                  <option value="lead.added_to_crm">Lead Added to CRM</option>
                </Select>
              </FormControl>

              <Alert status="info">
                <AlertIcon />
                <Box>
                  <AlertTitle>Webhook Format</AlertTitle>
                  <AlertDescription>
                    Webhooks will send POST requests with JSON payloads to your specified URL.
                  </AlertDescription>
                </Box>
              </Alert>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => setShowWebhookModal(false)}>
              Cancel
            </Button>
            <Button
              colorScheme="blue"
              onClick={() => handleCreateWebhook({ name: 'Test', url: 'https://test.com', events: ['job.completed'] })}
              isLoading={loading}
            >
              Create Webhook
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default APIDocumentation; 