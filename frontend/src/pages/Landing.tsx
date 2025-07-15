import React from 'react';
import {
  Box,
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Image,
  SimpleGrid,
  Icon,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import { 
  SearchIcon, 
  DownloadIcon, 
  StarIcon,
  CheckCircleIcon,
  ArrowForwardIcon
} from '@chakra-ui/icons';
import { useTranslation } from 'react-i18next';

const Landing = () => {
  const { t } = useTranslation();
  const features = [
    {
      icon: SearchIcon,
      title: t('landing.features.advancedSearch.title', 'Advanced Search'),
      description: t('landing.features.advancedSearch.description', 'Powerful location-based filtering and custom queries')
    },
    {
      icon: DownloadIcon,
      title: t('landing.features.multipleFormats.title', 'Multiple Formats'),
      description: t('landing.features.multipleFormats.description', 'Export in CSV, JSON, Excel and more formats')
    },
    {
      icon: StarIcon,
      title: t('landing.features.premiumQuality.title', 'Premium Quality'),
      description: t('landing.features.premiumQuality.description', 'High-quality, accurate data extraction')
    },
    {
      icon: CheckCircleIcon,
      title: t('landing.features.easyToUse.title', 'Easy to Use'),
      description: t('landing.features.easyToUse.description', 'No coding required, simple interface')
    }
  ];

  const stats = [
    { number: '10M+', label: t('landing.stats.dataPoints', 'Data Points Extracted'), help: t('landing.stats.reliable', 'Reliable and accurate') },
    { number: '50K+', label: t('landing.stats.happyCustomers', 'Happy Customers'), help: t('landing.stats.trusted', 'Trusted worldwide') },
    { number: '99.9%', label: t('landing.stats.uptime', 'Uptime'), help: t('landing.stats.alwaysAvailable', 'Always available') },
    { number: '24/7', label: t('landing.stats.support', 'Support'), help: t('landing.stats.roundClock', 'Round the clock') }
  ];

  return (
    <Box>
      {/* Hero Section with Fixed Background GIF */}
      <Box 
        py={20} 
        position="relative" 
        overflow="hidden"
        minH="100vh"
        display="flex"
        alignItems="center"
      >
        {/* Fixed Background GIF */}
        <Box
          position="fixed"
          top="0"
          left="0"
          width="100%"
          height="100%"
          zIndex="-2"
          transform="scale(1.2)"
          transformOrigin="center center"
        >
          <Image
            src="/2150499233.jpg"
            alt="LeadTap Hero Animation"
            width="100%"
            height="100%"
            objectFit="cover"
            objectPosition="center"
            style={{
              animation: 'fadeInOut 8s ease-in-out infinite'
            }}
          />
        </Box>

        {/* Black Mask Overlay */}
        <Box
          position="fixed"
          top="0"
          left="0"
          width="100%"
          height="100%"
          bg="rgba(0, 0, 0, 0.6)"
          zIndex="-1"
        />

        {/* Content */}
        <Container maxW="1200px" position="relative" zIndex="1">
          <VStack align="center" spacing={8} textAlign="center">
            <VStack align="center" spacing={6} maxW="800px">
                <Heading size="4xl" className="gradient-text" lineHeight="1.1">
                  {t('landing.hero.title', 'Collect Leads from Google Maps, Facebook, Instagram, and WhatsApp')}
                </Heading>
                <Text color="gray.200" fontSize="xl" lineHeight="1.6" maxW="600px">
                  {t('landing.hero.subtitle', 'LeadTap is the most advanced multi-source lead generation platform. Extract business and contact data from Google Maps, Facebook, Instagram, and WhatsApp—all in one dashboard.')}
                </Text>
              </VStack>

              <HStack spacing={6}>
                <Button
                  as={RouterLink}
                  to="/register"
                  size="lg"
                  className="btn-modern"
                  rightIcon={<ArrowForwardIcon />}
                >
                  {t('landing.hero.getStarted', 'Get Started Free')}
                </Button>
                <Button
                  as={RouterLink}
                  to="/pricing"
                  variant="outline"
                  size="lg"
                  color="white"
                  borderColor="rgba(255, 255, 255, 0.3)"
                  _hover={{
                    borderColor: "brand.400",
                    bg: "rgba(255, 255, 255, 0.05)"
                  }}
                >
                  {t('landing.hero.viewPricing', 'View Pricing')}
                </Button>
              </HStack>
            </VStack>
        </Container>
      </Box>

      {/* Stats Section with GIF Background */}
      <Box 
        py={16} 
        bg="rgba(255, 255, 255, 0.02)"
        position="relative"
        overflow="hidden"
      >
        {/* Background GIF for stats section */}
        <Box
          position="absolute"
          top="0"
          left="0"
          width="100%"
          height="100%"
          zIndex="-2"
          transform="scale(1.2)"
          transformOrigin="center center"
        >
          <Image
            src="/2150499233.jpg"
            alt="LeadTap Background"
            width="100%"
            height="100%"
            objectFit="cover"
            objectPosition="center"
            opacity="0.1"
          />
        </Box>
        
        {/* Dark overlay for stats */}
        <Box
          position="absolute"
          top="0"
          left="0"
          width="100%"
          height="100%"
          bg="rgba(0, 0, 0, 0.7)"
          zIndex="-1"
        />

        <Container maxW="1200px" position="relative" zIndex="1">
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={8}>
            {stats.map((stat, index) => (
              <Stat key={index} textAlign="center">
                <StatNumber fontSize="3xl" className="gradient-text" fontWeight="bold">
                  {stat.number}
                </StatNumber>
                <StatLabel color="gray.300" fontSize="lg">
                  {stat.label}
                </StatLabel>
                <StatHelpText color="gray.400" fontSize="sm">
                  {stat.help}
                </StatHelpText>
              </Stat>
            ))}
          </SimpleGrid>
        </Container>
      </Box>

      {/* Features Section */}
      <Box py={20}>
        <Container maxW="1200px">
          <VStack spacing={16}>
            <VStack spacing={6} textAlign="center">
              <Heading size="2xl" className="gradient-text">
                {t('landing.features.whyChooseLeadTap.title', 'Why Choose LeadTap?')}
              </Heading>
              <Text color="gray.400" fontSize="xl" maxW="800px">
                {t('landing.features.whyChooseLeadTap.description', 'Our platform combines cutting-edge technology with user-friendly design 
                to provide the most efficient data extraction solution.')}
              </Text>
            </VStack>

            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={8}>
              <Box className="card-modern" p={6} textAlign="center">
                <Icon as={SearchIcon} w={10} h={10} color="brand.400" mb={4} />
                <Heading size="md" mb={3}>{t('landing.features.googleMapsLeads.title', 'Google Maps Leads')}</Heading>
                <Text color="gray.400">{t('landing.features.googleMapsLeads.description', 'Extract business data from Google Maps with advanced search and filtering.')}</Text>
              </Box>
              <Box className="card-modern" p={6} textAlign="center">
                <Icon as={CheckCircleIcon} w={10} h={10} color="brand.400" mb={4} />
                <Heading size="md" mb={3}>{t('landing.features.facebookLeads.title', 'Facebook Leads')}</Heading>
                <Text color="gray.400">{t('landing.features.facebookLeads.description', 'Collect leads from Facebook pages and groups using keywords and location.')}</Text>
              </Box>
              <Box className="card-modern" p={6} textAlign="center">
                <Icon as={CheckCircleIcon} w={10} h={10} color="brand.400" mb={4} />
                <Heading size="md" mb={3}>{t('landing.features.instagramLeads.title', 'Instagram Leads')}</Heading>
                <Text color="gray.400">{t('landing.features.instagramLeads.description', 'Find leads on Instagram using hashtags and location targeting.')}</Text>
              </Box>
              <Box className="card-modern" p={6} textAlign="center">
                <Icon as={CheckCircleIcon} w={10} h={10} color="brand.400" mb={4} />
                <Heading size="md" mb={3}>{t('landing.features.whatsAppLeads.title', 'WhatsApp Leads')}</Heading>
                <Text color="gray.400">{t('landing.features.whatsAppLeads.description', 'Extract WhatsApp leads using phone numbers and keywords for outreach.')}</Text>
              </Box>
            </SimpleGrid>

            <VStack spacing={6} pt={8}>
              <Button
                as={RouterLink}
                to="/register"
                size="lg"
                className="btn-modern"
                rightIcon={<ArrowForwardIcon />}
              >
                {t('landing.features.startExtractingDataToday', 'Start Extracting Data Today')}
              </Button>
            </VStack>
    </VStack>
        </Container>
      </Box>
  </Box>
);
};

export default Landing; 