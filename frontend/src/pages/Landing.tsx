
import React from 'react';
import {
  Box,
  Button,
  Container,
  Heading,
  Text,
  VStack,
  HStack,
  SimpleGrid,
  Icon,
  Flex,
  Badge,
  useToast,
  Avatar,
  AvatarGroup,
  BoxProps,
} from '@chakra-ui/react';
import { motion, useScroll, useTransform } from 'framer-motion';
import {
  FiSearch,
  FiZap,
  FiArrowRight,
  FiPlay,
  FiStar,
  FiMessageSquare,
  FiBarChart2,
  FiTarget,
  FiAward,
  FiShield,
  FiGlobe,
} from 'react-icons/fi';

const MotionBox = motion(Box);

const GlassCard = (props: BoxProps & { children: React.ReactNode }) => (
  <Box
    bg="rgba(255, 255, 255, 0.03)"
    backdropFilter="blur(20px)"
    border="1px solid rgba(255, 255, 255, 0.08)"
    borderRadius="30px"
    p={8}
    transition="all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)"
    _hover={{
      transform: 'translateY(-10px)',
      bg: 'rgba(255, 255, 255, 0.05)',
      borderColor: 'rgba(255, 255, 255, 0.2)',
      boxShadow: '0 20px 40px rgba(0,0,0,0.4)',
    }}
    {...props}
  >
    {props.children}
  </Box>
);

