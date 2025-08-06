import React, { useState } from 'react';
import {
  Box,
  Button,
  Container,
  Heading,
  Text,
  VStack,
  HStack,
  Input,
  FormControl,
  FormLabel,
  FormErrorMessage,
  useColorModeValue,
  Link,
  Divider,
  Icon,
  useToast,
  Checkbox,
  Flex,
  Badge,
  InputGroup,
  InputLeftElement,
  InputRightElement,
  IconButton,
  SimpleGrid,
} from '@chakra-ui/react';
import { keyframes } from '@emotion/react';
import {
  FiMail,
  FiLock,
  FiEye,
  FiEyeOff,
  FiUser,
  FiSearch,
  FiArrowLeft,
  FiCheck,
  FiShield,
  FiZap,
  FiTarget,
  FiTrendingUp,
  FiAward,
  FiGlobe,
} from 'react-icons/fi';
import { useTranslation } from 'react-i18next';

// Animations
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;

const slideIn = keyframes`
  from { transform: translateX(-100px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
`;

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
`;

const Register: React.FC = () => {
  const { t } = useTranslation();
  const toast = useToast();
  
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    company: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const bgColor = useColorModeValue('white', 'gray.800');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const headingColor = useColorModeValue('gray.800', 'white');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const gradientBg = useColorModeValue(
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #4c1d95 0%, #7c3aed 100%)'
  );
  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.700');

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    }

    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last name is required';
    }

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = 'Password must contain uppercase, lowercase, and number';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (!acceptTerms) {
      newErrors.terms = 'Please accept the terms and conditions';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      toast({
        title: 'Account Created Successfully!',
        description: 'Welcome to LeadTap! Redirecting to dashboard...',
        status: 'success',
        duration: 3000,
      });
      
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 2000);
      
    } catch (error) {
      toast({
        title: 'Registration Failed',
        description: 'Please try again or contact support.',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const features = [
    { icon: FiSearch, text: 'Advanced Lead Search', color: 'blue.500' },
    { icon: FiZap, text: 'Bulk WhatsApp Automation', color: 'green.500' },
    { icon: FiTarget, text: 'Lead Scoring & Analytics', color: 'purple.500' },
    { icon: FiShield, text: 'Enterprise Security', color: 'orange.500' },
    { icon: FiTrendingUp, text: 'Performance Tracking', color: 'teal.500' },
    { icon: FiGlobe, text: 'Easy Integrations', color: 'pink.500' },
  ];

  const benefits = [
    '14-day free trial',
    'No credit card required',
    'Full access to all features',
    '24/7 customer support',
    'Cancel anytime',
    'GDPR compliant',
  ];

  return (
    <Box minH="100vh" bg={useColorModeValue('gray.50', 'gray.900')} py={12}>
      <Container maxW="7xl">
        <Flex
          direction={{ base: 'column', lg: 'row' }}
          align="center"
          justify="space-between"
          gap={12}
        >
          {/* Left Side - Features & Benefits */}
          <Box
            flex="1"
            maxW="500px"
            animation={`${slideIn} 1s ease-out`}
          >
            <VStack spacing={8} align="start">
              <Link href="/" _hover={{ textDecoration: 'none' }}>
                <HStack spacing={2} color={useColorModeValue('gray.600', 'gray.300')}>
                  <Icon as={FiArrowLeft} boxSize={4} />
                  <Text fontSize="sm">Back to Home</Text>
                </HStack>
              </Link>
              
              <VStack spacing={6} align="start">
                <Box
                  p={3}
                  borderRadius="xl"
                  bg={gradientBg}
                  boxShadow="lg"
                >
                  <Icon as={FiSearch} boxSize={8} color="white" />
                </Box>
                
                <VStack spacing={4} align="start">
                  <Heading size="xl" color={headingColor} lineHeight="1.2">
                    Join{' '}
                    <Text as="span" bg={gradientBg} bgClip="text" color="transparent">
                      LeadTap
                    </Text>{' '}
                    Today
                  </Heading>
                  <Text color={textColor} fontSize="lg">
                    Start your free trial and transform your lead generation process
                  </Text>
                </VStack>

                <VStack spacing={4} align="start" w="full">
                  <Text fontWeight="bold" color={headingColor} fontSize="lg">
                    What you'll get:
                  </Text>
                  <SimpleGrid columns={2} spacing={3} w="full">
                    {features.map((feature, index) => (
                      <HStack
                        key={index}
                        spacing={3}
                        p={3}
                        bg={cardBg}
                        borderRadius="lg"
                        border="1px"
                        borderColor={cardBorder}
                        _hover={{ transform: 'translateX(5px)', boxShadow: 'md' }}
                        transition="all 0.3s"
                      >
                        <Icon as={feature.icon} boxSize={5} color={feature.color} />
                        <Text color={headingColor} fontSize="sm" fontWeight="medium">
                          {feature.text}
                        </Text>
                      </HStack>
                    ))}
                  </SimpleGrid>
                </VStack>

                <Box
                  bg={useColorModeValue('green.50', 'green.900')}
                  p={4}
                  borderRadius="lg"
                  border="1px"
                  borderColor={useColorModeValue('green.200', 'green.700')}
                  w="full"
                >
                  <VStack spacing={2} align="start">
                    <Text fontSize="sm" fontWeight="bold" color="green.600">
                      🎉 Free Trial Benefits:
                    </Text>
                    <SimpleGrid columns={2} spacing={1} w="full">
                      {benefits.map((benefit, index) => (
                        <HStack key={index} spacing={2}>
                          <Icon as={FiCheck} boxSize={3} color="green.500" />
                          <Text fontSize="xs" color="green.600">
                            {benefit}
                          </Text>
                        </HStack>
                      ))}
                    </SimpleGrid>
                  </VStack>
                </Box>
              </VStack>
            </VStack>
          </Box>

          {/* Right Side - Registration Form */}
          <Box
            flex="1"
            maxW="500px"
            w="full"
            animation={`${fadeIn} 1s ease-out 0.5s both`}
          >
            <Box
              bg={cardBg}
              p={8}
              border="1px"
              borderColor={cardBorder}
              borderRadius="2xl"
              boxShadow="xl"
              position="relative"
              overflow="hidden"
            >
              {/* Gradient Border */}
              <Box
                position="absolute"
                top={0}
                left={0}
                right={0}
                h="4px"
                bg={gradientBg}
              />

              <VStack spacing={6}>
                <VStack spacing={2} textAlign="center">
                  <Badge colorScheme="green" px={3} py={1} borderRadius="full" fontSize="sm">
                    Get Started
                  </Badge>
                  <Heading size="lg" color={headingColor}>
                    Create Your Account
                  </Heading>
                </VStack>

                <form onSubmit={handleSubmit} style={{ width: '100%' }}>
                  <VStack spacing={6}>
                    {/* Name Fields */}
                    <HStack spacing={4} w="full">
                      <FormControl isInvalid={!!errors.firstName}>
                        <FormLabel color={headingColor} fontWeight="medium">
                          First Name
                        </FormLabel>
                        <InputGroup>
                          <InputLeftElement>
                            <Icon as={FiUser} color={textColor} />
                          </InputLeftElement>
                          <Input
                            type="text"
                            value={formData.firstName}
                            onChange={(e) => handleInputChange('firstName', e.target.value)}
                            placeholder="First name"
                            size="lg"
                            borderRadius="lg"
                            _focus={{
                              borderColor: useColorModeValue('blue.500', 'blue.300'),
                              boxShadow: '0 0 0 1px var(--chakra-colors-blue-500)',
                            }}
                          />
                        </InputGroup>
                        <FormErrorMessage>{errors.firstName}</FormErrorMessage>
                      </FormControl>

                      <FormControl isInvalid={!!errors.lastName}>
                        <FormLabel color={headingColor} fontWeight="medium">
                          Last Name
                        </FormLabel>
                        <InputGroup>
                          <InputLeftElement>
                            <Icon as={FiUser} color={textColor} />
                          </InputLeftElement>
                          <Input
                            type="text"
                            value={formData.lastName}
                            onChange={(e) => handleInputChange('lastName', e.target.value)}
                            placeholder="Last name"
                            size="lg"
                            borderRadius="lg"
                            _focus={{
                              borderColor: useColorModeValue('blue.500', 'blue.300'),
                              boxShadow: '0 0 0 1px var(--chakra-colors-blue-500)',
                            }}
                          />
                        </InputGroup>
                        <FormErrorMessage>{errors.lastName}</FormErrorMessage>
                      </FormControl>
                    </HStack>

                    {/* Email */}
                    <FormControl isInvalid={!!errors.email}>
                      <FormLabel color={headingColor} fontWeight="medium">
                        Email Address
                      </FormLabel>
                      <InputGroup>
                        <InputLeftElement>
                          <Icon as={FiMail} color={textColor} />
                        </InputLeftElement>
                        <Input
                          type="email"
                          value={formData.email}
                          onChange={(e) => handleInputChange('email', e.target.value)}
                          placeholder="Enter your email"
                          size="lg"
                          borderRadius="lg"
                          _focus={{
                            borderColor: useColorModeValue('blue.500', 'blue.300'),
                            boxShadow: '0 0 0 1px var(--chakra-colors-blue-500)',
                          }}
                        />
                      </InputGroup>
                      <FormErrorMessage>{errors.email}</FormErrorMessage>
                    </FormControl>

                    {/* Company */}
                    <FormControl>
                      <FormLabel color={headingColor} fontWeight="medium">
                        Company (Optional)
                      </FormLabel>
                      <Input
                        type="text"
                        value={formData.company}
                        onChange={(e) => handleInputChange('company', e.target.value)}
                        placeholder="Your company name"
                        size="lg"
                        borderRadius="lg"
                        _focus={{
                          borderColor: useColorModeValue('blue.500', 'blue.300'),
                          boxShadow: '0 0 0 1px var(--chakra-colors-blue-500)',
                        }}
                      />
                    </FormControl>

                    {/* Password */}
                    <FormControl isInvalid={!!errors.password}>
                      <FormLabel color={headingColor} fontWeight="medium">
                        Password
                      </FormLabel>
                      <InputGroup>
                        <InputLeftElement>
                          <Icon as={FiLock} color={textColor} />
                        </InputLeftElement>
                        <Input
                          type={showPassword ? 'text' : 'password'}
                          value={formData.password}
                          onChange={(e) => handleInputChange('password', e.target.value)}
                          placeholder="Create a strong password"
                          size="lg"
                          borderRadius="lg"
                          _focus={{
                            borderColor: useColorModeValue('blue.500', 'blue.300'),
                            boxShadow: '0 0 0 1px var(--chakra-colors-blue-500)',
                          }}
                        />
                        <InputRightElement>
                          <IconButton
                            aria-label={showPassword ? 'Hide password' : 'Show password'}
                            icon={<Icon as={showPassword ? FiEyeOff : FiEye} />}
                            variant="ghost"
                            size="sm"
                            onClick={() => setShowPassword(!showPassword)}
                          />
                        </InputRightElement>
                      </InputGroup>
                      <FormErrorMessage>{errors.password}</FormErrorMessage>
                    </FormControl>

                    {/* Confirm Password */}
                    <FormControl isInvalid={!!errors.confirmPassword}>
                      <FormLabel color={headingColor} fontWeight="medium">
                        Confirm Password
                      </FormLabel>
                      <InputGroup>
                        <InputLeftElement>
                          <Icon as={FiLock} color={textColor} />
                        </InputLeftElement>
                        <Input
                          type={showConfirmPassword ? 'text' : 'password'}
                          value={formData.confirmPassword}
                          onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                          placeholder="Confirm your password"
                          size="lg"
                          borderRadius="lg"
                          _focus={{
                            borderColor: useColorModeValue('blue.500', 'blue.300'),
                            boxShadow: '0 0 0 1px var(--chakra-colors-blue-500)',
                          }}
                        />
                        <InputRightElement>
                          <IconButton
                            aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                            icon={<Icon as={showConfirmPassword ? FiEyeOff : FiEye} />}
                            variant="ghost"
                            size="sm"
                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                          />
                        </InputRightElement>
                      </InputGroup>
                      <FormErrorMessage>{errors.confirmPassword}</FormErrorMessage>
                    </FormControl>

                    {/* Terms and Conditions */}
                    <FormControl isInvalid={!!errors.terms}>
                      <Checkbox
                        isChecked={acceptTerms}
                        onChange={(e) => setAcceptTerms(e.target.checked)}
                        colorScheme="blue"
                        size="lg"
                      >
                        <Text fontSize="sm" color={textColor}>
                          I agree to the{' '}
                          <Link href="/terms" color="blue.500" _hover={{ textDecoration: 'underline' }}>
                            Terms of Service
                          </Link>{' '}
                          and{' '}
                          <Link href="/privacy" color="blue.500" _hover={{ textDecoration: 'underline' }}>
                            Privacy Policy
                          </Link>
                        </Text>
                      </Checkbox>
                      <FormErrorMessage>{errors.terms}</FormErrorMessage>
                    </FormControl>

                    <Button
                      type="submit"
                      bg={gradientBg}
                      color="white"
                      size="lg"
                      w="full"
                      isLoading={isLoading}
                      loadingText="Creating account..."
                      leftIcon={<FiCheck />}
                      _hover={{ transform: 'translateY(-2px)', boxShadow: 'xl' }}
                      transition="all 0.3s"
                      fontWeight="bold"
                      borderRadius="lg"
                    >
                      Create Account
                    </Button>
                  </VStack>
                </form>
              </VStack>
            </Box>

            {/* Additional Options */}
            <VStack spacing={4} w="full" mt={6}>
              <Divider />

              <Text fontSize="sm" color={textColor} textAlign="center">
                Already have an account?{' '}
                <Link href="/login" color="blue.500" fontWeight="medium" _hover={{ textDecoration: 'underline' }}>
                  Sign in here
                </Link>
              </Text>
            </VStack>
          </Box>
        </Flex>
      </Container>
    </Box>
  );
};

export default Register; 