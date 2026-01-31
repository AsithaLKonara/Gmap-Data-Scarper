import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ChakraProvider, ColorModeScript } from '@chakra-ui/react';
import theme from './theme';
import Layout from './components/Layout';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import BulkWhatsAppSender from './components/BulkWhatsAppSender';
import { Box, Heading, Text } from '@chakra-ui/react';

import SocialDiscovery from './pages/SocialDiscovery';
import LeadSearch from './pages/LeadSearch';

function App() {
  return (
    <ChakraProvider theme={theme}>
      <ColorModeScript initialColorMode={theme.config.initialColorMode} />
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected routes with Layout */}
          <Route path="/dashboard" element={
            <Layout>
              <Dashboard />
            </Layout>
          } />
          <Route path="/social-discovery" element={
            <Layout>
              <SocialDiscovery />
            </Layout>
          } />
          <Route path="/leads/search" element={
            <Layout>
              <LeadSearch />
            </Layout>
          } />
          <Route path="/bulk-whatsapp" element={
            <Layout>
              <BulkWhatsAppSender />
            </Layout>
          } />

          {/* Redirect any unknown routes to landing page */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </ChakraProvider>
  );
}

export default App;
