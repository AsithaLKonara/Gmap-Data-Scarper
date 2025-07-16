import React, { useState, useEffect } from 'react';
import { Box, Heading, Text, HStack, Input, Button, VStack, useToast } from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import { getCRMStatus, connectCRM, disconnectCRM, getWebhookUrl, testWebhook } from '../api';
import { Link as RouterLink } from 'react-router-dom';

const Integrations: React.FC = () => {
  const { t } = useTranslation();
  const toast = useToast();
  const [crmStatus, setCrmStatus] = useState<any>(null);
  const [crmLoading, setCrmLoading] = useState(false);
  const [crmProvider, setCrmProvider] = useState('');
  const [crmConfig, setCrmConfig] = useState({});
  const [webhookUrl, setWebhookUrl] = useState('');
  const [webhookLoading, setWebhookLoading] = useState(false);
  const [testWebhookResult, setTestWebhookResult] = useState<string | null>(null);

  useEffect(() => {
    loadCRMStatus();
    loadWebhookUrl();
  }, []);

  const loadCRMStatus = async () => {
    try {
      const status = await getCRMStatus();
      setCrmStatus(status);
    } catch {
      setCrmStatus(null);
    }
  };

  const loadWebhookUrl = async () => {
    setWebhookLoading(true);
    try {
      const res = await getWebhookUrl();
      setWebhookUrl(res.url || '');
    } catch {
      setWebhookUrl('');
    } finally {
      setWebhookLoading(false);
    }
  };

  const handleConnectCRM = async (provider: string) => {
    setCrmLoading(true);
    try {
      await connectCRM(provider);
      setCrmStatus((s: any) => ({ ...s, crm_provider: provider, crm_connected: false }));
      toast({ title: t('integrations.connectToProvider', 'Connect to {{provider}}', { provider }), description: t('integrations.oauthFlow', 'OAuth flow will start (stub)'), status: 'info' });
    } catch (e: any) {
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setCrmLoading(false);
    }
  };
  const handleDisconnectCRM = async () => {
    setCrmLoading(true);
    try {
      await disconnectCRM();
      setCrmStatus(null);
      toast({ title: t('integrations.disconnected', 'Disconnected'), status: 'info' });
    } catch (e: any) {
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setCrmLoading(false);
    }
  };

  const handleTestWebhook = async () => {
    setWebhookLoading(true);
    setTestWebhookResult(null);
    try {
      const res = await testWebhook();
      setTestWebhookResult(res.message || 'Webhook test sent');
      toast({ title: 'Test webhook sent', status: 'success' });
    } catch (e: any) {
      setTestWebhookResult(e.message || 'Webhook test failed');
      toast({ title: 'Webhook test failed', description: e.message, status: 'error' });
    } finally {
      setWebhookLoading(false);
    }
  };

  return (
    <Box maxW="3xl" mx="auto" py={8}>
      <Heading size="lg" mb={6}>{t('integrations.title', 'Integrations')}</Heading>
      <Text fontSize="md" color="gray.600" mb={8}>{t('integrations.description', 'Connect LeadTap to your favorite tools and platforms. Manage CRM, email marketing, and automation integrations below.')}</Text>

      {/* CRM Integrations */}
      <Box bg="white" p={6} borderRadius="lg" border="1px" borderColor="gray.200" boxShadow="md" mb={8}>
        <Heading size="md" mb={2}>{t('integrations.crmIntegration', 'CRM Integration')}</Heading>
        <Text fontSize="sm" color="gray.600" mb={2}>{t('integrations.crmDescription', 'Connect to external CRMs like HubSpot or Salesforce to sync leads and automate workflows.')}</Text>
        <Text fontSize="sm" mb={2}>{t('integrations.crmStatus', 'Status: {{status}}', { status: crmStatus ? (crmStatus.crm_connected ? `${t('integrations.connectedToProvider', 'Connected to {{provider}}', { provider: crmStatus.crm_provider })}` : `${t('integrations.notConnected', 'Not connected')}${crmStatus.crm_provider ? ` (${crmStatus.crm_provider})` : ''}`) : t('integrations.notConnected') })}</Text>
        <HStack mb={2}>
          <Button colorScheme="blue" onClick={() => handleConnectCRM('hubspot')} isLoading={crmLoading} isDisabled={crmStatus?.crm_connected}>{t('integrations.connectHubspot', 'Connect HubSpot')}</Button>
          <Button colorScheme="orange" onClick={() => handleConnectCRM('salesforce')} isLoading={crmLoading} isDisabled={crmStatus?.crm_connected}>{t('integrations.connectSalesforce', 'Connect Salesforce')}</Button>
          <Button colorScheme="red" onClick={handleDisconnectCRM} isLoading={crmLoading} isDisabled={!crmStatus?.crm_connected}>{t('integrations.disconnect', 'Disconnect')}</Button>
        </HStack>
      </Box>

      {/* Email Marketing Integrations */}
      <Box bg="white" p={6} borderRadius="lg" border="1px" borderColor="gray.200" boxShadow="md" mb={8}>
        <Heading size="md" mb={2}>{t('integrations.emailMarketing', 'Email Marketing')}</Heading>
        <Text fontSize="sm" color="gray.600" mb={2}>{t('integrations.emailDescription', 'Connect to email marketing tools like Mailchimp to sync contacts and automate campaigns.')}</Text>
        <HStack mb={2}>
          <Button colorScheme="green" onClick={() => handleConnectCRM('mailchimp')} isLoading={crmLoading} isDisabled={crmStatus?.email_connected}>{t('integrations.connectMailchimp', 'Connect Mailchimp')}</Button>
        </HStack>
      </Box>

      {/* Zapier & Automation */}
      <Box bg="white" p={6} borderRadius="lg" border="1px" borderColor="gray.200" boxShadow="md" mb={8}>
        <Heading size="md" mb={2}>{t('integrations.zapier', 'Zapier & Automation')}</Heading>
        <Text fontSize="sm" color="gray.600" mb={2}>{t('integrations.zapierDescription', 'Connect LeadTap to thousands of apps using Zapier. Automate workflows and sync data across platforms.')}</Text>
        <Button colorScheme="yellow" as="a" href="https://zapier.com/apps/leadtap/integrations" target="_blank" rel="noopener noreferrer" mb={4}>{t('integrations.connectZapier', 'Connect Zapier')}</Button>
        <Box mt={4} mb={2}>
          <Heading size="sm" mb={1}>Available Webhook Events</Heading>
          <VStack align="start" spacing={1} fontSize="sm">
            <Text><b>lead.created</b> – Triggered when a new lead is created</Text>
            <Text><b>job.completed</b> – Triggered when a job completes</Text>
            <Text><b>lead.updated</b> – Triggered when a lead is updated</Text>
            <Text><b>lead.deleted</b> – Triggered when a lead is deleted</Text>
          </VStack>
        </Box>
        <Box mt={4} mb={2}>
          <Heading size="sm" mb={1}>Your Webhook URL</Heading>
          <HStack>
            <Input value={webhookUrl} isReadOnly size="sm" width="auto" isLoading={webhookLoading} />
            <Button size="sm" onClick={() => {navigator.clipboard.writeText(webhookUrl); toast({ title: 'Copied to clipboard', status: 'success' });}} disabled={!webhookUrl}>Copy</Button>
          </HStack>
        </Box>
        <Button colorScheme="blue" size="sm" mt={2} mb={2} onClick={handleTestWebhook} isLoading={webhookLoading} disabled={!webhookUrl}>Test Webhook</Button>
        {testWebhookResult && <Text fontSize="sm" color="gray.600" mt={1}>{testWebhookResult}</Text>}
        <Box mt={4}>
          <Button as="a" href="/docs/api_examples#zapier" target="_blank" rel="noopener noreferrer" variant="link" colorScheme="blue" size="sm">Read Zapier Integration Guide</Button>
        </Box>
      </Box>

      {/* Coming Soon / Placeholder for more integrations */}
      <Box bg="white" p={6} borderRadius="lg" border="1px" borderColor="gray.200" boxShadow="md" mb={8}>
        <Heading size="md" mb={2}>{t('integrations.moreComing', 'More Integrations Coming Soon')}</Heading>
        <Text fontSize="sm" color="gray.600">{t('integrations.moreDescription', 'We are working on more integrations. Let us know what you want to see!')}</Text>
      </Box>

      <Button as={RouterLink} to="/settings" variant="outline">{t('integrations.backToSettings', 'Back to Settings')}</Button>
    </Box>
  );
};

export default Integrations; 