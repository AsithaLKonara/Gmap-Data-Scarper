import { getWebhookUrl, setWebhookUrl, deleteWebhookUrl, testWebhook, connectCRM, getCRMStatus, disconnectCRM, enable2FA, verify2FA, disable2FA, exportUserData, deleteAccount, getReferralInfo, useReferralCode, getReferralStats, getUsage, purchaseCredits, getTenantSsoConfig, updateTenantSsoConfig, getTenantPlan, updateTenantPlan, getTenantBilling, updateTenantBilling } from '../api';
import { useState, useEffect } from 'react';
import { Box, Heading, Text, HStack, Input, Button, toast, useToast } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import QRCode from 'qrcode.react';

const [webhookUrl, setWebhookUrlState] = useState('');
const [webhookLoading, setWebhookLoading] = useState(false);
const [webhookTestResult, setWebhookTestResult] = useState<string | null>(null);
const [crmStatus, setCrmStatus] = useState<any>(null);
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
const tenantId = localStorage.getItem('tenantId');

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
  }
}, [tenantId]);

const handleSaveWebhook = async () => {
  setWebhookLoading(true);
  try {
    await setWebhookUrl(webhookUrl);
    toast({ title: 'Webhook URL saved', status: 'success' });
  } catch (e: any) {
    toast({ title: 'Error', description: e.message, status: 'error' });
  } finally {
    setWebhookLoading(false);
  }
};
const handleDeleteWebhook = async () => {
  setWebhookLoading(true);
  try {
    await deleteWebhookUrl();
    setWebhookUrlState('');
    toast({ title: 'Webhook URL deleted', status: 'info' });
  } catch (e: any) {
    toast({ title: 'Error', description: e.message, status: 'error' });
  } finally {
    setWebhookLoading(false);
  }
};
const handleTestWebhook = async () => {
  setWebhookLoading(true);
  setWebhookTestResult(null);
  try {
    const res = await testWebhook();
    setWebhookTestResult(`Success! Response code: ${res.response_code}`);
    toast({ title: 'Test sent', status: 'success' });
  } catch (e: any) {
    setWebhookTestResult(`Failed: ${e.message}`);
    toast({ title: 'Error', description: e.message, status: 'error' });
  } finally {
    setWebhookLoading(false);
  }
};

const handleConnectCRM = async (provider: string) => {
  setCrmLoading(true);
  try {
    const res = await connectCRM(provider);
    setCrmStatus((s: any) => ({ ...s, crm_provider: provider, crm_connected: false }));
    toast({ title: `Connect to ${provider}`, description: 'OAuth flow will start (stub)', status: 'info' });
  } catch (e: any) {
    toast({ title: 'Error', description: e.message, status: 'error' });
  } finally {
    setCrmLoading(false);
  }
};
const handleDisconnectCRM = async () => {
  setCrmLoading(true);
  try {
    await disconnectCRM();
    setCrmStatus(null);
    toast({ title: 'Disconnected', status: 'info' });
  } catch (e: any) {
    toast({ title: 'Error', description: e.message, status: 'error' });
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
    setTwoFAStatus('Scan the QR code or enter the secret in your authenticator app.');
  } catch (e: any) {
    toast({ title: 'Error', description: e.message, status: 'error' });
  } finally {
    setTwoFALoading(false);
  }
};
const handleVerify2FA = async () => {
  setTwoFALoading(true);
  try {
    await verify2FA(twoFACode);
    setTwoFAEnabled(true);
    setTwoFAStatus('2FA enabled!');
    toast({ title: '2FA enabled', status: 'success' });
  } catch (e: any) {
    setTwoFAStatus('Invalid code.');
    toast({ title: 'Error', description: e.message, status: 'error' });
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
    setTwoFAStatus('2FA disabled.');
    toast({ title: '2FA disabled', status: 'info' });
  } catch (e: any) {
    toast({ title: 'Error', description: e.message, status: 'error' });
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
    toast({ title: 'Data exported', status: 'success' });
  } catch (e: any) {
    toast({ title: 'Error', description: e.message, status: 'error' });
  } finally {
    setGdprLoading(false);
  }
};
const handleDeleteAccount = async () => {
  setGdprLoading(true);
  try {
    await deleteAccount();
    toast({ title: 'Account deleted', status: 'info' });
    // Optionally redirect or log out
  } catch (e: any) {
    toast({ title: 'Error', description: e.message, status: 'error' });
  } finally {
    setGdprLoading(false);
  }
};

const handleUseReferral = async () => {
  setReferralLoading(true);
  try {
    await useReferralCode(referralCodeInput);
    setReferralUsed(true);
    toast({ title: 'Referral applied', status: 'success' });
  } catch (e: any) {
    toast({ title: 'Error', description: e.message, status: 'error' });
  } finally {
    setReferralLoading(false);
  }
};

