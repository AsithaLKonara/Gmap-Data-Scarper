import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ChakraProvider, ColorModeScript } from '@chakra-ui/react';
import theme from './theme';
import Layout from './components/Layout';
import { Box, Heading, Text } from '@chakra-ui/react';
import BulkWhatsAppSender from './components/BulkWhatsAppSender';

// Placeholder components
const Dashboard = () => (
  <Box p={6}>
    <Heading size="lg" mb={4}>Dashboard</Heading>
    <Text>Welcome to LeadTap Dashboard - Coming Soon!</Text>
  </Box>
);

const LeadSearch = () => (
  <Box p={6}>
    <Heading size="lg" mb={4}>Lead Search</Heading>
    <Text>Lead Search functionality - Coming Soon!</Text>
  </Box>
);

function App() {
  return (
    <ChakraProvider theme={theme}>
      <ColorModeScript initialColorMode={theme.config.initialColorMode} />
      <Router>
        <Layout>
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/leads/search" element={<LeadSearch />} />
            <Route path="/bulk-whatsapp" element={<BulkWhatsAppSender />} />
            <Route path="/" element={<Dashboard />} />
          </Routes>
        </Layout>
      </Router>
    </ChakraProvider>
  );
}

export default App;
