import React from 'react';
import { ChakraProvider, Box, ColorModeScript } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import Pricing from './pages/Pricing';
import About from './pages/About';
import Login from './pages/Login';
import Register from './pages/Register';
import NotFound from './pages/NotFound';
import PaymentSuccess from './pages/PaymentSuccess';
import PaymentCancel from './pages/PaymentCancel';
import AdminDashboard from './pages/AdminDashboard';
import Profile from './pages/Profile';
import SharedJob from './pages/SharedJob';
import SharedLead from './pages/SharedLead';
import AuditLog from './pages/AuditLog';
import OnboardingTour from './components/OnboardingTour';
import ProtectedRoute from './components/ProtectedRoute';
import { useState, useEffect, Suspense, lazy } from 'react';
import { AuthProvider } from './hooks/useAuth';
import theme from './theme';
import './styles/global.css';
import LiveChatWidget from './components/LiveChatWidget';
import LeadCollection from './pages/LeadCollection';

const CRM = lazy(() => import('./pages/CRM'));
const Analytics = lazy(() => import('./pages/Analytics'));
const TeamManagement = lazy(() => import('./pages/TeamManagement'));
const KnowledgeBase = lazy(() => import('./pages/KnowledgeBase'));

function App() {
  console.log('🚀 [APP] GMap Data Scraper application starting...');
  console.log('📱 [APP] User agent:', navigator.userAgent);
  console.log('🌐 [APP] Current URL:', window.location.href);

  const [showTour, setShowTour] = useState(false);
  const [tourRun, setTourRun] = useState(false);

  // Example: Show onboarding tour for new users (localStorage flag)
  useEffect(() => {
    const hasCompletedTour = localStorage.getItem('onboarding_complete');
    if (!hasCompletedTour) {
      setShowTour(true);
      setTourRun(true);
    }
  }, []);

  const handleTourClose = () => {
    setShowTour(false);
    localStorage.setItem('onboarding_complete', 'true');
  };

  const tourSteps = [
    {
      target: '[data-tour="dashboard-header"]',
      content: 'Welcome to LeadTap! This is your dashboard where you can manage all your lead generation activities.',
      placement: 'bottom'
    },
    {
      target: '[data-tour="dashboard-sidebar"]',
      content: 'Use the sidebar to navigate between different sections of the platform.',
      placement: 'right'
    },
    {
      target: '[data-tour="dashboard-content"]',
      content: 'Create new scraping jobs, view results, and manage your CRM leads from here.',
      placement: 'top'
    }
  ];

  useEffect(() => {
    // White-label: detect domain and fetch tenant config
    const domain = window.location.hostname;
    fetch(`/api/branding/config?domain=${domain}`)
      .then(res => res.json())
      .then(cfg => {
        if (cfg && cfg.tenant_slug) {
          (window as any).tenantSlug = cfg.tenant_slug;
          localStorage.setItem('tenantSlug', cfg.tenant_slug);
        }
        // Optionally apply branding/colors here
      });
  }, []);

  return (
    <ChakraProvider theme={theme}>
      <AuthProvider>
        <ColorModeScript initialColorMode={theme.config.initialColorMode} />
        <Box 
          minH="100vh" 
          bg="transparent"
          className="fade-in-up"
          display="flex"
          flexDirection="column"
        >
          {showTour && (
            <OnboardingTour steps={tourSteps} run={tourRun} onClose={handleTourClose} />
          )}
          <LiveChatWidget />
          <Router>
            <Navbar />
            <Box as="main" pt="64px" flex="1">
              <Suspense fallback={<div style={{textAlign: 'center', marginTop: 40}}>Loading...</div>}>
                <Routes>
                  <Route path="/" element={<Landing />} />
                  <Route path="/dashboard" element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  } />
                  <Route path="/pricing" element={<Pricing />} />
                  <Route path="/about" element={<About />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                  <Route path="/payment/success" element={<PaymentSuccess />} />
                  <Route path="/payment/cancel" element={<PaymentCancel />} />
                  <Route path="/admin" element={
                    <ProtectedRoute adminOnly>
                      <AdminDashboard />
                    </ProtectedRoute>
                  } />
                  <Route path="/profile" element={
                    <ProtectedRoute>
                      <Profile />
                    </ProtectedRoute>
                  } />
                  <Route path="/teams" element={
                    <ProtectedRoute requiredPlan="pro">
                      <TeamManagement />
                    </ProtectedRoute>
                  } />
                  <Route path="/knowledge-base" element={<KnowledgeBase />} />
                  <Route path="/shared/job/:token" element={<SharedJob />} />
                  <Route path="/shared/lead/:token" element={<SharedLead />} />
                  <Route path="/audit-log" element={
                    <ProtectedRoute requiredPlan="pro">
                      <AuditLog />
                    </ProtectedRoute>
                  } />
                  <Route path="/lead-collection" element={
                    <ProtectedRoute requiredPlan="pro">
                      <LeadCollection />
                    </ProtectedRoute>
                  } />
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </Suspense>
            </Box>
            <Footer />
          </Router>
        </Box>
      </AuthProvider>
    </ChakraProvider>
  );
}

export default App; 