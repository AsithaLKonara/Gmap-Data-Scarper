/// <reference types="vite/client" />
const API_URL = import.meta.env.VITE_API_URL || '';

let token: string | null = null;

export function setToken(t: string | null) {
  token = t;
}

async function apiFetch(path: string, options: any = {}) {
  const headers: Record<string, string> = options.headers || {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (!(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
  // Add X-Tenant header if available
  let tenantSlug = localStorage.getItem('tenantSlug') || (window as any).tenantSlug;
  if (tenantSlug) headers['X-Tenant'] = tenantSlug;
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });
  if (!res.ok) throw new Error(await res.text());
  if (res.status === 204) return null;
  return res.headers.get('content-type')?.includes('application/json') ? res.json() : res.text();
}

export async function login(email: string, password: string) {
  const data = await apiFetch('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
  return data;
}

export async function register(email: string, password: string) {
  return apiFetch('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function getUser() {
  return apiFetch('/api/auth/user/me');
}

export async function createJob(queries: string[]) {
  return apiFetch('/api/scrape/', {
    method: 'POST',
    body: JSON.stringify({ queries }),
  });
}

export async function getJobStatus(jobId: number) {
  return apiFetch(`/api/scrape/${jobId}/status`);
}

export async function getJobResults(jobId: number) {
  return apiFetch(`/api/scrape/${jobId}/results`);
}

export function getJobCSV(jobId: number) {
  return `${API_URL}/api/scrape/${jobId}/csv`;
}

export async function createPayHereSession(plan: string) {
  const form = new FormData();
  form.append('plan', plan);
  return apiFetch('/api/payhere/create-session', {
    method: 'POST',
    body: form,
    headers: {},
  });
}

// Admin API functions
export async function adminGetUsers({ page = 1, pageSize = 20, email = '', plan = '' } = {}) {
  const params = new URLSearchParams();
  params.append('page', String(page));
  params.append('page_size', String(pageSize));
  if (email) params.append('email', email);
  if (plan) params.append('plan', plan);
  return apiFetch(`/api/admin/users?${params.toString()}`);
}

export async function adminGetJobs({ page = 1, pageSize = 20, userEmail = '', status = '' } = {}) {
  const params = new URLSearchParams();
  params.append('page', String(page));
  params.append('page_size', String(pageSize));
  if (userEmail) params.append('user_email', userEmail);
  if (status) params.append('status', status);
  return apiFetch(`/api/admin/jobs?${params.toString()}`);
}

export async function adminGetStats() {
  return apiFetch('/api/admin/stats');
}

export async function adminGetLogs() {
  return apiFetch('/api/admin/logs');
}

export async function adminBanUser(userId: number) {
  return apiFetch('/api/admin/ban_user', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId }),
  });
}

export async function adminUnbanUser(userId: number) {
  return apiFetch('/api/admin/unban_user', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId }),
  });
}

export async function adminResetPassword(userId: number, newPassword: string) {
  return apiFetch('/api/admin/reset_password', {
    method: 'POST',
    body: JSON.stringify({ 
      user_id: userId, 
      new_password: newPassword 
    }),
  });
}

// Export functions
export function adminExportUsers(format: 'csv' | 'json' = 'csv', filters?: { email?: string; plan?: string }) {
  const params = new URLSearchParams();
  params.append('format', format);
  if (filters?.email) params.append('email', filters.email);
  if (filters?.plan) params.append('plan', filters.plan);
  return `${API_URL}/api/admin/export/users?${params.toString()}`;
}

export function adminExportJobs(format: 'csv' | 'json' = 'csv', filters?: { userEmail?: string; status?: string }) {
  const params = new URLSearchParams();
  params.append('format', format);
  if (filters?.userEmail) params.append('user_email', filters.userEmail);
  if (filters?.status) params.append('status', filters.status);
  return `${API_URL}/api/admin/export/jobs?${params.toString()}`;
}

