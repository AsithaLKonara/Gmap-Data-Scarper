import React, { useState, useEffect, Suspense, lazy } from 'react';
import * as api from '../api';
import { getSupportOptions, submitSupportRequest, getSavedQueries, createSavedQuery, updateSavedQuery, deleteSavedQuery, bulkDeleteJobs, bulkDeleteLeads, bulkAddLeads, getNotifications, markNotificationRead, enrichLead, shareJob, unshareJob, shareLead, unshareLead, getCRMStatus } from '../api';
import { Home, Briefcase, Users, Settings, BarChart, Bell, LogOut, Menu, ChevronDown, Copy, Moon, Sun } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion, Reorder, useDragControls } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { OnboardingChecklist, MODULE_TOURS } from '../components/OnboardingTour';
import { OnboardingTour } from '../components/OnboardingTour';
import { Dialog } from '../components/ui/dialog';
// import { Checkbox } from '../components/ui/checkbox'; // Keep if ShadCN UI Checkbox exists

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
  const [showWidgetModal, setShowWidgetModal] = useState(false);
  
  // Define selectedWidgetIds first
  const [selectedWidgetIds, setSelectedWidgetIds] = useState<string[]>(() => {
    const saved = localStorage.getItem('dashboardWidgets');
    return saved ? JSON.parse(saved) : WIDGET_OPTIONS.map(w => w.id);
  });
  
  // Then define widgets using selectedWidgetIds
  const [widgets, setWidgets] = useState(
    WIDGET_OPTIONS.filter(w => selectedWidgetIds.includes(w.id))
  );

  // Add state for sharing modals
  const [shareJobModal, setShareJobModal] = useState<{ open: boolean; job: Job | null; link: string | null }>({ open: false, job: null, link: null });
  const [shareLeadModal, setShareLeadModal] = useState<{ open: boolean; lead: Lead | null; link: string | null }>({ open: false, lead: null, link: null });

  const location = useLocation();
  const navigate = useNavigate();

  // Remove Chakra UI hooks and replace with React state or placeholders
  // const toast = useToast();
  // const bgColor = useColorModeValue('white', 'gray.800');
  // const borderColor = useColorModeValue('gray.200', 'gray.700');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  // const { isOpen, onToggle } = useDisclosure({ defaultIsOpen: true });
  // const { colorMode, toggleColorMode } = useColorMode();
  const [colorMode, setColorMode] = useState<'light' | 'dark'>('light');
  const toggleColorMode = () => setColorMode((prev) => (prev === 'light' ? 'dark' : 'light'));
  const [isMobile, setIsMobile] = useState(false); // Placeholder, will update with effect

  // Responsive check for mobile
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Placeholder for toast notifications (replace with ShadCN UI toast)
  const showToast = (options: { title: string; description?: string; status?: string; duration?: number }) => {
    // TODO: Replace with ShadCN UI toast
    alert(`${options.title}${options.description ? ': ' + options.description : ''}`);
  };

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
    getCRMStatus().then(status => setCrmConnected(!!status?.crm_connected)).catch(() => setCrmConnected(false));
  }, []);

  useEffect(() => {
    setWidgets(WIDGET_OPTIONS.filter(w => selectedWidgetIds.includes(w.id)));
    localStorage.setItem('dashboardWidgets', JSON.stringify(selectedWidgetIds));
  }, [selectedWidgetIds]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [userData, jobsData, leadsData, limitsData] = await Promise.all([
        api.getUser().catch(() => ({ email: 'demo@example.com', plan: 'free' })),
        api.getJobs().catch(() => ({ jobs: [] })),
        api.getCRMLeads().catch(() => []),
        api.getPlanLimits().catch(() => ({
          max_queries_per_day: 5,
          max_results_per_query: 100,
          queries_used_today: 0,
          queries_remaining_today: 5,
          plan_name: 'free',
          subscription_status: 'active'
        }))
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
      // Set default data if API fails
      setUser({ email: 'demo@example.com', plan: 'free' });
      setJobs([]);
      setLeads([]);
      setPlanLimits({
        max_queries_per_day: 5,
        max_results_per_query: 100,
        queries_used_today: 0,
        queries_remaining_today: 5,
        plan_name: 'free',
        subscription_status: 'active'
      });
      showToast({ title: 'Demo Mode', description: 'Running in demo mode. Backend not connected.', status: 'info', duration: 5000 });
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
      showToast({ title: 'API Key Created', description: 'Copy and save your API key now. It will not be shown again.', status: 'success' });
    } catch (e: any) {
      showToast({ title: 'Error', description: e.message, status: 'error' });
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
      showToast({ title: 'API Key Revoked', status: 'info' });
    } catch (e: any) {
      showToast({ title: 'Error', description: e.message, status: 'error' });
    } finally {
      setApiKeyLoading(false);
    }
  };

  const createJob = async () => {
    if (!queries.trim()) {
      showToast({
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
      showToast({
        title: 'Job Created',
        description: `Job ${response.job_id} has been created and is being processed`,
        status: 'success',
        duration: 5000,
      });
      setQueries('');
      loadDashboardData();
    } catch (error: any) {
      console.error(error);
      showToast({
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
      
      showToast({
        title: 'Lead Added',
        description: 'Lead has been added to your CRM',
        status: 'success',
        duration: 3000,
      });
      
      // Refresh leads
      const leadsData = await api.getCRMLeads();
      setLeads(leadsData || []);
    } catch (error: any) {
      showToast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  const createNewLead = async () => {
    if (!newLead.name || !newLead.email) {
      showToast({
        title: 'Error',
        description: 'Name and email are required',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    try {
      await api.addLeadToCRM(newLead);
      showToast({
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
      showToast({
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
      showToast({ title: 'Error', description: error.message, status: 'error' });
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
      showToast({
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
    bg: 'gray.50', // Placeholder for ShadCN UI
    borderRight: '1px solid',
    borderColor: 'gray.200', // Placeholder for ShadCN UI
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
    <div className={`flex flex-col gap-2 pt-6 ${sidebarOpen ? 'px-4' : 'px-1'}`}>
      {sidebarItems.map(item => {
        const Icon = item.icon;
        const active = isActive(item.path);
        return (
          <button
            key={item.label}
            className={`flex items-center w-full text-left rounded-md mb-1 px-3 py-2 transition font-medium ${active ? 'bg-blue-100 text-blue-700 font-bold' : 'hover:bg-gray-100'} ${sidebarOpen ? '' : 'justify-center'}`}
            onClick={() => { navigate(item.path); if (isMobile) setSidebarOpen(false); }}
            data-tour={item.dataTour}
          >
            <Icon size={20} className="mr-2" />
            {sidebarOpen && item.label}
          </button>
        );
      })}
    </div>
  );

  const sidebar = isMobile ? (
    <div className={`fixed inset-0 z-50 bg-black bg-opacity-40`} onClick={() => setSidebarOpen(false)}>
      <div className="bg-white w-64 h-full shadow-lg" onClick={e => e.stopPropagation()}>
        <button className="absolute top-4 right-4 text-gray-500 hover:text-gray-700" onClick={() => setSidebarOpen(false)}>&times;</button>
        {sidebarContent}
      </div>
    </div>
  ) : (
    <div style={sidebarStyles} data-tour="dashboard-sidebar">{sidebarContent}</div>
  );

  // Hamburger icon only on mobile
  const header = (
    <header className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200 sticky top-0 z-[101] shadow-sm" data-tour="dashboard-header">
      <div className="flex items-center gap-4">
        {isMobile ? (
          <button
            className="p-2 rounded hover:bg-gray-100"
            aria-label="Open sidebar"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu size={24} />
          </button>
        ) : (
          <button
            className="p-2 rounded hover:bg-gray-100"
            aria-label="Toggle sidebar"
            onClick={() => setSidebarOpen((v) => !v)}
          >
            <Menu size={24} />
          </button>
        )}
        <span className="text-lg font-bold text-blue-500 gradient-text" data-tour="dashboard-brand">LeadTap</span>
      </div>
      <div className="flex items-center gap-4">
        <button
          className="p-2 rounded hover:bg-gray-100"
          aria-label="Toggle color mode"
          onClick={toggleColorMode}
        >
          {colorMode === 'light' ? <Moon size={20} /> : <Sun size={20} />}
        </button>
        {planLimits && planLimits.plan_name && (
          <span className={`px-2 py-1 rounded text-xs font-semibold ${planLimits.plan_name === 'free' ? 'bg-gray-200 text-gray-700' : planLimits.plan_name === 'pro' ? 'bg-blue-200 text-blue-700' : 'bg-green-200 text-green-700'}`} data-tour="dashboard-plan">
            {planLimits.plan_name.toUpperCase()}
          </span>
        )}
        {/* User Dropdown */}
        <div className="relative group">
          <button className="flex items-center gap-2 px-2 py-1 rounded hover:bg-gray-100">
            <span className="inline-block w-6 h-6 rounded-full bg-gray-300" />
            <span className="text-sm">{user?.email}</span>
            <ChevronDown size={16} />
          </button>
          <div className="absolute right-0 mt-2 w-40 bg-white border border-gray-200 rounded shadow-lg opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto transition-opacity z-50">
            <button className="block w-full text-left px-4 py-2 hover:bg-gray-100">Profile</button>
            <button className="block w-full text-left px-4 py-2 hover:bg-gray-100">Settings</button>
            <button className="block w-full text-left px-4 py-2 hover:bg-gray-100">Logout</button>
          </div>
        </div>
        {/* Notifications */}
        <div className="relative" data-tour="dashboard-notifications">
          <button className="p-2 rounded hover:bg-gray-100" aria-label="Notifications" onClick={() => setNotifModalOpen(true)}>
            <Bell size={20} />
          </button>
          {unreadCount > 0 && (
            <span className="absolute top-0 right-0 inline-flex items-center justify-center px-1.5 py-0.5 text-xs font-bold leading-none text-white bg-red-600 rounded-full">{unreadCount}</span>
          )}
        </div>
      </div>
    </header>
  );

  // FAB for Add Job/Add Lead on mobile
  const fab = isMobile ? (
    <button
      className="fixed bottom-6 right-6 z-2000 flex items-center justify-center w-12 h-12 rounded-full bg-blue-500 text-white shadow-lg"
      aria-label="Add Lead"
      onClick={() => setLeadModalOpen(true)}
    >
      <Home size={24} />
    </button>
  ) : null;

  const loadSupportOptions = async () => {
    setSupportLoading(true);
    try {
      const opts = await getSupportOptions();
      setSupportOptions(opts);
    } catch (e) {
      setSupportOptions({ support: ['email', 'phone'], priority: false });
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
      showToast({ title: 'Support request sent', status: 'success' });
    } catch (e: any) {
      showToast({ title: 'Error', description: e.message, status: 'error' });
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
      showToast({ title: 'Not implemented', description: 'This export format is not supported.', status: 'info' });
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
      showToast({ title: 'Error', description: error.message, status: 'error' });
    }
  };

  const loadSavedQueries = async () => {
    try {
      const data = await getSavedQueries();
      setSavedQueries(Array.isArray(data) ? data : []);
    } catch {
      setSavedQueries([]);
    }
  };

  const handleUseTemplate = (q: any) => {
    setQueries(q.queries.join('\n'));
  };

  const handleSaveTemplate = async () => {
    if (!templateName.trim() || !queries.trim()) return;
    await createSavedQuery({ name: templateName, queries: queries.split('\n').filter(q => q.trim()) });
    setTemplateName('');
    loadSavedQueries();
    showToast({ title: 'Saved', status: 'success' });
  };

  const handleUpdateTemplate = async () => {
    if (!editingQuery || !templateName.trim() || !queries.trim()) return;
    await updateSavedQuery(editingQuery.id, { name: templateName, queries: queries.split('\n').filter(q => q.trim()) });
    setEditingQuery(null);
    setTemplateName('');
    loadSavedQueries();
    showToast({ title: 'Updated', status: 'success' });
  };

  const handleDeleteTemplate = async (id: number) => {
    await deleteSavedQuery(id);
    loadSavedQueries();
    showToast({ title: 'Deleted', status: 'info' });
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
      showToast({ title: 'Jobs deleted', status: 'success' });
    } catch (e) {
      showToast({ title: 'Error', description: String(e), status: 'error' });
    }
  };
  const handleBulkAddLeadsToCRM = async () => {
    try {
      const leadsToAdd = leads.filter(l => selectedLeadIds.includes(l.id));
      await bulkAddLeads(leadsToAdd);
      setSelectedLeadIds([]);
      loadDashboardData();
      showToast({ title: 'Leads added to CRM', status: 'success' });
    } catch (e) {
      showToast({ title: 'Error', description: String(e), status: 'error' });
    }
  };
  const handleBulkDeleteLeads = async () => {
    try {
      await bulkDeleteLeads(selectedLeadIds);
      setSelectedLeadIds([]);
      loadDashboardData();
      showToast({ title: 'Leads deleted', status: 'success' });
    } catch (e) {
      showToast({ title: 'Error', description: String(e), status: 'error' });
    }
  };

  const loadNotifications = async () => {
    try {
      const data = await getNotifications();
      const notificationsArray = Array.isArray(data) ? data : [];
      setNotifications(notificationsArray);
      setUnreadCount(notificationsArray.filter((n: any) => !n.read).length);
    } catch {
      setNotifications([]);
      setUnreadCount(0);
    }
  };

  const handleMarkRead = async (id: number) => {
    await markNotificationRead(id);
    loadNotifications();
  };

  const handleEnrichLead = async (leadId: number) => {
    try {
      const enriched = await enrichLead(leadId);
      setLeads(leads => leads.map(l => l.id === leadId ? enriched : l));
      showToast({ title: 'Lead enriched', description: 'Additional info added.', status: 'success' });
    } catch (e) {
      showToast({ title: 'Error', description: String(e), status: 'error' });
    }
  };

  // Add share handlers
  const handleShareJob = async (job: Job) => {
    try {
      const res = await shareJob(job.id);
      setShareJobModal({ open: true, job, link: window.location.origin + res.url });
    } catch (e: any) {
      showToast({ title: 'Error', description: e.message, status: 'error' });
    }
  };
  const handleUnshareJob = async (job: Job) => {
    try {
      await unshareJob(job.id);
      setShareJobModal({ open: false, job: null, link: null });
      showToast({ title: 'Link disabled', status: 'info' });
    } catch (e: any) {
      showToast({ title: 'Error', description: e.message, status: 'error' });
    }
  };
  const handleShareLead = async (lead: Lead) => {
    try {
      const res = await shareLead(lead.id);
      setShareLeadModal({ open: true, lead, link: window.location.origin + res.url });
    } catch (e: any) {
      showToast({ title: 'Error', description: e.message, status: 'error' });
    }
  };
  const handleUnshareLead = async (lead: Lead) => {
    try {
      await unshareLead(lead.id);
      setShareLeadModal({ open: false, lead: null, link: null });
      showToast({ title: 'Link disabled', status: 'info' });
    } catch (e: any) {
      showToast({ title: 'Error', description: e.message, status: 'error' });
    }
  };

  const handlePushToCRM = async (leadId: number) => {
    try {
      await api.pushLeadToCRM(leadId);
      showToast({ title: 'Lead pushed to CRM', status: 'success' });
    } catch (e: any) {
      showToast({ title: 'Error', description: e.message, status: 'error' });
    }
  };

  // Main content
  return (
    <div className="min-h-screen bg-gray-100" data-tour="dashboard-main">
      {header}
      <div className="transition-all duration-300" style={{ paddingLeft: sidebarOpen ? 280 : 64 }}>
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8" data-tour="dashboard-content">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 20 }} transition={{ duration: 0.4 }}>
            {/* Tabs */}
            <div className="border-b border-gray-200 mb-6">
              <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                <button className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${true ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>{t('dashboard.tabs.dashboard')}</button>
                <button className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${false ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>{t('dashboard.tabs.crm')}</button>
                <button className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${false ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>{t('dashboard.tabs.analytics')}</button>
              </nav>
            </div>
            {/* Tab Panels - Only Dashboard for now, CRM/Analytics can be lazy loaded as before */}
            <div className="fade-in-up">
              {/* Widget Customization Modal */}
              <div className="flex justify-end mb-4">
                <button 
                  className="bg-blue-500 text-white px-4 py-2 rounded font-semibold shadow hover:bg-blue-600"
                  onClick={() => setShowWidgetModal(true)}
                >
                  {t('dashboard.customizeWidgets.button')}
                </button>
              </div>
              
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
              
              {/* Dashboard Widgets Area */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
                {widgets.map(widget => (
                  <div
                    key={widget.id}
                    className="bg-white border border-gray-200 rounded-lg p-6 shadow-md"
                  >
                    {widget.content}
                  </div>
                ))}
              </div>
              
              {/* Plan Status Alert */}
              {planLimits && planLimits.queries_remaining_today <= 0 && (
                <div className="bg-yellow-100 border border-yellow-200 text-yellow-800 px-4 py-3 rounded relative mb-6" role="alert">
                  <strong className="font-bold">{t('dashboard.planStatus.limitReached.title')}</strong>
                  <span className="block sm:inline"> {t('dashboard.planStatus.limitReached.description')}</span>
                  <span className="absolute top-0 bottom-0 right-0 px-4 py-3">
                    <button onClick={() => setShowUpgradeModal(true)} className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600">
                      {t('dashboard.planStatus.limitReached.upgradeButton')}
                    </button>
                  </span>
                </div>
              )}

              {/* Stats Cards */}
              {planLimits && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-10">
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="text-gray-600 text-sm mb-1">{t('dashboard.stats.queriesToday.label')}</div>
                    <div className="text-3xl font-bold text-blue-600">{planLimits.queries_used_today}</div>
                    <div className="text-gray-500 text-sm">{t('dashboard.stats.queriesToday.helpText')}</div>
                  </div>
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="text-gray-600 text-sm mb-1">{t('dashboard.stats.totalJobs.label')}</div>
                    <div className="text-3xl font-bold text-blue-600">{jobs.length}</div>
                    <div className="text-gray-500 text-sm">{t('dashboard.stats.totalJobs.helpText')}</div>
                  </div>
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="text-gray-600 text-sm mb-1">{t('dashboard.stats.crmLeads.label')}</div>
                    <div className="text-3xl font-bold text-blue-600">{leads.length}</div>
                    <div className="text-gray-500 text-sm">{t('dashboard.stats.crmLeads.helpText')}</div>
                  </div>
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="text-gray-600 text-sm mb-1">{t('dashboard.stats.plan.label')}</div>
                    <div className="text-3xl font-bold text-blue-600">{planLimits.plan_name?.toUpperCase() || 'FREE'}</div>
                    <div className="text-gray-500 text-sm">{planLimits.subscription_status}</div>
                  </div>
                </div>
              )}

              {/* API Key Management (Pro/Business) */}
              {user && (user.plan === 'pro' || user.plan === 'business') && (
                <div className="bg-white rounded-lg shadow p-6 mb-8">
                  <h2 className="text-lg font-semibold text-blue-600 mb-2">{t('dashboard.apiKeyManagement.title')}</h2>
                  <p className="text-gray-600 text-sm mb-4">{t('dashboard.apiKeyManagement.description')}</p>
                  {apiKeyLoading ? (
                    <div className="flex justify-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {newApiKey && (
                        <div className="bg-yellow-100 rounded-md p-4">
                          <h3 className="font-bold text-sm">{t('dashboard.apiKeyManagement.newApiKey.title')}</h3>
                          <div className="flex items-center gap-2 mt-2">
                            <span className="font-mono text-sm">{newApiKey}</span>
                            <button onClick={() => {navigator.clipboard.writeText(newApiKey); showToast({ title: 'Copied to clipboard', status: 'success' });}} className="bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded text-sm">
                              <Copy size={16} />
                            </button>
                          </div>
                          <p className="text-xs text-red-500 mt-2">{t('dashboard.apiKeyManagement.newApiKey.warning')}</p>
                        </div>
                      )}
                      {apiKeyInfo && apiKeyInfo.has_api_key && !newApiKey && (
                        <div className="bg-white rounded-md p-4 border border-gray-200">
                          <h3 className="font-bold text-sm">{t('dashboard.apiKeyManagement.activeApiKey.title')}</h3>
                          <p className="text-xs text-gray-500">{t('dashboard.apiKeyManagement.activeApiKey.createdAt')}: {apiKeyInfo.created_at ? new Date(apiKeyInfo.created_at).toLocaleString() : '-'}</p>
                          <p className="text-xs text-gray-500">{t('dashboard.apiKeyManagement.activeApiKey.lastUsed')}: {apiKeyInfo.last_used ? new Date(apiKeyInfo.last_used).toLocaleString() : '-'}</p>
                        </div>
                      )}
                      {!apiKeyInfo?.has_api_key && !newApiKey && (
                        <p className="text-gray-500">{t('dashboard.apiKeyManagement.noApiKey')}</p>
                      )}
                      <div className="flex gap-2">
                        <button onClick={handleCreateApiKey} className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 disabled:opacity-50" disabled={!!apiKeyInfo?.has_api_key}>
                          {t('dashboard.apiKeyManagement.generateApiKeyButton')}
                        </button>
                        <button onClick={handleRevokeApiKey} className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600 disabled:opacity-50" disabled={!apiKeyInfo?.has_api_key}>
                          {t('dashboard.apiKeyManagement.revokeApiKeyButton')}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Support/Contact Section */}
              <div className="bg-white rounded-lg shadow p-6 mb-8">
                <div className="flex justify-between items-center mb-2">
                  <h2 className="text-lg font-semibold text-blue-600">{t('dashboard.supportContact.title')}</h2>
                  <button onClick={() => setSupportModalOpen(true)} className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600">
                    {t('dashboard.supportContact.contactSupportButton')}
                  </button>
                </div>
                {supportLoading ? (
                  <div className="flex justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <p className="text-gray-600 text-sm">{t('dashboard.supportContact.availableOptions')}</p>
                    <div className="flex flex-wrap gap-2">
                      {supportOptions?.support?.map((opt: string) => (
                        <span key={opt} className={`px-2 py-1 rounded-full text-xs font-semibold ${opt === 'phone' ? 'bg-green-100 text-green-800' : opt === 'email' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}`}>
                          {opt?.replace('_', ' ')?.toUpperCase() || opt}
                        </span>
                      ))}
                    </div>
                    {supportOptions?.priority && <span className="px-2 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800">{t('dashboard.supportContact.priorityBadge')}</span>}
                  </div>
                )}
              </div>

              {/* Saved Searches Section */}
              <div className="bg-white rounded-lg shadow p-4 mb-6">
                <div className="flex justify-between items-center mb-2">
                  <h2 className="text-sm font-semibold text-blue-600">{t('dashboard.savedSearches.title')}</h2>
                  <button onClick={() => setSavedQueryModalOpen(true)} className="bg-blue-500 text-white px-2 py-1 rounded text-xs hover:bg-blue-600">
                    {t('dashboard.savedSearches.saveTemplateButton')}
                  </button>
                </div>
                {(savedQueries || []).length === 0 ? (
                  <p className="text-gray-500">{t('dashboard.savedSearches.noSavedSearches')}</p>
                ) : (
                  <div className="space-y-2">
                    {(savedQueries || []).map((q) => (
                      <div key={q.id} className="flex items-center gap-2">
                        <button onClick={() => handleUseTemplate(q)} className="bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded text-xs">
                          {q.name}
                        </button>
                        <button onClick={() => { setEditingQuery(q); setTemplateName(q.name); setQueries(q.queries.join('\n')); setSavedQueryModalOpen(true); }} className="bg-yellow-500 text-white px-2 py-1 rounded text-xs hover:bg-yellow-600">
                          {t('dashboard.savedSearches.editButton')}
                        </button>
                        <button onClick={() => handleDeleteTemplate(q.id)} className="bg-red-500 text-white px-2 py-1 rounded text-xs hover:bg-red-600">
                          {t('dashboard.savedSearches.deleteButton')}
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex flex-col sm:flex-row gap-8">
                {/* Left: Jobs List and Create Job */}
                <div className="flex-1 min-w-[320px]">
                  <div className="flex flex-col gap-8">
                    <div>
                      <h2 className="text-2xl font-bold text-blue-600 mb-4">{t('dashboard.dashboardSection.title')}</h2>
                      <p className="text-gray-600">{t('dashboard.dashboardSection.description')}</p>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                      <div className="flex flex-col gap-4">
                        <h2 className="text-lg font-semibold text-blue-600 mb-4">{t('dashboard.createNewJob.title')}</h2>
                        <p className="text-gray-600 text-sm">
                          {t('dashboard.createNewJob.description')}
                        </p>
                        <textarea
                          value={queries}
                          onChange={(e) => setQueries(e.target.value)}
                          placeholder={t('dashboard.createNewJob.placeholder')}
                          className="w-full min-h-[120px] resize-vertical mb-4 border border-gray-300 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                          disabled={planLimits ? planLimits.queries_remaining_today <= 0 : false}
                        />
                        <button
                          onClick={createJob}
                          disabled={planLimits ? planLimits.queries_remaining_today <= 0 : false}
                          className="w-full bg-blue-500 text-white px-4 py-2 rounded font-semibold hover:bg-blue-600 disabled:opacity-50"
                        >
                          {planLimits && planLimits.queries_remaining_today <= 0 
                            ? `${t('dashboard.createNewJob.dailyLimitReached', { limit: planLimits.max_queries_per_day })}` 
                            : t('dashboard.createNewJob.createJobButton')}
                        </button>
                      </div>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                      <h2 className="text-lg font-semibold text-blue-600 mb-4">{t('dashboard.yourJobs.title')}</h2>
                      {jobs.length === 0 ? (
                        <p className="text-gray-500">{t('dashboard.yourJobs.noJobsCreated')}</p>
                      ) : (
                        <div className="flex flex-col gap-4">
                          {/* Bulk Actions for Jobs */}
                          {jobs.length > 0 && (
                            <div className="flex gap-2 mb-2">
                              <button onClick={toggleAllJobs} className="bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded text-xs">
                                {selectedJobIds.length === jobs.length ? t('dashboard.yourJobs.unselectAll') : t('dashboard.yourJobs.selectAll')}
                              </button>
                              <button onClick={() => handleBulkExportJobs('csv')} className="bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded text-xs">
                                {t('dashboard.yourJobs.exportCsvButton')}
                              </button>
                              <button onClick={() => handleBulkExportJobs('json')} className="bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded text-xs">
                                {t('dashboard.yourJobs.exportJsonButton')}
                              </button>
                              <button onClick={handleBulkDeleteJobs} className="bg-red-500 text-white px-2 py-1 rounded text-xs hover:bg-red-600">
                                {t('dashboard.yourJobs.deleteButton')}
                              </button>
                            </div>
                          )}
                          {jobs.map((job) => (
                            <div
                              key={job.id}
                              className="p-4 border border-gray-200 rounded-md bg-blue-50 cursor-pointer hover:bg-blue-100 transition-colors"
                              onClick={() => {
                                setSelectedJob(job);
                                fetchJobResults(Number(job.id));
                              }}
                            >
                              <div className="flex justify-between items-center mb-2">
                                <span className="font-bold">{t('dashboard.jobItem.jobId', { id: job.id })}</span>
                                <span className={`px-2 py-1 rounded text-xs font-semibold ${getStatusColor(job.status) === 'green' ? 'bg-green-100 text-green-800' : getStatusColor(job.status) === 'red' ? 'bg-red-100 text-red-800' : getStatusColor(job.status) === 'yellow' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'}`}>
                                  {job.status}
                                </span>
                              </div>
                              <p className="text-gray-600 text-sm">{job.queries.join(', ')}</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                {/* Right: GMap and Results */}
                <div className="flex-1 min-w-[400px]">
                  <div className="flex flex-col gap-6">
                    {/* GMap Iframe */}
                    <div className="rounded-lg overflow-hidden border border-gray-200 min-h-[320px] shadow-md mb-6">
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
                        <div className="p-8 text-center text-gray-500">{t('dashboard.gmapIframe.noQueryMessage')}</div>
                      )}
                    </div>
                    {/* Results Table */}
                    <div className="overflow-x-auto">
                      <h2 className="text-lg font-semibold text-blue-600 mb-4">{t('dashboard.searchResults.title')}</h2>
                      {/* Advanced Filters (Pro/Business only) */}
                      {user && (user.plan === 'pro' || user.plan === 'business') && (
                        <div className="mb-4">
                          <div className="flex flex-wrap gap-4 mb-2">
                            <p className="text-gray-600 text-sm">{t('dashboard.searchResults.advancedFilters')}</p>
                            <select 
                              className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                              value={filters.status} 
                              onChange={e => setFilters(f => ({ ...f, status: e.target.value }))}
                            >
                              <option value="completed">{t('dashboard.searchResults.statusOptions.completed')}</option>
                              <option value="pending">{t('dashboard.searchResults.statusOptions.pending')}</option>
                              <option value="failed">{t('dashboard.searchResults.statusOptions.failed')}</option>
                            </select>
                            <input 
                              placeholder={t('dashboard.searchResults.companyPlaceholder')} 
                              className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" 
                              value={filters.company} 
                              onChange={e => setFilters(f => ({ ...f, company: e.target.value }))} 
                            />
                            <input 
                              type="date" 
                              className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" 
                              value={filters.dateFrom} 
                              onChange={e => setFilters(f => ({ ...f, dateFrom: e.target.value }))} 
                            />
                            <input 
                              type="date" 
                              className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" 
                              value={filters.dateTo} 
                              onChange={e => setFilters(f => ({ ...f, dateTo: e.target.value }))} 
                            />
                            <button onClick={() => selectedJob && fetchJobResults(Number(selectedJob.id), filters)} className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600">
                              {t('dashboard.searchResults.applyFiltersButton')}
                            </button>
                            <button onClick={() => { setFilters({ status: '', company: '', dateFrom: '', dateTo: '' }); selectedJob && fetchJobResults(Number(selectedJob.id), {}); }} className="bg-gray-200 hover:bg-gray-300 px-3 py-1 rounded text-sm">
                              {t('dashboard.searchResults.resetFiltersButton')}
                            </button>
                          </div>
                        </div>
                      )}
                      {resultsLoading ? (
                        <div className="flex justify-center py-8">
                          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                        </div>
                      ) : jobResults.length === 0 ? (
                        <p className="text-gray-500">{t('dashboard.searchResults.noResults')}</p>
                      ) : (
                        <div className="overflow-x-auto">
                          <table className="min-w-full border border-gray-200">
                            <thead className="bg-gray-50">
                              <tr>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  <input type="checkbox" checked={selectedJobIds.length === jobs.length} onChange={toggleAllJobs} />
                                </th>
                                {Object.keys(jobResults[0]).map((key) => (
                                  <th key={key} className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{key}</th>
                                ))}
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('dashboard.searchResults.actions')}</th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {jobResults.map((row, idx) => (
                                <tr key={idx} className="hover:bg-gray-50 transition-colors">
                                  <td className="px-4 py-2">
                                    <input type="checkbox" checked={selectedJobIds.includes(row.job_id)} onChange={() => toggleJobSelection(row.job_id)} />
                                  </td>
                                  {Object.values(row).map((val, i) => (
                                    <td key={i} className="px-4 py-2 text-sm text-gray-900">{String(val)}</td>
                                  ))}
                                  <td className="px-4 py-2">
                                    <button onClick={() => addLeadToCRM(row)} className="bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded text-xs">
                                      {t('dashboard.searchResults.addCrmButton')}
                                    </button>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                      {/* Export Buttons by Plan */}
                      {selectedJob && selectedJob.status === 'completed' && (
                        <div className="flex gap-2 mt-4">
                          {getAllowedExportFormats().map((format) => (
                            <button
                              key={format}
                              className={`px-3 py-1 rounded text-sm font-medium ${format === 'csv' ? 'bg-green-500 text-white hover:bg-green-600' : format === 'json' ? 'bg-blue-500 text-white hover:bg-blue-600' : format === 'xlsx' ? 'bg-purple-500 text-white hover:bg-purple-600' : 'bg-orange-500 text-white hover:bg-orange-600'}`}
                              onClick={() => handleExport(format)}
                            >
                              {t(`dashboard.searchResults.exportFormats.${format?.toUpperCase() || format}`)}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Upgrade Modal */}
      {showUpgradeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg max-w-lg w-full p-6 relative">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl font-bold"
              onClick={() => setShowUpgradeModal(false)}
              aria-label="Close"
            >
              &times;
            </button>
            <h2 className="text-xl font-bold mb-4 text-blue-600">{t('dashboard.upgradeModal.title')}</h2>
            <p className="mb-4 text-gray-700">{t('dashboard.upgradeModal.choosePlan')}</p>
            <div className="space-y-4">
              <div className="p-4 border border-gray-200 rounded-md bg-gray-50">
                <div className="font-semibold text-blue-600 mb-2">{t('dashboard.upgradeModal.freePlan.title')}</div>
                <div className="text-sm text-gray-700">{t('dashboard.upgradeModal.freePlan.description')}</div>
                <div className="text-xs text-gray-500 mt-1">{t('dashboard.upgradeModal.freePlan.included')}</div>
              </div>
              <div className="p-4 border-2 border-blue-400 rounded-md bg-blue-50">
                <div className="font-semibold text-blue-700 mb-2">{t('dashboard.upgradeModal.proPlan.title')}</div>
                <div className="text-sm text-gray-700">{t('dashboard.upgradeModal.proPlan.description')}</div>
                <div className="text-xs text-gray-500 mt-1">{t('dashboard.upgradeModal.proPlan.bestFor')}</div>
              </div>
              <div className="p-4 border-2 border-green-400 rounded-md bg-green-50">
                <div className="font-semibold text-green-700 mb-2">{t('dashboard.upgradeModal.businessPlan.title')}</div>
                <div className="text-sm text-gray-700">{t('dashboard.upgradeModal.businessPlan.description')}</div>
                <div className="text-xs text-gray-500 mt-1">{t('dashboard.upgradeModal.businessPlan.for')}</div>
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-6">
              <button
                className="px-4 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300"
                onClick={() => setShowUpgradeModal(false)}
              >
                {t('dashboard.upgradeModal.cancelButton')}
              </button>
              <button
                className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
              >
                {t('dashboard.upgradeModal.upgradeNowButton')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Lead Modal */}
      {leadModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full p-6 relative">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl font-bold"
              onClick={() => setLeadModalOpen(false)}
              aria-label="Close"
            >
              &times;
            </button>
            <h2 className="text-xl font-bold mb-4 text-blue-600">{t('dashboard.addLeadModal.title')}</h2>
            <form onSubmit={e => { e.preventDefault(); createNewLead(); }}>
              <div className="flex flex-col gap-3">
                <input
                  type="text"
                  placeholder={t('dashboard.addLeadModal.namePlaceholder')}
                  value={newLead.name}
                  onChange={e => setNewLead({ ...newLead, name: e.target.value })}
                  className="input-modern border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
                <input
                  type="email"
                  placeholder={t('dashboard.addLeadModal.emailPlaceholder')}
                  value={newLead.email}
                  onChange={e => setNewLead({ ...newLead, email: e.target.value })}
                  className="input-modern border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
                <input
                  type="text"
                  placeholder={t('dashboard.addLeadModal.phonePlaceholder')}
                  value={newLead.phone}
                  onChange={e => setNewLead({ ...newLead, phone: e.target.value })}
                  className="input-modern border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="text"
                  placeholder={t('dashboard.addLeadModal.companyPlaceholder')}
                  value={newLead.company}
                  onChange={e => setNewLead({ ...newLead, company: e.target.value })}
                  className="input-modern border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="text"
                  placeholder={t('dashboard.addLeadModal.websitePlaceholder')}
                  value={newLead.website}
                  onChange={e => setNewLead({ ...newLead, website: e.target.value })}
                  className="input-modern border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <textarea
                  placeholder={t('dashboard.addLeadModal.notesPlaceholder')}
                  value={newLead.notes}
                  onChange={e => setNewLead({ ...newLead, notes: e.target.value })}
                  className="input-modern border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[80px]"
                />
              </div>
              <div className="flex justify-end gap-2 mt-6">
                <button
                  type="button"
                  className="px-4 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300"
                  onClick={() => setLeadModalOpen(false)}
                >
                  {t('dashboard.addLeadModal.cancelButton')}
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
                >
                  {t('dashboard.addLeadModal.addLeadButton')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Support Modal */}
      {supportModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full p-6 relative">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl font-bold"
              onClick={() => setSupportModalOpen(false)}
              aria-label="Close"
            >
              &times;
            </button>
            <h2 className="text-xl font-bold mb-4 text-blue-600">{t('dashboard.supportModal.title')}</h2>
            <form onSubmit={e => { e.preventDefault(); handleSupportSubmit(); }}>
              <div className="flex flex-col gap-3">
                <input
                  type="text"
                  placeholder={t('dashboard.supportModal.subjectPlaceholder')}
                  value={supportForm.subject}
                  onChange={e => setSupportForm({ ...supportForm, subject: e.target.value })}
                  className="input-modern border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
                <textarea
                  placeholder={t('dashboard.supportModal.messagePlaceholder')}
                  value={supportForm.message}
                  onChange={e => setSupportForm({ ...supportForm, message: e.target.value })}
                  className="input-modern border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[100px]"
                  required
                />
                {supportOptions?.support?.includes('phone') && (
                  <input
                    type="text"
                    placeholder={t('dashboard.supportModal.phonePlaceholder')}
                    value={supportForm.phone}
                    onChange={e => setSupportForm({ ...supportForm, phone: e.target.value })}
                    className="input-modern border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                )}
              </div>
              <div className="flex justify-end gap-2 mt-6">
                <button
                  type="button"
                  className="px-4 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300"
                  onClick={() => setSupportModalOpen(false)}
                >
                  {t('dashboard.supportModal.cancelButton')}
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
                  disabled={supportLoading}
                >
                  {supportLoading ? t('dashboard.supportModal.sendingButton') : t('dashboard.supportModal.sendButton')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Saved Query Modal */}
      {savedQueryModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full p-6 relative">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl font-bold"
              onClick={() => { setSavedQueryModalOpen(false); setEditingQuery(null); setTemplateName(''); }}
              aria-label="Close"
            >
              &times;
            </button>
            <h2 className="text-xl font-bold mb-4 text-blue-600">
              {editingQuery ? t('dashboard.savedQueryModal.editTemplateTitle') : t('dashboard.savedQueryModal.saveSearchTitle')}
            </h2>
            <form onSubmit={e => { e.preventDefault(); editingQuery ? handleUpdateTemplate() : handleSaveTemplate(); }}>
              <div className="flex flex-col gap-3">
                <input
                  type="text"
                  placeholder={t('dashboard.savedQueryModal.templateNamePlaceholder')}
                  value={templateName}
                  onChange={e => setTemplateName(e.target.value)}
                  className="input-modern border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
                <textarea
                  value={queries}
                  onChange={e => setQueries(e.target.value)}
                  placeholder={t('dashboard.savedQueryModal.enterQueriesPlaceholder')}
                  className="input-modern border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[100px]"
                  required
                />
              </div>
              <div className="flex justify-end gap-2 mt-6">
                <button
                  type="button"
                  className="px-4 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300"
                  onClick={() => { setSavedQueryModalOpen(false); setEditingQuery(null); setTemplateName(''); }}
                >
                  {t('dashboard.savedQueryModal.cancelButton')}
                </button>
                <button
                  type="submit"
                  className={`px-4 py-2 rounded ${editingQuery ? 'bg-yellow-500 hover:bg-yellow-600' : 'bg-blue-600 hover:bg-blue-700'} text-white`}
                >
                  {editingQuery ? t('dashboard.savedQueryModal.updateButton') : t('dashboard.savedQueryModal.saveButton')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Notifications Modal */}
      {notifModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full p-6 relative">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl font-bold"
              onClick={() => setNotifModalOpen(false)}
              aria-label="Close"
            >
              &times;
            </button>
            <h2 className="text-xl font-bold mb-4 text-blue-600">{t('dashboard.notificationsModal.title')}</h2>
            <div className="flex flex-col gap-2">
              {(notifications || []).length === 0 ? (
                <p className="text-gray-500">{t('dashboard.notificationsModal.noNotifications')}</p>
              ) : (notifications || []).map((n) => (
                <div key={n.id} className="p-3 bg-yellow-100 rounded-md cursor-pointer" onClick={() => handleMarkRead(n.id)}>
                  <p className="font-bold">{n.type}</p>
                  <p>{n.message}</p>
                  <p className="text-xs text-gray-500">{new Date(n.created_at).toLocaleString()}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Share Job Modal */}
      {shareJobModal.open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full p-6 relative">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl font-bold"
              onClick={() => setShareJobModal({ open: false, job: null, link: null })}
              aria-label="Close"
            >
              &times;
            </button>
            <h2 className="text-xl font-bold mb-4 text-blue-600">{t('dashboard.shareJobModal.shareableLinkTitle')}</h2>
            <p className="mb-2 text-gray-700">{t('dashboard.shareJobModal.shareableLinkText')}</p>
            <input
              value={shareJobModal.link || ''}
              readOnly
              className="w-full border border-gray-300 rounded px-3 py-2 mb-4 font-mono text-sm bg-gray-50"
            />
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => {navigator.clipboard.writeText(shareJobModal.link || ''); showToast({ title: 'Copied', status: 'success' });}}
                className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
              >
                {t('dashboard.shareJobModal.copyLinkButton')}
              </button>
              <button
                onClick={() => handleUnshareJob(shareJobModal.job!)}
                className="px-4 py-2 rounded bg-red-500 text-white hover:bg-red-600"
              >
                {t('dashboard.shareJobModal.disableLinkButton')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Share Lead Modal */}
      {shareLeadModal.open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full p-6 relative">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl font-bold"
              onClick={() => setShareLeadModal({ open: false, lead: null, link: null })}
              aria-label="Close"
            >
              &times;
            </button>
            <h2 className="text-xl font-bold mb-4 text-blue-600">{t('dashboard.shareLeadModal.shareableLinkTitle')}</h2>
            <p className="mb-2 text-gray-700">{t('dashboard.shareLeadModal.shareableLinkText')}</p>
            <input
              value={shareLeadModal.link || ''}
              readOnly
              className="w-full border border-gray-300 rounded px-3 py-2 mb-4 font-mono text-sm bg-gray-50"
            />
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => {navigator.clipboard.writeText(shareLeadModal.link || ''); showToast({ title: 'Copied', status: 'success' });}}
                className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
              >
                {t('dashboard.shareLeadModal.copyLinkButton')}
              </button>
              <button
                onClick={() => handleUnshareLead(shareLeadModal.lead!)}
                className="px-4 py-2 rounded bg-red-500 text-white hover:bg-red-600"
              >
                {t('dashboard.shareLeadModal.disableLinkButton')}
              </button>
            </div>
          </div>
        </div>
      )}
      {fab}
    </div>
  );
};
