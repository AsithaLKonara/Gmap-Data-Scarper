import React from 'react';
import {
  Box,
  Button,
  Container,
  Heading,
  Text,
  VStack,
  HStack,
  Image,
  SimpleGrid,
  Icon,
  useColorModeValue,
  Flex,
  Badge,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  useToast,
  IconButton,
  Divider,
  Avatar,
  AvatarGroup,
} from '@chakra-ui/react';
import { keyframes } from '@emotion/react';
import {
  FiSearch,
  FiUsers,
  FiTrendingUp,
  FiShield,
  FiZap,
  FiCheckCircle,
  FiArrowRight,
  FiPlay,
  FiStar,
  FiMessageSquare,
  FiBarChart2,
  FiGlobe,
  FiSmartphone,
  FiTarget,
  FiAward,
  FiHeart,
} from 'react-icons/fi';
import { useTranslation } from 'react-i18next';

// Animations
const float = keyframes`
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
`;

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
`;

const slideIn = keyframes`
  from { transform: translateX(-100px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
`;

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;

const Landing: React.FC = () => {
  const { t } = useTranslation();
  const toast = useToast();
  
  const bgColor = useColorModeValue('white', 'gray.900');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const headingColor = useColorModeValue('gray.800', 'white');
  const accentColor = useColorModeValue('blue.500', 'blue.300');
  const gradientBg = useColorModeValue(
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #4c1d95 0%, #7c3aed 100%)'
  );
  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.700');

  const handleGetStarted = () => {
    window.location.href = '/register';
  };

  const handleLogin = () => {
    window.location.href = '/login';
  };

  const handleDemo = () => {
    toast({
      title: 'Demo Mode',
      description: 'Starting demo mode...',
      status: 'info',
      duration: 3000,
    });
    window.location.href = '/dashboard?demo=true';
  };

  const features = [
    {
      icon: FiSearch,
      title: 'Advanced Lead Search',
      description: 'Find high-quality leads from Google Maps with AI-powered filtering and search capabilities.',
      color: 'blue.500',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    {
      icon: FiMessageSquare,
      title: 'Bulk WhatsApp Sender',
      description: 'Send personalized WhatsApp messages to thousands of contacts with intelligent automation.',
      color: 'green.500',
      gradient: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'
    },
    {
      icon: FiBarChart2,
      title: 'Analytics & Insights',
      description: 'Track your lead generation performance with detailed analytics and predictive insights.',
      color: 'purple.500',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    {
      icon: FiShield,
      title: 'Secure & Compliant',
      description: 'Enterprise-grade security with GDPR compliance and advanced data protection.',
      color: 'orange.500',
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
    },
    {
      icon: FiZap,
      title: 'Automated Workflows',
      description: 'Create intelligent lead nurturing sequences and automated follow-up campaigns.',
      color: 'teal.500',
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
    },
    {
      icon: FiGlobe,
      title: 'Easy Integration',
      description: 'Integrate seamlessly with your existing CRM and marketing tools via API.',
      color: 'pink.500',
      gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
    }
  ];

  const stats = [
    { label: 'Active Users', value: '10,000+', help: 'Trusted by businesses worldwide', icon: FiUsers },
    { label: 'Leads Generated', value: '2M+', help: 'High-quality leads discovered', icon: FiTarget },
    { label: 'Success Rate', value: '95%', help: 'Customer satisfaction rate', icon: FiAward },
    { label: 'Response Time', value: '<2s', help: 'Average system response time', icon: FiZap }
  ];

  const testimonials = [
    {
      name: 'Sarah Johnson',
      company: 'TechStart Inc.',
      role: 'CEO',
      rating: 5,
      text: 'LeadTap transformed our lead generation process. We increased our qualified leads by 300% in just 3 months!',
      avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face'
    },
    {
      name: 'Mike Chen',
      company: 'Growth Marketing Co.',
      role: 'Marketing Director',
      rating: 5,
      text: 'The bulk WhatsApp feature is a game-changer. We can now reach thousands of prospects with personalized messages.',
      avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face'
    },
    {
      name: 'Emily Rodriguez',
      company: 'Digital Solutions',
      role: 'Founder',
      rating: 5,
      text: 'The analytics dashboard gives us insights we never had before. Highly recommended for any business!',
      avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face'
    }
  ];

  return (
    <Box bg={bgColor} minH="100vh" overflow="hidden">
      {/* Navigation */}
      <Box
        as="nav"
        bg={`${bgColor}dd`}
        backdropFilter="blur(10px)"
        borderBottom="1px"
        borderColor={useColorModeValue('gray.200', 'gray.700')}
        position="sticky"
        top={0}
        zIndex={10}
      >
        <Container maxW="7xl" py={4}>
          <Flex justify="space-between" align="center">
            <HStack spacing={3}>
              <Box
                p={2}
                borderRadius="lg"
                bg={gradientBg}
                boxShadow="lg"
              >
                <Icon as={FiSearch} boxSize={6} color="white" />
              </Box>
              <Heading size="lg" color={headingColor} fontWeight="bold">
                LeadTap
              </Heading>
            </HStack>
            <HStack spacing={4}>
              <Button variant="ghost" onClick={handleLogin} _hover={{ bg: 'gray.100' }}>
                Login
              </Button>
              <Button
                bg={gradientBg}
                color="white"
                _hover={{ transform: 'translateY(-2px)', boxShadow: 'xl' }}
                transition="all 0.3s"
                onClick={handleGetStarted}
              >
                Get Started
              </Button>
            </HStack>
          </Flex>
        </Container>
      </Box>

      {/* Hero Section */}
      <Box
        py={20}
        bg={gradientBg}
        position="relative"
        overflow="hidden"
      >
        {/* Background Elements */}
        <Box
          position="absolute"
          top="10%"
          left="10%"
          w="200px"
          h="200px"
          borderRadius="full"
          bg="white"
          opacity="0.1"
          animation={`${float} 6s ease-in-out infinite`}
        />
        <Box
          position="absolute"
          bottom="20%"
          right="15%"
          w="150px"
          h="150px"
          borderRadius="full"
          bg="white"
          opacity="0.1"
          animation={`${float} 8s ease-in-out infinite reverse`}
        />
        
        <Container maxW="7xl" position="relative" zIndex={1}>
          <VStack spacing={8} textAlign="center">
            <Badge
              colorScheme="whiteAlpha"
              px={4}
              py={2}
              borderRadius="full"
              fontSize="sm"
              fontWeight="medium"
              animation={`${pulse} 2s ease-in-out infinite`}
            >
              🚀 Now with Bulk WhatsApp Sender
            </Badge>
            
            <Heading
              size="2xl"
              color="white"
              maxW="4xl"
              lineHeight="1.2"
              animation={`${slideIn} 1s ease-out`}
            >
              Transform Your Lead Generation with{' '}
              <Text as="span" bg="white" bgClip="text" color="transparent">
                AI-Powered Search
              </Text>{' '}
              and Bulk WhatsApp Automation
            </Heading>
            
            <Text
              fontSize="xl"
              color="whiteAlpha.900"
              maxW="2xl"
              animation={`${fadeIn} 1s ease-out 0.5s both`}
            >
              Discover high-quality leads from Google Maps, send personalized WhatsApp messages at scale, 
              and track your success with advanced analytics - all in one powerful platform.
            </Text>
            
            <HStack spacing={6} pt={6} animation={`${fadeIn} 1s ease-out 1s both`}>
              <Button
                size="lg"
                bg="white"
                color="blue.600"
                _hover={{ transform: 'translateY(-3px)', boxShadow: '2xl' }}
                transition="all 0.3s"
                leftIcon={<FiArrowRight />}
                onClick={handleGetStarted}
                fontWeight="bold"
              >
                Start Free Trial
              </Button>
              <Button
                size="lg"
                variant="outline"
                color="white"
                borderColor="whiteAlpha.300"
                _hover={{ bg: 'whiteAlpha.200', transform: 'translateY(-3px)' }}
                transition="all 0.3s"
                leftIcon={<FiPlay />}
                onClick={handleDemo}
              >
                Watch Demo
              </Button>
            </HStack>

            {/* Social Proof */}
            <HStack spacing={8} pt={8} animation={`${fadeIn} 1s ease-out 1.5s both`}>
              <VStack spacing={1}>
                <Text color="whiteAlpha.800" fontSize="sm">Trusted by</Text>
                <AvatarGroup size="sm" max={4}>
                  <Avatar src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=40&h=40&fit=crop&crop=face" />
                  <Avatar src="https://images.unsplash.com/photo-1494790108755-2616b612b786?w=40&h=40&fit=crop&crop=face" />
                  <Avatar src="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=40&h=40&fit=crop&crop=face" />
                  <Avatar src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=40&h=40&fit=crop&crop=face" />
                </AvatarGroup>
              </VStack>
              <VStack spacing={1}>
                <Text color="whiteAlpha.800" fontSize="sm">Rated</Text>
                <HStack spacing={1}>
                  {[...Array(5)].map((_, i) => (
                    <Icon key={i} as={FiStar} color="yellow.300" boxSize={4} />
                  ))}
                </HStack>
              </VStack>
            </HStack>
          </VStack>
        </Container>
      </Box>

      {/* Stats Section */}
      <Box py={20} bg={bgColor}>
        <Container maxW="7xl">
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={8}>
            {stats.map((stat, index) => (
              <Box
                key={index}
                textAlign="center"
                p={6}
                borderRadius="xl"
                bg={cardBg}
                border="1px"
                borderColor={cardBorder}
                _hover={{ transform: 'translateY(-5px)', boxShadow: 'xl' }}
                transition="all 0.3s"
                animation={`${fadeIn} 1s ease-out ${index * 0.1}s both`}
              >
                <Icon as={stat.icon} boxSize={8} color={accentColor} mb={3} />
                <StatNumber fontSize="3xl" color={headingColor} fontWeight="bold">
                  {stat.value}
                </StatNumber>
                <StatLabel fontSize="lg" color={headingColor} fontWeight="medium">
                  {stat.label}
                </StatLabel>
                <StatHelpText color={textColor}>
                  {stat.help}
                </StatHelpText>
              </Box>
            ))}
          </SimpleGrid>
        </Container>
      </Box>

      {/* Features Section */}
      <Box py={20} bg={useColorModeValue('gray.50', 'gray.900')}>
        <Container maxW="7xl">
          <VStack spacing={12}>
            <VStack spacing={4} textAlign="center">
              <Badge colorScheme="blue" px={4} py={2} borderRadius="full" fontSize="sm">
                Features
              </Badge>
              <Heading size="xl" color={headingColor}>
                Everything You Need to Scale Your Business
              </Heading>
              <Text fontSize="lg" color={textColor} maxW="2xl">
                From lead discovery to customer conversion, LeadTap provides all the tools 
                you need to grow your business efficiently.
              </Text>
            </VStack>
            
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={8}>
              {features.map((feature, index) => (
                <Box
                  key={index}
                  p={8}
                  bg={cardBg}
                  border="1px"
                  borderColor={cardBorder}
                  borderRadius="xl"
                  _hover={{
                    transform: 'translateY(-8px)',
                    boxShadow: '2xl',
                    transition: 'all 0.3s'
                  }}
                  position="relative"
                  overflow="hidden"
                  animation={`${fadeIn} 1s ease-out ${index * 0.1}s both`}
                >
                  {/* Gradient Background */}
                  <Box
                    position="absolute"
                    top={0}
                    left={0}
                    right={0}
                    h="4px"
                    bg={feature.gradient}
                  />
                  
                  <VStack spacing={6} align="start">
                    <Box
                      p={3}
                      borderRadius="xl"
                      bg={feature.gradient}
                      boxShadow="lg"
                    >
                      <Icon as={feature.icon} boxSize={6} color="white" />
                    </Box>
                    <Heading size="md" color={headingColor}>
                      {feature.title}
                    </Heading>
                    <Text color={textColor} lineHeight="1.6">
                      {feature.description}
                    </Text>
                  </VStack>
                </Box>
              ))}
            </SimpleGrid>
          </VStack>
        </Container>
      </Box>

      {/* Testimonials Section */}
      <Box py={20} bg={bgColor}>
        <Container maxW="7xl">
          <VStack spacing={12}>
            <VStack spacing={4} textAlign="center">
              <Badge colorScheme="green" px={4} py={2} borderRadius="full" fontSize="sm">
                Testimonials
              </Badge>
              <Heading size="xl" color={headingColor}>
                Loved by Businesses Worldwide
              </Heading>
              <Text fontSize="lg" color={textColor} maxW="2xl">
                See what our customers have to say about their experience with LeadTap.
              </Text>
            </VStack>
            
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8}>
              {testimonials.map((testimonial, index) => (
                <Box
                  key={index}
                  p={8}
                  bg={cardBg}
                  border="1px"
                  borderColor={cardBorder}
                  borderRadius="xl"
                  _hover={{ transform: 'translateY(-5px)', boxShadow: 'xl' }}
                  transition="all 0.3s"
                  animation={`${fadeIn} 1s ease-out ${index * 0.2}s both`}
                >
                  <VStack spacing={6} align="start">
                    <HStack spacing={1}>
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Icon key={i} as={FiStar} color="yellow.400" boxSize={4} />
                      ))}
                    </HStack>
                    <Text color={textColor} fontSize="md" lineHeight="1.6" fontStyle="italic">
                      "{testimonial.text}"
                    </Text>
                    <HStack spacing={3}>
                      <Avatar src={testimonial.avatar} size="md" />
                      <VStack spacing={1} align="start">
                        <Text fontWeight="bold" color={headingColor}>
                          {testimonial.name}
                        </Text>
                        <Text fontSize="sm" color={textColor}>
                          {testimonial.role} at {testimonial.company}
                        </Text>
                      </VStack>
                    </HStack>
                  </VStack>
                </Box>
              ))}
            </SimpleGrid>
          </VStack>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box py={20} bg={gradientBg} position="relative" overflow="hidden">
        {/* Background Elements */}
        <Box
          position="absolute"
          top="20%"
          right="10%"
          w="100px"
          h="100px"
          borderRadius="full"
          bg="white"
          opacity="0.1"
          animation={`${float} 7s ease-in-out infinite`}
        />
        
        <Container maxW="7xl" position="relative" zIndex={1}>
          <VStack spacing={8} textAlign="center">
            <Heading size="xl" color="white">
              Ready to Transform Your Lead Generation?
            </Heading>
            <Text fontSize="lg" color="whiteAlpha.900" maxW="2xl">
              Join thousands of businesses that are already using LeadTap to scale their operations 
              and grow their customer base.
            </Text>
            <HStack spacing={6}>
              <Button
                size="lg"
                bg="white"
                color="blue.600"
                _hover={{ transform: 'translateY(-3px)', boxShadow: '2xl' }}
                transition="all 0.3s"
                fontWeight="bold"
                onClick={handleGetStarted}
              >
                Start Free Trial
              </Button>
              <Button
                size="lg"
                variant="outline"
                color="white"
                borderColor="whiteAlpha.300"
                _hover={{ bg: 'whiteAlpha.200', transform: 'translateY(-3px)' }}
                transition="all 0.3s"
                onClick={handleDemo}
              >
                Schedule Demo
              </Button>
            </HStack>
          </VStack>
        </Container>
      </Box>

      {/* Footer */}
      <Box py={12} bg={useColorModeValue('gray.900', 'black')} color="white">
        <Container maxW="7xl">
          <Flex
            direction={{ base: 'column', md: 'row' }}
            justify="space-between"
            align="center"
          >
            <HStack spacing={3}>
              <Box
                p={2}
                borderRadius="lg"
                bg={gradientBg}
                boxShadow="lg"
              >
                <Icon as={FiSearch} boxSize={5} color="white" />
              </Box>
              <Text fontSize="lg" fontWeight="bold">LeadTap</Text>
            </HStack>
            <Text fontSize="sm" color="gray.400">
              © 2024 LeadTap. All rights reserved.
            </Text>
          </Flex>
        </Container>
      </Box>
    </Box>
  );
};

export default Landing; 