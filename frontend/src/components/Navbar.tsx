import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Box,
  Flex,
  Button,
  Text,
  HStack,
  VStack,
  IconButton,
  useDisclosure,
  useColorModeValue,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  Avatar,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import {
  FiMenu,
  FiX,
  FiUser,
  FiLogOut,
  FiSettings,
  FiGlobe,
} from 'react-icons/fi';

const Navbar: React.FC = () => {
  const { isOpen, onToggle } = useDisclosure();
  const location = useLocation();
  const { t, i18n } = useTranslation();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  // Mock user state - replace with actual auth context
  const [user] = useState<any>(null);

  const navItems = [
    { path: '/dashboard', label: t('nav.dashboard', 'Dashboard') },
    { path: '/leads', label: t('nav.leads', 'Leads') },
    { path: '/analytics', label: t('nav.analytics', 'Analytics') },
    { path: '/integrations', label: t('nav.integrations', 'Integrations') },
  ];

  const isActive = (path: string) => location.pathname === path;

  const handleLogout = () => {
    // Implement logout logic
    console.log('Logout clicked');
  };

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <Box
      bg={bgColor}
      borderBottom="1px"
      borderColor={borderColor}
      position="sticky"
      top={0}
      zIndex={1000}
    >
      <Box maxW="1200px" mx="auto" px={4}>
        <Flex h={16} alignItems="center" justifyContent="space-between">
          {/* Logo */}
          <Flex alignItems="center">
            <Link to="/">
              <HStack spacing={2}>
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
                <Text fontSize="lg" fontWeight="bold" color={textColor}>
                  LeadTap
                </Text>
              </HStack>
            </Link>
          </Flex>

          {/* Desktop Navigation */}
          <HStack spacing={8} display={{ base: 'none', md: 'flex' }}>
            {navItems.map((item) => (
              <Link key={item.path} to={item.path}>
                <Text
                  color={isActive(item.path) ? 'blue.500' : textColor}
                  fontWeight={isActive(item.path) ? 'semibold' : 'medium'}
                  _hover={{ color: 'blue.500' }}
                >
                  {item.label}
                </Text>
              </Link>
            ))}
          </HStack>

          {/* Right side actions */}
          <HStack spacing={4}>
            {/* Language Switcher */}
            <Menu>
              <MenuButton
                as={IconButton}
                icon={<FiGlobe />}
                variant="ghost"
                size="sm"
                aria-label="Change language"
              />
              <MenuList>
                <MenuItem onClick={() => changeLanguage('en')}>
                  English
                </MenuItem>
                <MenuItem onClick={() => changeLanguage('es')}>
                  Español
                </MenuItem>
              </MenuList>
            </Menu>

            {/* User Menu */}
            {user ? (
              <Menu>
                <MenuButton
                  as={Button}
                  variant="ghost"
                  size="sm"
                  leftIcon={<Avatar size="sm" name={user.name} />}
                >
                  {user.name}
                </MenuButton>
                <MenuList>
                  <MenuItem icon={<FiUser />}>
                    {t('nav.profile', 'Profile')}
                  </MenuItem>
                  <MenuItem icon={<FiSettings />}>
                    {t('nav.settings', 'Settings')}
                  </MenuItem>
                  <MenuDivider />
                  <MenuItem icon={<FiLogOut />} onClick={handleLogout}>
                    {t('nav.logout', 'Logout')}
                  </MenuItem>
                </MenuList>
              </Menu>
            ) : (
              <HStack spacing={2}>
                <Link to="/login">
                  <Button variant="ghost" size="sm">
                    {t('nav.login', 'Login')}
                  </Button>
                </Link>
                <Link to="/register">
                  <Button size="sm" colorScheme="blue">
                    {t('nav.signup', 'Sign Up')}
                  </Button>
                </Link>
              </HStack>
            )}

            {/* Mobile menu button */}
            <IconButton
              display={{ base: 'flex', md: 'none' }}
              onClick={onToggle}
              icon={isOpen ? <FiX /> : <FiMenu />}
              variant="ghost"
              aria-label="Toggle menu"
            />
          </HStack>
        </Flex>

        {/* Mobile Navigation */}
        {isOpen && (
          <Box display={{ base: 'block', md: 'none' }} pb={4}>
            <VStack spacing={2} align="stretch">
              {navItems.map((item) => (
                <Link key={item.path} to={item.path}>
                  <Box
                    px={3}
                    py={2}
                    borderRadius="md"
                    bg={isActive(item.path) ? 'blue.50' : 'transparent'}
                    color={isActive(item.path) ? 'blue.600' : textColor}
                    _hover={{ bg: 'gray.50' }}
                  >
                    {item.label}
                  </Box>
                </Link>
              ))}
              {!user && (
                <VStack spacing={2} pt={4} borderTop="1px" borderColor={borderColor}>
                  <Link to="/login" style={{ width: '100%' }}>
                    <Button variant="ghost" size="sm" w="full">
                      {t('nav.login', 'Login')}
                    </Button>
                  </Link>
                  <Link to="/register" style={{ width: '100%' }}>
                    <Button size="sm" colorScheme="blue" w="full">
                      {t('nav.signup', 'Sign Up')}
                    </Button>
                  </Link>
                </VStack>
              )}
            </VStack>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default Navbar; 