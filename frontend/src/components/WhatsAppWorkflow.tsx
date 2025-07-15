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
    <Box p={6}>
      <Heading size="lg" mb={6}>{t('whatsappWorkflow.whatsAppWorkflowAutomation')}</Heading>
      
      {/* Analytics Overview */}
      {analytics && (
        <Card mb={6} bg={bgColor} border="1px" borderColor={borderColor}>
          <CardHeader>
            <Heading size="md">{t('whatsappWorkflow.workflowAnalytics')}</Heading>
          </CardHeader>
          <CardBody>
            <StatGroup>
              <Stat>
                <StatLabel>{t('whatsappWorkflow.totalWorkflows')}</StatLabel>
                <StatNumber>{analytics.total_workflows}</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  12.5%
                </StatHelpText>
              </Stat>
              <Stat>
                <StatLabel>{t('whatsappWorkflow.activeWorkflows')}</StatLabel>
                <StatNumber>{analytics.active_workflows}</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  8.2%
                </StatHelpText>
              </Stat>
              <Stat>
                <StatLabel>{t('whatsappWorkflow.totalMessages')}</StatLabel>
                <StatNumber>{analytics.total_messages}</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  23.1%
                </StatHelpText>
              </Stat>
              <Stat>
                <StatLabel>{t('whatsappWorkflow.successRate')}</StatLabel>
                <StatNumber>{analytics.success_rate.toFixed(1)}%</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  5.3%
                </StatHelpText>
              </Stat>
            </StatGroup>
          </CardBody>
        </Card>
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
            <Card bg={bgColor} border="1px" borderColor={borderColor}>
              <CardHeader>
                <Flex align="center" justify="space-between">
                  <Heading size="md">{t('whatsappWorkflow.myWorkflows')}</Heading>
                  <Button
                    leftIcon={<FaPlus />}
                    colorScheme="blue"
                    onClick={onOpen}
                  >
                    {t('whatsappWorkflow.createNewWorkflow')}
                  </Button>
                </Flex>
              </CardHeader>
              <CardBody>
                {workflows.length === 0 ? (
                  <Alert status="info">
                    <AlertIcon />
                    <AlertTitle>{t('whatsappWorkflow.noWorkflowsYet')}</AlertTitle>
                    <AlertDescription>
                      {t('whatsappWorkflow.createYourFirstWorkflow')}
                    </AlertDescription>
                  </Alert>
                ) : (
                  <VStack spacing={4} align="stretch">
                    {workflows.map((workflow) => (
                      <Card key={workflow.id} variant="outline">
                        <CardBody>
                          <Flex align="center" justify="space-between">
                            <VStack align="start" spacing={2}>
                              <HStack>
                                <Heading size="md">{workflow.name}</Heading>
                                <Badge colorScheme={workflow.is_active ? 'green' : 'red'}>
                                  {workflow.is_active ? t('whatsappWorkflow.active') : t('whatsappWorkflow.inactive')}
                                </Badge>
                                <Badge colorScheme={getTriggerTypeColor(workflow.trigger_type)}>
                                  {workflow.trigger_type}
                                </Badge>
                              </HStack>
                              {workflow.description && (
                                <Text color="gray.600">{workflow.description}</Text>
                              )}
                              <Text fontSize="sm" color="gray.500">
                                {workflow.steps.length} {t('whatsappWorkflow.steps')} • {t('whatsappWorkflow.createdAt', 'Created')} {new Date(workflow.created_at!).toLocaleDateString()}
                              </Text>
                            </VStack>
                            
                            <HStack spacing={2}>
                              <Tooltip label={t('whatsappWorkflow.executeWorkflow')}>
                                <IconButton
                                  aria-label={t('whatsappWorkflow.executeWorkflow')}
                                  icon={<FaPlay />}
                                  colorScheme="green"
                                  size="sm"
                                  onClick={() => handleExecuteWorkflow(workflow.id!)}
                                />
                              </Tooltip>
                              <Tooltip label={t('whatsappWorkflow.editWorkflow')}>
                                <IconButton
                                  aria-label={t('whatsappWorkflow.editWorkflow')}
                                  icon={<FaEdit />}
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => {
                                    setCurrentWorkflow(workflow);
                                    onOpen();
                                  }}
                                />
                              </Tooltip>
                              <Tooltip label={t('whatsappWorkflow.duplicate')}>
                                <IconButton
                                  aria-label={t('whatsappWorkflow.duplicateWorkflow')}
                                  icon={<FaCopy />}
                                  size="sm"
                                  variant="ghost"
                                />
                              </Tooltip>
                              <Tooltip label={t('whatsappWorkflow.delete')}>
                                <IconButton
                                  aria-label={t('whatsappWorkflow.deleteWorkflow')}
                                  icon={<FaTrash />}
                                  size="sm"
                                  variant="ghost"
                                  colorScheme="red"
                                />
                              </Tooltip>
                            </HStack>
                          </Flex>
                          
                          {/* Workflow Steps Preview */}
                          <Box mt={4}>
                            <Text fontSize="sm" fontWeight="bold" mb={2}>{t('whatsappWorkflow.steps')}:</Text>
                            <VStack spacing={2} align="stretch">
                              {workflow.steps.map((step, index) => (
                                <HStack key={index} spacing={3}>
                                  {getStepIcon(step.step_type)}
                                  <Text fontSize="sm">{step.name}</Text>
                                  {step.step_type === 'delay' && step.delay_minutes && (
                                    <Badge size="sm">{step.delay_minutes}{t('whatsappWorkflow.minutes')}</Badge>
                                  )}
                                </HStack>
                              ))}
                            </VStack>
                          </Box>
                        </CardBody>
                      </Card>
                    ))}
                  </VStack>
                )}
              </CardBody>
            </Card>
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
                  <FormControl>
                    <FormLabel>{t('whatsappWorkflow.workflowName')}</FormLabel>
                    <Input
                      placeholder={t('whatsappWorkflow.enterWorkflowName')}
                      value={currentWorkflow.name}
                      onChange={(e) => setCurrentWorkflow({...currentWorkflow, name: e.target.value})}
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>{t('whatsappWorkflow.description')}</FormLabel>
                    <Textarea
                      placeholder={t('whatsappWorkflow.describeWorkflow')}
                      value={currentWorkflow.description}
                      onChange={(e) => setCurrentWorkflow({...currentWorkflow, description: e.target.value})}
                    />
                  </FormControl>

                  <HStack spacing={4}>
                    <FormControl>
                      <FormLabel>{t('whatsappWorkflow.triggerType')}</FormLabel>
                      <Select
                        value={currentWorkflow.trigger_type}
                        onChange={(e) => setCurrentWorkflow({...currentWorkflow, trigger_type: e.target.value})}
                      >
                        <option value="manual">{t('whatsappWorkflow.manual')}</option>
                        <option value="lead_created">{t('whatsappWorkflow.leadCreated')}</option>
                        <option value="lead_qualified">{t('whatsappWorkflow.leadQualified')}</option>
                        <option value="scheduled">{t('whatsappWorkflow.scheduled')}</option>
                      </Select>
                    </FormControl>
                    
                    <FormControl>
                      <FormLabel>{t('whatsappWorkflow.active')}</FormLabel>
                      <Switch
                        isChecked={currentWorkflow.is_active}
                        onChange={(e) => setCurrentWorkflow({...currentWorkflow, is_active: e.target.checked})}
                      />
                    </FormControl>
                  </HStack>

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
                      <Accordion allowMultiple>
                        {currentWorkflow.steps.map((step, index) => (
                          <AccordionItem key={index}>
                            <AccordionButton>
                              <HStack flex="1" textAlign="left">
                                {getStepIcon(step.step_type)}
                                <Text fontWeight="bold">{step.name}</Text>
                                <Badge size="sm">{step.step_type}</Badge>
                              </HStack>
                              <AccordionIcon />
                            </AccordionButton>
                            <AccordionPanel>
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
                                
                                <Button
                                  leftIcon={<FaTrash />}
                                  colorScheme="red"
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleRemoveStep(index)}
                                >
                                  {t('whatsappWorkflow.removeStep')}
                                </Button>
                              </VStack>
                            </AccordionPanel>
                          </AccordionItem>
                        ))}
                      </Accordion>
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
      <Modal isOpen={isOpen} onClose={onClose} size="6xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            {selectedWorkflow ? t('whatsappWorkflow.editWorkflow') : t('whatsappWorkflow.createNewWorkflow')}
          </ModalHeader>
          <ModalBody>
            {/* Workflow creation form would go here - same as in the Create Workflow tab */}
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              {t('whatsappWorkflow.cancel')}
            </Button>
            <Button colorScheme="blue" onClick={handleCreateWorkflow}>
              {selectedWorkflow ? t('whatsappWorkflow.updateWorkflow') : t('whatsappWorkflow.createWorkflow')}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default WhatsAppWorkflow; 