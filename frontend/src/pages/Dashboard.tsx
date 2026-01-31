
import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  HStack,
  SimpleGrid,
  Button,
  Icon,
  Badge,
  Flex,
  Spacer,
  IconButton,
  Tooltip,
  Avatar,
} from '@chakra-ui/react';
import { motion } from 'framer-motion';
import {
  FiUsers,
  FiSend,
  FiTarget,
  FiZap,
  FiActivity,
  FiRefreshCw,
  FiSearch,
  FiArrowUpRight,
  FiMessageSquare,
} from 'react-icons/fi';

const MotionBox = motion(Box);

const StatCard = ({ icon, label, value, help, color }: any) => (
  <Box
    bg="rgba(255, 255, 255, 0.03)"
    backdropFilter="blur(20px)"
    border="1px solid rgba(255, 255, 255, 0.08)"
    borderRadius="24px"
    p={6}
    transition="all 0.3s"
    _hover={{ transform: 'translateY(-5px)', bg: 'rgba(255, 255, 255, 0.06)' }}
  >
    <VStack align="start" spacing={4}>
      <Box p={3} bg={`${color}.500`} borderRadius="14px" boxShadow={`0 0 20px ${color}44`}>
        <Icon as={icon} color="white" boxSize={5} />
      </Box>
      <VStack align="start" spacing={0}>
        <Text color="gray.500" fontSize="sm" fontWeight="bold" textTransform="uppercase" letterSpacing="1px">
          {label}
        </Text>
        <Heading size="xl" fontWeight="900" letterSpacing="-1px">
          {value}
        </Heading>
      </VStack>
      <Badge colorScheme="green" variant="subtle" borderRadius="full" px={2}>
        {help}
      </Badge>
    </VStack>
  </Box>
);

const Dashboard: React.FC = () => {
  return (
    <Box p={6}>
      <Container maxW="7xl">
        <VStack spacing={8} align="stretch">
          {/* Top Bar */}
          <Flex align="center">
            <VStack align="start" spacing={0}>
              <Heading size="lg" fontWeight="900" letterSpacing="-1px">Control Center.</Heading>
              <Text color="gray.500">Welcome to your discovery headquarters.</Text>
            </VStack>
            <Spacer />
            <HStack spacing={4}>
              <Tooltip label="Refresh Sync">
                <IconButton aria-label="refresh" icon={<FiRefreshCw />} variant="glass" />
              </Tooltip>
              <Button variant="glow" leftIcon={<FiZap />}>Manual Search</Button>
            </HStack>
          </Flex>

          {/* Stats */}
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
            <StatCard icon={FiTarget} label="Undergrad Leads" value="1,247" help="+12% this week" color="blue" />
            <StatCard icon={FiSend} label="Msgs Delivered" value="3.4K" help="99% Success" color="purple" />
            <StatCard icon={FiActivity} label="Active Scans" value="08" help="Running Now" color="pink" />
            <StatCard icon={FiUsers} label="Total Reach" value="12.5K" help="+2.4K Growth" color="cyan" />
          </SimpleGrid>

          {/* Main Grid */}
          <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={8}>
            {/* Recent Discoveries */}
            <Box gridColumn={{ lg: 'span 2' }}>
              <VStack align="stretch" spacing={6}>
                <Heading size="md">Live Discoveries.</Heading>
                <VStack spacing={4}>
                  {[1, 2, 3, 4].map((i) => (
                    <Flex
                      key={i} align="center" p={4} borderRadius="20px" bg="rgba(255,255,255,0.02)"
                      border="1px solid rgba(255,255,255,0.05)" _hover={{ bg: 'rgba(255,255,255,0.05)' }}
                      transition="0.2s" cursor="pointer"
                    >
                      <Avatar src={`https://i.pravatar.cc/150?u=${i}`} name="Student" size="md" borderRadius="12px" />
                      <VStack align="start" ml={4} spacing={0}>
                        <Text fontWeight="bold">Student Name #{i + 10} <Badge ml={2} colorScheme="blue">Undergraduate</Badge></Text>
                        <Text fontSize="sm" color="gray.500">SLIIT • Computer Science • Colombo</Text>
                      </VStack>
                      <Spacer />
                      <HStack spacing={4}>
                        <VStack align="end" spacing={0}>
                          <Text fontWeight="bold" fontSize="sm">077 123 45{i}6</Text>
                          <Text fontSize="xs" color="gray.600">Verified Contact</Text>
                        </VStack>
                        <IconButton aria-label="go" icon={<FiArrowUpRight />} variant="ghost" size="sm" />
                      </HStack>
                    </Flex>
                  ))}
                </VStack>
              </VStack>
            </Box>

            {/* Quick Actions & System Status */}
            <VStack spacing={8} align="stretch">
              <Box bg="vibrant.gradient" p={1} borderRadius="24px">
                <Box bg="dark.900" p={6} borderRadius="23px">
                  <Heading size="sm" mb={4}>System Integrity</Heading>
                  <VStack align="stretch" spacing={4}>
                    <Box>
                      <Flex justify="space-between" mb={2} fontSize="xs">
                        <Text color="gray.500">DISCOVERY ENGINE</Text>
                        <Text color="green.400">OPERATIONAL</Text>
                      </Flex>
                      <Box h="2px" bg="rgba(0,0,0,0.2)" borderRadius="full">
                        <Box h="2px" bg="green.400" w="100%" borderRadius="full" />
                      </Box>
                    </Box>
                    <Box>
                      <Flex justify="space-between" mb={2} fontSize="xs">
                        <Text color="gray.500">WHATSAPP GATEWAY</Text>
                        <Text color="blue.400">READY</Text>
                      </Flex>
                      <Box h="2px" bg="rgba(0,0,0,0.2)" borderRadius="full">
                        <Box h="2px" bg="blue.400" w="85%" borderRadius="full" />
                      </Box>
                    </Box>
                  </VStack>
                </Box>
              </Box>

              <VStack align="stretch" spacing={4}>
                <Button variant="glow" leftIcon={<FiSearch />} h="60px">Start New X-Ray</Button>
                <Button variant="glass" leftIcon={<FiMessageSquare />} h="60px">Blast Campaign</Button>
              </VStack>
            </VStack>
          </SimpleGrid>
        </VStack>
      </Container>
    </Box>
  );
};

export default Dashboard;