export async function adminGetAuditLogs({ page = 1, pageSize = 20, action = '', adminEmail = '', targetType = '' } = {}) {
  const params = new URLSearchParams();
  params.append('page', String(page));
  params.append('page_size', String(pageSize));
  if (action) params.append('action', action);
  if (adminEmail) params.append('admin_email', adminEmail);
  if (targetType) params.append('target_type', targetType);
  return apiFetch(`/api/admin/audit-logs?${params.toString()}`);
}

// Analytics API functions
export async function adminGetUserGrowth(days: number = 30) {
  return apiFetch(`/api/admin/analytics/user-growth?days=${days}`);
}

export async function adminGetJobTrends(days: number = 30) {
  return apiFetch(`/api/admin/analytics/job-trends?days=${days}`);
}

export async function adminGetPlanDistribution() {
  return apiFetch('/api/admin/analytics/plan-distribution');
}

export async function adminGetActiveUsers(days: number = 7) {
  return apiFetch(`/api/admin/analytics/active-users?days=${days}`);
}

// Real-time notifications
export function createWebSocketConnection(token: string) {
  const ws = new WebSocket(`ws://localhost:8000/ws/admin`);
  
  ws.onopen = () => {
    console.log('WebSocket connected');
    ws.send(JSON.stringify({ type: 'auth', token }));
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('WebSocket message:', data);
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };
  
  return ws;
}

export async function testNotification() {
  return apiFetch('/api/admin/notifications/test', {
    method: 'POST',
  });
}

// System health monitoring (Admin)
export async function adminGetSystemHealth() {
  return apiFetch('/api/admin/system/health');
}

export async function adminGetSystemPerformance(hours: number = 24) {
  return apiFetch(`/api/admin/system/performance?hours=${hours}`);
}

export async function adminGetRecentSystemLogs(limit: number = 100) {
  return apiFetch(`/api/admin/system/logs/recent?limit=${limit}`);
}

export async function getJobs() {
  return apiFetch('/api/scrape/jobs');
}

// User Profile Management
export async function getUserProfile() {
  return apiFetch('/api/auth/user/me');
}

// Plan Management (Legacy)
export async function upgradePlan(newPlan: string) {
  return apiFetch('/api/scrape/upgrade_plan', {
    method: 'POST',
    body: JSON.stringify({ plan: newPlan }),
  });
}

// CRM/Lead Management
export async function addLeadToCRM(leadData: any) {
  return apiFetch('/api/crm/leads', {
    method: 'POST',
    body: JSON.stringify(leadData),
  });
}

export async function getCRMLeads() {
  return apiFetch('/api/crm/leads');
}

export async function updateCRMLead(leadId: number, leadData: any) {
  return apiFetch(`/api/crm/leads/${leadId}`, {
    method: 'PUT',
    body: JSON.stringify(leadData),
  });
}

export async function deleteCRMLead(leadId: number) {
  return apiFetch(`/api/crm/leads/${leadId}`, {
    method: 'DELETE',
  });
}

export async function enrichLead(leadId: number) {
  return apiFetch(`/api/crm/leads/${leadId}/enrich`, { method: 'POST' });
}

export async function pushLeadToCRM(leadId: number) {
  // Replace with real endpoint if available
  // return apiFetch(`/api/crm/leads/${leadId}/push`, { method: 'POST' });
  return { success: true };
}

// Profile Management
export async function updateUserProfile(profileData: any) {
  return apiFetch('/api/profiles/me', {
    method: 'PUT',
    body: JSON.stringify(profileData),
  });
}

export async function uploadAvatar(formData: FormData) {
  return apiFetch('/api/profiles/me/avatar', {
    method: 'POST',
    body: formData,
    headers: {},
  });
}

export async function deleteAvatar() {
  return apiFetch('/api/profiles/me/avatar', {
    method: 'DELETE',
  });
}

export async function getUserStats() {
  return apiFetch('/api/profiles/me/stats');
}

// Plan Management
export async function getPlans() {
  return apiFetch('/api/plans/');
}

export async function getCurrentPlan() {
  return apiFetch('/api/plans/current');
}

export async function upgradeUserPlan(planName: string) {
  return apiFetch('/api/plans/upgrade', {
    method: 'POST',
    body: JSON.stringify({ plan_name: planName }),
  });
}

