import React, { useState, useEffect } from 'react';
import * as api from '../api';
import { getSupportOptions, submitSupportRequest, getSavedQueries, createSavedQuery, updateSavedQuery, deleteSavedQuery, bulkDeleteJobs, bulkDeleteLeads, bulkAddLeads, getNotifications, markNotificationRead, enrichLead, shareJob, unshareJob, shareLead, unshareLead, getCRMStatus } from '../api';
import { Suspense, lazy } from 'react';
import { Home, Briefcase, Users, Settings, BarChart, Bell, LogOut, Menu, ChevronDown, Copy, Moon, Sun } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { OnboardingChecklist, MODULE_TOURS } from '../components/OnboardingTour';
import { OnboardingTour } from '../components/OnboardingTour';
import { Reorder, useDragControls } from 'framer-motion';
import { Dialog } from '../components/ui/dialog';
import { Checkbox } from '../components/ui/checkbox';

const CRM = lazy(() => import('./CRM'));
const Analytics = lazy(() => import('./Analytics'));

interface Job {
  id: number;
  status: string;
  queries: string[];
  created_at: string;
  updated_at: string;
}

interface Lead {
  id: number;
  name: string;
  email: string;
  phone?: string;
  company?: string;
  website?: string;
  status: string;
  source: string;
  created_at: string;
}

interface PlanLimits {
  max_queries_per_day: number;
  max_results_per_query: number;
  queries_used_today: number;
  queries_remaining_today: number;
  plan_name: string;
  subscription_status: string;
  subscription_end?: string;
}

const WIDGET_OPTIONS = [
  { id: 'widget-1', label: 'Widget 1', content: 'Widget 1' },
  { id: 'widget-2', label: 'Widget 2', content: 'Widget 2' },
  { id: 'widget-3', label: 'Widget 3', content: 'Widget 3' },
];

