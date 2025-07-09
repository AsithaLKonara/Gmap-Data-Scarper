import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Progress,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
  Badge,
  Icon,
  Tooltip,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useToast,
  Flex,
  Spacer,
  Divider,
  List,
  ListItem,
  ListIcon,
} from '@chakra-ui/react';
import { CheckCircleIcon, InfoIcon, StarIcon, ArrowForwardIcon } from '@chakra-ui/icons';
import { useAuth } from '../hooks/useAuth';
import * as api from '../api';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  required: boolean;
  demo?: boolean;
  action?: () => void;
}

interface OnboardingProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

const EnhancedOnboarding: React.FC<OnboardingProps> = ({ isOpen, onClose, onComplete }) => {
  const { user } = useAuth();
  const toast = useToast();
  const [currentStep, setCurrentStep] = useState(0);
  const [demoJobCreated, setDemoJobCreated] = useState(false);
  const [demoResults, setDemoResults] = useState<any[]>([]);
  const [feedback, setFeedback] = useState<string>('');

  const onboardingSteps: OnboardingStep[] = [
    {
      id: 'welcome',
      title: 'Welcome to LeadTap! 🚀',
      description: 'Let\'s get you set up with your first lead generation campaign in just a few minutes.',
      completed: false,
      required: true,
    },
    {
      id: 'demo-job',
      title: 'Create Your First Job',
      description: 'We\'ll create a sample job to show you how LeadTap works.',
      completed: false,
      required: true,
      demo: true,
      action: async () => {
        try {
          // Create a demo job with sample data
          const demoQueries = ['restaurants in New York', 'coffee shops in San Francisco'];
          const response = await api.createJob(demoQueries);
          
          // Simulate results for demo
          const mockResults = [
            {
              business_name: 'Joe\'s Pizza',
              address: '123 Main St, New York, NY',
              phone: '+1-555-0123',
              website: 'www.joespizza.com',
              rating: 4.5,
              reviews: 150,
              category: 'Restaurant'
            },
            {
              business_name: 'Starbucks Coffee',
              address: '456 Market St, San Francisco, CA',
              phone: '+1-555-0456',
              website: 'www.starbucks.com',
              rating: 4.2,
              reviews: 89,
              category: 'Coffee Shop'
            },
            {
              business_name: 'Blue Bottle Coffee',
              address: '789 Mission St, San Francisco, CA',
              phone: '+1-555-0789',
              website: 'www.bluebottlecoffee.com',
              rating: 4.7,
              reviews: 234,
              category: 'Coffee Shop'
            }
          ];
          
          setDemoResults(mockResults);
          setDemoJobCreated(true);
          toast({
            title: 'Demo Job Created!',
            description: 'Your sample job has been created with realistic data.',
            status: 'success',
            duration: 3000,
          });
        } catch (error) {
          toast({
            title: 'Demo Creation Failed',
            description: 'We\'ll continue with the tour anyway.',
            status: 'warning',
            duration: 3000,
          });
        }
      }
    },
    {
      id: 'view-results',
      title: 'View Your Results',
      description: 'See how LeadTap extracts detailed business information automatically.',
      completed: false,
      required: true,
      demo: true,
    },
    {
      id: 'export-data',
      title: 'Export Your Data',
      description: 'Download your leads in multiple formats for your CRM or marketing tools.',
      completed: false,
      required: true,
      demo: true,
      action: () => {
        // Simulate export
        toast({
          title: 'Export Successful!',
          description: 'Your data has been exported in CSV format.',
          status: 'success',
          duration: 3000,
        });
      }
    },
    {
      id: 'crm-setup',
      title: 'Setup Your CRM',
      description: 'Import your leads into your CRM or use our built-in lead management.',
      completed: false,
      required: false,
      demo: true,
    },
    {
      id: 'complete',
      title: 'You\'re Ready to Go! 🎉',
      description: 'Start creating real jobs and generating leads for your business.',
      completed: false,
      required: true,
    }
  ];

  const [steps, setSteps] = useState(onboardingSteps);

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      // Mark current step as completed
      const updatedSteps = [...steps];
      updatedSteps[currentStep].completed = true;
      setSteps(updatedSteps);
      
      // Execute step action if exists
      if (steps[currentStep].action) {
        steps[currentStep].action!();
      }
      
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    // Mark all steps as completed
    const updatedSteps = steps.map(step => ({ ...step, completed: true }));
    setSteps(updatedSteps);
    
    // Save onboarding completion
    localStorage.setItem('onboarding_complete', 'true');
    localStorage.setItem('onboarding_feedback', feedback);
    
    toast({
      title: 'Onboarding Complete!',
      description: 'Welcome to LeadTap. Start generating leads now!',
      status: 'success',
      duration: 5000,
    });
    
    onComplete();
    onClose();
  };

  const getProgressPercentage = () => {
    const completedSteps = steps.filter(step => step.completed).length;
    return (completedSteps / steps.length) * 100;
  };

  const currentStepData = steps[currentStep];

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" isCentered>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          <HStack justify="space-between" align="center">
            <Text fontSize="lg" fontWeight="bold">
              {currentStepData.title}
            </Text>
            <Badge colorScheme="blue" variant="subtle">
              Step {currentStep + 1} of {steps.length}
            </Badge>
          </HStack>
        </ModalHeader>
        
        <ModalBody>
          <VStack spacing={6} align="stretch">
            {/* Progress Bar */}
            <Box>
              <HStack justify="space-between" mb={2}>
                <Text fontSize="sm" color="gray.600">
                  Progress
                </Text>
                <Text fontSize="sm" color="gray.600">
                  {Math.round(getProgressPercentage())}%
                </Text>
              </HStack>
              <Progress value={getProgressPercentage()} colorScheme="blue" size="sm" />
            </Box>

            {/* Step Description */}
            <Text color="gray.600" fontSize="md">
              {currentStepData.description}
            </Text>

            {/* Demo Content */}
            {currentStepData.demo && (
              <Box>
                {currentStepData.id === 'demo-job' && (
                  <Alert status="info" borderRadius="md">
                    <AlertIcon />
                    <Box>
                      <AlertTitle>Demo Job Created!</AlertTitle>
                      <AlertDescription>
                        We've created a sample job with queries like "restaurants in New York" and "coffee shops in San Francisco".
                      </AlertDescription>
                    </Box>
                  </Alert>
                )}

                {currentStepData.id === 'view-results' && demoResults.length > 0 && (
                  <Box border="1px" borderColor="gray.200" borderRadius="md" p={4}>
                    <Text fontWeight="bold" mb={3}>Sample Results:</Text>
                    <VStack spacing={2} align="stretch">
                      {demoResults.slice(0, 3).map((result, index) => (
                        <Box key={index} p={3} bg="gray.50" borderRadius="md">
                          <Text fontWeight="bold">{result.business_name}</Text>
                          <Text fontSize="sm" color="gray.600">{result.address}</Text>
                          <HStack spacing={4} mt={1}>
                            <Text fontSize="xs">📞 {result.phone}</Text>
                            <Text fontSize="xs">⭐ {result.rating}</Text>
                            <Text fontSize="xs">🏷️ {result.category}</Text>
                          </HStack>
                        </Box>
                      ))}
                    </VStack>
                  </Box>
                )}

                {currentStepData.id === 'export-data' && (
                  <Alert status="success" borderRadius="md">
                    <AlertIcon />
                    <Box>
                      <AlertTitle>Export Options Available</AlertTitle>
                      <AlertDescription>
                        Download your data in CSV, JSON, Excel, or PDF formats. Perfect for importing into your CRM or marketing tools.
                      </AlertDescription>
                    </Box>
                  </Alert>
                )}

                {currentStepData.id === 'crm-setup' && (
                  <Box border="1px" borderColor="gray.200" borderRadius="md" p={4}>
                    <Text fontWeight="bold" mb={3}>CRM Integration Options:</Text>
                    <List spacing={2}>
                      <ListItem>
                        <ListIcon as={CheckCircleIcon} color="green.500" />
                        Built-in Lead Management
                      </ListItem>
                      <ListItem>
                        <ListIcon as={CheckCircleIcon} color="green.500" />
                        Export to CSV/Excel
                      </ListItem>
                      <ListItem>
                        <ListIcon as={CheckCircleIcon} color="green.500" />
                        API Integration
                      </ListItem>
                      <ListItem>
                        <ListIcon as={CheckCircleIcon} color="green.500" />
                        Webhook Support
                      </ListItem>
                    </List>
                  </Box>
                )}
              </Box>
            )}

            {/* Feature Tips */}
            {currentStepData.id === 'complete' && (
              <Box>
                <Text fontWeight="bold" mb={3}>Pro Tips:</Text>
                <VStack spacing={2} align="stretch">
                  <HStack>
                    <Icon as={StarIcon} color="yellow.500" />
                    <Text fontSize="sm">Use specific queries for better results</Text>
                  </HStack>
                  <HStack>
                    <Icon as={StarIcon} color="yellow.500" />
                    <Text fontSize="sm">Export data regularly to your CRM</Text>
                  </HStack>
                  <HStack>
                    <Icon as={StarIcon} color="yellow.500" />
                    <Text fontSize="sm">Upgrade to Pro for advanced features</Text>
                  </HStack>
                </VStack>
              </Box>
            )}

            {/* Feedback Section */}
            {currentStepData.id === 'complete' && (
              <Box>
                <Text fontWeight="bold" mb={2}>How was your onboarding experience?</Text>
                <textarea
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="Share your thoughts (optional)..."
                  style={{
                    width: '100%',
                    minHeight: '80px',
                    padding: '8px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '4px',
                    resize: 'vertical'
                  }}
                />
              </Box>
            )}
          </VStack>
        </ModalBody>

        <ModalFooter>
          <HStack spacing={3}>
            {currentStep > 0 && (
              <Button variant="ghost" onClick={handlePrevious}>
                Previous
              </Button>
            )}
            
            <Spacer />
            
            {currentStep < steps.length - 1 ? (
              <Button
                colorScheme="blue"
                onClick={handleNext}
                rightIcon={<ArrowForwardIcon />}
              >
                {currentStepData.action ? 'Try It' : 'Next'}
              </Button>
            ) : (
              <Button
                colorScheme="green"
                onClick={handleComplete}
                size="lg"
              >
                Get Started! 🚀
              </Button>
            )}
          </HStack>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default EnhancedOnboarding; 