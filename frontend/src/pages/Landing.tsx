import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  SimpleGrid,
  Icon,
  Image,
  useColorModeValue,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import {
  FiArrowRight,
  FiCheck,
  FiStar,
  FiUsers,
  FiTrendingUp,
  FiShield,
  FiZap,
  FiGlobe,
  FiAward,
  FiPlay,
  FiSearch,
} from 'react-icons/fi';

const Landing: React.FC = () => {
  const { t } = useTranslation();
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  return (
    <Box>
      {/* Hero Section */}
      <Box
        bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        color="white"
        py={20}
        position="relative"
        overflow="hidden"
      >
        <Container maxW="1200px">
          <VStack spacing={8} textAlign="center">
            <Heading
              as="h1"
              size="2xl"
              fontWeight="bold"
              maxW="800px"
            >
              {t('landing.hero.title', 'Extract Leads from Google Maps with AI-Powered Precision')}
            </Heading>
            <Text fontSize="xl" maxW="600px" opacity={0.9}>
              {t('landing.hero.subtitle', 'Automate your lead generation process with our advanced scraping technology. Get business data, contact information, and insights from Google Maps in minutes.')}
            </Text>
            <HStack spacing={4}>
              <Button
                as={RouterLink}
                to="/register"
                size="lg"
                colorScheme="white"
                variant="solid"
                rightIcon={<FiArrowRight />}
              >
                {t('landing.hero.getStarted', 'Get Started Free')}
              </Button>
              <Button
                as={RouterLink}
                to="/pricing"
                size="lg"
                variant="outline"
                borderColor="white"
                color="white"
                _hover={{
                  borderColor: "white",
                  bg: "rgba(255, 255, 255, 0.1)"
                }}
              >
                {t('landing.hero.viewPricing', 'View Pricing')}
              </Button>
            </HStack>
          </VStack>
        </Container>
      </Box>

      {/* Features Section */}
      <Box py={16} bg={bgColor}>
        <Container maxW="1200px">
          <VStack spacing={12}>
            <VStack spacing={4} textAlign="center">
              <Heading size="xl" color={textColor}>
                {t('landing.features.title', 'Why Choose LeadTap?')}
              </Heading>
              <Text color={textColor} fontSize="lg" maxW="800px">
                {t('landing.features.description', 'Our platform combines cutting-edge technology with user-friendly design to provide the most efficient data extraction solution.')}
              </Text>
            </VStack>

            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={8}>
              <Box p={6} textAlign="center" bg="white" borderRadius="lg" shadow="md">
                <Icon as={FiSearch} w={10} h={10} color="blue.500" mb={4} />
                <Heading size="md" mb={3}>
                  {t('landing.features.googleMaps.title', 'Google Maps Leads')}
                </Heading>
                <Text color={textColor}>
                  {t('landing.features.googleMaps.description', 'Extract business data from Google Maps with advanced search and filtering.')}
                </Text>
              </Box>
              
              <Box p={6} textAlign="center" bg="white" borderRadius="lg" shadow="md">
                <Icon as={FiUsers} w={10} h={10} color="green.500" mb={4} />
                <Heading size="md" mb={3}>
                  {t('landing.features.facebook.title', 'Facebook Leads')}
                </Heading>
                <Text color={textColor}>
                  {t('landing.features.facebook.description', 'Collect leads from Facebook pages and groups using keywords and location.')}
                </Text>
              </Box>
              
              <Box p={6} textAlign="center" bg="white" borderRadius="lg" shadow="md">
                <Icon as={FiTrendingUp} w={10} h={10} color="purple.500" mb={4} />
                <Heading size="md" mb={3}>
                  {t('landing.features.instagram.title', 'Instagram Leads')}
                </Heading>
                <Text color={textColor}>
                  {t('landing.features.instagram.description', 'Find leads on Instagram using hashtags and location targeting.')}
                </Text>
              </Box>
              
              <Box p={6} textAlign="center" bg="white" borderRadius="lg" shadow="md">
                <Icon as={FiShield} w={10} h={10} color="orange.500" mb={4} />
                <Heading size="md" mb={3}>
                  {t('landing.features.whatsapp.title', 'WhatsApp Leads')}
                </Heading>
                <Text color={textColor}>
                  {t('landing.features.whatsapp.description', 'Extract WhatsApp leads using phone numbers and keywords for outreach.')}
                </Text>
              </Box>
            </SimpleGrid>

            <VStack spacing={6} pt={8}>
              <Button
                as={RouterLink}
                to="/register"
                size="lg"
                colorScheme="blue"
                rightIcon={<FiArrowRight />}
              >
                {t('landing.features.startExtracting', 'Start Extracting Data Today')}
              </Button>
            </VStack>
          </VStack>
        </Container>
      </Box>

      {/* Stats Section */}
      <Box py={16} bg="gray.800" color="white">
        <Container maxW="1200px">
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8} textAlign="center">
            <VStack>
              <Heading size="2xl" color="blue.400">10,000+</Heading>
              <Text fontSize="lg">Leads Generated</Text>
            </VStack>
            <VStack>
              <Heading size="2xl" color="green.400">500+</Heading>
              <Text fontSize="lg">Happy Customers</Text>
            </VStack>
            <VStack>
              <Heading size="2xl" color="purple.400">99.9%</Heading>
              <Text fontSize="lg">Uptime</Text>
            </VStack>
          </SimpleGrid>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box py={16} bg="blue.600" color="white">
        <Container maxW="1200px">
          <VStack spacing={6} textAlign="center">
            <Heading size="xl">
              {t('landing.cta.title', 'Ready to Transform Your Lead Generation?')}
            </Heading>
            <Text fontSize="lg" maxW="600px">
              {t('landing.cta.description', 'Join thousands of businesses that trust LeadTap for their data extraction needs. Start your free trial today.')}
            </Text>
            <Button
              as={RouterLink}
              to="/register"
              size="lg"
              colorScheme="white"
              variant="solid"
              rightIcon={<FiArrowRight />}
            >
              {t('landing.cta.getStarted', 'Get Started Free')}
            </Button>
          </VStack>
        </Container>
      </Box>
    </Box>
  );
};

export default Landing; 