export async function getPlanLimits() {
  return apiFetch('/api/plans/limits');
}

// System Health
export async function getSystemHealth() {
  return apiFetch('/api/system/health');
}

export async function getSystemPerformance() {
  return apiFetch('/api/system/performance');
}

export async function getSystemLogs(params?: { level?: string; module?: string; hours?: number; limit?: number }) {
  const queryParams = new URLSearchParams();
  if (params?.level) queryParams.append('level', params.level);
  if (params?.module) queryParams.append('module', params.module);
  if (params?.hours) queryParams.append('hours', String(params.hours));
  if (params?.limit) queryParams.append('limit', String(params.limit));
  
  const queryString = queryParams.toString();
  return apiFetch(`/api/system/logs${queryString ? `?${queryString}` : ''}`);
}

export async function getSystemInfo() {
  return apiFetch('/api/system/info');
}

export async function getApiKeyInfo() {
  return apiFetch('/api/auth/api-key');
}

export async function createApiKey() {
  return apiFetch('/api/auth/api-key', { method: 'POST' });
}

export async function revokeApiKey() {
  return apiFetch('/api/auth/api-key', { method: 'DELETE' });
}

export async function getSupportOptions() {
  return apiFetch('/api/support/options');
}

export async function submitSupportRequest(data: { subject: string; message: string; phone?: string }) {
  return apiFetch('/api/support/contact', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getJobResultsWithFilters(jobId: number, filters?: { status?: string; company?: string; dateFrom?: string; dateTo?: string }) {
  let params = '';
  if (filters) {
    const q: string[] = [];
    if (filters.status) q.push(`status=${encodeURIComponent(filters.status)}`);
    if (filters.company) q.push(`company=${encodeURIComponent(filters.company)}`);
    if (filters.dateFrom) q.push(`date_from=${encodeURIComponent(filters.dateFrom)}`);
    if (filters.dateTo) q.push(`date_to=${encodeURIComponent(filters.dateTo)}`);
    params = q.length ? '?' + q.join('&') : '';
  }
  return apiFetch(`/api/scrape/${jobId}/results${params}`);
}

export async function getSavedQueries() {
  return apiFetch('/api/saved-queries/');
}

export async function createSavedQuery(data: { name: string; queries: string[] }) {
  return apiFetch('/api/saved-queries/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateSavedQuery(id: number, data: { name: string; queries: string[] }) {
  return apiFetch(`/api/saved-queries/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteSavedQuery(id: number) {
  return apiFetch(`/api/saved-queries/${id}`, {
    method: 'DELETE',
  });
}

export async function bulkDeleteJobs(jobIds: number[]) {
  return apiFetch('/api/scrape/bulk-delete', {
    method: 'POST',
    body: JSON.stringify(jobIds),
  });
}

export async function bulkDeleteLeads(leadIds: number[]) {
  return apiFetch('/api/crm/leads/bulk-delete', {
    method: 'POST',
    body: JSON.stringify(leadIds),
  });
}

export async function bulkAddLeads(leads: any[]) {
  return apiFetch('/api/crm/leads/bulk-add', {
    method: 'POST',
    body: JSON.stringify(leads),
  });
}

export async function getNotifications() {
  return apiFetch('/api/notifications/');
}

export async function markNotificationRead(id: number) {
  return apiFetch(`/api/notifications/${id}/read`, { method: 'POST' });
}

export async function createNotification(data: { type: string; message: string }) {
  return apiFetch('/api/notifications/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getScheduledJobs() {
  return apiFetch('/api/scheduler/');
}

export async function createScheduledJob(data: { name: string; queries: string[]; schedule: string; active?: boolean }) {
  return apiFetch('/api/scheduler/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateScheduledJob(id: number, data: { name: string; queries: string[]; schedule: string; active?: boolean }) {
  return apiFetch(`/api/scheduler/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteScheduledJob(id: number) {
  return apiFetch(`/api/scheduler/${id}`, { method: 'DELETE' });
}

export async function activateScheduledJob(id: number) {
  return apiFetch(`/api/scheduler/${id}/activate`, { method: 'POST' });
}

export async function deactivateScheduledJob(id: number) {
  return apiFetch(`/api/scheduler/${id}/deactivate`, { method: 'POST' });
}

export async function getCustomDashboards() {
  return apiFetch('/api/analytics/custom-dashboards/');
}

export async function createCustomDashboard(data: { name: string; config: object }) {
  return apiFetch('/api/analytics/custom-dashboards/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateCustomDashboard(id: number, data: { name: string; config: object }) {
  return apiFetch(`/api/analytics/custom-dashboards/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteCustomDashboard(id: number) {
  return apiFetch(`/api/analytics/custom-dashboards/${id}`, { method: 'DELETE' });
}

export async function getTeams() {
  return apiFetch('/api/teams/');
}

export async function createTeam(data: { name: string }) {
  return apiFetch('/api/teams/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function inviteToTeam(teamId: number, data: { email: string; role: string }) {
  return apiFetch(`/api/teams/${teamId}/invite`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function listTeamMembers(teamId: number) {
  return apiFetch(`/api/teams/${teamId}/members`);
}

export async function removeTeamMember(teamId: number, memberId: number) {
  return apiFetch(`/api/teams/${teamId}/members/${memberId}/remove`, { method: 'POST' });
}

export async function changeTeamMemberRole(teamId: number, memberId: number, role: string) {
  return apiFetch(`/api/teams/${teamId}/members/${memberId}/role`, {
    method: 'POST',
    body: JSON.stringify({ role }),
  });
}

export async function transferTeamOwnership(teamId: number, newOwnerId: number) {
  return apiFetch(`/api/teams/${teamId}/transfer-ownership/${newOwnerId}`, { method: 'POST' });
}

export async function acceptTeamInvite(membershipId: number) {
  return apiFetch(`/api/teams/memberships/${membershipId}/accept`, { method: 'POST' });
}

export async function declineTeamInvite(membershipId: number) {
  return apiFetch(`/api/teams/memberships/${membershipId}/decline`, { method: 'POST' });
}

export async function shareJob(jobId: number) {
  return apiFetch(`/api/scrape/${jobId}/share`, { method: 'POST' });
}

export async function unshareJob(jobId: number) {
  return apiFetch(`/api/scrape/${jobId}/unshare`, { method: 'POST' });
}

export async function getSharedJob(shareToken: string) {
  return apiFetch(`/api/scrape/shared/${shareToken}`);
}

export async function shareLead(leadId: number) {
  return apiFetch(`/api/crm/leads/${leadId}/share`, { method: 'POST' });
}

export async function unshareLead(leadId: number) {
  return apiFetch(`/api/crm/leads/${leadId}/unshare`, { method: 'POST' });
}

export async function getSharedLead(shareToken: string) {
  return apiFetch(`/api/crm/leads/shared/${shareToken}`);
}

export async function getWebhookUrl() {
  return apiFetch('/api/notifications/webhook');
}

export async function setWebhookUrl(webhook_url: string) {
  return apiFetch('/api/notifications/webhook', {
    method: 'POST',
    body: JSON.stringify({ webhook_url }),
  });
}

export async function deleteWebhookUrl() {
  return apiFetch('/api/notifications/webhook', { method: 'DELETE' });
}

export async function testWebhook() {
  return apiFetch('/api/notifications/webhook/test', { method: 'POST' });
} 

export async function connectCRM(provider: string) {
  return apiFetch('/api/crm/connect', {
    method: 'POST',
    body: JSON.stringify({ provider }),
  });
}

export async function getCRMStatus() {
  return apiFetch('/api/crm/status');
}

export async function disconnectCRM() {
  return apiFetch('/api/crm/disconnect', { method: 'POST' });
}

export async function oauthCallbackCRM(provider: string, params: any) {
  const query = new URLSearchParams(params).toString();
  return apiFetch(`/api/crm/oauth/${provider}?${query}`);
} 

export async function getMyAuditLogs() {
  return apiFetch('/api/audit/my');
} 

// Enhanced 2FA (Security) API
export async function setup2FA() {
  return apiFetch('/api/security/2fa/setup', { method: 'POST' });
}

export async function verifyAndEnable2FA(code: string) {
  return apiFetch('/api/security/2fa/verify-and-enable', {
    method: 'POST',
    body: JSON.stringify({ code }),
  });
}

export async function disable2FAEnhanced() {
  return apiFetch('/api/security/2fa/disable', { method: 'POST' });
} 

export async function regenerate2FABackupCodes() {
  return apiFetch('/api/security/2fa/regenerate-backup-codes', { method: 'POST' });
} 

export async function getSecurityStatus() {
  return apiFetch('/api/security/security-status');
}

// Affiliate Program API
export async function generateAffiliateCode() {
  return apiFetch('/api/affiliate/generate', { method: 'POST' });
}

export async function getAffiliateStats() {
  return apiFetch('/api/affiliate/stats');
} 

export async function listAffiliateCommissions() {
  return apiFetch('/api/affiliate/commissions');
}

export async function requestAffiliatePayout(amount: number, notes?: string) {
  return apiFetch('/api/affiliate/payout', {
    method: 'POST',
    body: JSON.stringify({ amount, notes }),
  });
} 

// FAQ API
export async function getFaqs() {
  // If backend endpoint exists, use:
  // return apiFetch('/api/faq');
  // Otherwise, return mock data for now:
  return [
    { question: 'How do I create a job?', answer: 'Go to the dashboard and enter your queries, then click Create Job.' },
    { question: 'How do I export results?', answer: 'After a job completes, use the Export buttons in the results section.' },
    { question: 'How do I upgrade my plan?', answer: 'Go to Settings or click Upgrade in the dashboard.' },
  ];
} 

// Lead Collection API
export async function getLeadSources() {
  return apiFetch('/api/lead-collection/sources');
}

export async function createLeadSource(data: { name: string; type: string; config?: any }) {
  return apiFetch('/api/lead-collection/sources', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getLeadCollections() {
  return apiFetch('/api/lead-collection/collections');
}

export async function createLeadCollection(data: { name: string; description?: string; source_id: number; config?: any }) {
  return apiFetch('/api/lead-collection/collections', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function collectFacebookLeads(data: { keywords: string[]; location?: string; max_results: number }) {
  return apiFetch('/api/lead-collection/collect/facebook', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function collectInstagramLeads(data: { hashtags: string[]; location?: string; max_results: number }) {
  return apiFetch('/api/lead-collection/collect/instagram', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function collectWhatsAppLeads(data: { phone_numbers: string[]; keywords: string[] }) {
  return apiFetch('/api/lead-collection/collect/whatsapp', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getSocialMediaLeads(params?: { platform?: string; status?: string; collection_id?: number; page?: number; page_size?: number }) {
  const queryParams = new URLSearchParams();
  if (params?.platform) queryParams.append('platform', params.platform);
  if (params?.status) queryParams.append('status', params.status);
  if (params?.collection_id) queryParams.append('collection_id', String(params.collection_id));
  if (params?.page) queryParams.append('page', String(params.page));
  if (params?.page_size) queryParams.append('page_size', String(params.page_size));
  
  const queryString = queryParams.toString();
  return apiFetch(`/api/lead-collection/leads${queryString ? `?${queryString}` : ''}`);
} 

// Tenant SSO Config
export async function getTenantSsoConfig(tenantId: string) {
  // Replace with real endpoint if available
  return apiFetch(`/api/tenant/${tenantId}/sso-config`);
}
export async function updateTenantSsoConfig(tenantId: string, data: any) {
  // Replace with real endpoint if available
  return apiFetch(`/api/tenant/${tenantId}/sso-config`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}
// Tenant Plan
export async function getTenantPlan(tenantId: string) {
  // Replace with real endpoint if available
  return apiFetch(`/api/tenant/${tenantId}/plan`);
}
export async function updateTenantPlan(tenantId: string, data: any) {
  // Replace with real endpoint if available
  return apiFetch(`/api/tenant/${tenantId}/plan`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}
// Tenant Billing
export async function getTenantBilling(tenantId: string) {
  // Replace with real endpoint if available
  return apiFetch(`/api/tenant/${tenantId}/billing`);
}
export async function updateTenantBilling(tenantId: string, data: any) {
  // Replace with real endpoint if available
  return apiFetch(`/api/tenant/${tenantId}/billing`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}
// Tenant Info
export async function getTenant(tenantId: string) {
  // Replace with real endpoint if available
  return apiFetch(`/api/tenant/${tenantId}`);
}
export async function updateTenant(tenantId: string, data: any) {
  // Replace with real endpoint if available
  return apiFetch(`/api/tenant/${tenantId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
} 

// Analytics
export async function getAnalytics(timeRange: string = '30') {
  return apiFetch(`/api/analytics?timeRange=${timeRange}`);
}

// Social Media Scraping API
export async function scrapeSocialMedia(data: {
  platform: string;
  keywords: string[];
  location?: string;
  max_results: number;
  filters?: {
    min_followers?: number;
    max_followers?: number;
    has_email?: boolean;
    has_phone?: boolean;
    has_website?: boolean;
    verified_only?: boolean;
  };
  include_engagement: boolean;
  include_contact_info: boolean;
}) {
  return apiFetch('/api/social-scraper/scrape', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getSocialLeads(params?: {
  platform?: string;
  status?: string;
  page?: number;
  page_size?: number;
}) {
  const queryParams = new URLSearchParams();
  if (params?.platform) queryParams.append('platform', params.platform);
  if (params?.status) queryParams.append('status', params.status);
  if (params?.page) queryParams.append('page', String(params.page));
  if (params?.page_size) queryParams.append('page_size', String(params.page_size));
  
  const queryString = queryParams.toString();
  return apiFetch(`/api/social-scraper/leads${queryString ? `?${queryString}` : ''}`);
}

export async function getSocialAnalytics() {
  return apiFetch('/api/social-scraper/analytics');
}

// WhatsApp Workflow API
export async function getWhatsAppWorkflows() {
  return apiFetch('/api/whatsapp-workflow/workflows');
}

export async function createWhatsAppWorkflow(data: {
  name: string;
  description?: string;
  trigger_type: string;
  trigger_conditions?: any;
  steps: Array<{
    name: string;
    step_type: string;
    content?: string;
    delay_minutes?: number;
    conditions?: any;
    actions?: string[];
    order: number;
  }>;
  is_active: boolean;
}) {
  return apiFetch('/api/whatsapp-workflow/workflows', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getWhatsAppWorkflowTemplates() {
  return apiFetch('/api/whatsapp-workflow/templates');
}

export async function executeWhatsAppWorkflow(data: {
  workflow_id: number;
  lead_id?: number;
  social_lead_id?: number;
  execution_data?: any;
}) {
  return apiFetch('/api/whatsapp-workflow/execute', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getWhatsAppWorkflowAnalytics() {
  return apiFetch('/api/whatsapp-workflow/analytics');
} 

export async function login2FA(userId: number, code: string) {
  const data = await apiFetch('/api/auth/login/2fa', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, code }),
  });
  setToken(data.access_token);
  return data;
} 

// RBAC/Role Management API
export async function getRoles() {
  return apiFetch('/api/security/roles');
}

export async function createRole(data: { name: string; description: string; permissions: string[] }) {
  return apiFetch('/api/security/roles', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateRole(roleId: number, data: { name: string; description: string; permissions: string[] }) {
  return apiFetch(`/api/security/roles/${roleId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteRole(roleId: number) {
  return apiFetch(`/api/security/roles/${roleId}`, {
    method: 'DELETE',
  });
}

export async function assignRoleToUser(userId: number, roleId: number) {
  return apiFetch(`/api/security/users/${userId}/roles/${roleId}`, {
    method: 'POST',
  });
}

export async function removeRoleFromUser(userId: number, roleId: number) {
  return apiFetch(`/api/security/users/${userId}/roles/${roleId}`, {
    method: 'DELETE',
  });
} 