const handlePurchaseCredits = async () => {
  setUsageLoading(true);
  try {
    await purchaseCredits(purchaseAmount);
    toast({ title: 'Credits purchased', status: 'success' });
    getUsage().then(setUsageInfo);
  } catch (e: any) {
    toast({ title: 'Error', description: e.message, status: 'error' });
  } finally {
    setUsageLoading(false);
  }
};

const handleSaveSsoConfig = async () => {
  setSsoLoading(true);
  try {
    await updateTenantSsoConfig(tenantId, { sso_config: ssoForm });
    setSsoConfig(ssoForm);
    setSsoEdit(false);
    toast({ title: 'SSO config saved', status: 'success' });
  } catch (e: any) {
    toast({ title: 'Error', description: e.message, status: 'error' });
  } finally {
    setSsoLoading(false);
  }
};

const handleSavePlan = async () => {
  setPlanLoading(true);
  try {
    await updateTenantPlan(tenantId, planForm);
    setPlanInfo(planForm);
    setPlanEdit(false);
    toast({ title: 'Plan updated', status: 'success' });
  } catch (e: any) {
    toast({ title: 'Error', description: e.message, status: 'error' });
  } finally {
    setPlanLoading(false);
  }
};
const handleSaveBilling = async () => {
  setBillingLoading(true);
  try {
    await updateTenantBilling(tenantId, billingForm);
    setBillingInfo(billingForm);
    setBillingEdit(false);
    toast({ title: 'Billing info updated', status: 'success' });
  } catch (e: any) {
    toast({ title: 'Error', description: e.message, status: 'error' });
  } finally {
    setBillingLoading(false);
  }
};

<Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} data-tour="settings-webhook-section">
  <Heading size="md" mb={2} data-tour="settings-webhook-title">Webhook Management</Heading>
  <Text fontSize="sm" color="gray.600" mb={2}>Receive real-time notifications in your own systems or Zapier. Enter your webhook URL below.</Text>
  <HStack>
    <Input value={webhookUrl} onChange={e => setWebhookUrlState(e.target.value)} placeholder="https://your-webhook-url.com/endpoint" />
    <Button colorScheme="blue" onClick={handleSaveWebhook} isLoading={webhookLoading}>Save</Button>
    <Button colorScheme="red" onClick={handleDeleteWebhook} isLoading={webhookLoading} isDisabled={!webhookUrl}>Delete</Button>
    <Button colorScheme="green" onClick={handleTestWebhook} isLoading={webhookLoading} isDisabled={!webhookUrl}>Test</Button>
  </HStack>
  {webhookTestResult && <Text mt={2}>{webhookTestResult}</Text>}
</Box>

<Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8}>
  <Heading size="md" mb={2}>Zapier Integration</Heading>
  <Text fontSize="sm" color="gray.600" mb={2}>
    Connect LeadTap to 5,000+ apps using Zapier! Use your webhook URL above as a Zapier trigger to automate workflows like adding leads to your CRM, sending notifications, or updating spreadsheets.
  </Text>
  <Text fontSize="sm" mb={2}>
    <b>How to use:</b>
    <ol style={{ marginLeft: 20 }}>
      <li>Go to <a href="https://zapier.com/app/editor" target="_blank" rel="noopener noreferrer">Zapier Editor</a>.</li>
      <li>Choose <b>Webhooks by Zapier</b> as the trigger app.</li>
      <li>Select <b>Catch Hook</b> and paste your webhook URL from above.</li>
      <li>Test the trigger using the <b>Test</b> button above.</li>
      <li>Connect any action app (e.g., Gmail, Google Sheets, Slack, HubSpot, etc.).</li>
    </ol>
  </Text>
  <Text fontSize="sm" color="gray.500">
    Need a template? Try this: <a href="https://zapier.com/apps/webhook/integrations" target="_blank" rel="noopener noreferrer">Zapier Webhook Templates</a>
  </Text>
  <Text fontSize="xs" color="gray.400" mt={2}>
    Tip: You can use filters and formatting in Zapier to customize your automation.
  </Text>
</Box>

<Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} data-tour="settings-crm-section">
  <Heading size="md" mb={2} data-tour="settings-crm-title">CRM & Email Integration</Heading>
  <Text fontSize="sm" color="gray.600" mb={2}>
    Connect your account to external CRMs (HubSpot, Salesforce) or email marketing tools (Mailchimp) to sync leads and automate campaigns.
  </Text>
  <Text fontSize="sm" mb={2}>
    Status: {crmStatus ? (crmStatus.crm_connected ? `Connected to ${crmStatus.crm_provider}` : `Not connected (${crmStatus.crm_provider || 'none'})`) : 'Not connected'}
  </Text>
  <HStack>
    <Button colorScheme="blue" onClick={() => handleConnectCRM('hubspot')} isLoading={crmLoading} isDisabled={crmStatus?.crm_connected}>Connect HubSpot</Button>
    <Button colorScheme="orange" onClick={() => handleConnectCRM('salesforce')} isLoading={crmLoading} isDisabled={crmStatus?.crm_connected}>Connect Salesforce</Button>
    <Button colorScheme="green" onClick={() => handleConnectCRM('mailchimp')} isLoading={crmLoading} isDisabled={crmStatus?.email_connected}>Connect Mailchimp</Button>
    <Button colorScheme="red" onClick={handleDisconnectCRM} isLoading={crmLoading} isDisabled={!crmStatus?.crm_connected && !crmStatus?.email_connected}>Disconnect</Button>
  </HStack>
</Box>

<Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} data-tour="settings-2fa-section">
  <Heading size="md" mb={2} data-tour="settings-2fa-title">Two-Factor Authentication (2FA)</Heading>
  <Text fontSize="sm" color="gray.600" mb={2}>
    Protect your account with an extra layer of security. Use an authenticator app (Google Authenticator, Authy, etc.).
  </Text>
  {twoFAEnabled ? (
    <Button colorScheme="red" onClick={handleDisable2FA} isLoading={twoFALoading}>Disable 2FA</Button>
  ) : (
    <Button colorScheme="blue" onClick={handleEnable2FA} isLoading={twoFALoading}>Enable 2FA</Button>
  )}
  {twoFAUri && (
    <Box mt={4}>
      <Text mb={2}>Scan this QR code in your authenticator app:</Text>
      <QRCode value={twoFAUri} size={180} />
      <Text mt={2} fontSize="sm">Or enter this secret: <b>{twoFASecret}</b></Text>
      <Box mt={2}>
        <Text mb={1}>Enter code from app:</Text>
        <input value={twoFACode} onChange={e => setTwoFACode(e.target.value)} placeholder="123456" style={{ padding: 8, border: '1px solid #ccc', borderRadius: 4 }} />
        <Button ml={2} colorScheme="green" onClick={handleVerify2FA} isLoading={twoFALoading}>Verify</Button>
      </Box>
      {twoFAStatus && <Text mt={2}>{twoFAStatus}</Text>}
    </Box>
  )}
</Box>

<Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} data-tour="settings-gdpr-section">
  <Heading size="md" mb={2} data-tour="settings-gdpr-title">GDPR & Privacy</Heading>
  <Text fontSize="sm" color="gray.600" mb={2}>
    You can export all your data or request account deletion at any time.
  </Text>
  <Button colorScheme="blue" onClick={handleExportData} isLoading={gdprLoading} mb={2}>Export My Data (JSON)</Button>
  {gdprExportUrl && <a href={gdprExportUrl} download="leadtap_data.json"><Button colorScheme="green" mb={2}>Download Export</Button></a>}
  <Button colorScheme="red" onClick={() => setDeleteConfirm(true)} isLoading={gdprLoading}>Delete My Account</Button>
  {deleteConfirm && (
    <Box mt={2}>
      <Text color="red.500" mb={2}>Are you sure? This will permanently delete your account and all data. This action cannot be undone.</Text>
      <Button colorScheme="red" onClick={handleDeleteAccount} isLoading={gdprLoading}>Yes, Delete My Account</Button>
      <Button ml={2} onClick={() => setDeleteConfirm(false)}>Cancel</Button>
    </Box>
  )}
</Box>

<Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8}>
  <Heading size="md" mb={2}>Referral Program</Heading>
  {referralInfo && (
    <>
      <Text fontSize="sm" color="gray.600" mb={2}>Share your referral link to earn credits! Both you and your friends get rewards.</Text>
      <Text mb={2}><b>Referral Link:</b> <Input value={referralInfo.referral_link} isReadOnly w="60%" display="inline-block" mr={2} /><Button size="sm" onClick={() => {navigator.clipboard.writeText(referralInfo.referral_link); toast({ title: 'Copied', status: 'success' });}}>Copy</Button></Text>
      <Text mb={2}><b>Referred:</b> {referralInfo.referred_count} | <b>Credits:</b> {referralInfo.referral_credits}</Text>
    </>
  )}
  {referralStats && referralStats.referred && referralStats.referred.length > 0 && (
    <Box mt={4}>
      <Text fontWeight="bold" mb={2}>Your Referrals:</Text>
      {referralStats.referred.map((u: any) => (
        <Text key={u.email} fontSize="sm">{u.email} (joined {new Date(u.created_at).toLocaleDateString()}) - Credits: {u.credits}</Text>
      ))}
    </Box>
  )}
  {!referralUsed && (
    <Box mt={4}>
      <Text fontSize="sm" mb={1}>Have a referral code?</Text>
      <Input value={referralCodeInput} onChange={e => setReferralCodeInput(e.target.value)} placeholder="Enter referral code" w="40%" display="inline-block" mr={2} />
      <Button size="sm" colorScheme="blue" onClick={handleUseReferral} isLoading={referralLoading}>Apply</Button>
    </Box>
  )}
