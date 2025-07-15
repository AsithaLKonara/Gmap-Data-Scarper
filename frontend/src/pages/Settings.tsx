import React, { useState, useEffect } from 'react';
import { getWebhookUrl, setWebhookUrl, deleteWebhookUrl, testWebhook, connectCRM, getCRMStatus, disconnectCRM, enable2FA, verify2FA, disable2FA, exportUserData, deleteAccount, getReferralInfo, useReferralCode, getReferralStats, getUsage, purchaseCredits, getTenantSsoConfig, updateTenantSsoConfig, getTenantPlan, updateTenantPlan, getTenantBilling, updateTenantBilling, createPayHereSession, getTenant, updateTenant } from '../api';
import { Box, Heading, Text, HStack, Input, Button, useToast } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import QRCode from 'qrcode.react';
import { useTranslation } from 'react-i18next';
const bgColor = 'white'; // or useColorModeValue('white', 'gray.800') if Chakra hook is available
const borderColor = 'gray.200'; // or useColorModeValue('gray.200', 'gray.700')

function Settings() {
  const { t } = useTranslation();
  const [webhookUrl, setWebhookUrlState] = useState('');
  const [webhookLoading, setWebhookLoading] = useState(false);
  const [webhookTestResult, setWebhookTestResult] = useState<string | null>(null);
  const [crmStatus, setCrmStatus] = useState<any>({});
  const [crmProvider, setCrmProvider] = useState('');
  const [crmConfig, setCrmConfig] = useState<any>({});
  const [crmLoading, setCrmLoading] = useState(false);
  const [twoFAEnabled, setTwoFAEnabled] = useState(false);
  const [twoFASecret, setTwoFASecret] = useState<string | null>(null);
  const [twoFAUri, setTwoFAUri] = useState<string | null>(null);
  const [twoFACode, setTwoFACode] = useState('');
  const [twoFALoading, setTwoFALoading] = useState(false);
  const [twoFAStatus, setTwoFAStatus] = useState<string | null>(null);
  const [gdprLoading, setGdprLoading] = useState(false);
  const [gdprExportUrl, setGdprExportUrl] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [referralInfo, setReferralInfo] = useState<any>(null);
  const [referralStats, setReferralStats] = useState<any>(null);
  const [referralLoading, setReferralLoading] = useState(false);
  const [referralCodeInput, setReferralCodeInput] = useState('');
  const [referralUsed, setReferralUsed] = useState(false);
  const [usageInfo, setUsageInfo] = useState<any>(null);
  const [purchaseAmount, setPurchaseAmount] = useState(10);
  const [usageLoading, setUsageLoading] = useState(false);
  const [ssoConfig, setSsoConfig] = useState<any>({});
  const [ssoLoading, setSsoLoading] = useState(false);
  const [ssoEdit, setSsoEdit] = useState(false);
  const [ssoForm, setSsoForm] = useState<any>({ entity_id: '', sso_url: '', cert: '' });
  const [planInfo, setPlanInfo] = useState<any>({});
  const [billingInfo, setBillingInfo] = useState<any>({});
  const [planLoading, setPlanLoading] = useState(false);
  const [billingLoading, setBillingLoading] = useState(false);
  const [planEdit, setPlanEdit] = useState(false);
  const [planForm, setPlanForm] = useState<any>({ plan: '', plan_expiry: '' });
  const [billingEdit, setBillingEdit] = useState(false);
  const [billingForm, setBillingForm] = useState<any>({ billing_email: '' });
  const [customDomain, setCustomDomain] = useState('');
  const [customDomainLoading, setCustomDomainLoading] = useState(false);
  const [customDomainEdit, setCustomDomainEdit] = useState(false);
  const tenantId = localStorage.getItem('tenantId') || '';

  const toast = useToast();

  useEffect(() => {
    getWebhookUrl().then(res => setWebhookUrlState(res.webhook_url || ''));
    getCRMStatus().then(setCrmStatus);
    getReferralInfo().then(setReferralInfo);
    getReferralStats().then(setReferralStats);
    getUsage().then(setUsageInfo);
    if (tenantId) {
      setSsoLoading(true);
      getTenantSsoConfig(tenantId).then(cfg => {
        setSsoConfig(cfg);
        setSsoForm(cfg || { entity_id: '', sso_url: '', cert: '' });
      }).finally(() => setSsoLoading(false));
      setPlanLoading(true);
      getTenantPlan(tenantId).then(info => {
        setPlanInfo(info);
        setPlanForm(info);
      }).finally(() => setPlanLoading(false));
      setBillingLoading(true);
      getTenantBilling(tenantId).then(info => {
        setBillingInfo(info);
        setBillingForm(info);
      }).finally(() => setBillingLoading(false));
      getTenant(tenantId).then(t => setCustomDomain(t.custom_domain || ''));
    }
  }, [tenantId]);

  const handleSaveWebhook = async () => {
    setWebhookLoading(true);
    try {
      await setWebhookUrl(webhookUrl);
      toast({ title: t('settings.webhookSaved', 'Webhook URL saved'), status: 'success' });
    } catch (e: any) {
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setWebhookLoading(false);
    }
  };
  const handleDeleteWebhook = async () => {
    setWebhookLoading(true);
    try {
      await deleteWebhookUrl();
      setWebhookUrlState('');
      toast({ title: t('settings.webhookDeleted', 'Webhook URL deleted'), status: 'info' });
    } catch (e: any) {
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setWebhookLoading(false);
    }
  };
  const handleTestWebhook = async () => {
    setWebhookLoading(true);
    setWebhookTestResult(null);
    try {
      const res = await testWebhook();
      setWebhookTestResult(t('settings.webhookTestSuccess', 'Success! Response code: {{code}}', { code: res.response_code }));
      toast({ title: t('settings.webhookTestSent', 'Test sent'), status: 'success' });
    } catch (e: any) {
      setWebhookTestResult(t('settings.webhookTestFailed', 'Failed: {{message}}', { message: e.message }));
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setWebhookLoading(false);
    }
  };

  const handleConnectCRM = async (provider: string) => {
    setCrmLoading(true);
    try {
      const res = await connectCRM(provider);
      setCrmStatus((s: any) => ({ ...s, crm_provider: provider, crm_connected: false }));
      toast({ title: t('settings.connectToProvider', 'Connect to {{provider}}', { provider }), description: t('settings.oauthFlow', 'OAuth flow will start (stub)'), status: 'info' });
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
      toast({ title: t('settings.disconnected', 'Disconnected'), status: 'info' });
    } catch (e: any) {
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setCrmLoading(false);
    }
  };

  const handleEnable2FA = async () => {
    setTwoFALoading(true);
    try {
      const res = await enable2FA();
      setTwoFASecret(res.secret);
      setTwoFAUri(res.uri);
      setTwoFAStatus(t('settings.2faScan', 'Scan the QR code or enter the secret in your authenticator app.'));
    } catch (e: any) {
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setTwoFALoading(false);
    }
  };
  const handleVerify2FA = async () => {
    setTwoFALoading(true);
    try {
      await verify2FA(twoFACode);
      setTwoFAEnabled(true);
      setTwoFAStatus(t('settings.2faEnabled', '2FA enabled!'));
      toast({ title: t('settings.2faEnabled', '2FA enabled!'), status: 'success' });
    } catch (e: any) {
      setTwoFAStatus(t('settings.2faInvalidCode', 'Invalid code.'));
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setTwoFALoading(false);
    }
  };
  const handleDisable2FA = async () => {
    setTwoFALoading(true);
    try {
      await disable2FA();
      setTwoFAEnabled(false);
      setTwoFASecret(null);
      setTwoFAUri(null);
      setTwoFAStatus(t('settings.2faDisabled', '2FA disabled.'));
      toast({ title: t('settings.2faDisabled', '2FA disabled.'), status: 'info' });
    } catch (e: any) {
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setTwoFALoading(false);
    }
  };

  const handleExportData = async () => {
    setGdprLoading(true);
    try {
      const data = await exportUserData();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      setGdprExportUrl(url);
      toast({ title: t('settings.dataExported', 'Data exported'), status: 'success' });
    } catch (e: any) {
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setGdprLoading(false);
    }
  };
  const handleDeleteAccount = async () => {
    setGdprLoading(true);
    try {
      await deleteAccount();
      toast({ title: t('settings.accountDeleted', 'Account deleted'), status: 'info' });
      // Optionally redirect or log out
    } catch (e: any) {
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setGdprLoading(false);
    }
  };

  const handleUseReferral = async () => {
    setReferralLoading(true);
    try {
      await useReferralCode(referralCodeInput);
      setReferralUsed(true);
      toast({ title: t('settings.referralApplied', 'Referral applied'), status: 'success' });
    } catch (e: any) {
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setReferralLoading(false);
    }
  };

  const handlePurchaseCredits = async () => {
    setUsageLoading(true);
    try {
      await purchaseCredits(purchaseAmount);
      toast({ title: t('settings.creditsPurchased', 'Credits purchased'), status: 'success' });
      getUsage().then(setUsageInfo);
    } catch (e: any) {
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setUsageLoading(false);
    }
  };

  const handleSaveSsoConfig = async () => {
    setSsoLoading(true);
    try {
      if (tenantId) {
        await updateTenantSsoConfig(tenantId, { sso_config: ssoForm });
        setSsoConfig(ssoForm);
        setSsoEdit(false);
        toast({ title: t('settings.ssoConfigSaved', 'SSO config saved'), status: 'success' });
      }
    } catch (e: any) {
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setSsoLoading(false);
    }
  };

  const handleSavePlan = async () => {
    setPlanLoading(true);
    try {
      if (tenantId) {
        await updateTenantPlan(tenantId, planForm);
        setPlanInfo(planForm);
        setPlanEdit(false);
        toast({ title: t('settings.planUpdated', 'Plan updated'), status: 'success' });
      }
    } catch (e: any) {
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setPlanLoading(false);
    }
  };
  const handleSaveBilling = async () => {
    setBillingLoading(true);
    try {
      if (tenantId) {
        await updateTenantBilling(tenantId, billingForm);
        setBillingInfo(billingForm);
        setBillingEdit(false);
        toast({ title: t('settings.billingInfoUpdated', 'Billing info updated'), status: 'success' });
      }
    } catch (e: any) {
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setBillingLoading(false);
    }
  };

  const handleUpgradePlan = async () => {
    setPlanLoading(true);
    try {
      const res = await createPayHereSession(planForm.plan);
      if (res.payhere_url) {
        window.location.href = res.payhere_url;
      }
    } catch (e: any) {
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setPlanLoading(false);
    }
  };

  const handleSaveCustomDomain = async () => {
    setCustomDomainLoading(true);
    try {
      if (tenantId) {
        await updateTenant(tenantId, { custom_domain: customDomain });
        setCustomDomainEdit(false);
        toast({ title: t('settings.customDomainUpdated', 'Custom domain updated'), status: 'success' });
      }
    } catch (e: any) {
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setCustomDomainLoading(false);
    }
  };

  return (
    <>
      <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} data-tour="settings-webhook-section">
        <Heading size="md" mb={2} data-tour="settings-webhook-title">{t('settings.webhookManagement', 'Webhook Management')}</Heading>
        <Text fontSize="sm" color="gray.600" mb={2}>{t('settings.webhookDescription', 'Receive real-time notifications in your own systems or Zapier. Enter your webhook URL below.')}</Text>
        <HStack>
          <Input value={webhookUrl} onChange={e => setWebhookUrlState(e.target.value)} placeholder={t('settings.webhookPlaceholder', 'https://your-webhook-url.com/endpoint')} />
          <Button colorScheme="blue" onClick={handleSaveWebhook} isLoading={webhookLoading}>{t('settings.saveWebhook', 'Save')}</Button>
          <Button colorScheme="red" onClick={handleDeleteWebhook} isLoading={webhookLoading} isDisabled={!webhookUrl}>{t('settings.deleteWebhook', 'Delete')}</Button>
          <Button colorScheme="green" onClick={handleTestWebhook} isLoading={webhookLoading} isDisabled={!webhookUrl}>{t('settings.testWebhook', 'Test')}</Button>
        </HStack>
        {webhookTestResult && <Text mt={2}>{webhookTestResult}</Text>}
      </Box>

      <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8}>
        <Heading size="md" mb={2}>{t('settings.integrations', 'Integrations')}</Heading>
        <Box mb={4}>
          <Heading size="sm" mb={2}>{t('settings.crmIntegration', 'CRM Integration')}</Heading>
          <Input placeholder={t('settings.crmProviderPlaceholder', 'CRM Provider (e.g., HubSpot)')} value={crmProvider} onChange={e => setCrmProvider(e.target.value)} mb={2} />
          <Input placeholder={t('settings.crmConfigPlaceholder', 'CRM Config (JSON)')} value={JSON.stringify(crmConfig)} onChange={e => setCrmConfig(JSON.parse(e.target.value || '{}'))} mb={2} />
          <Button colorScheme="blue" onClick={handleConnectCRM} isLoading={crmLoading}>{t('settings.connectCrm', 'Connect CRM')}</Button>
          <Text mt={2}>{t('settings.currentCrmStatus', 'Current: {{provider}} {{config}}', { provider: crmStatus.provider || '-', config: crmStatus.config ? JSON.stringify(crmStatus.config) : '' })}</Text>
        </Box>
        <Box>
          <Heading size="sm" mb={2}>{t('settings.webhookIntegration', 'Webhook Integration')}</Heading>
          <Input placeholder={t('settings.webhookUrlPlaceholder', 'Webhook URL')} value={webhookUrl} onChange={e => setWebhookUrlState(e.target.value)} mb={2} />
          <Button colorScheme="blue" onClick={handleSaveWebhook} isLoading={webhookLoading}>{t('settings.saveWebhook', 'Save Webhook')}</Button>
          <Text mt={2}>{t('settings.currentWebhookUrl', 'Current: {{url}}', { url: webhookUrl || '-' })}</Text>
        </Box>
      </Box>

      <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} data-tour="settings-crm-section">
        <Heading size="md" mb={2} data-tour="settings-crm-title">{t('settings.crmEmailIntegration', 'CRM & Email Integration')}</Heading>
        <Text fontSize="sm" color="gray.600" mb={2}>
          {t('settings.crmEmailDescription', 'Connect your account to external CRMs (HubSpot, Salesforce) or email marketing tools (Mailchimp) to sync leads and automate campaigns.')}
        </Text>
        <Text fontSize="sm" mb={2}>
          {t('settings.crmEmailStatus', 'Status: {{status}}', { status: crmStatus ? (crmStatus.crm_connected ? `${t('settings.connectedToProvider', 'Connected to {{provider}}', { provider: crmStatus.crm_provider })}` : `${t('settings.notConnected', 'Not connected')}${crmStatus.crm_provider ? ` (${crmStatus.crm_provider})` : ''}`) : t('settings.notConnected') })}
        </Text>
        <HStack>
          <Button colorScheme="blue" onClick={() => handleConnectCRM('hubspot')} isLoading={crmLoading} isDisabled={crmStatus?.crm_connected}>{t('settings.connectHubspot', 'Connect HubSpot')}</Button>
          <Button colorScheme="orange" onClick={() => handleConnectCRM('salesforce')} isLoading={crmLoading} isDisabled={crmStatus?.crm_connected}>{t('settings.connectSalesforce', 'Connect Salesforce')}</Button>
          <Button colorScheme="green" onClick={() => handleConnectCRM('mailchimp')} isLoading={crmLoading} isDisabled={crmStatus?.email_connected}>{t('settings.connectMailchimp', 'Connect Mailchimp')}</Button>
          <Button colorScheme="red" onClick={handleDisconnectCRM} isLoading={crmLoading} isDisabled={!crmStatus?.crm_connected && !crmStatus?.email_connected}>{t('settings.disconnect', 'Disconnect')}</Button>
        </HStack>
      </Box>

      <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} data-tour="settings-2fa-section">
        <Heading size="md" mb={2} data-tour="settings-2fa-title">{t('settings.twoFactorAuth', 'Two-Factor Authentication (2FA)')}</Heading>
        <Text fontSize="sm" color="gray.600" mb={2}>
          {t('settings.twoFactorAuthDescription', 'Protect your account with an extra layer of security. Use an authenticator app (Google Authenticator, Authy, etc.).')}
        </Text>
        {twoFAEnabled ? (
          <Button colorScheme="red" onClick={handleDisable2FA} isLoading={twoFALoading}>{t('settings.disableTwoFactorAuth', 'Disable 2FA')}</Button>
        ) : (
          <Button colorScheme="blue" onClick={handleEnable2FA} isLoading={twoFALoading}>{t('settings.enableTwoFactorAuth', 'Enable 2FA')}</Button>
        )}
        {twoFAUri && (
          <Box mt={4}>
            <Text mb={2}>{t('settings.twoFactorAuthScan', 'Scan this QR code in your authenticator app:')}</Text>
            <QRCode value={twoFAUri} size={180} />
            <Text mt={2} fontSize="sm">{t('settings.twoFactorAuthSecret', 'Or enter this secret: <b>{{secret}}</b>', { secret: twoFASecret })}</Text>
            <Box mt={2}>
              <Text mb={1}>{t('settings.twoFactorAuthEnterCode', 'Enter code from app:')}</Text>
              <input value={twoFACode} onChange={e => setTwoFACode(e.target.value)} placeholder={t('settings.twoFactorAuthCodePlaceholder', '123456')} style={{ padding: 8, border: '1px solid #ccc', borderRadius: 4 }} />
              <Button ml={2} colorScheme="green" onClick={handleVerify2FA} isLoading={twoFALoading}>{t('settings.verifyTwoFactorAuth', 'Verify')}</Button>
            </Box>
            {twoFAStatus && <Text mt={2}>{twoFAStatus}</Text>}
          </Box>
        )}
      </Box>

      <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} data-tour="settings-gdpr-section">
        <Heading size="md" mb={2} data-tour="settings-gdpr-title">{t('settings.gdprPrivacy', 'GDPR & Privacy')}</Heading>
        <Text fontSize="sm" color="gray.600" mb={2}>
          {t('settings.gdprPrivacyDescription', 'You can export all your data or request account deletion at any time.')}
        </Text>
        <Button colorScheme="blue" onClick={handleExportData} isLoading={gdprLoading} mb={2}>{t('settings.exportMyData', 'Export My Data (JSON)')}</Button>
        {gdprExportUrl && <a href={gdprExportUrl} download="leadtap_data.json"><Button colorScheme="green" mb={2}>{t('settings.downloadExport', 'Download Export')}</Button></a>}
        <Button colorScheme="red" onClick={() => setDeleteConfirm(true)} isLoading={gdprLoading}>{t('settings.deleteMyAccount', 'Delete My Account')}</Button>
        {deleteConfirm && (
          <Box mt={2}>
            <Text color="red.500" mb={2}>{t('settings.deleteConfirmation', 'Are you sure? This will permanently delete your account and all data. This action cannot be undone.')}</Text>
            <Button colorScheme="red" onClick={handleDeleteAccount} isLoading={gdprLoading}>{t('settings.yesDeleteMyAccount', 'Yes, Delete My Account')}</Button>
            <Button ml={2} onClick={() => setDeleteConfirm(false)}>{t('settings.cancel', 'Cancel')}</Button>
          </Box>
        )}
      </Box>

      <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8}>
        <Heading size="md" mb={2}>{t('settings.referralProgram', 'Referral Program')}</Heading>
        {referralInfo && (
          <>
            <Text fontSize="sm" color="gray.600" mb={2}>{t('settings.referralShare', 'Share your referral link to earn credits! Both you and your friends get rewards.')}</Text>
            <Text mb={2}><b>{t('settings.referralLink', 'Referral Link:')}</b> <Input value={referralInfo.referral_link} isReadOnly w="60%" display="inline-block" mr={2} /><Button size="sm" onClick={() => {navigator.clipboard.writeText(referralInfo.referral_link); toast({ title: t('settings.copied', 'Copied'), status: 'success' });}}>{t('settings.copy', 'Copy')}</Button></Text>
            <Text mb={2}><b>{t('settings.referred', 'Referred:')}</b> {referralInfo.referred_count} | <b>{t('settings.credits', 'Credits:')}</b> {referralInfo.referral_credits}</Text>
          </>
        )}
        {referralStats && referralStats.referred && referralStats.referred.length > 0 && (
          <Box mt={4}>
            <Text fontWeight="bold" mb={2}>{t('settings.yourReferrals', 'Your Referrals:')}</Text>
            {referralStats.referred.map((u: any) => (
              <Text key={u.email} fontSize="sm">{u.email} ({new Date(u.created_at).toLocaleDateString()}) - {t('settings.credits', 'Credits:')} {u.credits}</Text>
            ))}
          </Box>
        )}
        {!referralUsed && (
          <Box mt={4}>
            <Text fontSize="sm" mb={1}>{t('settings.haveReferralCode', 'Have a referral code?')}</Text>
            <Input value={referralCodeInput} onChange={e => setReferralCodeInput(e.target.value)} placeholder={t('settings.enterReferralCode', 'Enter referral code')} w="40%" display="inline-block" mr={2} />
            <Button size="sm" colorScheme="blue" onClick={handleUseReferral} isLoading={referralLoading}>{t('settings.applyReferral', 'Apply')}</Button>
          </Box>
        )}
      </Box>

      <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} data-tour="settings-usage-section">
        <Heading size="md" mb={2} data-tour="settings-usage-title">{t('settings.usageBilling', 'Usage & Billing')}</Heading>
        {usageInfo && (
          <>
            <Text mb={2}><b>{t('settings.plan', 'Plan:')}</b> {usageInfo.plan}</Text>
            <Text mb={2}><b>{t('settings.jobsToday', 'Jobs Today:')}</b> {usageInfo.jobs_today} / {usageInfo.max_queries_per_day}</Text>
            <Text mb={2}><b>{t('settings.usageCredits', 'Usage Credits:')}</b> {usageInfo.usage_credits} | <b>{t('settings.referralCredits', 'Referral Credits:')}</b> {usageInfo.referral_credits}</Text>
            <HStack mt={2}>
              <Input type="number" value={purchaseAmount} min={1} onChange={e => setPurchaseAmount(Number(e.target.value))} w="120px" />
              <Button colorScheme="blue" onClick={handlePurchaseCredits} isLoading={usageLoading}>{t('settings.purchaseCredits', 'Purchase Credits')}</Button>
            </HStack>
          </>
        )}
      </Box>

      <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} data-tour="settings-sso-section">
        <Heading size="md" mb={2} data-tour="settings-sso-title">{t('settings.ssoSamlConfig', 'SSO/SAML Configuration')}</Heading>
        {ssoLoading ? <Text>{t('settings.loading', 'Loading...')}</Text> : (
          <>
            {!ssoEdit ? (
              <>
                <Text>{t('settings.ssoEntityId', 'Entity ID: {{id}}', { id: ssoConfig.entity_id || '-' })}</Text>
                <Text>{t('settings.ssoSsoUrl', 'SSO URL: {{url}}', { url: ssoConfig.sso_url || '-' })}</Text>
                <Text>{t('settings.ssoCertificate', 'Certificate: {{cert}}', { cert: ssoConfig.cert ? '[set]' : '-' })}</Text>
                <Button mt={2} onClick={() => setSsoEdit(true)}>{t('settings.edit', 'Edit')}</Button>
              </>
            ) : (
              <>
                <Input placeholder={t('settings.ssoEntityIdPlaceholder', 'Entity ID')} value={ssoForm.entity_id} onChange={e => setSsoForm(f => ({ ...f, entity_id: e.target.value }))} mb={2} />
                <Input placeholder={t('settings.ssoSsoUrlPlaceholder', 'SSO URL')} value={ssoForm.sso_url} onChange={e => setSsoForm(f => ({ ...f, sso_url: e.target.value }))} mb={2} />
                <Input placeholder={t('settings.ssoCertificatePlaceholder', 'Certificate')} value={ssoForm.cert} onChange={e => setSsoForm(f => ({ ...f, cert: e.target.value }))} mb={2} />
                <Button colorScheme="blue" onClick={handleSaveSsoConfig} isLoading={ssoLoading}>{t('settings.save', 'Save')}</Button>
                <Button ml={2} onClick={() => setSsoEdit(false)}>{t('settings.cancel', 'Cancel')}</Button>
              </>
            )}
          </>
        )}
      </Box>

      <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8}>
        <Heading size="md" mb={2}>{t('settings.planBilling', 'Plan & Billing')}</Heading>
        {planLoading ? <Text>{t('settings.loading', 'Loading...')}</Text> : (
          <>
            {!planEdit ? (
              <>
                <Text>{t('settings.currentPlan', 'Current Plan: {{plan}}', { plan: planInfo.plan || '-' })}</Text>
                <Text>{t('settings.planExpiry', 'Expiry: {{expiry}}', { expiry: planInfo.plan_expiry || '-' })}</Text>
                <Button mt={2} onClick={() => setPlanEdit(true)}>{t('settings.changePlan', 'Change Plan')}</Button>
                <Button mt={2} colorScheme="green" onClick={handleUpgradePlan} isLoading={planLoading}>{t('settings.upgradePlan', 'Upgrade Plan (PayHere)')}</Button>
              </>
            ) : (
              <>
                <Input placeholder={t('settings.planPlaceholder', 'Plan')} value={planForm.plan} onChange={e => setPlanForm(f => ({ ...f, plan: e.target.value }))} mb={2} />
                <Input placeholder={t('settings.planExpiryPlaceholder', 'Expiry')} value={planForm.plan_expiry} onChange={e => setPlanForm(f => ({ ...f, plan_expiry: e.target.value }))} mb={2} />
                <Button colorScheme="blue" onClick={handleSavePlan} isLoading={planLoading}>{t('settings.save', 'Save')}</Button>
                <Button ml={2} onClick={() => setPlanEdit(false)}>{t('settings.cancel', 'Cancel')}</Button>
              </>
            )}
          </>
        )}
        <Box mt={6}>
          <Heading size="sm" mb={2}>{t('settings.billingInfo', 'Billing Info')}</Heading>
          {billingLoading ? <Text>{t('settings.loading', 'Loading...')}</Text> : (
            <>
              {!billingEdit ? (
                <>
                  <Text>{t('settings.billingEmail', 'Email: {{email}}', { email: billingInfo.billing_email || '-' })}</Text>
                  <Button mt={2} onClick={() => setBillingEdit(true)}>{t('settings.editBilling', 'Edit Billing')}</Button>
                </>
              ) : (
                <>
                  <Input placeholder={t('settings.billingEmailPlaceholder', 'Billing Email')} value={billingForm.billing_email} onChange={e => setBillingForm(f => ({ ...f, billing_email: e.target.value }))} mb={2} />
                  <Button colorScheme="blue" onClick={handleSaveBilling} isLoading={billingLoading}>{t('settings.save', 'Save')}</Button>
                  <Button ml={2} onClick={() => setBillingEdit(false)}>{t('settings.cancel', 'Cancel')}</Button>
                </>
              )}
            </>
          )}
        </Box>
      </Box>

      <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} data-tour="settings-custom-domain-section">
        <Heading size="md" mb={2} data-tour="settings-custom-domain-title">{t('settings.customDomain', 'Custom Domain (White-Label)')}</Heading>
        {!customDomainEdit ? (
          <>
            <Text>{t('settings.currentDomain', 'Current Domain: {{domain}}', { domain: customDomain || '-' })}</Text>
            <Button mt={2} onClick={() => setCustomDomainEdit(true)}>{t('settings.setChangeDomain', 'Set/Change Domain')}</Button>
          </>
        ) : (
          <>
            <Input placeholder={t('settings.customDomainPlaceholder', 'your.customdomain.com')} value={customDomain} onChange={e => setCustomDomain(e.target.value)} mb={2} />
            <Button colorScheme="blue" onClick={handleSaveCustomDomain} isLoading={customDomainLoading}>{t('settings.save', 'Save')}</Button>
            <Button ml={2} onClick={() => setCustomDomainEdit(false)}>{t('settings.cancel', 'Cancel')}</Button>
          </>
        )}
        <Text mt={4} fontSize="sm" color="gray.500">
          {t('settings.customDomainDescription', 'To use a custom domain, point your DNS CNAME to our platform and enter your domain above. SSL will be automatically provisioned.')}
        </Text>
      </Box>

      <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} data-tour="settings-audit-section">
        <Button as={RouterLink} to="/audit-log" colorScheme="gray" mb={2} data-tour="settings-audit-btn">{t('settings.viewActivityHistory', 'View Activity History')}</Button>
      </Box>
    </>
  );
}

export default Settings; 