const Landing: React.FC = () => {
  const toast = useToast();
  const { scrollYProgress } = useScroll();
  const y1 = useTransform(scrollYProgress, [0, 1], [0, -200]);

  const handleGetStarted = () => (window.location.href = '/register');
  const handleLogin = () => (window.location.href = '/login');

  return (
    <Box position="relative" overflow="hidden">
      {/* Dynamic Background */}
      <Box
        position="absolute" top="-10%" left="-10%" w="50%" h="50%"
        bg="radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%)"
        zIndex={0}
      />
      <Box
        position="absolute" bottom="-10%" right="-10%" w="50%" h="50%"
        bg="radial-gradient(circle, rgba(236, 72, 153, 0.1) 0%, transparent 70%)"
        zIndex={0}
      />

      {/* Navigation */}
      <Container maxW="7xl" py={6} position="relative" zIndex={10}>
        <Flex justify="space-between" align="center">
          <HStack spacing={2}>
            <Box bg="vibrant.gradient" p={2} borderRadius="12px" boxShadow="0 0 15px rgba(139, 92, 246, 0.5)">
              <Icon as={FiZap} color="white" boxSize={6} />
            </Box>
            <Heading size="md" letterSpacing="-1px" fontWeight="900" bgGradient="linear(to-r, white, gray.400)" bgClip="text">
              LEADTAP.
            </Heading>
          </HStack>
          <HStack spacing={8}>
            <Button variant="ghost" color="gray.400" _hover={{ color: 'white' }} onClick={handleLogin}>Log In</Button>
            <Button variant="glow" px={8} onClick={handleGetStarted}>Get Started</Button>
          </HStack>
        </Flex>
      </Container>

      {/* Hero Section */}
      <Container maxW="7xl" pt={24} pb={20} position="relative" zIndex={1}>
        <VStack spacing={8} align="center">
          <MotionBox
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
          >
            <Badge
              variant="outline" color="vibrant.purple" borderColor="vibrant.purple"
              px={4} py={1} borderRadius="full" textTransform="none" letterSpacing="1px"
              boxShadow="0 0 10px rgba(139, 92, 246, 0.2)"
            >
              GENERATE LEADS AT 10X SPEED
            </Badge>
          </MotionBox>

          <Heading
            size="4xl" textAlign="center" lineHeight="1.1" letterSpacing="-4px" maxW="4xl"
            bgGradient="linear(to-b, white, gray.500)" bgClip="text"
          >
            The Automated Social <br /> Discovery Engine.
          </Heading>

          <Text fontSize="xl" color="gray.400" textAlign="center" maxW="2xl" lineHeight="1.6">
            Find high-quality undergraduate leads, filter by skills, and automate WhatsApp
            campaigns using our high-priority X-Ray search engine.
          </Text>

          <HStack spacing={4} pt={4}>
            <Button variant="glow" size="lg" px={10} h="70px" fontSize="xl" onClick={handleGetStarted}>
              Start Hunting Now
            </Button>
            <Button variant="glass" size="lg" px={10} h="70px" leftIcon={<FiPlay />}>
              Live Demo
            </Button>
          </HStack>

          {/* Floating UI Elements Simulation */}
          <MotionBox style={{ y: y1 }} mt={20} w="full">
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8}>
              <GlassCard>
                <Icon as={FiTarget} color="brand.400" boxSize={10} mb={6} />
                <Heading size="md" mb={4}>X-Ray Discovery</Heading>
                <Text color="gray.500">Target undergraduates across LinkedIn, Facebook & Instagram with precision filtering.</Text>
              </GlassCard>
              <GlassCard>
                <Icon as={FiMessageSquare} color="vibrant.pink" boxSize={10} mb={6} />
                <Heading size="md" mb={4}>Bulk WhatsApp</Heading>
                <Text color="gray.500">Send personalized messages to 5000+ students with single-click automation.</Text>
              </GlassCard>
              <GlassCard>
                <Icon as={FiBarChart2} color="vibrant.yellow" boxSize={10} mb={6} />
                <Heading size="md" mb={4}>Lead Scoring</Heading>
                <Text color="gray.500">AI-driven scoring to prioritize response-ready prospects instantly.</Text>
              </GlassCard>
            </SimpleGrid>
          </MotionBox>
        </VStack>
      </Container>

      {/* Stats Section */}
      <Box py={20} bg="rgba(255,255,255,0.02)">
        <Container maxW="7xl">
          <SimpleGrid columns={{ base: 1, md: 4 }} spacing={10} textAlign="center">
            <VStack>
              <Text fontSize="4xl" fontWeight="900" color="brand.400">50K+</Text>
              <Text color="gray.500">Total Leads Found</Text>
            </VStack>
            <VStack>
              <Text fontSize="4xl" fontWeight="900" color="vibrant.purple">98%</Text>
              <Text color="gray.500">Accuracy Rate</Text>
            </VStack>
            <VStack>
              <Text fontSize="4xl" fontWeight="900" color="vibrant.pink">1s</Text>
              <Text color="gray.500">Inquiry Response</Text>
            </VStack>
            <VStack>
              <Text fontSize="4xl" fontWeight="900" color="vibrant.yellow">∞ </Text>
              <Text color="gray.500">Auto-Growth</Text>
            </VStack>
          </SimpleGrid>
        </Container>
      </Box>

      {/* Social Proof */}
      <Container maxW="7xl" py={20}>
        <VStack spacing={10}>
          <Text textTransform="uppercase" letterSpacing="4px" fontSize="xs" color="gray.600">Trusted By Innovators</Text>
          <AvatarGroup size="lg" max={5}>
            <Avatar src="https://bit.ly/dan-abramov" />
            <Avatar src="https://bit.ly/kent-c-dodds" />
            <Avatar src="https://bit.ly/ryan-florence" />
            <Avatar src="https://bit.ly/sage-adebayo" />
            <Avatar src="https://bit.ly/prosper-baba" />
          </AvatarGroup>
        </VStack>
      </Container>

      {/* Footer */}
      <Box py={10} borderTop="1px solid rgba(255,255,255,0.05)">
        <Container maxW="7xl">
          <Flex justify="space-between" align="center" direction={{ base: 'column', md: 'row' }} gap={4}>
            <Text color="gray.600" fontSize="sm">© 2026 LEADTAP. Built for Students.</Text>
            <HStack spacing={6}>
              <Text color="gray.600" fontSize="sm" cursor="pointer" _hover={{ color: 'white' }}>Privacy</Text>
              <Text color="gray.600" fontSize="sm" cursor="pointer" _hover={{ color: 'white' }}>Terms</Text>
              <Text color="gray.600" fontSize="sm" cursor="pointer" _hover={{ color: 'white' }}>Support</Text>
            </HStack>
          </Flex>
        </Container>
      </Box>
    </Box>
  );
};

export default Landing;