</Box>

<Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} data-tour="settings-usage-section">
  <Heading size="md" mb={2} data-tour="settings-usage-title">Usage & Billing</Heading>
  {usageInfo && (
    <>
      <Text mb={2}><b>Plan:</b> {usageInfo.plan}</Text>
      <Text mb={2}><b>Jobs Today:</b> {usageInfo.jobs_today} / {usageInfo.max_queries_per_day}</Text>
      <Text mb={2}><b>Usage Credits:</b> {usageInfo.usage_credits} | <b>Referral Credits:</b> {usageInfo.referral_credits}</Text>
      <HStack mt={2}>
        <Input type="number" value={purchaseAmount} min={1} onChange={e => setPurchaseAmount(Number(e.target.value))} w="120px" />
        <Button colorScheme="blue" onClick={handlePurchaseCredits} isLoading={usageLoading}>Purchase Credits</Button>
      </HStack>
    </>
  )}
</Box>

<Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} data-tour="settings-sso-section">
  <Heading size="md" mb={2} data-tour="settings-sso-title">SSO/SAML Configuration</Heading>
  {ssoLoading ? <Text>Loading...</Text> : (
    <>
      {!ssoEdit ? (
        <>
          <Text>Entity ID: {ssoConfig.entity_id || '-'}</Text>
          <Text>SSO URL: {ssoConfig.sso_url || '-'}</Text>
          <Text>Certificate: {ssoConfig.cert ? '[set]' : '-'}</Text>
          <Button mt={2} onClick={() => setSsoEdit(true)}>Edit</Button>
        </>
      ) : (
        <>
          <Input placeholder="Entity ID" value={ssoForm.entity_id} onChange={e => setSsoForm(f => ({ ...f, entity_id: e.target.value }))} mb={2} />
          <Input placeholder="SSO URL" value={ssoForm.sso_url} onChange={e => setSsoForm(f => ({ ...f, sso_url: e.target.value }))} mb={2} />
          <Input placeholder="Certificate" value={ssoForm.cert} onChange={e => setSsoForm(f => ({ ...f, cert: e.target.value }))} mb={2} />
          <Button colorScheme="blue" onClick={handleSaveSsoConfig} isLoading={ssoLoading}>Save</Button>
          <Button ml={2} onClick={() => setSsoEdit(false)}>Cancel</Button>
        </>
      )}
    </>
  )}
</Box>

<Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8}>
  <Heading size="md" mb={2}>Plan & Billing</Heading>
  {planLoading ? <Text>Loading...</Text> : (
    <>
      {!planEdit ? (
        <>
          <Text>Current Plan: {planInfo.plan || '-'}</Text>
          <Text>Expiry: {planInfo.plan_expiry || '-'}</Text>
          <Button mt={2} onClick={() => setPlanEdit(true)}>Change Plan</Button>
        </>
      ) : (
        <>
          <Input placeholder="Plan" value={planForm.plan} onChange={e => setPlanForm(f => ({ ...f, plan: e.target.value }))} mb={2} />
          <Input placeholder="Expiry" value={planForm.plan_expiry} onChange={e => setPlanForm(f => ({ ...f, plan_expiry: e.target.value }))} mb={2} />
          <Button colorScheme="blue" onClick={handleSavePlan} isLoading={planLoading}>Save</Button>
          <Button ml={2} onClick={() => setPlanEdit(false)}>Cancel</Button>
        </>
      )}
    </>
  )}
  <Box mt={6}>
    <Heading size="sm" mb={2}>Billing Info</Heading>
    {billingLoading ? <Text>Loading...</Text> : (
      <>
        {!billingEdit ? (
          <>
            <Text>Email: {billingInfo.billing_email || '-'}</Text>
            <Button mt={2} onClick={() => setBillingEdit(true)}>Edit Billing</Button>
          </>
        ) : (
          <>
            <Input placeholder="Billing Email" value={billingForm.billing_email} onChange={e => setBillingForm(f => ({ ...f, billing_email: e.target.value }))} mb={2} />
            <Button colorScheme="blue" onClick={handleSaveBilling} isLoading={billingLoading}>Save</Button>
            <Button ml={2} onClick={() => setBillingEdit(false)}>Cancel</Button>
          </>
        )}
      </>
    )}
  </Box>
</Box>

<Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor} boxShadow="md" mb={8} data-tour="settings-audit-section">
  <Button as={RouterLink} to="/audit-log" colorScheme="gray" mb={2} data-tour="settings-audit-btn">
    View Activity History
  </Button>
</Box> 