const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(false);
  const [queries, setQueries] = useState('');
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [jobResults, setJobResults] = useState<any[]>([]);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [planLimits, setPlanLimits] = useState<PlanLimits | null>(null);
  const [user, setUser] = useState<any>(null);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [leadModalOpen, setLeadModalOpen] = useState(false);
  const [newLead, setNewLead] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    website: '',
    notes: ''
  });
  const [apiKeyInfo, setApiKeyInfo] = useState<any>(null);
  const [apiKeyLoading, setApiKeyLoading] = useState(false);
  const [newApiKey, setNewApiKey] = useState<string | null>(null);
  const [supportOptions, setSupportOptions] = useState<any>(null);
  const [supportLoading, setSupportLoading] = useState(false);
  const [supportModalOpen, setSupportModalOpen] = useState(false);
  const [supportForm, setSupportForm] = useState({ subject: '', message: '', phone: '' });
  const [filters, setFilters] = useState({ status: '', company: '', dateFrom: '', dateTo: '' });
  const [savedQueries, setSavedQueries] = useState<any[]>([]);
  const [savedQueryModalOpen, setSavedQueryModalOpen] = useState(false);
  const [editingQuery, setEditingQuery] = useState<any>(null);
  const [templateName, setTemplateName] = useState('');
  const [selectedJobIds, setSelectedJobIds] = useState<number[]>([]);
  const [selectedLeadIds, setSelectedLeadIds] = useState<number[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [notifModalOpen, setNotifModalOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [crmConnected, setCrmConnected] = useState(false);
  const [onboarding, setOnboarding] = useState({
    dashboard: false,
    leads: false,
  });
  const [tourKey, setTourKey] = useState<string | null>(null);
  const [tourRun, setTourRun] = useState(false);
  const [widgets, setWidgets] = useState(
    WIDGET_OPTIONS.filter(w => selectedWidgetIds.includes(w.id))
  );
  const [showWidgetModal, setShowWidgetModal] = useState(false);
  const [selectedWidgetIds, setSelectedWidgetIds] = useState<string[]>(() => {
    const saved = localStorage.getItem('dashboardWidgets');
    return saved ? JSON.parse(saved) : WIDGET_OPTIONS.map(w => w.id);
  });

  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { isOpen, onToggle } = useDisclosure({ defaultIsOpen: true });
  const { colorMode, toggleColorMode } = useColorMode();

  // Add state for sharing modals
  const [shareJobModal, setShareJobModal] = useState<{ open: boolean; job: Job | null; link: string | null }>({ open: false, job: null, link: null });
  const [shareLeadModal, setShareLeadModal] = useState<{ open: boolean; lead: Lead | null; link: string | null }>({ open: false, lead: null, link: null });

  const location = useLocation();
  const navigate = useNavigate();

  const isMobile = useBreakpointValue({ base: true, md: false });
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Persist sidebar state in localStorage
  useEffect(() => {
    const savedSidebar = localStorage.getItem('sidebarOpen');
    if (savedSidebar !== null) setSidebarOpen(savedSidebar === 'true');
  }, []);
  useEffect(() => {
    localStorage.setItem('sidebarOpen', sidebarOpen ? 'true' : 'false');
  }, [sidebarOpen]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  useEffect(() => {
    if (user && (user.plan === 'pro' || user.plan === 'business')) {
      loadApiKeyInfo();
    }
  }, [user]);

  useEffect(() => {
    loadSupportOptions();
  }, [user]);

  useEffect(() => {
    loadSavedQueries();
  }, []);

  useEffect(() => {
    loadNotifications();
    const interval = setInterval(loadNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    getCRMStatus().then(status => setCrmConnected(!!status?.crm_connected));
  }, []);

  useEffect(() => {
    setWidgets(WIDGET_OPTIONS.filter(w => selectedWidgetIds.includes(w.id)));
    localStorage.setItem('dashboardWidgets', JSON.stringify(selectedWidgetIds));
  }, [selectedWidgetIds]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [userData, jobsData, leadsData, limitsData] = await Promise.all([
        api.getUser(),
        api.getJobs(),
        api.getCRMLeads(),
        api.getPlanLimits()
      ]);
      
      setUser(userData);
      setJobs(jobsData.jobs || []);
      setLeads(leadsData || []);
      setPlanLimits(limitsData);
      
      if (jobsData.jobs && jobsData.jobs.length > 0) {
        setSelectedJob(jobsData.jobs[0]);
        fetchJobResults(jobsData.jobs[0].id);
      }
    } catch (error: any) {
      console.error(error);
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const loadApiKeyInfo = async () => {
    setApiKeyLoading(true);
    try {
      const info = await api.getApiKeyInfo();
      setApiKeyInfo(info);
    } catch (e) {
      setApiKeyInfo(null);
    } finally {
      setApiKeyLoading(false);
    }
  };

  const handleCreateApiKey = async () => {
    setApiKeyLoading(true);
    try {
      const res = await api.createApiKey();
      setNewApiKey(res.api_key);
      loadApiKeyInfo();
      toast({ title: 'API Key Created', description: 'Copy and save your API key now. It will not be shown again.', status: 'success' });
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    } finally {
      setApiKeyLoading(false);
    }
  };

  const handleRevokeApiKey = async () => {
    setApiKeyLoading(true);
    try {
      await api.revokeApiKey();
      setNewApiKey(null);
      loadApiKeyInfo();
      toast({ title: 'API Key Revoked', status: 'info' });
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    } finally {
      setApiKeyLoading(false);
    }
  };

  const createJob = async () => {
    if (!queries.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter at least one query',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    // Check plan limits
    if (planLimits && planLimits.queries_remaining_today <= 0) {
      setShowUpgradeModal(true);
      return;
    }

    const queryList = queries.split('\n').filter(q => q.trim());
    setLoading(true);
    try {
      const response = await api.createJob(queryList);
      toast({
        title: 'Job Created',
        description: `Job ${response.job_id} has been created and is being processed`,
        status: 'success',
        duration: 5000,
      });
      setQueries('');
      loadDashboardData();
    } catch (error: any) {
      console.error(error);
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const addLeadToCRM = async (leadData: any) => {
    try {
      await api.addLeadToCRM({
        name: leadData.name || leadData.business_name || 'Unknown',
        email: leadData.email || '',
        phone: leadData.phone || '',
        company: leadData.company || leadData.business_name || '',
        website: leadData.website || '',
        source: 'gmaps',
        notes: `Added from job results: ${JSON.stringify(leadData)}`
      });
      
      toast({
        title: 'Lead Added',
        description: 'Lead has been added to your CRM',
        status: 'success',
        duration: 3000,
      });
      
      // Refresh leads
      const leadsData = await api.getCRMLeads();
      setLeads(leadsData || []);
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  const createNewLead = async () => {
    if (!newLead.name || !newLead.email) {
      toast({
        title: 'Error',
        description: 'Name and email are required',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    try {
      await api.addLeadToCRM(newLead);
      toast({
        title: 'Lead Created',
        description: 'New lead has been added to your CRM',
        status: 'success',
        duration: 3000,
      });
      
      setNewLead({
        name: '',
        email: '',
        phone: '',
        company: '',
        website: '',
        notes: ''
      });
      setLeadModalOpen(false);
      
      // Refresh leads
      const leadsData = await api.getCRMLeads();
      setLeads(leadsData || []);
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'green';
      case 'failed': return 'red';
      case 'pending': return 'yellow';
      default: return 'gray';
    }
  };

  const fetchJobResults = async (jobId: number, customFilters?: any) => {
    setResultsLoading(true);
    try {
      let res;
      if (customFilters && (customFilters.status || customFilters.company || customFilters.dateFrom || customFilters.dateTo)) {
        res = await api.getJobResultsWithFilters(jobId, customFilters);
      } else {
        res = await api.getJobResults(jobId);
      }
      setJobResults(res.result || []);
    } catch (error: any) {
      setJobResults([]);
      toast({ title: 'Error', description: error.message, status: 'error' });
    } finally {
      setResultsLoading(false);
    }
  };

  const downloadCSV = async (jobId: number) => {
    try {
      const token = localStorage.getItem('token');
      const url = api.getJobCSV(jobId);
      const res = await fetch(url, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error(await res.text());
      const blob = await res.blob();
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `gmap_leads_${jobId}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error: any) {
      console.error(error);
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  // GMap iframe URL for the first query of the selected job
  const getGMapUrl = (job: Job | null) => {
    if (!job || !job.queries || job.queries.length === 0) return '';
    const query = encodeURIComponent(job.queries[0]);
    return `https://www.google.com/maps?q=${query}&output=embed`;
  };

  // Sidebar animation styles
  const sidebarStyles = {
    transition: 'width 0.3s cubic-bezier(.4,0,.2,1)',
    width: sidebarOpen ? 280 : 64,
    minWidth: sidebarOpen ? 280 : 64,
    bg: useColorModeValue('gray.50', 'gray.900'),
    borderRight: '1px solid',
    borderColor: useColorModeValue('gray.200', 'gray.700'),
    height: '100vh',
    position: 'fixed' as const,
    top: 0,
    left: 0,
    zIndex: 100,
    overflow: 'hidden',
    boxShadow: 'md',
  };

  const sidebarItems = [
    { label: 'Dashboard', icon: Home, path: '/dashboard', dataTour: 'dashboard-sidebar-dashboard' },
    { label: 'My Jobs', icon: Briefcase, path: '/dashboard/jobs', dataTour: 'dashboard-sidebar-jobs' },
    { label: 'CRM', icon: Users, path: '/dashboard/crm', dataTour: 'dashboard-sidebar-crm' },
    { label: 'Analytics', icon: BarChart, path: '/dashboard/analytics', dataTour: 'dashboard-sidebar-analytics' },
    { label: 'Settings', icon: Settings, path: '/dashboard/settings', dataTour: 'dashboard-sidebar-settings' },
  ];
  if (user && (user.plan === 'pro' || user.plan === 'business')) {
    sidebarItems.splice(4, 0, { label: 'Team Management', icon: Users, path: '/teams', dataTour: 'dashboard-sidebar-teams' });
  }

  const isActive = (path: string) => location.pathname === path;

  // Sidebar as Drawer on mobile
  const sidebarContent = (
    <VStack align="stretch" spacing={2} pt={6} px={sidebarOpen ? 4 : 1}>
      {sidebarItems.map(item => {
        const Icon = item.icon;
        const active = isActive(item.path);
        return (
          <Tooltip label={sidebarOpen ? undefined : item.label} placement="right" key={item.label} openDelay={300}>
            <Button
              variant={active ? 'solid' : 'ghost'}
              colorScheme={active ? 'blue' : undefined}
              justifyContent={sidebarOpen ? 'flex-start' : 'center'}
              leftIcon={<Icon size={20} />}
              size="lg"
              onClick={() => { navigate(item.path); if (isMobile) setDrawerOpen(false); }}
              data-tour={item.dataTour}
              fontWeight={active ? 'bold' : 'normal'}
              bg={active ? useColorModeValue('blue.100', 'blue.900') : undefined}
              _hover={{ bg: active ? useColorModeValue('blue.200', 'blue.800') : useColorModeValue('gray.100', 'gray.700') }}
              borderRadius="md"
              mb={1}
            >
              {sidebarOpen && item.label}
            </Button>
          </Tooltip>
        );
      })}
    </VStack>
  );

  const sidebar = isMobile ? (
    <Drawer isOpen={drawerOpen} placement="left" onClose={() => setDrawerOpen(false)}>
      <DrawerOverlay />
      <DrawerContent>
        <DrawerCloseButton />
        <DrawerBody>{sidebarContent}</DrawerBody>
      </DrawerContent>
    </Drawer>
  ) : (
    <Box {...sidebarStyles} data-tour="dashboard-sidebar">{sidebarContent}</Box>
  );

  // Hamburger icon only on mobile
  const header = (
    <Flex as="header" align="center" justify="space-between" px={6} py={4} bg={useColorModeValue('white', 'gray.800')} borderBottom="1px solid" borderColor={useColorModeValue('gray.200', 'gray.700')} position="sticky" top={0} zIndex={101} boxShadow="sm" data-tour="dashboard-header">
      <HStack spacing={4}>
        {isMobile ? (
          <IconButton
            icon={<Menu />}
            aria-label="Open sidebar"
            variant="ghost"
            onClick={() => setDrawerOpen(true)}
          />
        ) : (
        <IconButton
          icon={<Menu />}
          aria-label="Toggle sidebar"
          variant="ghost"
          onClick={() => setSidebarOpen((v) => !v)}
        />
        )}
        <Heading size="md" fontWeight="bold" color="blue.500" className="gradient-text" data-tour="dashboard-brand">LeadTap</Heading>
      </HStack>
      <HStack spacing={4}>
        <IconButton
          aria-label="Toggle color mode"
          icon={colorMode === 'light' ? <Moon /> : <Sun />}
          onClick={toggleColorMode}
          variant="ghost"
          size="sm"
          color="gray.300"
          _hover={{ color: 'brand.400', bg: 'rgba(255, 255, 255, 0.1)' }}
        />
        {planLimits && (
          <Tag colorScheme={planLimits.plan_name === 'free' ? 'gray' : planLimits.plan_name === 'pro' ? 'blue' : 'green'} data-tour="dashboard-plan">
            {planLimits.plan_name.toUpperCase()}
          </Tag>
        )}
        <Menu>
          <MenuButton as={Button} rightIcon={<ChevronDown />} variant="ghost">
            <HStack>
              <Avatar size="sm" name={user?.email} src="" />
              <Text fontSize="sm">{user?.email}</Text>
            </HStack>
          </MenuButton>
          <MenuList>
            <MenuItem>Profile</MenuItem>
            <MenuItem>Settings</MenuItem>
            <MenuItem>Logout</MenuItem>
          </MenuList>
        </Menu>
        <Box position="relative" data-tour="dashboard-notifications">
          <IconButton icon={<span role="img" aria-label="bell">🔔</span>} aria-label="Notifications" variant="ghost" onClick={() => setNotifModalOpen(true)} />
          {unreadCount > 0 && (
            <Badge colorScheme="red" position="absolute" top={0} right={0} borderRadius="full">{unreadCount}</Badge>
          )}
        </Box>
      </HStack>
    </Flex>
  );

  // FAB for Add Job/Add Lead on mobile
  const fab = isMobile ? (
    <IconButton
      icon={<Home size={24} />}
      colorScheme="blue"
      aria-label="Add Lead"
      position="fixed"
      bottom={6}
      right={6}
      zIndex={2000}
      borderRadius="full"
      boxShadow="lg"
      size="lg"
      onClick={() => setLeadModalOpen(true)}
    />
  ) : null;

  const loadSupportOptions = async () => {
    setSupportLoading(true);
    try {
      const opts = await getSupportOptions();
      setSupportOptions(opts);
    } catch (e) {
      setSupportOptions(null);
    } finally {
      setSupportLoading(false);
    }
  };

  const handleSupportSubmit = async () => {
    setSupportLoading(true);
    try {
      await submitSupportRequest(supportForm);
      setSupportModalOpen(false);
      setSupportForm({ subject: '', message: '', phone: '' });
      toast({ title: 'Support request sent', status: 'success' });
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    } finally {
      setSupportLoading(false);
    }
  };

  // Helper: get allowed export formats by plan
  const getAllowedExportFormats = () => {
    if (!planLimits) return ['csv'];
    if (planLimits.plan_name === 'free') return ['csv'];
    if (planLimits.plan_name === 'pro') return ['csv', 'json', 'xlsx'];
    if (planLimits.plan_name === 'business') return ['csv', 'json', 'xlsx', 'pdf'];
    return ['csv'];
  };

  const handleExport = async (format: string, jobIdOverride?: number) => {
    const jobId = jobIdOverride || (selectedJob ? selectedJob.id : null);
    if (!jobId) return;
    if (!getAllowedExportFormats().includes(format)) {
      setShowUpgradeModal(true);
      return;
    }
    let url = '';
    let filename = '';
    if (format === 'csv') {
      url = api.getJobCSV(jobId);
      filename = `gmap_leads_${jobId}.csv`;
    } else if (format === 'json') {
      url = `${api.getJobCSV(jobId).replace('/csv', '/json')}`;
      filename = `gmap_leads_${jobId}.json`;
    } else if (format === 'xlsx') {
      url = `${api.getJobCSV(jobId).replace('/csv', '/xlsx')}`;
      filename = `gmap_leads_${jobId}.xlsx`;
    } else if (format === 'pdf') {
      url = `${api.getJobCSV(jobId).replace('/csv', '/pdf')}`;
      filename = `gmap_leads_${jobId}.pdf`;
    } else {
      toast({ title: 'Not implemented', description: 'This export format is not supported.', status: 'info' });
      return;
    }
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(url, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error(await res.text());
      const blob = await res.blob();
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error: any) {
      toast({ title: 'Error', description: error.message, status: 'error' });
    }
  };

  const loadSavedQueries = async () => {
    try {
      const data = await getSavedQueries();
      setSavedQueries(data);
    } catch {}
  };

  const handleUseTemplate = (q: any) => {
    setQueries(q.queries.join('\n'));
  };

  const handleSaveTemplate = async () => {
    if (!templateName.trim() || !queries.trim()) return;
    await createSavedQuery({ name: templateName, queries: queries.split('\n').filter(q => q.trim()) });
    setTemplateName('');
    loadSavedQueries();
    toast({ title: 'Saved', status: 'success' });
  };

  const handleUpdateTemplate = async () => {
    if (!editingQuery || !templateName.trim() || !queries.trim()) return;
    await updateSavedQuery(editingQuery.id, { name: templateName, queries: queries.split('\n').filter(q => q.trim()) });
    setEditingQuery(null);
    setTemplateName('');
    loadSavedQueries();
    toast({ title: 'Updated', status: 'success' });
  };

  const handleDeleteTemplate = async (id: number) => {
    await deleteSavedQuery(id);
    loadSavedQueries();
    toast({ title: 'Deleted', status: 'info' });
  };

  // Bulk selection helpers
  const toggleJobSelection = (id: number) => {
    setSelectedJobIds(ids => ids.includes(id) ? ids.filter(jid => jid !== id) : [...ids, id]);
  };
  const toggleAllJobs = () => {
    if (selectedJobIds.length === jobs.length) setSelectedJobIds([]);
    else setSelectedJobIds(jobs.map(j => j.id));
  };
  const toggleLeadSelection = (id: number) => {
    setSelectedLeadIds(ids => ids.includes(id) ? ids.filter(lid => lid !== id) : [...ids, id]);
  };
  const toggleAllLeads = () => {
    if (selectedLeadIds.length === leads.length) setSelectedLeadIds([]);
    else setSelectedLeadIds(leads.map(l => l.id));
  };

  // Bulk actions (implement backend next)
  const handleBulkExportJobs = (format: string) => {
    selectedJobIds.forEach(id => handleExport(format, id));
  };
  const handleBulkDeleteJobs = async () => {
    try {
      await bulkDeleteJobs(selectedJobIds);
      setSelectedJobIds([]);
      loadDashboardData();
      toast({ title: 'Jobs deleted', status: 'success' });
    } catch (e) {
      toast({ title: 'Error', description: String(e), status: 'error' });
    }
  };
  const handleBulkAddLeadsToCRM = async () => {
    try {
      const leadsToAdd = leads.filter(l => selectedLeadIds.includes(l.id));
      await bulkAddLeads(leadsToAdd);
      setSelectedLeadIds([]);
      loadDashboardData();
      toast({ title: 'Leads added to CRM', status: 'success' });
    } catch (e) {
      toast({ title: 'Error', description: String(e), status: 'error' });
    }
  };
  const handleBulkDeleteLeads = async () => {
    try {
      await bulkDeleteLeads(selectedLeadIds);
      setSelectedLeadIds([]);
      loadDashboardData();
      toast({ title: 'Leads deleted', status: 'success' });
    } catch (e) {
      toast({ title: 'Error', description: String(e), status: 'error' });
    }
  };

  const loadNotifications = async () => {
    try {
      const data = await getNotifications();
      setNotifications(data);
      setUnreadCount(data.filter((n: any) => !n.read).length);
    } catch {}
  };

  const handleMarkRead = async (id: number) => {
    await markNotificationRead(id);
    loadNotifications();
  };

  const handleEnrichLead = async (leadId: number) => {
    try {
      const enriched = await enrichLead(leadId);
      setLeads(leads => leads.map(l => l.id === leadId ? enriched : l));
      toast({ title: 'Lead enriched', description: 'Additional info added.', status: 'success' });
    } catch (e) {
      toast({ title: 'Error', description: String(e), status: 'error' });
    }
  };

  // Add share handlers
  const handleShareJob = async (job: Job) => {
    try {
      const res = await shareJob(job.id);
      setShareJobModal({ open: true, job, link: window.location.origin + res.url });
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    }
  };
  const handleUnshareJob = async (job: Job) => {
    try {
      await unshareJob(job.id);
      setShareJobModal({ open: false, job: null, link: null });
      toast({ title: 'Link disabled', status: 'info' });
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    }
  };
  const handleShareLead = async (lead: Lead) => {
    try {
      const res = await shareLead(lead.id);
      setShareLeadModal({ open: true, lead, link: window.location.origin + res.url });
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    }
  };
  const handleUnshareLead = async (lead: Lead) => {
    try {
      await unshareLead(lead.id);
      setShareLeadModal({ open: false, lead: null, link: null });
      toast({ title: 'Link disabled', status: 'info' });
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    }
  };

  const handlePushToCRM = async (leadId: number) => {
    try {
      await api.pushLeadToCRM(leadId);
      toast({ title: 'Lead pushed to CRM', status: 'success' });
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    }
  };

  // Main content
  return (
    <Box minH="100vh" bg={useColorModeValue('gray.100', 'gray.800')} data-tour="dashboard-main">
      {header}
      <Box pl={sidebarOpen ? 280 : 64} transition="pl 0.3s cubic-bezier(.4,0,.2,1)">
        <Container maxW="container.xl" py={8} data-tour="dashboard-content">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 20 }} transition={{ duration: 0.4 }}>
          <Tabs isFitted variant="enclosed" colorScheme="blue">
            <TabList mb="1em">
              <Tab>{t('dashboard.tabs.dashboard')}</Tab>
              <Tab>{t('dashboard.tabs.crm')}</Tab>
              <Tab>{t('dashboard.tabs.analytics')}</Tab>
            </TabList>
            <TabPanels>
              <TabPanel>
                <Box className="fade-in-up">
                  {/* Widget Customization Modal */}
                  <Dialog open={showWidgetModal} onOpenChange={setShowWidgetModal}>
                    <Dialog.Trigger asChild>
                      <Button className="ml-auto block bg-primary text-primary-foreground px-4 py-2 rounded font-semibold shadow hover:bg-primary/90" onClick={() => setShowWidgetModal(true)}>{t('dashboard.customizeWidgets.button')}</Button>
                    </Dialog.Trigger>
                    <Dialog.Content>
                      <Dialog.Title>{t('dashboard.customizeWidgets.title')}</Dialog.Title>
                      <div className="space-y-2 mt-4">
                        {WIDGET_OPTIONS.map(widget => (
                          <label key={widget.id} className="flex items-center gap-2">
                            <Checkbox
                              checked={selectedWidgetIds.includes(widget.id)}
                              onCheckedChange={checked => {
                                setSelectedWidgetIds(ids =>
                                  checked ? [...ids, widget.id] : ids.filter(id => id !== widget.id)
                                );
                              }}
                            />
                            {widget.label}
                          </label>
                        ))}
                      </div>
                      <Dialog.Close asChild>
                        <Button className="mt-6 bg-primary text-primary-foreground px-4 py-2 rounded font-semibold shadow hover:bg-primary/90">{t('dashboard.customizeWidgets.doneButton')}</Button>
                      </Dialog.Close>
                    </Dialog.Content>
                  </Dialog>
                  {/* Onboarding Checklist */}
                  <OnboardingChecklist
                    items={[
                      { key: 'dashboard', label: 'Explore your dashboard', completed: onboarding.dashboard },
                      { key: 'leads', label: 'View and filter leads', completed: onboarding.leads },
                    ]}
                    onStartTour={key => {
                      setTourKey(key);
                      setTourRun(true);
                    }}
                  />
                  {/* Onboarding Tour (per module) */}
                  {tourKey && (
                    <OnboardingTour
                      steps={MODULE_TOURS[tourKey]}
                      run={tourRun}
                      onClose={() => {
                        setOnboarding(o => ({ ...o, [tourKey]: true }));
                        setTourRun(false);
                        setTourKey(null);
                      }}
                    />
                  )}
                  {/* Dashboard Widgets Area (drag-and-drop, only selected widgets) */}
                  <Reorder.Group
                    axis="x"
                    values={widgets}
                    onReorder={setWidgets}
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8"
                  >
                    {widgets.map(widget => (
                      <Reorder.Item
                        key={widget.id}
                        value={widget}
                        className="dashboard-widget bg-card border border-border rounded-lg p-6 shadow-md cursor-move select-none"
                        whileDrag={{ scale: 1.03, boxShadow: '0 8px 32px rgba(99,102,241,0.15)' }}
                      >
                        {widget.content}
                      </Reorder.Item>
                    ))}
                  </Reorder.Group>
                  {/* Plan Status Alert */}
                  {planLimits && planLimits.queries_remaining_today <= 0 && (
                    <Alert status="warning" mb={6} className="card-modern">
                      <AlertIcon />
                      <AlertTitle>{t('dashboard.planStatus.limitReached.title')}</AlertTitle>
                      <AlertDescription>
                        {t('dashboard.planStatus.limitReached.description')} <Button size="sm" className="btn-modern" ml={2} onClick={() => setShowUpgradeModal(true)}>{t('dashboard.planStatus.limitReached.upgradeButton')}</Button>
                      </AlertDescription>
                    </Alert>
                  )}

                  {/* Stats Cards */}
                  {planLimits && (
                    <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={8} mb={10}>
                      <Box className="card-modern glass">
                        <Stat>
                          <StatLabel className="gradient-text">{t('dashboard.stats.queriesToday.label')}</StatLabel>
                          <StatNumber>{planLimits.queries_used_today}</StatNumber>
                          <StatHelpText>{t('dashboard.stats.queriesToday.helpText')}</StatHelpText>
                        </Stat>
                      </Box>
                      <Box className="card-modern glass">
                        <Stat>
                          <StatLabel className="gradient-text">{t('dashboard.stats.totalJobs.label')}</StatLabel>
                          <StatNumber>{jobs.length}</StatNumber>
                          <StatHelpText>{t('dashboard.stats.totalJobs.helpText')}</StatHelpText>
                        </Stat>
                      </Box>
                      <Box className="card-modern glass">
                        <Stat>
                          <StatLabel className="gradient-text">{t('dashboard.stats.crmLeads.label')}</StatLabel>
                          <StatNumber>{leads.length}</StatNumber>
                          <StatHelpText>{t('dashboard.stats.crmLeads.helpText')}</StatHelpText>
                        </Stat>
                      </Box>
                      <Box className="card-modern glass">
                        <Stat>
                          <StatLabel className="gradient-text">{t('dashboard.stats.plan.label')}</StatLabel>
                          <StatNumber>{planLimits.plan_name.toUpperCase()}</StatNumber>
                          <StatHelpText>{planLimits.subscription_status}</StatHelpText>
                        </Stat>
                      </Box>
                    </SimpleGrid>
                  )}

                  {/* API Key Management (Pro/Business) */}
                  {user && (user.plan === 'pro' || user.plan === 'business') && (
                    <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} className="card-modern glass">
                      <Heading size="md" mb={2} className="gradient-text">{t('dashboard.apiKeyManagement.title')}</Heading>
                      <Text fontSize="sm" color="gray.600" mb={4}>
                        {t('dashboard.apiKeyManagement.description')}
                      </Text>
                      {apiKeyLoading ? (
                        <Spinner />
                      ) : (
                        <VStack align="start" spacing={4}>
                          {newApiKey && (
                            <Box bg="yellow.100" p={3} borderRadius="md" w="100%" className="glass">
                              <Text fontWeight="bold">{t('dashboard.apiKeyManagement.newApiKey.title')}</Text>
                              <HStack>
                                <Text fontFamily="mono" fontSize="sm">{newApiKey}</Text>
                                <Button size="xs" onClick={() => {navigator.clipboard.writeText(newApiKey); toast({ title: 'Copied to clipboard', status: 'success' });}} leftIcon={<Copy />}>{t('dashboard.apiKeyManagement.newApiKey.copyButton')}</Button>
                              </HStack>
                              <Text fontSize="xs" color="red.500">{t('dashboard.apiKeyManagement.newApiKey.warning')}</Text>
                            </Box>
                          )}
                          {apiKeyInfo && apiKeyInfo.has_api_key && !newApiKey && (
                            <Box className="glass">
                              <Text fontWeight="bold">{t('dashboard.apiKeyManagement.activeApiKey.title')}</Text>
                              <Text fontSize="xs" color="gray.500">{t('dashboard.apiKeyManagement.activeApiKey.createdAt')}: {apiKeyInfo.created_at ? new Date(apiKeyInfo.created_at).toLocaleString() : '-'}</Text>
                              <Text fontSize="xs" color="gray.500">{t('dashboard.apiKeyManagement.activeApiKey.lastUsed')}: {apiKeyInfo.last_used ? new Date(apiKeyInfo.last_used).toLocaleString() : '-'}</Text>
                            </Box>
                          )}
                          {!apiKeyInfo?.has_api_key && !newApiKey && (
                            <Text color="gray.500">{t('dashboard.apiKeyManagement.noApiKey')}</Text>
                          )}
                          <HStack>
                            <Button colorScheme="blue" size="sm" onClick={handleCreateApiKey} isLoading={apiKeyLoading} isDisabled={!!apiKeyInfo?.has_api_key}>{t('dashboard.apiKeyManagement.generateApiKeyButton')}</Button>
                            <Button colorScheme="red" size="sm" onClick={handleRevokeApiKey} isLoading={apiKeyLoading} isDisabled={!apiKeyInfo?.has_api_key}>{t('dashboard.apiKeyManagement.revokeApiKeyButton')}</Button>
                          </HStack>
                        </VStack>
                      )}
                    </Box>
                  )}

                  {/* Support/Contact Section */}
                  <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} className="card-modern glass">
                    <HStack justify="space-between" mb={2}>
                      <Heading size="md" className="gradient-text">{t('dashboard.supportContact.title')}</Heading>
                      <Button size="sm" colorScheme="blue" onClick={() => setSupportModalOpen(true)}>{t('dashboard.supportContact.contactSupportButton')}</Button>
                    </HStack>
                    {supportLoading ? <Spinner /> : (
                      <VStack align="start" spacing={2}>
                        <Text fontSize="sm" color="gray.600">{t('dashboard.supportContact.availableOptions')}</Text>
                        <HStack>
                          {supportOptions?.support?.map((opt: string) => (
                            <Badge key={opt} colorScheme={opt === 'phone' ? 'green' : opt === 'email' ? 'blue' : 'purple'}>{opt.replace('_', ' ').toUpperCase()}</Badge>
                          ))}
                        </HStack>
                        {supportOptions?.priority && <Badge colorScheme="red">{t('dashboard.supportContact.priorityBadge')}</Badge>}
                      </VStack>
                    )}
                  </Box>

                  {/* Saved Searches Section */}
                  <Box bg={bgColor} p={4} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={6} className="card-modern glass">
                    <HStack justify="space-between" mb={2}>
                      <Heading size="sm" className="gradient-text">{t('dashboard.savedSearches.title')}</Heading>
                      <Button size="xs" colorScheme="blue" onClick={() => setSavedQueryModalOpen(true)}>{t('dashboard.savedSearches.saveTemplateButton')}</Button>
                    </HStack>
                    {savedQueries.length === 0 ? (
                      <Text color="gray.500">{t('dashboard.savedSearches.noSavedSearches')}</Text>
                    ) : (
                      <VStack align="stretch" spacing={2}>
                        {savedQueries.map((q) => (
                          <HStack key={q.id} spacing={2}>
                            <Button size="xs" variant="ghost" onClick={() => handleUseTemplate(q)}>{q.name}</Button>
                            <Button size="xs" colorScheme="yellow" variant="outline" onClick={() => { setEditingQuery(q); setTemplateName(q.name); setQueries(q.queries.join('\n')); setSavedQueryModalOpen(true); }}>{t('dashboard.savedSearches.editButton')}</Button>
                            <Button size="xs" colorScheme="red" variant="outline" onClick={() => handleDeleteTemplate(q.id)}>{t('dashboard.savedSearches.deleteButton')}</Button>
                          </HStack>
                        ))}
                      </VStack>
                    )}
                  </Box>

                  <HStack align="start" spacing={8}>
                    {/* Left: Jobs List and Create Job */}
                    <Box flex="1" minW="320px">
                      <VStack spacing={8} align="stretch">
                        <Box>
                          <Heading size="lg" mb={4} className="gradient-text">{t('dashboard.dashboardSection.title')}</Heading>
                          <Text color="gray.600">{t('dashboard.dashboardSection.description')}</Text>
                        </Box>
                        <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" className="card-modern glass">
                          <VStack spacing={4} align="stretch">
                            <Heading size="md" className="gradient-text">{t('dashboard.createNewJob.title')}</Heading>
                            <Text fontSize="sm" color="gray.600">
                              {t('dashboard.createNewJob.description')}
                            </Text>
                            <textarea
                              value={queries}
                              onChange={(e) => setQueries(e.target.value)}
                              placeholder={t('dashboard.createNewJob.placeholder')}
                              className="input-modern"
                              style={{ width: '100%', minHeight: '120px', resize: 'vertical', marginBottom: 16 }}
                              disabled={planLimits ? planLimits.queries_remaining_today <= 0 : false}
                            />
                            <Button
                              colorScheme="blue"
                              onClick={createJob}
                              isLoading={loading}
                              loadingText={t('dashboard.createNewJob.loadingText')}
                              isDisabled={planLimits ? planLimits.queries_remaining_today <= 0 : false}
                              className="btn-modern"
                            >
                              {planLimits && planLimits.queries_remaining_today <= 0 
                                ? `${t('dashboard.createNewJob.dailyLimitReached', { limit: planLimits.max_queries_per_day })}` 
                                : t('dashboard.createNewJob.createJobButton')}
                            </Button>
                          </VStack>
                        </Box>
                        <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" className="card-modern glass">
                          <Heading size="md" mb={4} className="gradient-text">{t('dashboard.yourJobs.title')}</Heading>
                          {jobs.length === 0 ? (
                            <Text color="gray.500">{t('dashboard.yourJobs.noJobsCreated')}</Text>
                          ) : (
                            <VStack spacing={4} align="stretch">
                              {/* Bulk Actions for Jobs */}
                              {jobs.length > 0 && (
                                <HStack mb={2}>
                                  <Button size="xs" className="btn-modern" variant="outline" onClick={toggleAllJobs}>{selectedJobIds.length === jobs.length ? t('dashboard.yourJobs.unselectAll') : t('dashboard.yourJobs.selectAll')}</Button>
                                  <Button size="xs" className="btn-modern" onClick={() => handleBulkExportJobs('csv')}>{t('dashboard.yourJobs.exportCsvButton')}</Button>
                                  <Button size="xs" className="btn-modern" onClick={() => handleBulkExportJobs('json')}>{t('dashboard.yourJobs.exportJsonButton')}</Button>
                                  <Button size="xs" className="btn-modern" colorScheme="red" onClick={handleBulkDeleteJobs}>{t('dashboard.yourJobs.deleteButton')}</Button>
                                </HStack>
                              )}
                              {jobs.map((job) => (
                                <Box
                                  key={job.id}
                                  p={4}
                                  border="1px"
                                  borderColor={borderColor}
                                  borderRadius="md"
                                  bg={selectedJob?.id === job.id ? 'blue.50' : 'transparent'}
                                  cursor="pointer"
                                  onClick={() => {
                                    setSelectedJob(job);
                                    fetchJobResults(Number(job.id));
                                  }}
                                  _hover={{ bg: 'blue.100' }}
                                  transition="background 0.2s"
                                  className="glass"
                                >
                                  <HStack justify="space-between" mb={2}>
                                    <Text fontWeight="bold">{t('dashboard.jobItem.jobId', { id: job.id })}</Text>
                                    <Badge colorScheme={getStatusColor(job.status)}>{job.status}</Badge>
                                  </HStack>
                                  <Text color="gray.400" fontSize="sm">{job.queries.join(', ')}</Text>
                                </Box>
                              ))}
                            </VStack>
                          )}
                        </Box>
                      </VStack>
                    </Box>
                    {/* Right: GMap and Results */}
                    <Box flex="2" minW="400px">
                      <VStack spacing={6} align="stretch">
                        {/* GMap Iframe */}
                        <Box borderRadius="lg" overflow="hidden" border="1px" borderColor={borderColor} minH="320px" boxShadow="md" mb={6} className="glass">
                          {selectedJob && selectedJob.queries && selectedJob.queries.length > 0 ? (
                            <iframe
                              title={t('dashboard.gmapIframe.title')}
                              src={getGMapUrl(selectedJob)}
                              width="100%"
                              height="320"
                              style={{ border: 0 }}
                              allowFullScreen
                              loading="lazy"
                              referrerPolicy="no-referrer-when-downgrade"
                            />
                          ) : (
                            <Text color="gray.500" p={8} textAlign="center">{t('dashboard.gmapIframe.noQueryMessage')}</Text>
                          )}
                        </Box>
                        {/* Results Table */}
                        <Box overflowX="auto" className="glass">
                          <Heading size="md" mb={4} className="gradient-text">{t('dashboard.searchResults.title')}</Heading>
                          {/* Advanced Filters (Pro/Business only) */}
                          {user && (user.plan === 'pro' || user.plan === 'business') && (
                            <Box mb={4}>
                              <HStack spacing={4} mb={2}>
                                <Text fontSize="sm" color="gray.600">{t('dashboard.searchResults.advancedFilters')}</Text>
                                <Select placeholder={t('dashboard.searchResults.statusPlaceholder')} size="sm" w="120px" value={filters.status} onChange={e => setFilters(f => ({ ...f, status: e.target.value }))}>
                                  <option value="completed">{t('dashboard.searchResults.statusOptions.completed')}</option>
                                  <option value="pending">{t('dashboard.searchResults.statusOptions.pending')}</option>
                                  <option value="failed">{t('dashboard.searchResults.statusOptions.failed')}</option>
                                </Select>
                                <Input placeholder={t('dashboard.searchResults.companyPlaceholder')} size="sm" w="160px" value={filters.company} onChange={e => setFilters(f => ({ ...f, company: e.target.value }))} />
                                <Input type="date" size="sm" w="140px" value={filters.dateFrom} onChange={e => setFilters(f => ({ ...f, dateFrom: e.target.value }))} />
                                <Input type="date" size="sm" w="140px" value={filters.dateTo} onChange={e => setFilters(f => ({ ...f, dateTo: e.target.value }))} />
                                <Button size="sm" colorScheme="blue" onClick={() => selectedJob && fetchJobResults(Number(selectedJob.id), filters)}>{t('dashboard.searchResults.applyFiltersButton')}</Button>
                                <Button size="sm" variant="ghost" onClick={() => { setFilters({ status: '', company: '', dateFrom: '', dateTo: '' }); selectedJob && fetchJobResults(Number(selectedJob.id), {}); }}>{t('dashboard.searchResults.resetFiltersButton')}</Button>
                              </HStack>
                            </Box>
                          )}
                          {resultsLoading ? (
                            <Spinner />
                          ) : jobResults.length === 0 ? (
                            <Text color="gray.500">{t('dashboard.searchResults.noResults')}</Text>
                          ) : (
                            <Table size="sm">
                              <Thead>
                                <Tr>
                                  <Th><input type="checkbox" checked={selectedJobIds.length === jobs.length} onChange={toggleAllJobs} /></Th>
                                  {Object.keys(jobResults[0]).map((key) => (
                                    <Th key={key}>{key}</Th>
                                  ))}
                                  <Th>{t('dashboard.searchResults.actions')}</Th>
                                </Tr>
                              </Thead>
                              <Tbody>
                                {jobResults.map((row, idx) => (
                                  <Tr key={idx} _hover={{ bg: 'gray.100' }} transition="background 0.2s">
                                    <Td><input type="checkbox" checked={selectedJobIds.includes(row.job_id)} onChange={() => toggleJobSelection(row.job_id)} /></Td>
                                    {Object.values(row).map((val, i) => (
                                      <Td key={i}>{String(val)}</Td>
                                    ))}
                                    <Td>
                                      <Tooltip label={t('dashboard.searchResults.addCrmTooltip')} aria-label={t('dashboard.searchResults.addCrmTooltip')}>
                                        <Button size="xs" onClick={() => addLeadToCRM(row)}>{t('dashboard.searchResults.addCrmButton')}</Button>
                                      </Tooltip>
                                    </Td>
                                  </Tr>
                                ))}
                              </Tbody>
                            </Table>
                          )}
                          {/* Export Buttons by Plan */}
                          {selectedJob && selectedJob.status === 'completed' && (
                            <HStack mt={4} spacing={2}>
                              {getAllowedExportFormats().map((format) => (
                                <Button
                                  key={format}
                                  colorScheme={format === 'csv' ? 'green' : format === 'json' ? 'blue' : format === 'xlsx' ? 'purple' : 'orange'}
                                  onClick={() => handleExport(format)}
                                >
                                  {t(`dashboard.searchResults.exportFormats.${format.toUpperCase()}`)}
                                </Button>
                              ))}
                            </HStack>
                          )}
                        </Box>
                      </VStack>
                    </Box>
                  </HStack>
                </Box>
              </TabPanel>
              <TabPanel>
                  <Suspense fallback={<Skeleton height="300px" width="100%" />}>
                  <CRM />
                </Suspense>
              </TabPanel>
              <TabPanel>
                  <Suspense fallback={<Skeleton height="300px" width="100%" />}>
                  <Analytics />
                </Suspense>
              </TabPanel>
            </TabPanels>
          </Tabs>
          </motion.div>
        </Container>
      </Box>

      {/* Upgrade Modal */}
      <Modal isOpen={showUpgradeModal} onClose={() => setShowUpgradeModal(false)}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t('dashboard.upgradeModal.title')}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Text mb={4}>{t('dashboard.upgradeModal.choosePlan')}</Text>
            <VStack spacing={4} align="stretch">
              <Box p={4} border="1px" borderColor="gray.200" borderRadius="md" bg="gray.50" className="card-modern glass">
                <Heading size="sm" mb={2} className="gradient-text">{t('dashboard.upgradeModal.freePlan.title')}</Heading>
                <Text fontSize="sm">{t('dashboard.upgradeModal.freePlan.description')}</Text>
                <Text fontSize="xs" color="gray.500">{t('dashboard.upgradeModal.freePlan.included')}</Text>
              </Box>
              <Box p={4} border="2px" borderColor="blue.400" borderRadius="md" bg="blue.50" className="card-modern glass">
                <Heading size="sm" mb={2} className="gradient-text">{t('dashboard.upgradeModal.proPlan.title')}</Heading>
                <Text fontSize="sm">{t('dashboard.upgradeModal.proPlan.description')}</Text>
                <Text fontSize="xs" color="gray.500">{t('dashboard.upgradeModal.proPlan.bestFor')}</Text>
              </Box>
              <Box p={4} border="2px" borderColor="green.400" borderRadius="md" bg="green.50" className="card-modern glass">
                <Heading size="sm" mb={2} className="gradient-text">{t('dashboard.upgradeModal.businessPlan.title')}</Heading>
                <Text fontSize="sm">{t('dashboard.upgradeModal.businessPlan.description')}</Text>
                <Text fontSize="xs" color="gray.500">{t('dashboard.upgradeModal.businessPlan.for')}</Text>
              </Box>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => setShowUpgradeModal(false)}>{t('dashboard.upgradeModal.cancelButton')}</Button>
            <Button colorScheme="blue">{t('dashboard.upgradeModal.upgradeNowButton')}</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Add Lead Modal */}
      <Modal isOpen={leadModalOpen} onClose={() => setLeadModalOpen(false)}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t('dashboard.addLeadModal.title')}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <Input
                placeholder={t('dashboard.addLeadModal.namePlaceholder')}
                value={newLead.name}
                onChange={(e) => setNewLead({...newLead, name: e.target.value})}
                className="input-modern"
              />
              <Input
                placeholder={t('dashboard.addLeadModal.emailPlaceholder')}
                type="email"
                value={newLead.email}
                onChange={(e) => setNewLead({...newLead, email: e.target.value})}
                className="input-modern"
              />
              <Input
                placeholder={t('dashboard.addLeadModal.phonePlaceholder')}
                value={newLead.phone}
                onChange={(e) => setNewLead({...newLead, phone: e.target.value})}
                className="input-modern"
              />
              <Input
                placeholder={t('dashboard.addLeadModal.companyPlaceholder')}
                value={newLead.company}
                onChange={(e) => setNewLead({...newLead, company: e.target.value})}
                className="input-modern"
              />
              <Input
                placeholder={t('dashboard.addLeadModal.websitePlaceholder')}
                value={newLead.website}
                onChange={(e) => setNewLead({...newLead, website: e.target.value})}
                className="input-modern"
              />
              <textarea
                placeholder={t('dashboard.addLeadModal.notesPlaceholder')}
                value={newLead.notes}
                onChange={(e) => setNewLead({...newLead, notes: e.target.value})}
                style={{
                  width: '100%',
                  minHeight: '80px',
                  padding: '8px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '4px',
                }}
                className="input-modern"
              />
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => setLeadModalOpen(false)}>{t('dashboard.addLeadModal.cancelButton')}</Button>
            <Button colorScheme="blue" onClick={createNewLead}>{t('dashboard.addLeadModal.addLeadButton')}</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Support Modal */}
      <Modal isOpen={supportModalOpen} onClose={() => setSupportModalOpen(false)}>
          <ModalOverlay />
          <ModalContent>
          <ModalHeader>{t('dashboard.supportModal.title')}</ModalHeader>
          <ModalCloseButton />
            <ModalBody>
            <VStack spacing={4} align="stretch">
              <Input
                placeholder={t('dashboard.supportModal.subjectPlaceholder')}
                value={supportForm.subject}
                onChange={e => setSupportForm({ ...supportForm, subject: e.target.value })}
                className="input-modern"
              />
              <textarea
                placeholder={t('dashboard.supportModal.messagePlaceholder')}
                value={supportForm.message}
                onChange={e => setSupportForm({ ...supportForm, message: e.target.value })}
                style={{ width: '100%', minHeight: '100px', padding: '8px', border: '1px solid #e2e8f0', borderRadius: '4px' }}
                className="input-modern"
              />
              {supportOptions?.support?.includes('phone') && (
                <Input
                  placeholder={t('dashboard.supportModal.phonePlaceholder')}
                  value={supportForm.phone}
                  onChange={e => setSupportForm({ ...supportForm, phone: e.target.value })}
                  className="input-modern"
                />
              )}
            </VStack>
            </ModalBody>
            <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => setSupportModalOpen(false)}>{t('dashboard.supportModal.cancelButton')}</Button>
            <Button colorScheme="blue" onClick={handleSupportSubmit} isLoading={supportLoading}>{t('dashboard.supportModal.sendButton')}</Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

      {/* Saved Query Modal */}
      <Modal isOpen={savedQueryModalOpen} onClose={() => { setSavedQueryModalOpen(false); setEditingQuery(null); setTemplateName(''); }}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{editingQuery ? t('dashboard.savedQueryModal.editTemplateTitle') : t('dashboard.savedQueryModal.saveSearchTitle')}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <Input placeholder={t('dashboard.savedQueryModal.templateNamePlaceholder')} value={templateName} onChange={e => setTemplateName(e.target.value)} className="input-modern" />
              <textarea
                value={queries}
                onChange={e => setQueries(e.target.value)}
                placeholder={t('dashboard.savedQueryModal.enterQueriesPlaceholder')}
                style={{ width: '100%', minHeight: '120px', padding: '12px', border: '1px solid #e2e8f0', borderRadius: '8px', fontFamily: 'inherit', fontSize: '14px', resize: 'vertical', background: useColorModeValue('white', 'gray.900') }}
                className="input-modern"
              />
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => { setSavedQueryModalOpen(false); setEditingQuery(null); setTemplateName(''); }}>{t('dashboard.savedQueryModal.cancelButton')}</Button>
            {editingQuery ? (
              <Button colorScheme="yellow" onClick={handleUpdateTemplate}>{t('dashboard.savedQueryModal.updateButton')}</Button>
            ) : (
              <Button colorScheme="blue" onClick={handleSaveTemplate}>{t('dashboard.savedQueryModal.saveButton')}</Button>
            )}
            </ModalFooter>
          </ModalContent>
        </Modal>

      {/* Notifications Modal */}
      <Modal isOpen={notifModalOpen} onClose={() => setNotifModalOpen(false)}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t('dashboard.notificationsModal.title')}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack align="stretch" spacing={2}>
              {notifications.length === 0 ? (
                <Text color="gray.500">{t('dashboard.notificationsModal.noNotifications')}</Text>
              ) : notifications.map((n) => (
                <Box key={n.id} p={3} bg={n.read ? 'gray.100' : 'yellow.100'} borderRadius="md" cursor="pointer" onClick={() => handleMarkRead(n.id)}>
                  <Text fontWeight="bold">{n.type}</Text>
                  <Text>{n.message}</Text>
                  <Text fontSize="xs" color="gray.500">{new Date(n.created_at).toLocaleString()}</Text>
                </Box>
              ))}
            </VStack>
          </ModalBody>
          </ModalContent>
        </Modal>

      {/* Share Job Modal */}
      <Modal isOpen={shareJobModal.open} onClose={() => setShareJobModal({ open: false, job: null, link: null })}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t('dashboard.shareJobModal.shareableLinkTitle')}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Text mb={2}>{t('dashboard.shareJobModal.shareableLinkText')}</Text>
            <Input value={shareJobModal.link || ''} isReadOnly />
            <Button mt={2} onClick={() => {navigator.clipboard.writeText(shareJobModal.link || ''); toast({ title: 'Copied', status: 'success' });}}>{t('dashboard.shareJobModal.copyLinkButton')}</Button>
            <Button mt={2} colorScheme="red" onClick={() => handleUnshareJob(shareJobModal.job!)}>{t('dashboard.shareJobModal.disableLinkButton')}</Button>
          </ModalBody>
        </ModalContent>
      </Modal>

      {/* Share Lead Modal */}
      <Modal isOpen={shareLeadModal.open} onClose={() => setShareLeadModal({ open: false, lead: null, link: null })}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t('dashboard.shareLeadModal.shareableLinkTitle')}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Text mb={2}>{t('dashboard.shareLeadModal.shareableLinkText')}</Text>
            <Input value={shareLeadModal.link || ''} isReadOnly />
            <Button mt={2} onClick={() => {navigator.clipboard.writeText(shareLeadModal.link || ''); toast({ title: 'Copied', status: 'success' });}}>{t('dashboard.shareLeadModal.copyLinkButton')}</Button>
            <Button mt={2} colorScheme="red" onClick={() => handleUnshareLead(shareLeadModal.lead!)}>{t('dashboard.shareLeadModal.disableLinkButton')}</Button>
          </ModalBody>
          </ModalContent>
        </Modal>
      {fab}
      </Box>
  );
};

export default Dashboard; 