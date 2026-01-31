
import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Icon,
  Flex,
  Badge,
  useColorModeValue,
  Spacer,
  Avatar,
} from '@chakra-ui/react';
import {
  FiHome,
  FiSearch,
  FiSend,
  FiBarChart2,
  FiSettings,
  FiTarget,
  FiZap,
} from 'react-icons/fi';

const MenuItem = ({ icon, label, path, active, badge }: any) => {
  const isActive = window.location.pathname === path;

  return (
    <Flex
      as="a"
      href={path}
      w="100%"
      align="center"
      p={4}
      mb={2}
      borderRadius="20px"
      bg={isActive ? 'rgba(14, 165, 233, 0.15)' : 'transparent'}
      color={isActive ? 'brand.400' : 'gray.500'}
      transition="0.3s"
      _hover={{
        bg: 'rgba(255, 255, 255, 0.05)',
        color: 'white',
        transform: 'translateX(5px)',
      }}
      cursor="pointer"
      position="relative"
    >
      <Icon as={icon} boxSize={5} mr={4} />
      <Text fontWeight={isActive ? 'bold' : 'medium'} fontSize="sm">{label}</Text>
      {badge && (
        <Badge ml="auto" colorScheme="red" variant="solid" borderRadius="full" fontSize="xs">
          {badge}
        </Badge>
      )}
      {isActive && (
        <Box
          position="absolute" left="-15px" w="4px" h="20px"
          bg="brand.400" borderRadius="full"
          boxShadow="0 0 15px #0EA5E9"
        />
      )}
    </Flex>
  );
};

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen }) => {
  return (
    <Box
      w="280px"
      bg="rgba(15, 23, 42, 0.8)"
      backdropFilter="blur(30px)"
      borderRight="1px solid rgba(255, 255, 255, 0.05)"
      h="100vh"
      p={6}
      position="fixed"
      left={0}
      top={0}
      zIndex={200}
      display={{ base: isOpen ? 'block' : 'none', md: 'block' }}
    >
      <VStack h="100%" align="stretch" spacing={8}>
        {/* Brand */}
        <HStack spacing={3} px={2}>
          <Box bg="vibrant.gradient" p={2} borderRadius="12px" boxShadow="0 0 20px rgba(139, 92, 246, 0.4)">
            <Icon as={FiZap} color="white" boxSize={5} />
          </Box>
          <Text fontSize="xl" fontWeight="900" letterSpacing="-1px">LEADTAP.</Text>
        </HStack>

        {/* Menu */}
        <VStack align="stretch" spacing={1}>
          <MenuItem icon={FiHome} label="Dashboard" path="/dashboard" />
          <MenuItem icon={FiTarget} label="Social Discovery" path="/social-discovery" badge="HOT" />
          <MenuItem icon={FiSearch} label="Lead Search" path="/leads/search" />
          <MenuItem icon={FiSend} label="WP Automator" path="/bulk-whatsapp" badge="NEW" />
          <MenuItem icon={FiBarChart2} label="Analytics" path="/analytics" />
        </VStack>

        <Spacer />

        {/* User / Settings */}
        <VStack align="stretch" spacing={2}>
          <MenuItem icon={FiSettings} label="Settings" path="/settings" />

          <Box
            bg="rgba(255, 255, 255, 0.03)" p={4} borderRadius="24px"
            border="1px solid rgba(255, 255, 255, 0.05)"
          >
            <HStack>
              <Avatar size="sm" src="https://i.pravatar.cc/150?u=me" borderRadius="10px" />
              <VStack align="start" spacing={0}>
                <Text fontSize="xs" fontWeight="bold">Asitha Konara</Text>
                <Text fontSize="10px" color="gray.600">Pro License</Text>
              </VStack>
            </HStack>
          </Box>
        </VStack>
      </VStack>
    </Box>
  );
};

export default Sidebar;