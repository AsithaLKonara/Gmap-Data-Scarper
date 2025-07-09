import React from 'react';
import { Box, Heading, Text, Container, VStack, SimpleGrid, Icon } from '@chakra-ui/react';
import { 
  SearchIcon, 
  DownloadIcon, 
  LockIcon, 
  StarIcon,
  CheckCircleIcon,
  TimeIcon
} from '@chakra-ui/icons';

const About = () => {
  const features = [
    {
      icon: SearchIcon,
      title: 'Advanced Search',
      description: 'Powerful search capabilities with location-based filtering and custom queries'
    },
    {
      icon: DownloadIcon,
      title: 'Multiple Export Formats',
      description: 'Export your data in CSV, JSON, Excel, and other popular formats'
    },
    {
      icon: LockIcon,
      title: 'Secure & Reliable',
      description: 'Enterprise-grade security with 99.9% uptime and data protection'
    },
    {
      icon: StarIcon,
      title: 'Premium Quality',
      description: 'High-quality, accurate data extraction with validation and verification'
    },
    {
      icon: CheckCircleIcon,
      title: 'Easy to Use',
      description: 'No coding required. Simple interface for users of all skill levels'
    },
    {
      icon: TimeIcon,
      title: 'Real-time Updates',
      description: 'Access the latest business information and contact details'
    }
  ];

  return (
    <Box py={20} minH="calc(100vh - 64px)">
      <Container maxW="1200px">
        <VStack spacing={16}>
          <VStack spacing={6} textAlign="center">
            <Heading size="3xl" className="gradient-text">
              About LeadTap
            </Heading>
            <Text color="gray.400" fontSize="xl" maxW="800px" lineHeight="1.6">
              LeadTap is a powerful Google Maps data extraction platform designed to help 
              businesses, researchers, and marketers gather comprehensive location data 
              efficiently and accurately. Our advanced technology makes it easy to extract 
              business information, contact details, and location data from Google Maps.
            </Text>
          </VStack>

          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={8}>
            {features.map((feature, index) => (
              <Box
                key={index}
                className="card-modern"
                p={6}
                textAlign="center"
                transition="all 0.3s ease"
                _hover={{
                  transform: 'translateY(-4px)',
                  boxShadow: '0 12px 24px rgba(0, 0, 0, 0.15)'
                }}
              >
                <Icon 
                  as={feature.icon} 
                  w={10} 
                  h={10} 
                  color="brand.400" 
                  mb={4}
                />
                <Heading size="md" mb={3}>
                  {feature.title}
                </Heading>
                <Text color="gray.400" lineHeight="1.6">
                  {feature.description}
    </Text>
              </Box>
            ))}
          </SimpleGrid>

          <VStack spacing={6} textAlign="center" pt={8}>
            <Heading size="lg" color="white">
              Why Choose LeadTap?
            </Heading>
            <Text color="gray.400" fontSize="lg" maxW="800px" lineHeight="1.6">
              Our platform combines cutting-edge technology with user-friendly design to 
              provide the most efficient and reliable Google Maps data extraction solution. 
              Whether you're a small business looking for leads or an enterprise requiring 
              bulk data extraction, LeadTap has the tools and features you need to succeed.
            </Text>
          </VStack>
        </VStack>
      </Container>
  </Box>
);
};

export default About; 