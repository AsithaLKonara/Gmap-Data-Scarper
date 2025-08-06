import React, { useState } from 'react';
import {
  Box,
  Flex,
  useColorModeValue,
  IconButton,
  useDisclosure,
} from '@chakra-ui/react';
import { FiMenu } from 'react-icons/fi';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isOpen, onToggle } = useDisclosure();
  const bgColor = useColorModeValue('gray.50', 'gray.900');

  return (
    <Flex h="100vh" bg={bgColor}>
      {/* Sidebar */}
      <Sidebar isOpen={isOpen} onToggle={onToggle} />

      {/* Main Content */}
      <Box
        flex={1}
        ml={{ base: 0, md: '280px' }}
        transition="margin-left 0.3s ease"
      >
        {/* Top Navigation */}
        <Flex
          as="header"
          align="center"
          justify="space-between"
          p={4}
          bg={useColorModeValue('white', 'gray.800')}
          borderBottom="1px"
          borderColor={useColorModeValue('gray.200', 'gray.700')}
          position="sticky"
          top={0}
          zIndex={100}
        >
          <IconButton
            aria-label="Open sidebar"
            icon={<FiMenu />}
            onClick={onToggle}
            display={{ base: 'flex', md: 'none' }}
            variant="ghost"
          />
          <Box flex={1} />
        </Flex>

        {/* Page Content */}
        <Box as="main" p={6} minH="calc(100vh - 80px)">
          {children}
        </Box>
      </Box>
    </Flex>
  );
};

export default Layout; 