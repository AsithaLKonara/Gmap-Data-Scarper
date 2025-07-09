import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { 
  Box, 
  Flex, 
  HStack, 
  Link, 
  Button, 
  useColorMode, 
  Spacer, 
  Text,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  IconButton,
  useColorModeValue
} from '@chakra-ui/react';
import { MoonIcon, SunIcon, ChevronDownIcon } from '@chakra-ui/icons';
import { useAuth } from '../hooks/useAuth';
import { useState } from 'react';

const Navbar = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const { user, logout } = useAuth();
  const bg = useColorModeValue('rgba(255, 255, 255, 0.1)', 'rgba(0, 0, 0, 0.2)');
  const borderColor = useColorModeValue('rgba(255, 255, 255, 0.2)', 'rgba(255, 255, 255, 0.1)');
  const [restartTour, setRestartTour] = useState(false);

  const handleRestartTour = () => {
    localStorage.removeItem('onboarding_complete');
    setRestartTour(true);
    window.location.reload();
  };

  return (
    <Box 
      as="nav" 
      position="fixed"
      top={0}
      left={0}
      right={0}
      zIndex={1000}
      bg={bg}
      backdropFilter="blur(20px)"
      borderBottom="1px solid"
      borderColor={borderColor}
      px={6}
      py={4}
    >
      <Flex align="center" maxW="1200px" mx="auto">
        <HStack spacing={8}>
          <Link 
            as={RouterLink} 
            to="/" 
            fontWeight="bold" 
            fontSize="xl"
            className="gradient-text"
            _hover={{ textDecoration: 'none' }}
          >
            🚀 LeadTap
          </Link>
          <HStack spacing={6}>
            {user && (
              <>
                <Link as={RouterLink} to="/dashboard" px={3} py={2} rounded="md" _hover={{ textDecoration: 'none', bg: 'rgba(255, 255, 255, 0.1)' }}>
                  Dashboard
                </Link>
                <Link as={RouterLink} to="/crm" px={3} py={2} rounded="md" _hover={{ textDecoration: 'none', bg: 'rgba(255, 255, 255, 0.1)' }}>
                  CRM
                </Link>
                {user.plan === 'pro' || user.plan === 'business' ? (
                  <Link as={RouterLink} to="/lead-collection" px={3} py={2} rounded="md" _hover={{ textDecoration: 'none', bg: 'rgba(255, 255, 255, 0.1)' }}>
                    Lead Collection
                  </Link>
                ) : null}
                {user.plan === 'pro' || user.plan === 'business' ? (
                  <Link as={RouterLink} to="/analytics" px={3} py={2} rounded="md" _hover={{ textDecoration: 'none', bg: 'rgba(255, 255, 255, 0.1)' }}>
                    Analytics
                  </Link>
                ) : null}
                {user.plan === 'pro' || user.plan === 'business' ? (
                  <Link as={RouterLink} to="/teams" px={3} py={2} rounded="md" _hover={{ textDecoration: 'none', bg: 'rgba(255, 255, 255, 0.1)' }}>
                    Teams
                  </Link>
                ) : null}
                {user.plan === 'business' ? (
                  <Link as={RouterLink} to="/admin" px={3} py={2} rounded="md" _hover={{ textDecoration: 'none', bg: 'rgba(255, 255, 255, 0.1)' }}>
                    Admin
                  </Link>
                ) : null}
              </>
            )}
            <Button size="sm" colorScheme="blue" variant="outline" onClick={handleRestartTour}>
              Restart Tour
            </Button>
          </HStack>
        </HStack>
        
        <Spacer />
        
        <HStack spacing={4}>
          <IconButton
            aria-label="Toggle color mode"
            icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
            onClick={toggleColorMode}
            variant="ghost"
            size="sm"
            color="gray.300"
            _hover={{ color: 'brand.400', bg: 'rgba(255, 255, 255, 0.1)' }}
          />
          
          {user ? (
            <Menu>
              <MenuButton
                as={Button}
                rightIcon={<ChevronDownIcon />}
                variant="ghost"
                size="sm"
                color="gray.300"
                _hover={{ color: 'brand.400', bg: 'rgba(255, 255, 255, 0.1)' }}
              >
                <HStack spacing={2}>
                  <Avatar size="xs" name={user.email} />
                  <Text fontSize="sm">{user.email}</Text>
                </HStack>
              </MenuButton>
              <MenuList bg="dark.800" border="1px solid" borderColor="gray.600">
                <MenuItem 
                  as={RouterLink}
                  to="/profile"
                  bg="transparent"
                  _hover={{ bg: 'rgba(255, 255, 255, 0.1)' }}
                  color="gray.300"
                >
                  Profile
                </MenuItem>
                <MenuItem 
                  bg="transparent"
                  _hover={{ bg: 'rgba(255, 255, 255, 0.1)' }}
                  color="gray.300"
                >
                  Plan: {user.plan}
                </MenuItem>
                <MenuItem 
                  onClick={logout}
                  bg="transparent"
                  _hover={{ bg: 'error.red', color: 'white' }}
                  color="gray.300"
                >
                  Logout
                </MenuItem>
              </MenuList>
            </Menu>
          ) : (
            <Button 
              as={RouterLink} 
              to="/login" 
              size="sm" 
              variant="solid"
              bg="linear-gradient(135deg, brand.500 0%, brand.600 100%)"
              _hover={{
                bg: 'linear-gradient(135deg, brand.600 0%, brand.700 100%)',
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 25px rgba(99, 102, 241, 0.4)'
              }}
            >
              Login
            </Button>
          )}
        </HStack>
      </Flex>
    </Box>
  );
};

export default Navbar; 