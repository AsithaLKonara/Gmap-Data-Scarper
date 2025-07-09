import React from 'react';
import {
  Box,
  Container,
  VStack,
  HStack,
  Text,
  Link,
  Divider,
  Icon,
  SimpleGrid
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import { 
  FaTwitter, 
  FaLinkedin, 
  FaGithub, 
  FaEnvelope,
  FaMapMarkerAlt,
  FaPhone
} from 'react-icons/fa';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <Box 
      bg="rgba(30, 41, 59, 0.8)" 
      backdropFilter="blur(10px)"
      borderTop="1px solid rgba(255, 255, 255, 0.1)"
      mt="auto"
    >
      <Container maxW="1200px" py={12}>
        <SimpleGrid columns={{ base: 1, md: 4 }} spacing={8}>
          {/* Company Info */}
          <VStack align="start" spacing={4}>
            <Text fontSize="xl" fontWeight="bold" className="gradient-text">
              LeadTap
            </Text>
            <Text color="gray.400" fontSize="sm" lineHeight="1.6">
              Advanced Google Maps data extraction platform for businesses, researchers, and marketers.
            </Text>
            <HStack spacing={4}>
              <Link href="#" color="gray.400" _hover={{ color: "brand.400" }}>
                <Icon as={FaTwitter} boxSize={5} />
              </Link>
              <Link href="#" color="gray.400" _hover={{ color: "brand.400" }}>
                <Icon as={FaLinkedin} boxSize={5} />
              </Link>
              <Link href="#" color="gray.400" _hover={{ color: "brand.400" }}>
                <Icon as={FaGithub} boxSize={5} />
              </Link>
              <Link href="mailto:contact@leadtap.com" color="gray.400" _hover={{ color: "brand.400" }}>
                <Icon as={FaEnvelope} boxSize={5} />
              </Link>
            </HStack>
          </VStack>

          {/* Quick Links */}
          <VStack align="start" spacing={4}>
            <Text fontWeight="bold" color="white" fontSize="lg">
              Quick Links
            </Text>
            <VStack align="start" spacing={2}>
              <Link as={RouterLink} to="/" color="gray.400" _hover={{ color: "brand.400" }}>
                Home
              </Link>
              <Link as={RouterLink} to="/about" color="gray.400" _hover={{ color: "brand.400" }}>
                About
              </Link>
              <Link as={RouterLink} to="/pricing" color="gray.400" _hover={{ color: "brand.400" }}>
                Pricing
              </Link>
              <Link as={RouterLink} to="/dashboard" color="gray.400" _hover={{ color: "brand.400" }}>
                Dashboard
              </Link>
            </VStack>
          </VStack>

          {/* Features */}
          <VStack align="start" spacing={4}>
            <Text fontWeight="bold" color="white" fontSize="lg">
              Features
            </Text>
            <VStack align="start" spacing={2}>
              <Text color="gray.400" fontSize="sm">Data Extraction</Text>
              <Text color="gray.400" fontSize="sm">Export Formats</Text>
              <Text color="gray.400" fontSize="sm">Real-time Updates</Text>
              <Text color="gray.400" fontSize="sm">Advanced Search</Text>
            </VStack>
          </VStack>

          {/* Contact Info */}
          <VStack align="start" spacing={4}>
            <Text fontWeight="bold" color="white" fontSize="lg">
              Contact
            </Text>
            <VStack align="start" spacing={3}>
              <HStack spacing={3}>
                <Icon as={FaMapMarkerAlt} color="brand.400" />
                <Text color="gray.400" fontSize="sm">
                  Colombo, Sri Lanka
                </Text>
              </HStack>
              <HStack spacing={3}>
                <Icon as={FaPhone} color="brand.400" />
                <Text color="gray.400" fontSize="sm">
                  +94 11 123 4567
                </Text>
              </HStack>
              <HStack spacing={3}>
                <Icon as={FaEnvelope} color="brand.400" />
                <Text color="gray.400" fontSize="sm">
                  contact@leadtap.com
                </Text>
              </HStack>
            </VStack>
          </VStack>
        </SimpleGrid>

        <Divider my={8} borderColor="rgba(255, 255, 255, 0.1)" />

        {/* Bottom Section */}
        <HStack justify="space-between" align="center" flexWrap="wrap">
          <Text color="gray.400" fontSize="sm">
            © {currentYear} LeadTap. All rights reserved.
          </Text>
          <HStack spacing={6}>
            <Link color="gray.400" fontSize="sm" _hover={{ color: "brand.400" }}>
              Privacy Policy
            </Link>
            <Link color="gray.400" fontSize="sm" _hover={{ color: "brand.400" }}>
              Terms of Service
            </Link>
            <Link color="gray.400" fontSize="sm" _hover={{ color: "brand.400" }}>
              Cookie Policy
            </Link>
          </HStack>
        </HStack>
      </Container>
    </Box>
  );
};

export default Footer; 