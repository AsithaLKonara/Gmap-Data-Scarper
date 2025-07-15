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
import * as api from '../api';
import { useTranslation } from 'react-i18next';

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
  const { t } = useTranslation();
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

  // Remove mock webhooks/integrations useEffect and replace with real API calls
  useEffect(() => {
    async function fetchApiDocsData() {
      try {
        // TODO: Replace with real API calls for endpoints, webhooks, and integrations if available
        // setWebhooks(await api.getWebhooks());
        // setIntegrations(await api.getIntegrations());
      } catch (e) {
        setWebhooks([]);
        setIntegrations([]);
      }
    }
    fetchApiDocsData();
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
    <div>
      <div className="space-y-6">
        {/* API Key Section */}
        <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <div className="flex items-center justify-between mb-4">
            <span className="text-lg font-bold">API Key</span>
            <button
              className="inline-flex items-center px-3 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-sm"
              onClick={() => handleCopyCode(apiKey)}
            >
              <span className="mr-2">📋</span>Copy Key
            </button>
          </div>
          <div className="p-4 bg-gray-50 rounded font-mono text-sm">{apiKey}</div>
          <span className="text-sm text-gray-600 mt-2 block">
            Use this API key in the Authorization header: <code className="bg-gray-100 px-1 rounded">Authorization: Bearer YOUR_API_KEY</code>
          </span>
        </div>
        {/* API Documentation */}
        <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <span className="text-lg font-bold mb-4 block">API Endpoints</span>
          <div>
            <div className="flex border-b border-gray-200 mb-4">
              <button className="px-4 py-2 text-sm font-medium text-gray-700 border-b-2 border-primary">{t('apiDocs.jobs', 'Jobs')}</button>
              <button className="px-4 py-2 text-sm font-medium text-gray-500">{t('apiDocs.leads', 'Leads')}</button>
              <button className="px-4 py-2 text-sm font-medium text-gray-500">{t('apiDocs.exports', 'Exports')}</button>
              <button className="px-4 py-2 text-sm font-medium text-gray-500">{t('apiDocs.webhooks', 'Webhooks')}</button>
            </div>
            <div>
              {/* Jobs TabPanel */}
              <div>
                <div className="flex items-start p-4 bg-blue-50 border border-blue-200 rounded-md">
                  <span className="text-blue-500 mr-2">ℹ️</span>
                  <div>
                    <span className="font-semibold block">{t('apiDocs.apiEndpoints', 'API Endpoints')}</span>
                    <span className="text-sm text-gray-700 dark:text-gray-300 block">
                      API endpoints are currently being fetched from the backend. Please check back later or contact support for more details.
                    </span>
                  </div>
                </div>
              </div>
              {/* Leads TabPanel */}
              <div className="hidden">
                <span>{t('apiDocs.leadsComingSoon', 'Lead management endpoints coming soon...')}</span>
              </div>
              {/* Exports TabPanel */}
              <div className="hidden">
                <span>{t('apiDocs.exportsComingSoon', 'Export endpoints coming soon...')}</span>
              </div>
              {/* Webhooks TabPanel */}
              <div className="hidden">
                <span>{t('apiDocs.webhooksComingSoon', 'Webhook endpoints coming soon...')}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Webhooks */}
        <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <div className="flex items-center justify-between mb-4">
            <span className="text-lg font-bold">{t('apiDocs.webhooks', 'Webhooks')}</span>
            <button
              className="inline-flex items-center px-3 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-sm"
              onClick={() => setShowWebhookModal(true)}
            >
              {t('apiDocs.createWebhook', 'Create Webhook')}
            </button>
          </div>
          {webhooks.length === 0 ? (
            <span className="text-gray-500">{t('apiDocs.noWebhooksConfigured', 'No webhooks configured yet.')}</span>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm border-separate border-spacing-y-2">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-2 py-1 font-medium text-gray-700 text-left">{t('apiDocs.name', 'Name')}</th>
                    <th className="px-2 py-1 font-medium text-gray-700 text-left">{t('apiDocs.url', 'URL')}</th>
                    <th className="px-2 py-1 font-medium text-gray-700 text-left">{t('apiDocs.events', 'Events')}</th>
                    <th className="px-2 py-1 font-medium text-gray-700 text-left">{t('apiDocs.status', 'Status')}</th>
                    <th className="px-2 py-1 font-medium text-gray-700 text-left">{t('apiDocs.successRate', 'Success Rate')}</th>
                    <th className="px-2 py-1 font-medium text-gray-700 text-left">{t('apiDocs.lastTriggered', 'Last Triggered')}</th>
                    <th className="px-2 py-1 font-medium text-gray-700 text-left">{t('apiDocs.actions', 'Actions')}</th>
                  </tr>
                </thead>
                <tbody>
                  {webhooks.map((webhook) => (
                    <tr key={webhook.id} className="even:bg-gray-50">
                      <td className="px-2 py-1">{webhook.name}</td>
                      <td className="px-2 py-1 max-w-[200px] truncate text-xs">{webhook.url}</td>
                      <td className="px-2 py-1">
                        <div className="flex flex-wrap gap-1">
                          {webhook.events.map((event) => (
                            <span key={event} className="inline-flex items-center px-2 py-0.5 rounded bg-blue-100 text-blue-700 text-xs font-semibold">{event}</span>
                          ))}
                        </div>
                      </td>
                      <td className="px-2 py-1">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${getStatusColor(webhook.status) === 'green' ? 'bg-green-100 text-green-700' : getStatusColor(webhook.status) === 'red' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'}`}>{webhook.status}</span>
                      </td>
                      <td className="px-2 py-1">{webhook.successRate}%</td>
                      <td className="px-2 py-1 text-xs">{webhook.lastTriggered ? new Date(webhook.lastTriggered).toLocaleString() : 'Never'}</td>
                      <td className="px-2 py-1">
                        <div className="flex items-center space-x-1">
                          <button aria-label={t('apiDocs.edit', 'Edit')} className="p-1 rounded hover:bg-gray-200" title={t('apiDocs.edit', 'Edit')}>
                            <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path d="M15.232 5.232l3.536 3.536M9 13l6-6 3 3-6 6H9v-3z" /></svg>
                          </button>
                          <button aria-label={t('apiDocs.delete', 'Delete')} className="p-1 rounded hover:bg-gray-200" title={t('apiDocs.delete', 'Delete')}>
                            <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path d="M3 6h18M9 6v12a2 2 0 002 2h2a2 2 0 002-2V6" /></svg>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
        {/* Integrations */}
        <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <span className="text-lg font-bold mb-4 block">{t('apiDocs.integrations', 'Integrations')}</span>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {integrations.map((integration) => (
              <div
                key={integration.name}
                className="p-4 border rounded-md hover:shadow-md transition-all"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-lg">{integration.logo}</span>
                  <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${integration.status === 'available' ? 'bg-green-100 text-green-700' : integration.status === 'coming_soon' ? 'bg-yellow-100 text-yellow-700' : 'bg-blue-100 text-blue-700'}`}>{integration.status}</span>
                </div>
                <span className="font-medium block mb-1">{integration.name}</span>
                <span className="text-sm text-gray-600 block mb-3">{integration.description}</span>
                <span className="inline-flex items-center px-2 py-0.5 rounded bg-gray-100 text-gray-700 text-xs font-semibold mb-3">{integration.category}</span>
                {integration.setupUrl && integration.status === 'available' && (
                  <button
                    className="inline-flex items-center px-3 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-sm"
                    onClick={() => window.open(integration.setupUrl, '_blank')}
                  >
                    {t('apiDocs.setup', 'Setup')}
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
        {/* SDKs & Libraries */}
        <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <span className="text-lg font-bold mb-4 block">{t('apiDocs.sdksLibraries', 'SDKs & Libraries')}</span>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border rounded-md">
              <span className="font-medium block mb-2">{t('apiDocs.javascriptNodejs', 'JavaScript/Node.js')}</span>
              <span className="bg-gray-100 px-2 py-1 rounded font-mono text-sm block">npm install leadtap-sdk</span>
              <button className="inline-flex items-center px-3 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-sm mt-2" onClick={() => handleCopyCode('npm install leadtap-sdk')}>
                {t('apiDocs.copy', 'Copy')}
              </button>
            </div>
            <div className="p-4 border rounded-md">
              <span className="font-medium block mb-2">{t('apiDocs.python', 'Python')}</span>
              <span className="bg-gray-100 px-2 py-1 rounded font-mono text-sm block">pip install leadtap-python</span>
              <button className="inline-flex items-center px-3 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-sm mt-2" onClick={() => handleCopyCode('pip install leadtap-python')}>
                {t('apiDocs.copy', 'Copy')}
              </button>
            </div>
            <div className="p-4 border rounded-md">
              <span className="font-medium block mb-2">{t('apiDocs.php', 'PHP')}</span>
              <span className="bg-gray-100 px-2 py-1 rounded font-mono text-sm block">composer require leadtap/php-sdk</span>
              <button className="inline-flex items-center px-3 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-sm mt-2" onClick={() => handleCopyCode('composer require leadtap/php-sdk')}>
                {t('apiDocs.copy', 'Copy')}
              </button>
            </div>
            <div className="p-4 border rounded-md">
              <span className="font-medium block mb-2">{t('apiDocs.postmanCollection', 'Postman Collection')}</span>
              <button className="inline-flex items-center px-3 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-sm mt-2">
                {t('apiDocs.download', 'Download')}
              </button>
            </div>
          </div>
        </div>
      </div>
      {/* Test Endpoint Modal */}
      {showTestModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg w-full max-w-xl mx-4 animate-fade-in">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <span className="text-lg font-bold">{t('apiDocs.testApiEndpoint', 'Test API Endpoint')}</span>
              <button onClick={() => setShowTestModal(false)} className="text-gray-400 hover:text-gray-600">&times;</button>
            </div>
            <div className="px-6 py-4 space-y-4">
              {selectedEndpoint && (
                <>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${getMethodColor(selectedEndpoint.method) === 'green' ? 'bg-green-100 text-green-700' : getMethodColor(selectedEndpoint.method) === 'blue' ? 'bg-blue-100 text-blue-700' : getMethodColor(selectedEndpoint.method) === 'yellow' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>{selectedEndpoint.method}</span>
                    <span className="bg-gray-100 px-2 py-1 rounded font-mono text-xs">{selectedEndpoint.path}</span>
                  </div>
                  <span className="text-sm text-gray-600 block">{selectedEndpoint.description}</span>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('apiDocs.requestUrl', 'Request URL')}</label>
                    <input
                      value={`https://api.leadtap.com${selectedEndpoint.path}`}
                      readOnly
                      className="w-full rounded-md border border-gray-300 p-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('apiDocs.headers', 'Headers')}</label>
                    <textarea
                      value={`Authorization: Bearer ${apiKey}\nContent-Type: application/json`}
                      readOnly
                      rows={3}
                      className="w-full rounded-md border border-gray-300 p-2 text-sm font-mono focus:ring-2 focus:ring-primary focus:border-primary"
                    />
                  </div>
                  {selectedEndpoint.method === 'POST' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">{t('apiDocs.requestBody', 'Request Body')}</label>
                      <textarea
                        placeholder={t('apiDocs.enterJsonPayload', 'Enter JSON payload...')}
                        rows={5}
                        className="w-full rounded-md border border-gray-300 p-2 text-sm font-mono focus:ring-2 focus:ring-primary focus:border-primary"
                      />
                    </div>
                  )}
                  <button
                    className="inline-flex items-center px-4 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    onClick={() => {
                      setTestResponse('{"status": "success", "message": "Test completed successfully"}');
                      toast({
                        title: t('apiDocs.testCompleted', 'Test Completed'),
                        description: t('apiDocs.apiCallSuccess', 'API call was successful'),
                        status: 'success',
                        duration: 3000,
                      });
                    }}
                  >
                    {t('apiDocs.sendTestRequest', 'Send Test Request')}
                  </button>
                  {testResponse && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">{t('apiDocs.response', 'Response')}</label>
                      <textarea
                        value={testResponse}
                        readOnly
                        rows={5}
                        className="w-full rounded-md border border-gray-300 p-2 text-sm font-mono focus:ring-2 focus:ring-primary focus:border-primary"
                      />
                    </div>
                  )}
                </>
              )}
            </div>
            <div className="flex items-center justify-end px-6 py-4 border-t border-gray-200 dark:border-gray-700 space-x-2">
              <button onClick={() => setShowTestModal(false)} className="inline-flex items-center px-4 py-2 rounded-md bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-200 font-medium">
                {t('apiDocs.close', 'Close')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Webhook Modal */}
      <Modal isOpen={showWebhookModal} onClose={() => setShowWebhookModal(false)}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t('apiDocs.createWebhook', 'Create Webhook')}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl>
                <FormLabel>{t('apiDocs.webhookName', 'Webhook Name')}</FormLabel>
                <Input placeholder={t('apiDocs.webhookNamePlaceholder', 'e.g., Job Completion Notifications')} />
              </FormControl>

              <FormControl>
                <FormLabel>{t('apiDocs.webhookUrl', 'Webhook URL')}</FormLabel>
                <Input placeholder={t('apiDocs.webhookUrlPlaceholder', 'https://your-app.com/webhooks/leadtap')} />
              </FormControl>

              <FormControl>
                <FormLabel>{t('apiDocs.events', 'Events')}</FormLabel>
                <Select placeholder={t('apiDocs.selectEvents', 'Select events')}>
                  <option value="job.completed">{t('apiDocs.jobCompleted', 'Job Completed')}</option>
                  <option value="job.failed">{t('apiDocs.jobFailed', 'Job Failed')}</option>
                  <option value="lead.exported">{t('apiDocs.leadExported', 'Lead Exported')}</option>
                  <option value="lead.added_to_crm">{t('apiDocs.leadAddedToCrm', 'Lead Added to CRM')}</option>
                </Select>
              </FormControl>

              <Alert status="info">
                <AlertIcon />
                <Box>
                  <AlertTitle>{t('apiDocs.webhookFormat', 'Webhook Format')}</AlertTitle>
                  <AlertDescription>
                    {t('apiDocs.webhookFormatDescription', 'Webhooks will send POST requests with JSON payloads to your specified URL.')}
                  </AlertDescription>
                </Box>
              </Alert>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => setShowWebhookModal(false)}>
              {t('apiDocs.cancel', 'Cancel')}
            </Button>
            <Button
              colorScheme="blue"
              onClick={() => handleCreateWebhook({ name: 'Test', url: 'https://test.com', events: ['job.completed'] })}
              isLoading={loading}
            >
              {t('apiDocs.createWebhook', 'Create Webhook')}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </div>
  );
};

export default APIDocumentation; 