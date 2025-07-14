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
        description: 'Please enter a workflow name',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    if (currentWorkflow.steps.length === 0) {
      toast({
        title: 'Error',
        description: 'Please add at least one step to the workflow',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    try {
      const response = await api.createWhatsAppWorkflow(currentWorkflow);
      
      toast({
        title: 'Success',
        description: 'Workflow created successfully',
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
      name: `Step ${currentWorkflow.steps.length + 1}`,
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
        description: 'Workflow execution started',
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
      <Heading size="lg" mb={6}>WhatsApp Workflow Automation</Heading>
      
      {/* Analytics Overview */}
      {analytics && (
        <Card mb={6} bg={bgColor} border="1px" borderColor={borderColor}>
          <CardHeader>
            <Heading size="md">Workflow Analytics</Heading>
          </CardHeader>
          <CardBody>
            <StatGroup>
              <Stat>
                <StatLabel>Total Workflows</StatLabel>
                <StatNumber>{analytics.total_workflows}</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  12.5%
                </StatHelpText>
              </Stat>
              <Stat>
                <StatLabel>Active Workflows</StatLabel>
                <StatNumber>{analytics.active_workflows}</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  8.2%
                </StatHelpText>
              </Stat>
              <Stat>
                <StatLabel>Total Messages</StatLabel>
                <StatNumber>{analytics.total_messages}</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  23.1%
                </StatHelpText>
              </Stat>
              <Stat>
                <StatLabel>Success Rate</StatLabel>
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
          <Tab>My Workflows</Tab>
          <Tab>Create Workflow</Tab>
          <Tab>Templates</Tab>
        </TabList>

        <TabPanels>
          {/* My Workflows */}
          <TabPanel>
            <Card bg={bgColor} border="1px" borderColor={borderColor}>
              <CardHeader>
                <Flex align="center" justify="space-between">
                  <Heading size="md">My Workflows</Heading>
                  <Button
                    leftIcon={<FaPlus />}
                    colorScheme="blue"
                    onClick={onOpen}
                  >
                    Create New Workflow
                  </Button>
                </Flex>
              </CardHeader>
              <CardBody>
                {workflows.length === 0 ? (
                  <Alert status="info">
                    <AlertIcon />
                    <AlertTitle>No workflows yet</AlertTitle>
                    <AlertDescription>
                      Create your first workflow to start automating your WhatsApp messaging.
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
                                  {workflow.is_active ? 'Active' : 'Inactive'}
                                </Badge>
                                <Badge colorScheme={getTriggerTypeColor(workflow.trigger_type)}>
                                  {workflow.trigger_type}
                                </Badge>
                              </HStack>
                              {workflow.description && (
                                <Text color="gray.600">{workflow.description}</Text>
                              )}
                              <Text fontSize="sm" color="gray.500">
                                {workflow.steps.length} steps • Created {new Date(workflow.created_at!).toLocaleDateString()}
                              </Text>
                            </VStack>
                            
                            <HStack spacing={2}>
                              <Tooltip label="Execute Workflow">
                                <IconButton
                                  aria-label="Execute workflow"
                                  icon={<FaPlay />}
                                  colorScheme="green"
                                  size="sm"
                                  onClick={() => handleExecuteWorkflow(workflow.id!)}
                                />
                              </Tooltip>
                              <Tooltip label="Edit Workflow">
                                <IconButton
                                  aria-label="Edit workflow"
                                  icon={<FaEdit />}
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => {
                                    setCurrentWorkflow(workflow);
                                    onOpen();
                                  }}
                                />
                              </Tooltip>
                              <Tooltip label="Duplicate">
                                <IconButton
                                  aria-label="Duplicate workflow"
                                  icon={<FaCopy />}
                                  size="sm"
                                  variant="ghost"
                                />
                              </Tooltip>
                              <Tooltip label="Delete">
                                <IconButton
                                  aria-label="Delete workflow"
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
                            <Text fontSize="sm" fontWeight="bold" mb={2}>Steps:</Text>
                            <VStack spacing={2} align="stretch">
                              {workflow.steps.map((step, index) => (
                                <HStack key={index} spacing={3}>
                                  {getStepIcon(step.step_type)}
                                  <Text fontSize="sm">{step.name}</Text>
                                  {step.step_type === 'delay' && step.delay_minutes && (
                                    <Badge size="sm">{step.delay_minutes}min</Badge>
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
                <Heading size="md">Create New Workflow</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={6} align="stretch">
                  {/* Basic Information */}
                  <FormControl>
                    <FormLabel>Workflow Name</FormLabel>
                    <Input
                      placeholder="Enter workflow name"
                      value={currentWorkflow.name}
                      onChange={(e) => setCurrentWorkflow({...currentWorkflow, name: e.target.value})}
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>Description</FormLabel>
                    <Textarea
                      placeholder="Describe your workflow"
                      value={currentWorkflow.description}
                      onChange={(e) => setCurrentWorkflow({...currentWorkflow, description: e.target.value})}
                    />
                  </FormControl>

                  <HStack spacing={4}>
                    <FormControl>
                      <FormLabel>Trigger Type</FormLabel>
                      <Select
                        value={currentWorkflow.trigger_type}
                        onChange={(e) => setCurrentWorkflow({...currentWorkflow, trigger_type: e.target.value})}
                      >
                        <option value="manual">Manual</option>
                        <option value="lead_created">Lead Created</option>
                        <option value="lead_qualified">Lead Qualified</option>
                        <option value="scheduled">Scheduled</option>
                      </Select>
                    </FormControl>
                    
                    <FormControl>
                      <FormLabel>Active</FormLabel>
                      <Switch
                        isChecked={currentWorkflow.is_active}
                        onChange={(e) => setCurrentWorkflow({...currentWorkflow, is_active: e.target.checked})}
                      />
                    </FormControl>
                  </HStack>

                  {/* Workflow Steps */}
                  <Box>
                    <Flex align="center" justify="space-between" mb={4}>
                      <Heading size="sm">Workflow Steps</Heading>
                      <Button
                        leftIcon={<FaPlus />}
                        size="sm"
                        onClick={handleAddStep}
                      >
                        Add Step
                      </Button>
                    </Flex>
                    
                    {currentWorkflow.steps.length === 0 ? (
                      <Alert status="info">
                        <AlertIcon />
                        <AlertTitle>No steps added</AlertTitle>
                        <AlertDescription>
                          Add steps to your workflow to define the automation sequence.
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
                                  <FormLabel>Step Name</FormLabel>
                                  <Input
                                    value={step.name}
                                    onChange={(e) => handleUpdateStep(index, 'name', e.target.value)}
                                  />
                                </FormControl>
                                
                                <FormControl>
                                  <FormLabel>Step Type</FormLabel>
                                  <Select
                                    value={step.step_type}
                                    onChange={(e) => handleUpdateStep(index, 'step_type', e.target.value)}
                                  >
                                    <option value="message">Message</option>
                                    <option value="delay">Delay</option>
                                    <option value="condition">Condition</option>
                                    <option value="action">Action</option>
                                  </Select>
                                </FormControl>
                                
                                {step.step_type === 'message' && (
                                  <FormControl>
                                    <FormLabel>Message Content</FormLabel>
                                    <Textarea
                                      placeholder="Enter your message content. Use {{name}}, {{company}}, {{followers}} for variables."
                                      value={step.content}
                                      onChange={(e) => handleUpdateStep(index, 'content', e.target.value)}
                                    />
                                  </FormControl>
                                )}
                                
                                {step.step_type === 'delay' && (
                                  <FormControl>
                                    <FormLabel>Delay (minutes)</FormLabel>
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
                                      <FormLabel>Minimum Followers</FormLabel>
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
                                      <FormLabel>Minimum Engagement Score</FormLabel>
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
                                      <FormLabel>Required Contact Info</FormLabel>
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
                                          <Text fontSize="sm">Email</Text>
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
                                          <Text fontSize="sm">Phone</Text>
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
                                          <Text fontSize="sm">Website</Text>
                                        </HStack>
                                      </VStack>
                                    </FormControl>
                                  </VStack>
                                )}
                                
                                {step.step_type === 'action' && (
                                  <FormControl>
                                    <FormLabel>Actions</FormLabel>
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
                                        <Text fontSize="sm">Add to CRM</Text>
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
                                        <Text fontSize="sm">Send Follow-up</Text>
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
                                        <Text fontSize="sm">Update Status</Text>
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
                                        <Text fontSize="sm">Create Task</Text>
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
                                  Remove Step
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
                    Create Workflow
                  </Button>
                </VStack>
              </CardBody>
            </Card>
          </TabPanel>

          {/* Templates */}
          <TabPanel>
            <Card bg={bgColor} border="1px" borderColor={borderColor}>
              <CardHeader>
                <Heading size="md">Workflow Templates</Heading>
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
                            
                            <Text fontSize="sm" fontWeight="bold">Steps:</Text>
                            <VStack align="start" spacing={2}>
                              {template.steps.map((step, index) => (
                                <HStack key={index} spacing={2}>
                                  {getStepIcon(step.step_type)}
                                  <Text fontSize="sm">{step.name}</Text>
                                  {step.step_type === 'delay' && step.delay_minutes && (
                                    <Badge size="sm">{step.delay_minutes}min</Badge>
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
                              Use Template
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
            {selectedWorkflow ? 'Edit Workflow' : 'Create New Workflow'}
          </ModalHeader>
          <ModalBody>
            {/* Workflow creation form would go here - same as in the Create Workflow tab */}
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button colorScheme="blue" onClick={handleCreateWorkflow}>
              {selectedWorkflow ? 'Update' : 'Create'} Workflow
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default WhatsAppWorkflow; 