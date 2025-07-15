import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  VStack,
  HStack,
  Input,
  Select,
  Textarea,
  Badge,
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
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  StatGroup,
  Grid,
  GridItem,
  Flex,
  Spacer,
  Divider,
  List,
  ListItem,
  ListIcon,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Box as ChakraBox
} from '@chakra-ui/react';
import { 
  FaPlay,
  FaPause,
  FaStop,
  FaPlus,
  FaEdit,
  FaTrash,
  FaCopy,
  FaEye,
  FaCheck,
  FaTimes,
  FaClock,
  FaMessage,
  FaFilter,
  FaCog,
  FaChartLine,
  FaUsers,
  FaEnvelope,
  FaPhone,
  FaGlobe,
  FaCheckCircle,
  FaExclamationTriangle,
  FaInfoCircle
} from 'react-icons/fa';
import { api } from '../api';
import { useTranslation } from 'react-i18next';

interface WorkflowStep {
  id?: number;
  name: string;
  step_type: string;
  content?: string;
  delay_minutes?: number;
  conditions?: any;
  actions?: string[];
  order: number;
}

interface Workflow {
  id?: number;
  name: string;
  description?: string;
  trigger_type: string;
  trigger_conditions?: any;
  is_active: boolean;
  steps: WorkflowStep[];
  created_at?: string;
  updated_at?: string;
}

interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  trigger_type: string;
  steps: WorkflowStep[];
}

interface WorkflowAnalytics {
  total_workflows: number;
  active_workflows: number;
  total_messages: number;
  successful_messages: number;
  success_rate: number;
}

