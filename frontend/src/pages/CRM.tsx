import React, { useState, useEffect } from 'react';
import {
  Button,
  Badge,
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
  TableFooter,
  TablePagination,
  Input,
  Select,
  useDisclosure,
  FormControl,
  FormLabel,
  Textarea,
  Spinner,
  useToast,
  HStack,
  VStack,
  Flex,
  Tooltip,
  IconButton,
} from '../components/ui';
import { AddIcon, EditIcon, DeleteIcon, ViewIcon } from '@chakra-ui/icons';
import * as api from '../api';
import { LeadKanban, KanbanLead, LeadStage } from '../components/LeadKanban';
import { AIAssistantSidebar } from '../components/AIAssistantSidebar';
import { useQuery, useMutation, gql } from '@apollo/client';
import { useTranslation } from 'react-i18next';

interface Lead {
  id: number;
  name: string;
  email: string;
  phone?: string;
  company?: string;
  tag?: string;
  notes?: string;
  status: string;
  source?: string;
  created_at: string;
  updated_at: string;
}

interface LeadStats {
  total_leads: number;
  new_leads: number;
  contacted_leads: number;
  qualified_leads: number;
  converted_leads: number;
  conversion_rate: number;
}

const LEADS_QUERY = gql`
  query Leads {
    leads {
      id
      name
      email
      phone
      company
      tag
      notes
      status
      source
      created_at
      updated_at
    }
  }
`;

const ANALYTICS_QUERY = gql`
  query Analytics {
    analytics {
      totalLeads
      leadsByStatus
      conversionRate
    }
  }
`;

const CREATE_LEAD = gql`
  mutation CreateLead($name: String!, $email: String!, $phone: String, $company: String, $tag: String, $notes: String, $status: String, $source: String) {
    createLead(name: $name, email: $email, phone: $phone, company: $company, tag: $tag, notes: $notes, status: $status, source: $source) {
      lead { id name email status }
    }
  }
`;

const UPDATE_LEAD = gql`
  mutation UpdateLead($leadId: Int!, $name: String, $email: String, $phone: String, $company: String, $tag: String, $notes: String, $status: String, $source: String) {
    updateLead(leadId: $leadId, name: $name, email: $email, phone: $phone, company: $company, tag: $tag, notes: $notes, status: $status, source: $source) {
      lead { id name email status }
    }
  }
`;

const DELETE_LEAD = gql`
  mutation DeleteLead($leadId: Int!) {
    deleteLead(leadId: $leadId) { ok }
  }
`;

