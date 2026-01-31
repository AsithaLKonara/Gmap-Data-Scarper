
import React from 'react';
import {
  Box,
  Flex,
  IconButton,
  useDisclosure,
} from '@chakra-ui/react';
import { FiMenu } from 'react-icons/fi';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isOpen, onToggle } = useDisclosure({ defaultIsOpen: true });

  return (
    <Flex h="100vh" bg="dark.900" overflow="hidden">
      {/* Sidebar - Always visible on desktop */}
      <Sidebar isOpen={isOpen} onToggle={onToggle} />

      {/* Main Content */}
      <Box
        flex={1}
        ml={{ base: 0, md: isOpen ? '280px' : '0' }}
        transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)"
        h="100vh"
        overflowY="auto"
        position="relative"
        bg="dark.900"
      >
        {/* Dynamic Background Blob for every page */}
        <Box
          position="fixed" top="0" right="0" w="40vw" h="40vw"
          bg="radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%)"
          zIndex={0} pointerEvents="none"
        />

        {/* Mobile Header */}
        <Flex
          as="header"
          align="center"
          p={4}
          display={{ base: 'flex', md: 'none' }}
          position="sticky"
          top={0}
          zIndex={100}
          backdropFilter="blur(20px)"
          bg="rgba(15, 23, 42, 0.6)"
        >
          <IconButton
            aria-label="Toggle menu"
            icon={<FiMenu />}
            onClick={onToggle}
            variant="glass"
          />
        </Flex>

        {/* Page Content */}
        <Box as="main" p={{ base: 4, md: 8 }} position="relative" zIndex={1}>
          {children}
        </Box>
      </Box>
    </Flex>
  );
};

export default Layout;