const WhatsAppWorkflow: React.FC = () => {
  const { t } = useTranslation();
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [analytics, setAnalytics] = useState<WorkflowAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [currentWorkflow, setCurrentWorkflow] = useState<Workflow>({
    name: '',
    description: '',
    trigger_type: 'manual',
    is_active: true,
    steps: []
  });

  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isOpen: isTemplateOpen, onOpen: onTemplateOpen, onClose: onTemplateClose } = useDisclosure();
  
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    loadWorkflows();
    loadTemplates();
    loadAnalytics();
  }, []);

  const loadWorkflows = async () => {
    setLoading(true);
    try {
      const response = await api.getWhatsAppWorkflows();
      setWorkflows(response);
    } catch (error: any) {
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

  const loadTemplates = async () => {
    try {
      const response = await api.getWhatsAppWorkflowTemplates();
      setTemplates(response);
    } catch (error: any) {
      console.error('Error loading templates:', error);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await api.getWhatsAppWorkflowAnalytics();
      setAnalytics(response);
    } catch (error: any) {
      console.error('Error loading analytics:', error);
    }
  };

  const handleCreateWorkflow = async () => {
    if (!currentWorkflow.name.trim()) {
      toast({
        title: 'Error',
        description: t('whatsappWorkflow.pleaseEnterWorkflowName'),
        status: 'error',
        duration: 3000,
      });
      return;
    }

    if (currentWorkflow.steps.length === 0) {
      toast({
        title: 'Error',
        description: t('whatsappWorkflow.pleaseAddAtLeastOneStep'),
        status: 'error',
        duration: 3000,
      });
      return;
    }

    try {
      const response = await api.createWhatsAppWorkflow(currentWorkflow);
      
      toast({
        title: 'Success',
        description: t('whatsappWorkflow.workflowCreatedSuccessfully'),
        status: 'success',
        duration: 3000,
      });
      
      // Reset form
      setCurrentWorkflow({
        name: '',
        description: '',
        trigger_type: 'manual',
        is_active: true,
        steps: []
      });
      
      loadWorkflows();
      onClose();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleAddStep = () => {
    const newStep: WorkflowStep = {
      name: `${t('whatsappWorkflow.step')} ${currentWorkflow.steps.length + 1}`,
      step_type: 'message',
      content: '',
      order: currentWorkflow.steps.length + 1
    };
    
    setCurrentWorkflow({
      ...currentWorkflow,
      steps: [...currentWorkflow.steps, newStep]
    });
  };

  const handleUpdateStep = (index: number, field: string, value: any) => {
    const updatedSteps = [...currentWorkflow.steps];
    updatedSteps[index] = { ...updatedSteps[index], [field]: value };
    
    setCurrentWorkflow({
      ...currentWorkflow,
      steps: updatedSteps
    });
  };

  const handleRemoveStep = (index: number) => {
    const updatedSteps = currentWorkflow.steps.filter((_, i) => i !== index);
    // Reorder steps
    updatedSteps.forEach((step, i) => {
      step.order = i + 1;
    });
    
    setCurrentWorkflow({
      ...currentWorkflow,
      steps: updatedSteps
    });
  };

  const handleUseTemplate = (template: WorkflowTemplate) => {
    setCurrentWorkflow({
      name: template.name,
      description: template.description,
      trigger_type: template.trigger_type,
      is_active: true,
      steps: template.steps.map((step, index) => ({
        ...step,
        order: index + 1
      }))
    });
    onTemplateClose();
    onOpen();
  };

  const handleExecuteWorkflow = async (workflowId: number) => {
    try {
      await api.executeWhatsAppWorkflow({
        workflow_id: workflowId,
        lead_id: null,
        social_lead_id: null
      });
      
      toast({
        title: 'Success',
        description: t('whatsappWorkflow.workflowExecutionStarted'),
        status: 'success',
        duration: 3000,
      });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  const getStepIcon = (stepType: string) => {
    switch (stepType) {
      case 'message': return <FaMessage />;
      case 'delay': return <FaClock />;
      case 'condition': return <FaFilter />;
      case 'action': return <FaCog />;
      default: return <FaCog />;
    }
  };

  const getTriggerTypeColor = (triggerType: string) => {
    switch (triggerType) {
      case 'lead_created': return 'green';
      case 'lead_qualified': return 'blue';
      case 'manual': return 'orange';
      case 'scheduled': return 'purple';
      default: return 'gray';
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">{t('whatsappWorkflow.whatsAppWorkflowAutomation')}</h1>
      
      {/* Analytics Overview */}
      {analytics && (
        <div className="mb-6 rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <h2 className="text-lg font-semibold mb-4">{t('whatsappWorkflow.workflowAnalytics')}</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-gray-500 text-sm">{t('whatsappWorkflow.totalWorkflows')}</div>
              <div className="text-2xl font-bold">{analytics.total_workflows}</div>
              <div className="text-green-600 text-xs mt-1">+12.5%</div>
            </div>
            <div>
              <div className="text-gray-500 text-sm">{t('whatsappWorkflow.activeWorkflows')}</div>
              <div className="text-2xl font-bold">{analytics.active_workflows}</div>
              <div className="text-green-600 text-xs mt-1">+8.2%</div>
            </div>
            <div>
              <div className="text-gray-500 text-sm">{t('whatsappWorkflow.totalMessages')}</div>
              <div className="text-2xl font-bold">{analytics.total_messages}</div>
              <div className="text-green-600 text-xs mt-1">+23.1%</div>
            </div>
            <div>
              <div className="text-gray-500 text-sm">{t('whatsappWorkflow.successRate')}</div>
              <div className="text-2xl font-bold">{analytics.success_rate.toFixed(1)}%</div>
              <div className="text-green-600 text-xs mt-1">+5.3%</div>
            </div>
          </div>
        </div>
      )}

      <Tabs>
        <TabList>
          <Tab>{t('whatsappWorkflow.myWorkflows')}</Tab>
          <Tab>{t('whatsappWorkflow.createWorkflow')}</Tab>
          <Tab>{t('whatsappWorkflow.templates')}</Tab>
        </TabList>

        <TabPanels>
          {/* My Workflows */}
          <TabPanel>
            <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">{t('whatsappWorkflow.myWorkflows')}</h2>
                <button
                  className="inline-flex items-center px-4 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  onClick={onOpen}
                >
                  <span className="mr-2">+</span>{t('whatsappWorkflow.createNewWorkflow')}
                </button>
              </div>
              {workflows.length === 0 ? (
                <div className="flex items-center p-4 bg-blue-50 border border-blue-200 rounded-md">
                  <span className="text-blue-500 mr-2">i</span>
                  <div>
                    <div className="font-semibold">{t('whatsappWorkflow.noWorkflowsYet')}</div>
                    <div className="text-sm text-gray-700 dark:text-gray-300">{t('whatsappWorkflow.createYourFirstWorkflow')}</div>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {workflows.map((workflow) => (
                    <div key={workflow.id} className="border rounded-lg p-4 bg-white dark:bg-gray-800 shadow-sm">
                      <div className="flex items-center justify-between">
                        <div className="flex flex-col space-y-2">
                          <div className="flex items-center space-x-2">
                            <span className="text-lg font-bold">{workflow.name}</span>
                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${workflow.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>{workflow.is_active ? t('whatsappWorkflow.active') : t('whatsappWorkflow.inactive')}</span>
                            <span className="inline-flex items-center px-2 py-0.5 rounded bg-gray-100 text-gray-700 text-xs font-semibold">{workflow.trigger_type}</span>
                          </div>
                          {workflow.description && (
                            <span className="text-gray-600 dark:text-gray-300">{workflow.description}</span>
                          )}
                          <span className="text-xs text-gray-500">{workflow.steps.length} {t('whatsappWorkflow.steps')} • {t('whatsappWorkflow.createdAt', 'Created')} {new Date(workflow.created_at!).toLocaleDateString()}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          {/* Replace with Lucide/Heroicons or inline SVGs for play, edit, copy, trash, etc. */}
                          <button aria-label={t('whatsappWorkflow.executeWorkflow')} className="p-2 rounded-full bg-green-100 hover:bg-green-200" onClick={() => handleExecuteWorkflow(workflow.id!)}>
                            {/* Play Icon */}
                            <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20"><polygon points="6,4 16,10 6,16" /></svg>
                          </button>
                          <button aria-label={t('whatsappWorkflow.editWorkflow')} className="p-2 rounded-full hover:bg-gray-200" onClick={() => { setCurrentWorkflow(workflow); onOpen(); }}>
                            {/* Edit Icon */}
                            <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path d="M15.232 5.232l3.536 3.536M9 13l6-6 3 3-6 6H9v-3z" /></svg>
                          </button>
                          <button aria-label={t('whatsappWorkflow.duplicateWorkflow')} className="p-2 rounded-full hover:bg-gray-200">
                            {/* Copy Icon */}
                            <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" /><rect x="3" y="3" width="13" height="13" rx="2" /></svg>
                          </button>
                          <button aria-label={t('whatsappWorkflow.deleteWorkflow')} className="p-2 rounded-full bg-red-100 hover:bg-red-200">
                            {/* Trash Icon */}
                            <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path d="M3 6h18M9 6v12a2 2 0 002 2h2a2 2 0 002-2V6" /></svg>
                          </button>
                        </div>
                      </div>
                      {/* Workflow Steps Preview */}
                      <div className="mt-4">
                        <span className="text-xs font-bold mb-2 block">{t('whatsappWorkflow.steps')}:</span>
                        <div className="space-y-2">
                          {workflow.steps.map((step, index) => (
                            <div key={index} className="flex items-center space-x-3">
                              {/* Replace with step icon as needed */}
                              <span className="w-4 h-4 bg-gray-200 rounded-full flex items-center justify-center text-xs font-bold">{step.step_type[0].toUpperCase()}</span>
                              <span className="text-xs">{step.name}</span>
                              {step.step_type === 'delay' && step.delay_minutes && (
                                <span className="inline-flex items-center px-2 py-0.5 rounded bg-gray-100 text-gray-700 text-xs font-semibold">{step.delay_minutes}{t('whatsappWorkflow.minutes')}</span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </TabPanel>

          {/* Create Workflow */}
          <TabPanel>
            <Card bg={bgColor} border="1px" borderColor={borderColor}>
              <CardHeader>
                <Heading size="md">{t('whatsappWorkflow.createNewWorkflow')}</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={6} align="stretch">
                  {/* Basic Information */}
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">{t('whatsappWorkflow.workflowName')}</label>
                      <input
                        type="text"
                        className="w-full rounded-md border border-gray-300 p-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary"
                        placeholder={t('whatsappWorkflow.enterWorkflowName')}
                        value={currentWorkflow.name}
                        onChange={(e) => setCurrentWorkflow({...currentWorkflow, name: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">{t('whatsappWorkflow.description')}</label>
                      <textarea
                        className="w-full rounded-md border border-gray-300 p-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary"
                        placeholder={t('whatsappWorkflow.describeWorkflow')}
                        value={currentWorkflow.description}
                        onChange={(e) => setCurrentWorkflow({...currentWorkflow, description: e.target.value})}
                      />
                    </div>
                    <div className="flex space-x-4">
                      <div className="flex-1">
                        <label className="block text-sm font-medium text-gray-700 mb-1">{t('whatsappWorkflow.triggerType')}</label>
                        <select
                          className="w-full rounded-md border border-gray-300 p-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary"
                          value={currentWorkflow.trigger_type}
                          onChange={(e) => setCurrentWorkflow({...currentWorkflow, trigger_type: e.target.value})}
                        >
                          <option value="manual">{t('whatsappWorkflow.manual')}</option>
                          <option value="lead_created">{t('whatsappWorkflow.leadCreated')}</option>
                          <option value="lead_qualified">{t('whatsappWorkflow.leadQualified')}</option>
                          <option value="scheduled">{t('whatsappWorkflow.scheduled')}</option>
                        </select>
                      </div>
                      <div className="flex items-center space-x-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">{t('whatsappWorkflow.active')}</label>
                        <input
                          type="checkbox"
                          checked={currentWorkflow.is_active}
                          onChange={(e) => setCurrentWorkflow({...currentWorkflow, is_active: e.target.checked})}
                          className="rounded border-gray-300 text-primary focus:ring-primary"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Workflow Steps */}
                  <Box>
                    <Flex align="center" justify="space-between" mb={4}>
                      <Heading size="sm">{t('whatsappWorkflow.workflowSteps')}</Heading>
                      <Button
                        leftIcon={<FaPlus />}
                        size="sm"
                        onClick={handleAddStep}
                      >
                        {t('whatsappWorkflow.addStep')}
                      </Button>
                    </Flex>
                    
                    {currentWorkflow.steps.length === 0 ? (
                      <Alert status="info">
                        <AlertIcon />
                        <AlertTitle>{t('whatsappWorkflow.noStepsAdded')}</AlertTitle>
                        <AlertDescription>
                          {t('whatsappWorkflow.addStepsDescription')}
                        </AlertDescription>
                      </Alert>
                    ) : (
                      <div className="border rounded-lg divide-y">
                        {currentWorkflow.steps.map((step, index) => (
                          <div key={index} className="p-4">
                            <div className="flex items-center justify-between cursor-pointer" onClick={() => {/* handle expand/collapse */}}>
                              <div className="flex items-center space-x-2">
                                {/* Replace with step icon as needed */}
                                <span className="w-4 h-4 bg-gray-200 rounded-full flex items-center justify-center text-xs font-bold">{step.step_type[0].toUpperCase()}</span>
                                <span className="font-bold">{step.name}</span>
                                <span className="inline-flex items-center px-2 py-0.5 rounded bg-gray-100 text-gray-700 text-xs font-semibold">{step.step_type}</span>
                              </div>
                              {/* Expand/collapse icon */}
                              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path d="M19 9l-7 7-7-7" /></svg>
                            </div>
                            {/* Expanded content for editing step details */}
                            <div className="mt-4">
                              <VStack spacing={4} align="stretch">
                                <FormControl>
                                  <FormLabel>{t('whatsappWorkflow.stepName')}</FormLabel>
                                  <Input
                                    value={step.name}
                                    onChange={(e) => handleUpdateStep(index, 'name', e.target.value)}
                                  />
                                </FormControl>
                                
                                <FormControl>
                                  <FormLabel>{t('whatsappWorkflow.stepType')}</FormLabel>
                                  <Select
                                    value={step.step_type}
                                    onChange={(e) => handleUpdateStep(index, 'step_type', e.target.value)}
                                  >
                                    <option value="message">{t('whatsappWorkflow.message')}</option>
                                    <option value="delay">{t('whatsappWorkflow.delay')}</option>
                                    <option value="condition">{t('whatsappWorkflow.condition')}</option>
                                    <option value="action">{t('whatsappWorkflow.action')}</option>
                                  </Select>
                                </FormControl>
                                
                                {step.step_type === 'message' && (
                                  <FormControl>
                                    <FormLabel>{t('whatsappWorkflow.messageContent')}</FormLabel>
                                    <Textarea
                                      placeholder={t('whatsappWorkflow.enterMessageContent')}
                                      value={step.content}
                                      onChange={(e) => handleUpdateStep(index, 'content', e.target.value)}
                                    />
                                  </FormControl>
                                )}
                                
                                {step.step_type === 'delay' && (
                                  <FormControl>
                                    <FormLabel>{t('whatsappWorkflow.delayMinutes')}</FormLabel>
                                    <NumberInput
                                      value={step.delay_minutes}
                                      onChange={(value) => handleUpdateStep(index, 'delay_minutes', parseInt(value))}
                                      min={0}
                                      max={1440}
                                    >
                                      <NumberInputField />
                                      <NumberInputStepper>
                                        <NumberIncrementStepper />
                                        <NumberDecrementStepper />
                                      </NumberInputStepper>
                                    </NumberInput>
                                  </FormControl>
                                )}
                                
                                {step.step_type === 'condition' && (
                                  <VStack spacing={4} align="stretch">
                                    <FormControl>
                                      <FormLabel>{t('whatsappWorkflow.minimumFollowers')}</FormLabel>
                                      <NumberInput
                                        value={step.conditions?.followers_min || 0}
                                        onChange={(value) => handleUpdateStep(index, 'conditions', {
                                          ...step.conditions,
                                          followers_min: parseInt(value)
                                        })}
                                        min={0}
                                      >
                                        <NumberInputField />
                                      </NumberInput>
                                    </FormControl>
                                    
                                    <FormControl>
                                      <FormLabel>{t('whatsappWorkflow.minimumEngagementScore')}</FormLabel>
                                      <NumberInput
                                        value={step.conditions?.engagement_score_min || 0}
                                        onChange={(value) => handleUpdateStep(index, 'conditions', {
                                          ...step.conditions,
                                          engagement_score_min: parseInt(value)
                                        })}
                                        min={0}
                                        max={100}
                                      >
                                        <NumberInputField />
                                      </NumberInput>
                                    </FormControl>
                                    
                                    <FormControl>
                                      <FormLabel>{t('whatsappWorkflow.requiredContactInfo')}</FormLabel>
                                      <VStack align="start" spacing={2}>
                                        <HStack>
                                          <Switch
                                            isChecked={step.conditions?.has_contact?.includes('email')}
                                            onChange={(e) => {
                                              const hasContact = step.conditions?.has_contact || [];
                                              const newHasContact = e.target.checked
                                                ? [...hasContact, 'email']
                                                : hasContact.filter(c => c !== 'email');
                                              handleUpdateStep(index, 'conditions', {
                                                ...step.conditions,
                                                has_contact: newHasContact
                                              });
                                            }}
                                          />
                                          <Text fontSize="sm">{t('whatsappWorkflow.email')}</Text>
                                        </HStack>
                                        <HStack>
                                          <Switch
                                            isChecked={step.conditions?.has_contact?.includes('phone')}
                                            onChange={(e) => {
                                              const hasContact = step.conditions?.has_contact || [];
                                              const newHasContact = e.target.checked
                                                ? [...hasContact, 'phone']
                                                : hasContact.filter(c => c !== 'phone');
                                              handleUpdateStep(index, 'conditions', {
                                                ...step.conditions,
                                                has_contact: newHasContact
                                              });
                                            }}
                                          />
                                          <Text fontSize="sm">{t('whatsappWorkflow.phone')}</Text>
                                        </HStack>
                                        <HStack>
                                          <Switch
                                            isChecked={step.conditions?.has_contact?.includes('website')}
                                            onChange={(e) => {
                                              const hasContact = step.conditions?.has_contact || [];
                                              const newHasContact = e.target.checked
                                                ? [...hasContact, 'website']
                                                : hasContact.filter(c => c !== 'website');
                                              handleUpdateStep(index, 'conditions', {
                                                ...step.conditions,
                                                has_contact: newHasContact
                                              });
                                            }}
                                          />
                                          <Text fontSize="sm">{t('whatsappWorkflow.website')}</Text>
                                        </HStack>
                                      </VStack>
                                    </FormControl>
                                  </VStack>
                                )}
                                
                                {step.step_type === 'action' && (
                                  <FormControl>
                                    <FormLabel>{t('whatsappWorkflow.actions')}</FormLabel>
                                    <VStack align="start" spacing={2}>
                                      <HStack>
                                        <Switch
                                          isChecked={step.actions?.includes('add_to_crm')}
                                          onChange={(e) => {
                                            const actions = step.actions || [];
                                            const newActions = e.target.checked
                                              ? [...actions, 'add_to_crm']
                                              : actions.filter(a => a !== 'add_to_crm');
                                            handleUpdateStep(index, 'actions', newActions);
                                          }}
                                        />
                                        <Text fontSize="sm">{t('whatsappWorkflow.addToCrm')}</Text>
                                      </HStack>
                                      <HStack>
                                        <Switch
                                          isChecked={step.actions?.includes('send_follow_up')}
                                          onChange={(e) => {
                                            const actions = step.actions || [];
                                            const newActions = e.target.checked
                                              ? [...actions, 'send_follow_up']
                                              : actions.filter(a => a !== 'send_follow_up');
                                            handleUpdateStep(index, 'actions', newActions);
                                          }}
                                        />
                                        <Text fontSize="sm">{t('whatsappWorkflow.sendFollowUp')}</Text>
                                      </HStack>
                                      <HStack>
                                        <Switch
                                          isChecked={step.actions?.includes('update_status')}
                                          onChange={(e) => {
                                            const actions = step.actions || [];
                                            const newActions = e.target.checked
                                              ? [...actions, 'update_status']
                                              : actions.filter(a => a !== 'update_status');
                                            handleUpdateStep(index, 'actions', newActions);
                                          }}
                                        />
                                        <Text fontSize="sm">{t('whatsappWorkflow.updateStatus')}</Text>
                                      </HStack>
                                      <HStack>
                                        <Switch
                                          isChecked={step.actions?.includes('create_task')}
                                          onChange={(e) => {
                                            const actions = step.actions || [];
                                            const newActions = e.target.checked
                                              ? [...actions, 'create_task']
                                              : actions.filter(a => a !== 'create_task');
                                            handleUpdateStep(index, 'actions', newActions);
                                          }}
                                        />
                                        <Text fontSize="sm">{t('whatsappWorkflow.createTask')}</Text>
                                      </HStack>
                                    </VStack>
                                  </FormControl>
                                )}
                                
                                <button
                                  className="mt-4 inline-flex items-center px-3 py-1.5 rounded-md border border-red-300 bg-red-50 text-red-700 text-xs font-medium hover:bg-red-100"
                                  onClick={() => handleRemoveStep(index)}
                                >
                                  {/* Trash Icon */}
                                  <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path d="M3 6h18M9 6v12a2 2 0 002 2h2a2 2 0 002-2V6" /></svg>
                                  {t('whatsappWorkflow.removeStep')}
                                </button>
                              </VStack>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </Box>

                  <Button
                    colorScheme="blue"
                    size="lg"
                    onClick={handleCreateWorkflow}
                    isDisabled={currentWorkflow.steps.length === 0}
                  >
                    {t('whatsappWorkflow.createWorkflow')}
                  </Button>
                </VStack>
              </CardBody>
            </Card>
          </TabPanel>

          {/* Templates */}
          <TabPanel>
            <Card bg={bgColor} border="1px" borderColor={borderColor}>
              <CardHeader>
                <Heading size="md">{t('whatsappWorkflow.workflowTemplates')}</Heading>
              </CardHeader>
              <CardBody>
                <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={6}>
                  {templates.map((template) => (
                    <GridItem key={template.id}>
                      <Card variant="outline">
                        <CardHeader>
                          <Heading size="md">{template.name}</Heading>
                          <Text color="gray.600">{template.description}</Text>
                        </CardHeader>
                        <CardBody>
                          <VStack align="start" spacing={3}>
                            <Badge colorScheme={getTriggerTypeColor(template.trigger_type)}>
                              {template.trigger_type}
                            </Badge>
                            
                            <Text fontSize="sm" fontWeight="bold">{t('whatsappWorkflow.steps')}:</Text>
                            <VStack align="start" spacing={2}>
                              {template.steps.map((step, index) => (
                                <HStack key={index} spacing={2}>
                                  {getStepIcon(step.step_type)}
                                  <Text fontSize="sm">{step.name}</Text>
                                  {step.step_type === 'delay' && step.delay_minutes && (
                                    <Badge size="sm">{step.delay_minutes}{t('whatsappWorkflow.minutes')}</Badge>
                                  )}
                                </HStack>
                              ))}
                            </VStack>
                            
                            <Button
                              leftIcon={<FaPlus />}
                              colorScheme="blue"
                              size="sm"
                              onClick={() => handleUseTemplate(template)}
                            >
                              {t('whatsappWorkflow.useTemplate')}
                            </Button>
                          </VStack>
                        </CardBody>
                      </Card>
                    </GridItem>
                  ))}
                </Grid>
              </CardBody>
            </Card>
          </TabPanel>
        </TabPanels>
      </Tabs>

      {/* Create/Edit Workflow Modal */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg w-full max-w-4xl mx-4 animate-fade-in">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <span className="text-lg font-bold">{selectedWorkflow ? t('whatsappWorkflow.editWorkflow') : t('whatsappWorkflow.createNewWorkflow')}</span>
              <button onClick={onClose} className="text-gray-400 hover:text-gray-600">&times;</button>
            </div>
            <div className="px-6 py-4">
              {/* Workflow creation form would go here - same as in the Create Workflow tab */}
            </div>
            <div className="flex items-center justify-end px-6 py-4 border-t border-gray-200 dark:border-gray-700 space-x-2">
              <button onClick={onClose} className="inline-flex items-center px-4 py-2 rounded-md bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-200 font-medium">
                {t('whatsappWorkflow.cancel')}
              </button>
              <button onClick={handleCreateWorkflow} className="inline-flex items-center px-4 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
                {selectedWorkflow ? t('whatsappWorkflow.updateWorkflow') : t('whatsappWorkflow.createWorkflow')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WhatsAppWorkflow; 