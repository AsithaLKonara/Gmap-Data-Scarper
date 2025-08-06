import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  VStack,
  HStack,
  Heading,
  Text,
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
  SimpleGrid,
  useDisclosure as useChakraDisclosure,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import {
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
} from 'react-icons/fi';

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
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useChakraDisclosure();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [analytics, setAnalytics] = useState<WorkflowAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentWorkflow, setCurrentWorkflow] = useState<Workflow | null>(null);
  const [editingStep, setEditingStep] = useState<number | null>(null);

  // Mock data - replace with actual API calls
  useEffect(() => {
    const mockWorkflows: Workflow[] = [
      {
        id: 1,
        name: 'Welcome Series',
        description: 'Welcome new leads with a 3-step sequence',
        trigger_type: 'lead_created',
        is_active: true,
        steps: [
          {
            id: 1,
            name: 'Welcome Message',
            step_type: 'message',
            content: 'Hi {{name}}, welcome to LeadTap! We\'re excited to help you grow your business.',
            order: 1,
          },
          {
            id: 2,
            name: 'Delay',
            step_type: 'delay',
            delay_minutes: 60,
            order: 2,
          },
          {
            id: 3,
            name: 'Follow-up',
            step_type: 'message',
            content: 'Have you had a chance to explore our features? Let me know if you need any help!',
            order: 3,
          },
        ],
        created_at: '2024-01-15T10:30:00Z',
      },
    ];

    const mockTemplates: WorkflowTemplate[] = [
      {
        id: 'welcome',
        name: 'Welcome Series',
        description: '3-step welcome sequence for new leads',
        trigger_type: 'lead_created',
        steps: [
          {
            name: 'Welcome Message',
            step_type: 'message',
            content: 'Welcome to our platform!',
            order: 1,
          },
          {
            name: 'Delay',
            step_type: 'delay',
            delay_minutes: 30,
            order: 2,
          },
          {
            name: 'Follow-up',
            step_type: 'message',
            content: 'How can we help you?',
            order: 3,
          },
        ],
      },
    ];

    const mockAnalytics: WorkflowAnalytics = {
      total_workflows: 5,
      active_workflows: 3,
      total_messages: 1250,
      successful_messages: 1180,
      success_rate: 94.4,
    };

    setWorkflows(mockWorkflows);
    setTemplates(mockTemplates);
    setAnalytics(mockAnalytics);
  }, []);

  const handleCreateWorkflow = () => {
    const newWorkflow: Workflow = {
      name: 'New Workflow',
      description: '',
      trigger_type: 'manual',
      is_active: false,
      steps: [],
    };
    setCurrentWorkflow(newWorkflow);
    onOpen();
  };

  const handleSaveWorkflow = async () => {
    if (!currentWorkflow) return;

    setLoading(true);
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      
      if (currentWorkflow.id) {
        // Update existing workflow
        setWorkflows(workflows.map(w => 
          w.id === currentWorkflow.id ? currentWorkflow : w
        ));
        toast({
          title: 'Workflow updated',
          status: 'success',
          duration: 3000,
        });
      } else {
        // Create new workflow
        const newWorkflow = { ...currentWorkflow, id: Date.now() };
        setWorkflows([...workflows, newWorkflow]);
        toast({
          title: 'Workflow created',
          status: 'success',
          duration: 3000,
        });
      }
      onClose();
    } catch (error) {
      toast({
        title: 'Error saving workflow',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddStep = () => {
    if (!currentWorkflow) return;
    
    const newStep: WorkflowStep = {
      name: 'New Step',
      step_type: 'message',
      content: '',
      order: currentWorkflow.steps.length + 1,
    };
    
    setCurrentWorkflow({
      ...currentWorkflow,
      steps: [...currentWorkflow.steps, newStep],
    });
  };

  const handleUpdateStep = (index: number, field: string, value: any) => {
    if (!currentWorkflow) return;
    
    const updatedSteps = [...currentWorkflow.steps];
    updatedSteps[index] = { ...updatedSteps[index], [field]: value };
    
    setCurrentWorkflow({
      ...currentWorkflow,
      steps: updatedSteps,
    });
  };

  const handleRemoveStep = (index: number) => {
    if (!currentWorkflow) return;
    
    const updatedSteps = currentWorkflow.steps.filter((_, i) => i !== index);
    setCurrentWorkflow({
      ...currentWorkflow,
      steps: updatedSteps,
    });
  };

  const handleUseTemplate = (template: WorkflowTemplate) => {
    const newWorkflow: Workflow = {
      name: template.name,
      description: template.description,
      trigger_type: template.trigger_type,
      is_active: false,
      steps: template.steps.map((step, index) => ({
        ...step,
        order: index + 1,
      })),
    };
    setCurrentWorkflow(newWorkflow);
    onOpen();
  };

  const getStepIcon = (stepType: string) => {
    switch (stepType) {
      case 'message':
        return <FiMessageSquare />;
      case 'delay':
        return <FiClock />;
      case 'condition':
        return <FiFilter />;
      default:
        return <FiSettings />;
    }
  };

  const getTriggerTypeColor = (triggerType: string) => {
    switch (triggerType) {
      case 'lead_created':
        return 'green';
      case 'manual':
        return 'blue';
      case 'schedule':
        return 'purple';
      default:
        return 'gray';
    }
  };

  return (
    <Box>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>WhatsApp Workflows</Heading>
          <Text color={textColor}>
            Create automated messaging sequences for your leads
          </Text>
        </Box>

        {/* Analytics */}
        {analytics && (
          <SimpleGrid columns={{ base: 1, md: 4 }} spacing={6}>
            <Stat>
              <StatLabel>Total Workflows</StatLabel>
              <StatNumber>{analytics.total_workflows}</StatNumber>
              <StatHelpText>Created workflows</StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Active Workflows</StatLabel>
              <StatNumber color="green.500">{analytics.active_workflows}</StatNumber>
              <StatHelpText>Currently running</StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Total Messages</StatLabel>
              <StatNumber>{analytics.total_messages.toLocaleString()}</StatNumber>
              <StatHelpText>Sent this month</StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Success Rate</StatLabel>
              <StatNumber color="blue.500">{analytics.success_rate}%</StatNumber>
              <StatHelpText>Message delivery rate</StatHelpText>
            </Stat>
          </SimpleGrid>
        )}

        {/* Main Content */}
        <Tabs variant="enclosed">
          <TabList>
            <Tab>My Workflows</Tab>
            <Tab>Templates</Tab>
          </TabList>

          <TabPanels>
            {/* Workflows Tab */}
            <TabPanel>
              <VStack spacing={6} align="stretch">
                <HStack justify="space-between">
                  <Text fontSize="lg" fontWeight="medium">Your Workflows</Text>
                  <Button
                    leftIcon={<FiPlus />}
                    colorScheme="blue"
                    onClick={handleCreateWorkflow}
                  >
                    Create Workflow
                  </Button>
                </HStack>

                <VStack spacing={4} align="stretch">
                  {workflows.map((workflow) => (
                    <Box
                      key={workflow.id}
                      bg={bgColor}
                      border="1px"
                      borderColor={borderColor}
                      borderRadius="lg"
                      p={6}
                    >
                      <VStack spacing={4} align="stretch">
                        <HStack justify="space-between">
                          <VStack align="start" spacing={1}>
                            <Heading size="md">{workflow.name}</Heading>
                            <Text color={textColor}>{workflow.description}</Text>
                          </VStack>
                          <HStack spacing={2}>
                            <Badge colorScheme={getTriggerTypeColor(workflow.trigger_type)}>
                              {workflow.trigger_type}
                            </Badge>
                            <Badge colorScheme={workflow.is_active ? 'green' : 'gray'}>
                              {workflow.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                          </HStack>
                        </HStack>

                        <Text fontSize="sm" fontWeight="medium">Steps ({workflow.steps.length})</Text>
                        <VStack spacing={2} align="stretch">
                          {workflow.steps.map((step, index) => (
                            <HStack key={index} p={3} bg="gray.50" borderRadius="md">
                              <Text fontSize="sm" fontWeight="bold" minW="20px">
                                {index + 1}
                              </Text>
                              {getStepIcon(step.step_type)}
                              <Text fontSize="sm" flex={1}>
                                {step.name}
                              </Text>
                              <Text fontSize="xs" color={textColor}>
                                {step.step_type}
                              </Text>
                            </HStack>
                          ))}
                        </VStack>

                        <HStack spacing={2} justify="end">
                          <IconButton
                            size="sm"
                            variant="ghost"
                            icon={<FiEdit />}
                            onClick={() => {
                              setCurrentWorkflow(workflow);
                              onOpen();
                            }}
                            aria-label="Edit workflow"
                          />
                          <IconButton
                            size="sm"
                            variant="ghost"
                            icon={<FiPlay />}
                            aria-label="Start workflow"
                          />
                          <IconButton
                            size="sm"
                            variant="ghost"
                            colorScheme="red"
                            icon={<FiTrash2 />}
                            aria-label="Delete workflow"
                          />
                        </HStack>
                      </VStack>
                    </Box>
                  ))}
                </VStack>
              </VStack>
            </TabPanel>

            {/* Templates Tab */}
            <TabPanel>
              <VStack spacing={6} align="stretch">
                <Text fontSize="lg" fontWeight="medium">Workflow Templates</Text>
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                  {templates.map((template) => (
                    <Box
                      key={template.id}
                      bg={bgColor}
                      border="1px"
                      borderColor={borderColor}
                      borderRadius="lg"
                      p={6}
                    >
                      <VStack spacing={4} align="stretch">
                        <Heading size="md">{template.name}</Heading>
                        <Text color={textColor}>{template.description}</Text>
                        <Badge colorScheme={getTriggerTypeColor(template.trigger_type)} alignSelf="start">
                          {template.trigger_type}
                        </Badge>
                        <Text fontSize="sm">
                          {template.steps.length} steps
                        </Text>
                        <Button
                          leftIcon={<FiPlus />}
                          onClick={() => handleUseTemplate(template)}
                          size="sm"
                        >
                          Use Template
                        </Button>
                      </VStack>
                    </Box>
                  ))}
                </SimpleGrid>
              </VStack>
            </TabPanel>
          </TabPanels>
        </Tabs>

        {/* Create/Edit Workflow Modal */}
        <Modal isOpen={isOpen} onClose={onClose} size="xl">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>
              {currentWorkflow?.id ? 'Edit Workflow' : 'Create Workflow'}
            </ModalHeader>
            <ModalBody>
              {currentWorkflow && (
                <VStack spacing={6} align="stretch">
                  <FormControl>
                    <FormLabel>Workflow Name</FormLabel>
                    <Input
                      value={currentWorkflow.name}
                      onChange={(e) => setCurrentWorkflow({
                        ...currentWorkflow,
                        name: e.target.value,
                      })}
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>Description</FormLabel>
                    <Textarea
                      value={currentWorkflow.description || ''}
                      onChange={(e) => setCurrentWorkflow({
                        ...currentWorkflow,
                        description: e.target.value,
                      })}
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>Trigger Type</FormLabel>
                    <Select
                      value={currentWorkflow.trigger_type}
                      onChange={(e) => setCurrentWorkflow({
                        ...currentWorkflow,
                        trigger_type: e.target.value,
                      })}
                    >
                      <option value="manual">Manual</option>
                      <option value="lead_created">Lead Created</option>
                      <option value="schedule">Scheduled</option>
                    </Select>
                  </FormControl>

                  <Box>
                    <HStack justify="space-between" mb={4}>
                      <Text fontWeight="medium">Workflow Steps</Text>
                      <Button size="sm" leftIcon={<FiPlus />} onClick={handleAddStep}>
                        Add Step
                      </Button>
                    </HStack>

                    <VStack spacing={3} align="stretch">
                      {currentWorkflow.steps.map((step, index) => (
                        <Box
                          key={index}
                          p={4}
                          border="1px"
                          borderColor={borderColor}
                          borderRadius="md"
                        >
                          <VStack spacing={3} align="stretch">
                            <HStack justify="space-between">
                              <Text fontWeight="medium">Step {index + 1}</Text>
                              <IconButton
                                size="sm"
                                variant="ghost"
                                colorScheme="red"
                                icon={<FiTrash2 />}
                                onClick={() => handleRemoveStep(index)}
                                aria-label="Remove step"
                              />
                            </HStack>

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
                              </Select>
                            </FormControl>

                            {step.step_type === 'message' && (
                              <FormControl>
                                <FormLabel>Message Content</FormLabel>
                                <Textarea
                                  value={step.content || ''}
                                  onChange={(e) => handleUpdateStep(index, 'content', e.target.value)}
                                  placeholder="Enter your message..."
                                />
                              </FormControl>
                            )}

                            {step.step_type === 'delay' && (
                              <FormControl>
                                <FormLabel>Delay (minutes)</FormLabel>
                                <NumberInput
                                  value={step.delay_minutes || 0}
                                  onChange={(value) => handleUpdateStep(index, 'delay_minutes', parseInt(value))}
                                  min={0}
                                >
                                  <NumberInputField />
                                  <NumberInputStepper>
                                    <NumberIncrementStepper />
                                    <NumberDecrementStepper />
                                  </NumberInputStepper>
                                </NumberInput>
                              </FormControl>
                            )}
                          </VStack>
                        </Box>
                      ))}
                    </VStack>
                  </Box>
                </VStack>
              )}
            </ModalBody>

            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onClose}>
                Cancel
              </Button>
              <Button
                onClick={handleSaveWorkflow}
                isLoading={loading}
                colorScheme="blue"
              >
                {currentWorkflow?.id ? 'Update' : 'Create'} Workflow
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Box>
  );
};

export default WhatsAppWorkflow; 