import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Icon,
  useColorModeValue,
  Flex,
  Collapse,
  useDisclosure,
  IconButton,
  Avatar,
  Badge,
  Divider,
  Tooltip,
} from '@chakra-ui/react';
import { keyframes } from '@emotion/react';
import {
  FiHome,
  FiSearch,
  FiSend,
  FiBarChart2,
  FiUsers,
  FiSettings,
  FiMenu,
  FiX,
  FiChevronDown,
  FiChevronRight,
  FiZap,
  FiTarget,
  FiShield,
  FiGlobe,
  FiTrendingUp,
  FiMessageSquare,
  FiBell,
  FiUser,
} from 'react-icons/fi';
import { useTranslation } from 'react-i18next';

// Animations
const slideIn = keyframes`
  from { transform: translateX(-100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
`;

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
`;

interface MenuItem {
  name: string;
  icon: any;
  path: string;
  children?: MenuItem[];
  badge?: string;
  color?: string;
}

const menuItems: MenuItem[] = [
  {
    name: 'Dashboard',
    icon: FiHome,
    path: '/dashboard',
    color: 'blue.500'
  },
  {
    name: 'Lead Search',
    icon: FiSearch,
    path: '/leads/search',
    color: 'green.500'
  },
  {
    name: 'Bulk WhatsApp Sender',
    icon: FiSend,
    path: '/bulk-whatsapp',
    badge: 'New',
    color: 'purple.500'
  },
  {
    name: 'Analytics',
    icon: FiBarChart2,
    path: '/analytics',
    color: 'orange.500',
    children: [
      { name: 'Overview', icon: FiBarChart2, path: '/analytics/overview', color: 'blue.400' },
      { name: 'Reports', icon: FiBarChart2, path: '/analytics/reports', color: 'green.400' },
      { name: 'Insights', icon: FiBarChart2, path: '/analytics/insights', color: 'purple.400' }
    ]
  },
  {
    name: 'Team Management',
    icon: FiUsers,
    path: '/team',
    color: 'teal.500',
    children: [
      { name: 'Members', icon: FiUsers, path: '/team/members', color: 'blue.400' },
      { name: 'Roles', icon: FiShield, path: '/team/roles', color: 'green.400' },
      { name: 'Permissions', icon: FiGlobe, path: '/team/permissions', color: 'purple.400' }
    ]
  },
  {
    name: 'Settings',
    icon: FiSettings,
    path: '/settings',
    color: 'gray.500',
    children: [
      { name: 'Profile', icon: FiUser, path: '/settings/profile', color: 'blue.400' },
      { name: 'Account', icon: FiSettings, path: '/settings/account', color: 'green.400' },
      { name: 'Integrations', icon: FiGlobe, path: '/settings/integrations', color: 'purple.400' }
    ]
  }
];

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle }) => {
  const { t } = useTranslation();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const hoverBgColor = useColorModeValue('gray.50', 'gray.700');
  const activeBgColor = useColorModeValue('blue.50', 'blue.900');
  const activeTextColor = useColorModeValue('blue.600', 'blue.200');
  const gradientBg = useColorModeValue(
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #4c1d95 0%, #7c3aed 100%)'
  );

  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  const toggleExpanded = (itemName: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemName)) {
      newExpanded.delete(itemName);
    } else {
      newExpanded.add(itemName);
    }
    setExpandedItems(newExpanded);
  };

  const renderMenuItem = (item: MenuItem, level: number = 0) => {
    const isExpanded = expandedItems.has(item.name);
    const hasChildren = item.children && item.children.length > 0;
    const paddingLeft = `${level * 16 + 16}px`;

    return (
      <Box key={item.name}>
        <Flex
          as="a"
          href={item.path}
          alignItems="center"
          px={4}
          py={3}
          pl={paddingLeft}
          color={textColor}
          _hover={{
            bg: hoverBgColor,
            color: activeTextColor,
            textDecoration: 'none',
            transform: 'translateX(5px)',
            boxShadow: 'md'
          }}
          _active={{
            bg: activeBgColor,
            color: activeTextColor
          }}
          cursor="pointer"
          transition="all 0.3s"
          borderRadius="lg"
          mb={1}
          position="relative"
        >
          <HStack spacing={3} flex="1">
            <Box
              p={2}
              borderRadius="lg"
              bg={item.color ? `${item.color}20` : 'gray.100'}
              color={item.color || 'gray.500'}
              _groupHover={{
                bg: item.color || 'blue.500',
                color: 'white'
              }}
              transition="all 0.3s"
            >
              <Icon as={item.icon} boxSize={4} />
            </Box>
            <Text fontSize="sm" fontWeight="medium" textAlign="left" flex="1">
              {t(item.name)}
            </Text>
            {item.badge && (
              <Badge
                colorScheme="red"
                variant="solid"
                fontSize="xs"
                px={2}
                py={1}
                borderRadius="full"
                animation={`${pulse} 2s ease-in-out infinite`}
              >
                {item.badge}
              </Badge>
            )}
          </HStack>
          {hasChildren && (
            <Icon
              as={isExpanded ? FiChevronDown : FiChevronRight}
              boxSize={4}
              ml="auto"
              transition="transform 0.3s"
              transform={isExpanded ? 'rotate(0deg)' : 'rotate(-90deg)'}
            />
          )}
        </Flex>
        
        {hasChildren && (
          <Collapse in={isExpanded} animateOpacity>
            <VStack spacing={0} align="stretch" ml={4} borderLeft="2px" borderColor={borderColor}>
              {item.children!.map(child => renderMenuItem(child, level + 1))}
            </VStack>
          </Collapse>
        )}
      </Box>
    );
  };

  return (
    <Box
      as="nav"
      bg={bgColor}
      borderRight="1px"
      borderColor={borderColor}
      w={{ base: 'full', md: '280px' }}
      h="100vh"
      py={5}
      overflowY="auto"
      position="fixed"
      left={0}
      top={0}
      zIndex={20}
      transform={isOpen ? 'translateX(0)' : 'translateX(-100%)'}
      transition="transform 0.3s ease-in-out"
      display={{ base: 'block', md: 'block' }}
      animation={`${slideIn} 0.3s ease-out`}
      boxShadow="xl"
    >
      {/* Header */}
      <Box px={4} mb={6} pb={4} borderBottom="1px" borderColor={borderColor}>
        <Flex alignItems="center" justifyContent="space-between" mb={4}>
          <HStack spacing={3}>
            <Box
              p={2}
              borderRadius="xl"
              bg={gradientBg}
              boxShadow="lg"
            >
              <Icon as={FiSearch} boxSize={5} color="white" />
            </Box>
            <VStack spacing={0} align="start">
              <Text fontSize="lg" fontWeight="bold" color={useColorModeValue('gray.800', 'white')}>
                LeadTap
              </Text>
              <Text fontSize="xs" color={textColor}>
                Lead Generation Platform
              </Text>
            </VStack>
          </HStack>
          <IconButton
            aria-label="Close sidebar"
            icon={<FiX />}
            size="sm"
            variant="ghost"
            onClick={onToggle}
            display={{ base: 'flex', md: 'none' }}
          />
        </Flex>

        {/* User Profile */}
        <Box
          p={3}
          bg={useColorModeValue('gray.50', 'gray.700')}
          borderRadius="lg"
          border="1px"
          borderColor={borderColor}
        >
          <HStack spacing={3}>
            <Avatar
              size="sm"
              src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=40&h=40&fit=crop&crop=face"
              name="User"
            />
            <VStack spacing={0} align="start" flex="1">
              <Text fontSize="sm" fontWeight="medium" color={useColorModeValue('gray.800', 'white')}>
                John Doe
              </Text>
              <Text fontSize="xs" color={textColor}>
                Premium Plan
              </Text>
            </VStack>
            <Tooltip label="Notifications">
              <IconButton
                aria-label="Notifications"
                icon={<FiBell />}
                size="sm"
                variant="ghost"
                colorScheme="blue"
              />
            </Tooltip>
          </HStack>
        </Box>
      </Box>

      {/* Menu Items */}
      <VStack spacing={1} align="stretch" px={2}>
        {menuItems.map((item, index) => (
          <Box key={item.name} animation={`${fadeIn} 0.3s ease-out ${index * 0.1}s both`}>
            <Flex
              as="a"
              href={item.path}
              alignItems="center"
              px={4}
              py={3}
              color={textColor}
              _hover={{
                bg: hoverBgColor,
                color: activeTextColor,
                textDecoration: 'none',
                transform: 'translateX(5px)',
                boxShadow: 'md'
              }}
              _active={{
                bg: activeBgColor,
                color: activeTextColor
              }}
              cursor="pointer"
              transition="all 0.3s"
              borderRadius="lg"
              mb={1}
              onClick={() => {
                if (item.children && item.children.length > 0) {
                  toggleExpanded(item.name);
                }
              }}
            >
              <HStack spacing={3} flex="1">
                <Box
                  p={2}
                  borderRadius="lg"
                  bg={item.color ? `${item.color}20` : 'gray.100'}
                  color={item.color || 'gray.500'}
                  _groupHover={{
                    bg: item.color || 'blue.500',
                    color: 'white'
                  }}
                  transition="all 0.3s"
                >
                  <Icon as={item.icon} boxSize={4} />
                </Box>
                <Text fontSize="sm" fontWeight="medium" textAlign="left" flex="1">
                  {t(item.name)}
                </Text>
                {item.badge && (
                  <Badge
                    colorScheme="red"
                    variant="solid"
                    fontSize="xs"
                    px={2}
                    py={1}
                    borderRadius="full"
                    animation={`${pulse} 2s ease-in-out infinite`}
                  >
                    {item.badge}
                  </Badge>
                )}
              </HStack>
              {item.children && item.children.length > 0 && (
                <Icon
                  as={expandedItems.has(item.name) ? FiChevronDown : FiChevronRight}
                  boxSize={4}
                  ml="auto"
                  transition="transform 0.3s"
                  transform={expandedItems.has(item.name) ? 'rotate(0deg)' : 'rotate(-90deg)'}
                />
              )}
            </Flex>
            
            {item.children && item.children.length > 0 && (
              <Collapse in={expandedItems.has(item.name)} animateOpacity>
                <VStack spacing={0} align="stretch" ml={4} borderLeft="2px" borderColor={borderColor}>
                  {item.children.map(child => renderMenuItem(child, 1))}
                </VStack>
              </Collapse>
            )}
          </Box>
        ))}
      </VStack>

      {/* Footer */}
      <Box px={4} mt="auto" pt={6}>
        <Divider mb={4} />
        <Box
          p={3}
          bg={useColorModeValue('blue.50', 'blue.900')}
          borderRadius="lg"
          border="1px"
          borderColor={useColorModeValue('blue.200', 'blue.700')}
        >
          <VStack spacing={2} align="start">
            <Text fontSize="sm" fontWeight="bold" color="blue.600">
              🚀 Pro Features
            </Text>
            <Text fontSize="xs" color="blue.600">
              Upgrade to unlock advanced analytics and unlimited campaigns
            </Text>
          </VStack>
        </Box>
      </Box>
    </Box>
  );
};

export default Sidebar; 