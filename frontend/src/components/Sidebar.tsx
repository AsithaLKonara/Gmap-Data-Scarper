import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Icon,
  Flex,
  useColorModeValue,
  useDisclosure,
  IconButton,
  Divider,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
} from '@chakra-ui/react';
import {
  FiHome,
  FiSearch,
  FiUsers,
  FiBarChart2,
  FiSettings,
  FiMessageCircle,
  FiCreditCard,
  FiGrid,
  FiGift,
  FiMenu,
  FiX,
  FiChevronDown,
  FiLogOut,
  FiUser,
  FiHelpCircle,
  FiDatabase,
  FiFileText,
  FiZap,
  FiShield,
  FiMonitor,
  FiSend,
} from 'react-icons/fi';
import { Link, useLocation } from 'react-router-dom';

interface SidebarItem {
  label: string;
  icon: React.ElementType;
  path: string;
  children?: SidebarItem[];
}

const sidebarItems: SidebarItem[] = [
  {
    label: 'Dashboard',
    icon: FiHome,
    path: '/dashboard',
  },
  {
    label: 'Lead Generation',
    icon: FiSearch,
    path: '/leads',
    children: [
      { label: 'New Search', icon: FiSearch, path: '/leads/search' },
      { label: 'Bulk Search', icon: FiDatabase, path: '/leads/bulk-search' },
      { label: 'Job History', icon: FiFileText, path: '/jobs' },
    ],
  },
  {
    label: 'Leads',
    icon: FiUsers,
    path: '/leads',
    children: [
      { label: 'All Leads', icon: FiUsers, path: '/leads' },
      { label: 'Lead Scoring', icon: FiBarChart2, path: '/scoring' },
      { label: 'Collections', icon: FiGrid, path: '/collections' },
    ],
  },
  {
    label: 'Analytics',
    icon: FiBarChart2,
    path: '/analytics',
  },
  {
    label: 'Integrations',
    icon: FiZap,
    path: '/integrations',
  },
  {
    label: 'WhatsApp',
    icon: FiMessageCircle,
    path: '/whatsapp',
  },
  {
    label: 'Team Management',
    icon: FiUsers,
    path: '/team',
  },
  {
    label: 'Billing & Usage',
    icon: FiCreditCard,
    path: '/billing',
  },
  {
    label: 'Widgets',
    icon: FiGrid,
    path: '/widgets',
  },
  {
    label: 'Affiliate',
    icon: FiGift,
    path: '/affiliate',
  },
  {
    label: 'Settings',
    icon: FiSettings,
    path: '/settings',
  },
  {
    label: 'Support',
    icon: FiHelpCircle,
    path: '/support',
  },
  {
    label: 'Bulk WhatsApp Sender',
    icon: FiSend,
    path: '/bulk-whatsapp',
  },
];

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle }) => {
  const location = useLocation();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const activeBgColor = useColorModeValue('blue.50', 'blue.900');
  const activeTextColor = useColorModeValue('blue.600', 'blue.200');

  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  const toggleExpanded = (label: string) => {
    setExpandedItems(prev =>
      prev.includes(label)
        ? prev.filter(item => item !== label)
        : [...prev, label]
    );
  };

  const isActive = (path: string) => location.pathname === path;
  const isExpanded = (label: string) => expandedItems.includes(label);

  const SidebarItem: React.FC<{ item: SidebarItem; level?: number }> = ({
    item,
    level = 0,
  }) => {
    const hasChildren = item.children && item.children.length > 0;
    const active = isActive(item.path);
    const expanded = isExpanded(item.label);

    return (
      <Box>
        <Link to={item.path}>
          <Flex
            align="center"
            px={4}
            py={2}
            mx={2}
            borderRadius="lg"
            cursor="pointer"
            bg={active ? activeBgColor : 'transparent'}
            color={active ? activeTextColor : textColor}
            _hover={{
              bg: active ? activeBgColor : useColorModeValue('gray.100', 'gray.700'),
            }}
            onClick={() => hasChildren && toggleExpanded(item.label)}
            pl={4 + level * 4}
          >
            <Icon as={item.icon} mr={3} />
            <Text fontSize="sm" fontWeight={active ? 'semibold' : 'medium'}>
              {item.label}
            </Text>
            {hasChildren && (
              <Icon
                as={FiChevronDown}
                ml="auto"
                transform={expanded ? 'rotate(180deg)' : 'none'}
                transition="transform 0.2s"
              />
            )}
          </Flex>
        </Link>
        {hasChildren && expanded && (
          <VStack spacing={1} mt={1}>
            {item.children!.map((child, index) => (
              <SidebarItem key={index} item={child} level={level + 1} />
            ))}
          </VStack>
        )}
      </Box>
    );
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <Box
          position="fixed"
          top={0}
          left={0}
          right={0}
          bottom={0}
          bg="blackAlpha.600"
          zIndex={999}
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <Box
        position="fixed"
        left={0}
        top={0}
        h="100vh"
        w={{ base: isOpen ? '280px' : '0', md: '280px' }}
        bg={bgColor}
        borderRight="1px"
        borderColor={borderColor}
        zIndex={1000}
        transition="width 0.3s ease"
        overflow="hidden"
      >
        <VStack h="100%" spacing={0}>
          {/* Header */}
          <Flex
            w="100%"
            align="center"
            justify="space-between"
            p={4}
            borderBottom="1px"
            borderColor={borderColor}
          >
            <HStack>
              <Box
                w={8}
                h={8}
                bg="blue.500"
                borderRadius="lg"
                display="flex"
                alignItems="center"
                justifyContent="center"
              >
                <Text color="white" fontWeight="bold" fontSize="lg">
                  L
                </Text>
              </Box>
              <Text fontSize="lg" fontWeight="bold" color={useColorModeValue('gray.800', 'white')}>
                LeadTap
              </Text>
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

          {/* Navigation Items */}
          <VStack flex={1} w="100%" spacing={1} py={4} overflowY="auto">
            {sidebarItems.map((item, index) => (
              <SidebarItem key={index} item={item} />
            ))}
          </VStack>

          {/* Footer */}
          <Box w="100%" p={4} borderTop="1px" borderColor={borderColor}>
            <Menu>
              <MenuButton
                as={Flex}
                align="center"
                justify="space-between"
                w="100%"
                p={2}
                borderRadius="lg"
                cursor="pointer"
                _hover={{ bg: useColorModeValue('gray.100', 'gray.700') }}
              >
                <HStack>
                  <Avatar size="sm" name="User Name" src="" />
                  <VStack align="start" spacing={0}>
                    <Text fontSize="sm" fontWeight="medium">
                      User Name
                    </Text>
                    <Text fontSize="xs" color={textColor}>
                      user@example.com
                    </Text>
                  </VStack>
                </HStack>
                <Icon as={FiChevronDown} />
              </MenuButton>
              <MenuList>
                <MenuItem icon={<FiUser />}>Profile</MenuItem>
                <MenuItem icon={<FiSettings />}>Settings</MenuItem>
                <MenuDivider />
                <MenuItem icon={<FiLogOut />} color="red.500">
                  Logout
                </MenuItem>
              </MenuList>
            </Menu>
          </Box>
        </VStack>
      </Box>
    </>
  );
};

export default Sidebar; 