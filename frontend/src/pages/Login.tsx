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
  Flex,
  Badge,
  InputGroup,
  InputLeftElement,
  InputRightElement,
  IconButton,
} from '@chakra-ui/react';
import { keyframes } from '@emotion/react';
import {
  FiMail,
  FiLock,
  FiEye,
  FiEyeOff,
  FiSearch,
  FiArrowLeft,
  FiCheck,
  FiUser,
  FiShield,
  FiZap,
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

const Login: React.FC = () => {
  const { t } = useTranslation();
  const toast = useToast();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

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

  const validateForm = () => {
    const newErrors: { email?: string; password?: string } = {};

    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
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
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (email && password) {
        toast({
          title: 'Login Successful',
          description: 'Welcome back to LeadTap!',
          status: 'success',
          duration: 3000,
        });
        
        window.location.href = '/dashboard';
      } else {
        throw new Error('Invalid credentials');
      }
    } catch (error) {
      toast({
        title: 'Login Failed',
        description: 'Please check your email and password.',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = () => {
    setEmail('demo@leadtap.com');
    setPassword('demo123');
    toast({
      title: 'Demo Credentials Loaded',
      description: 'Click Login to continue with demo account',
      status: 'info',
      duration: 3000,
    });
  };

  const benefits = [
    { icon: FiSearch, text: 'Advanced Lead Search' },
    { icon: FiZap, text: 'Bulk WhatsApp Automation' },
    { icon: FiShield, text: 'Enterprise Security' },
    { icon: FiUser, text: 'Team Collaboration' },
  ];

  return (
    <Box minH="100vh" bg={useColorModeValue('gray.50', 'gray.900')} py={12}>
      <Container maxW="6xl">
        <Flex
          direction={{ base: 'column', lg: 'row' }}
          align="center"
          justify="space-between"
          gap={12}
        >
          {/* Left Side - Benefits */}
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
                    Welcome back to{' '}
                    <Text as="span" bg={gradientBg} bgClip="text" color="transparent">
                      LeadTap
                    </Text>
                  </Heading>
                  <Text color={textColor} fontSize="lg">
                    Sign in to your account to continue your lead generation journey
                  </Text>
                </VStack>

                <VStack spacing={4} align="start" w="full">
                  {benefits.map((benefit, index) => (
                    <HStack
                      key={index}
                      spacing={3}
                      p={3}
                      bg={cardBg}
                      borderRadius="lg"
                      border="1px"
                      borderColor={cardBorder}
                      w="full"
                      _hover={{ transform: 'translateX(5px)', boxShadow: 'md' }}
                      transition="all 0.3s"
                    >
                      <Icon as={benefit.icon} boxSize={5} color={useColorModeValue('blue.500', 'blue.300')} />
                      <Text color={headingColor} fontWeight="medium">
                        {benefit.text}
                      </Text>
                    </HStack>
                  ))}
                </VStack>
              </VStack>
            </VStack>
          </Box>

          {/* Right Side - Login Form */}
          <Box
            flex="1"
            maxW="450px"
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
                  <Badge colorScheme="blue" px={3} py={1} borderRadius="full" fontSize="sm">
                    Sign In
                  </Badge>
                  <Heading size="lg" color={headingColor}>
                    Access Your Account
                  </Heading>
                </VStack>

                <form onSubmit={handleSubmit} style={{ width: '100%' }}>
                  <VStack spacing={6}>
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
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
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
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          placeholder="Enter your password"
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

                    <Button
                      type="submit"
                      bg={gradientBg}
                      color="white"
                      size="lg"
                      w="full"
                      isLoading={isLoading}
                      loadingText="Signing in..."
                      _hover={{ transform: 'translateY(-2px)', boxShadow: 'xl' }}
                      transition="all 0.3s"
                      fontWeight="bold"
                      borderRadius="lg"
                    >
                      Sign In
                    </Button>

                    <Button
                      variant="outline"
                      size="lg"
                      w="full"
                      onClick={handleDemoLogin}
                      _hover={{ bg: useColorModeValue('gray.50', 'gray.700') }}
                      borderRadius="lg"
                    >
                      Try Demo Account
                    </Button>
                  </VStack>
                </form>
              </VStack>
            </Box>

            {/* Additional Options */}
            <VStack spacing={4} w="full" mt={6}>
              <HStack justify="space-between" w="full">
                <Link href="/forgot-password" color="blue.500" fontSize="sm" _hover={{ textDecoration: 'underline' }}>
                  Forgot password?
                </Link>
                <Link href="/register" color="blue.500" fontSize="sm" _hover={{ textDecoration: 'underline' }}>
                  Create account
                </Link>
              </HStack>

              <Divider />

              <Box
                bg={useColorModeValue('blue.50', 'blue.900')}
                p={4}
                borderRadius="lg"
                border="1px"
                borderColor={useColorModeValue('blue.200', 'blue.700')}
                w="full"
              >
                <VStack spacing={2} align="start">
                  <Text fontSize="sm" fontWeight="bold" color="blue.600">
                    🎉 New to LeadTap?
                  </Text>
                  <Text fontSize="sm" color="blue.600">
                    Start your free trial today and discover how easy lead generation can be!
                  </Text>
                </VStack>
              </Box>

              <Text fontSize="sm" color={textColor} textAlign="center">
                Don't have an account?{' '}
                <Link href="/register" color="blue.500" fontWeight="medium" _hover={{ textDecoration: 'underline' }}>
                  Sign up for free
                </Link>
              </Text>
            </VStack>
          </Box>
        </Flex>
      </Container>
    </Box>
  );
};

export default Login; 