const CRM: React.FC = () => {
  const { t } = useTranslation();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [stats, setStats] = useState<LeadStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(false);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [filterStatus, setFilterStatus] = useState('');
  const [filterTag, setFilterTag] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();

  const { data: leadsData, loading: leadsLoading, refetch: refetchLeads } = useQuery(LEADS_QUERY);
  const { data: analyticsData, loading: statsLoading, refetch: refetchStats } = useQuery(ANALYTICS_QUERY);
  const [createLead] = useMutation(CREATE_LEAD);
  const [updateLeadMutation] = useMutation(UPDATE_LEAD);
  const [deleteLeadMutation] = useMutation(DELETE_LEAD);

  useEffect(() => {
    if (leadsData && leadsData.leads) setLeads(leadsData.leads);
  }, [leadsData]);
  useEffect(() => {
    if (analyticsData && analyticsData.analytics) {
      setStats({
        total_leads: analyticsData.analytics.totalLeads,
        new_leads: analyticsData.analytics.leadsByStatus?.new || 0,
        contacted_leads: analyticsData.analytics.leadsByStatus?.contacted || 0,
        qualified_leads: analyticsData.analytics.leadsByStatus?.qualified || 0,
        converted_leads: analyticsData.analytics.leadsByStatus?.converted || 0,
        conversion_rate: analyticsData.analytics.conversionRate * 100,
      });
    }
  }, [analyticsData]);

  const addLead = async (leadData: Partial<Lead>) => {
    try {
      await createLead({ variables: leadData });
      toast({ title: t('Success'), description: t('Lead added successfully'), status: 'success', duration: 3000 });
      refetchLeads();
      refetchStats();
      onClose();
    } catch (error: any) {
      toast({ title: t('Error'), description: error.message, status: 'error', duration: 3000 });
    }
  };

  const updateLead = async (leadId: number, leadData: Partial<Lead>) => {
    try {
      await updateLeadMutation({ variables: { leadId, ...leadData } });
      toast({ title: t('Success'), description: t('Lead updated successfully'), status: 'success', duration: 3000 });
      refetchLeads();
      refetchStats();
      onClose();
    } catch (error: any) {
      toast({ title: t('Error'), description: error.message, status: 'error', duration: 3000 });
    }
  };

  const deleteLead = async (leadId: number) => {
    if (!confirm(t('Are you sure you want to delete this lead?'))) return;
    try {
      await deleteLeadMutation({ variables: { leadId } });
      toast({ title: t('Success'), description: t('Lead deleted successfully'), status: 'success', duration: 3000 });
      refetchLeads();
      refetchStats();
    } catch (error: any) {
      toast({ title: t('Error'), description: error.message, status: 'error', duration: 3000 });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new': return 'blue';
      case 'contacted': return 'yellow';
      case 'qualified': return 'orange';
      case 'converted': return 'green';
      default: return 'gray';
    }
  };

  const filteredLeads = leads.filter(lead => {
    const matchesStatus = !filterStatus || lead.status === filterStatus;
    const matchesTag = !filterTag || lead.tag === filterTag;
    const matchesSearch = !searchTerm || 
      lead.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (lead.company && lead.company.toLowerCase().includes(searchTerm.toLowerCase()));
    
    return matchesStatus && matchesTag && matchesSearch;
  });

  const uniqueTags = [...new Set(leads.map(lead => lead.tag).filter(Boolean))];

  // Map CRM lead status to Kanban stage
  const statusToStage = (status: string): LeadStage => {
    if (status === 'converted') return 'converted';
    if (status === 'contacted' || status === 'qualified') return 'in_progress';
    return 'to_contact';
  };
  const stageToStatus = (stage: LeadStage): string => {
    if (stage === 'converted') return 'converted';
    if (stage === 'in_progress') return 'contacted';
    return 'new';
  };
  const kanbanLeads: KanbanLead[] = leads.map(l => ({
    id: l.id.toString(),
    name: l.name,
    email: l.email,
    company: l.company,
    stage: statusToStage(l.status),
  }));
  const handleStageChange = (leadId: string, newStage: LeadStage) => {
    const lead = leads.find(l => l.id.toString() === leadId);
    if (lead) {
      updateLead(lead.id, { status: stageToStatus(newStage) });
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-800" data-tour="crm-main">
      <div className="max-w-7xl mx-auto py-8 px-4" data-tour="crm-content">
        <h1 className="text-3xl font-bold mb-6 gradient-text" data-tour="crm-title">{t('CRM Leads')}</h1>
        <div className="flex justify-between items-center mb-4" data-tour="crm-actions">
          <Button colorScheme="blue" onClick={onOpen} data-tour="crm-add-lead">{t('Add Lead')}</Button>
          <Button colorScheme="green" onClick={handleExportLeads} data-tour="crm-export">{t('Export Leads')}</Button>
        </div>

        {/* Statistics */}
        {stats && (
          <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-4">
            <div>
              <div className="bg-white dark:bg-gray-900 rounded-lg p-4 shadow">
                <span className="text-sm text-gray-500">{t('Total Leads')}</span>
                <span className="text-2xl font-bold">{stats.total_leads}</span>
                <span className="inline-block text-green-500 mr-1">↑</span>
                <span className="text-xs text-gray-400">23.36%</span>
              </div>
            </div>
            <div>
              <div className="bg-white dark:bg-gray-900 rounded-lg p-4 shadow">
                <span className="text-sm text-gray-500">{t('New Leads')}</span>
                <span className="text-2xl font-bold">{stats.new_leads}</span>
                <span className="text-xs text-gray-400">{t('This month')}</span>
              </div>
            </div>
            <div>
              <div className="bg-white dark:bg-gray-900 rounded-lg p-4 shadow">
                <span className="text-sm text-gray-500">{t('Conversion Rate')}</span>
                <span className="text-2xl font-bold">{stats.conversion_rate.toFixed(1)}%</span>
                <span className="inline-block text-green-500 mr-1">↑</span>
                <span className="text-xs text-gray-400">12.5%</span>
              </div>
            </div>
            <div>
              <div className="bg-white dark:bg-gray-900 rounded-lg p-4 shadow">
                <span className="text-sm text-gray-500">{t('Converted')}</span>
                <span className="text-2xl font-bold">{stats.converted_leads}</span>
                <span className="text-xs text-gray-400">{t('This month')}</span>
              </div>
            </div>
          </div>
        )}

        {/* Filters and Actions */}
        <div className="bg-white dark:bg-gray-900 rounded-lg p-4 shadow" data-tour="crm-filters">
          <div className="flex flex-col sm:flex-row items-center gap-4 mb-4">
            <Input
              placeholder={t('Search leads...')}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              maxW="300px"
            />
            <Select
              placeholder={t('Filter by status')}
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              maxW="200px"
            >
              <option value="new">{t('New')}</option>
              <option value="contacted">{t('Contacted')}</option>
              <option value="qualified">{t('Qualified')}</option>
              <option value="converted">{t('Converted')}</option>
            </Select>
            <Select
              placeholder={t('Filter by tag')}
              value={filterTag}
              onChange={(e) => setFilterTag(e.target.value)}
              maxW="200px"
            >
              {uniqueTags.map(tag => (
                <option key={tag} value={tag}>{tag}</option>
              ))}
            </Select>
            <Button
              leftIcon={<AddIcon />}
              colorScheme="blue"
              onClick={() => {
                setSelectedLead(null);
                onOpen();
              }}
            >
              {t('Add Lead')}
            </Button>
          </div>
        </div>

        {/* Leads Table */}
        <div className="bg-white dark:bg-gray-900 rounded-lg p-4 shadow" data-tour="crm-leads-table">
          <h2 className="text-xl font-bold mb-4">{t('Leads')}</h2>
          {loading ? (
            <Flex justify="center" py={8}>
              <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            </Flex>
          ) : filteredLeads.length === 0 ? (
            <div className="flex items-center p-4 mb-4 text-blue-800 rounded-lg bg-blue-50 dark:bg-gray-800 dark:text-blue-400">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><path d="M18 10A8 8 0 11..." /></svg>
              {t('No leads found. Add your first lead to get started!')}
            </div>
          ) : (
            <Table variant="simple">
              <TableHeader>
                <TableRow>
                  <TableHead>{t('Name')}</TableHead>
                  <TableHead>{t('Email')}</TableHead>
                  <TableHead>{t('Company')}</TableHead>
                  <TableHead>{t('Status')}</TableHead>
                  <TableHead>{t('Tag')}</TableHead>
                  <TableHead>{t('Created')}</TableHead>
                  <TableHead>{t('Actions')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredLeads.map((lead) => (
                  <TableRow key={lead.id}>
                    <TableCell fontWeight="bold">{lead.name}</TableCell>
                    <TableCell>{lead.email}</TableCell>
                    <TableCell>{lead.company || '-'}</TableCell>
                    <TableCell>
                      <Badge colorScheme={getStatusColor(lead.status)}>
                        {t(lead.status)}
                      </Badge>
                    </TableCell>
                    <TableCell>{lead.tag || '-'}</TableCell>
                    <TableCell>{new Date(lead.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <HStack spacing={2}>
                        <Tooltip label={t('View Details')}>
                          <IconButton
                            aria-label={t('View lead')}
                            icon={<ViewIcon />}
                            size="sm"
                            variant="ghost"
                            onClick={() => {
                              setSelectedLead(lead);
                              onOpen();
                            }}
                          />
                        </Tooltip>
                        <Tooltip label={t('Edit Lead')}>
                          <div className="relative group">
                            <button className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700" aria-label={t('Edit Lead')} onClick={() => {
                              setSelectedLead(lead);
                              onOpen();
                            }}>
                              <EditIcon />
                            </button>
                            <span className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded py-1 px-2 z-10">
                              {t('Edit Lead')}
                            </span>
                          </div>
                        </Tooltip>
                        <Tooltip label={t('Delete Lead')}>
                          <div className="relative group">
                            <button className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700" aria-label={t('Delete Lead')} onClick={() => deleteLead(lead.id)}>
                              <DeleteIcon />
                            </button>
                            <span className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded py-1 px-2 z-10">
                              {t('Delete Lead')}
                            </span>
                          </div>
                        </Tooltip>
                      </HStack>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </div>

      {/* Add/Edit Lead Modal */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg w-full max-w-lg p-6 relative">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-600"
              onClick={onClose}
              aria-label="Close"
            >
              ×
            </button>
            <h2 className="text-xl font-semibold mb-4">
              {selectedLead ? t('Edit Lead') : t('Add New Lead')}
            </h2>
            <LeadForm lead={selectedLead} onSubmit={selectedLead ? updateLead : addLead} onCancel={onClose} />
          </div>
        </div>
      )}
    </div>
  );
};

// Lead Form Component
interface LeadFormProps {
  lead?: Lead | null;
  onSubmit: (data: Partial<Lead>) => void;
  onCancel: () => void;
}

const LeadForm: React.FC<LeadFormProps> = ({ lead, onSubmit, onCancel }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    name: lead?.name || '',
    email: lead?.email || '',
    phone: lead?.phone || '',
    company: lead?.company || '',
    tag: lead?.tag || '',
    notes: lead?.notes || '',
    status: lead?.status || 'new',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (lead) {
      onSubmit(lead.id, formData);
    } else {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-4">
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">
            {t('Name')}
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">
            {t('Email')}
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">
            {t('Phone')}
          </label>
          <input
            type="tel"
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">
            {t('Company')}
          </label>
          <input
            type="text"
            value={formData.company}
            onChange={(e) => setFormData({ ...formData, company: e.target.value })}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">
            {t('Tag')}
          </label>
          <input
            type="text"
            value={formData.tag}
            onChange={(e) => setFormData({ ...formData, tag: e.target.value })}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">
            {t('Status')}
          </label>
          <select
            value={formData.status}
            onChange={(e) => setFormData({ ...formData, status: e.target.value })}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="new">{t('New')}</option>
            <option value="contacted">{t('Contacted')}</option>
            <option value="qualified">{t('Qualified')}</option>
            <option value="converted">{t('Converted')}</option>
          </select>
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">
            {t('Notes')}
          </label>
          <textarea
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
        </div>
        
        <HStack spacing={4} w="full">
          <Button type="submit" colorScheme="blue" flex={1}>
            {lead ? t('Update Lead') : t('Add Lead')}
          </Button>
          <Button onClick={onCancel} variant="outline" flex={1}>
            {t('Cancel')}
          </Button>
        </HStack>
      </div>
    </form>
  );
};

export default CRM; 