import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Text,
  HStack,
  VStack,
  Input,
  Button,
  useToast,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  IconButton,
  FormControl,
  FormLabel,
  Switch,
  Divider,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useColorModeValue,
  Badge,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import {
  FiCopy,
  FiDownload,
  FiTrash2,
  FiShield,
  FiKey,
  FiGlobe,
  FiCreditCard,
  FiUsers,
  FiSettings,
} from 'react-icons/fi';

const Settings: React.FC = () => {
  const { t } = useTranslation();
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  // State management
  const [webhookUrl, setWebhookUrl] = useState('');
  const [webhookLoading, setWebhookLoading] = useState(false);
  const [twoFAEnabled, setTwoFAEnabled] = useState(false);
  const [twoFALoading, setTwoFALoading] = useState(false);
  const [securityStatus, setSecurityStatus] = useState<any>(null);
  const [planInfo, setPlanInfo] = useState<any>({});
  const [billingInfo, setBillingInfo] = useState<any>({});
  const [customDomain, setCustomDomain] = useState('');
  const [referralCode, setReferralCode] = useState('');

  // Mock data - replace with actual API calls
  useEffect(() => {
    // Simulate loading data
    setSecurityStatus({
      twoFAEnabled: false,
      lastLogin: '2024-01-15T10:30:00Z',
      loginHistory: [
        { date: '2024-01-15', ip: '192.168.1.1', location: 'New York' },
        { date: '2024-01-14', ip: '192.168.1.1', location: 'New York' },
      ],
    });
    
    setPlanInfo({
      plan: 'Pro',
      status: 'active',
      nextBilling: '2024-02-15',
      features: ['Google Maps', 'Facebook', 'Instagram', 'WhatsApp'],
    });
    
    setBillingInfo({
      email: 'billing@example.com',
      card: '**** **** **** 1234',
      nextPayment: '$29.00',
    });
  }, []);

  const handleSaveWebhook = async () => {
    setWebhookLoading(true);
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast({
        title: 'Webhook saved',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error saving webhook',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setWebhookLoading(false);
    }
  };

  const handleTestWebhook = async () => {
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast({
        title: 'Webhook test successful',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Webhook test failed',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleToggle2FA = async () => {
    setTwoFALoading(true);
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setTwoFAEnabled(!twoFAEnabled);
      toast({
        title: twoFAEnabled ? '2FA disabled' : '2FA enabled',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error updating 2FA',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setTwoFALoading(false);
    }
  };

  const handleSaveCustomDomain = async () => {
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast({
        title: 'Custom domain saved',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error saving domain',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: 'Copied to clipboard',
      status: 'success',
      duration: 2000,
    });
  };

  return (
    <Box>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>Settings</Heading>
          <Text color={textColor}>Manage your account settings and preferences</Text>
        </Box>

        {/* Security Settings */}
        <Box
          bg={bgColor}
          border="1px"
          borderColor={borderColor}
          borderRadius="lg"
          p={6}
        >
          <HStack justify="space-between" mb={4}>
            <VStack align="start" spacing={1}>
              <HStack>
                <FiShield />
                <Heading size="md">Security</Heading>
              </HStack>
              <Text fontSize="sm" color={textColor}>Manage your account security</Text>
            </VStack>
          </HStack>

          <VStack spacing={4} align="stretch">
            {/* 2FA Setting */}
            <HStack justify="space-between">
              <VStack align="start" spacing={1}>
                <Text fontWeight="medium">Two-Factor Authentication</Text>
                <Text fontSize="sm" color={textColor}>
                  Add an extra layer of security to your account
                </Text>
              </VStack>
              <Switch
                isChecked={twoFAEnabled}
                onChange={handleToggle2FA}
                isDisabled={twoFALoading}
              />
            </HStack>

            {/* Last Login */}
            {securityStatus && (
              <Box>
                <Text fontSize="sm" fontWeight="medium" mb={2}>Last Login</Text>
                <Text fontSize="sm" color={textColor}>
                  {new Date(securityStatus.lastLogin).toLocaleString()}
                </Text>
              </Box>
            )}

            <Divider />

            {/* Login History */}
            {securityStatus?.loginHistory && (
              <Box>
                <Text fontSize="sm" fontWeight="medium" mb={2}>Recent Logins</Text>
                <VStack spacing={2} align="stretch">
                  {securityStatus.loginHistory.map((login: any, index: number) => (
                    <HStack key={index} justify="space-between">
                      <Text fontSize="sm">{login.date}</Text>
                      <Text fontSize="sm" color={textColor}>{login.location}</Text>
                    </HStack>
                  ))}
                </VStack>
              </Box>
            )}
          </VStack>
        </Box>

        {/* Webhook Settings */}
        <Box
          bg={bgColor}
          border="1px"
          borderColor={borderColor}
          borderRadius="lg"
          p={6}
        >
          <HStack justify="space-between" mb={4}>
            <VStack align="start" spacing={1}>
              <HStack>
                <FiGlobe />
                <Heading size="md">Webhooks</Heading>
              </HStack>
              <Text fontSize="sm" color={textColor}>Configure webhook notifications</Text>
            </VStack>
          </HStack>

          <VStack spacing={4} align="stretch">
            <FormControl>
              <FormLabel>Webhook URL</FormLabel>
              <HStack>
                <Input
                  value={webhookUrl}
                  onChange={(e) => setWebhookUrl(e.target.value)}
                  placeholder="https://your-domain.com/webhook"
                />
                <IconButton
                  icon={<FiCopy />}
                  onClick={() => copyToClipboard(webhookUrl)}
                  aria-label="Copy webhook URL"
                />
              </HStack>
            </FormControl>

            <HStack spacing={2}>
              <Button
                onClick={handleSaveWebhook}
                isLoading={webhookLoading}
                colorScheme="blue"
              >
                Save Webhook
              </Button>
              <Button
                onClick={handleTestWebhook}
                variant="outline"
              >
                Test Webhook
              </Button>
            </HStack>
          </VStack>
        </Box>

        {/* Plan & Billing */}
        <Box
          bg={bgColor}
          border="1px"
          borderColor={borderColor}
          borderRadius="lg"
          p={6}
        >
          <HStack justify="space-between" mb={4}>
            <VStack align="start" spacing={1}>
              <HStack>
                <FiCreditCard />
                <Heading size="md">Plan & Billing</Heading>
              </HStack>
              <Text fontSize="sm" color={textColor}>Manage your subscription and billing</Text>
            </VStack>
          </HStack>

          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
            {/* Current Plan */}
            <Box>
              <Text fontSize="sm" fontWeight="medium" mb={2}>Current Plan</Text>
              <HStack spacing={2} mb={2}>
                <Badge colorScheme="green">{planInfo.plan}</Badge>
                <Badge colorScheme="blue">{planInfo.status}</Badge>
              </HStack>
              <Text fontSize="sm" color={textColor}>
                Next billing: {planInfo.nextBilling}
              </Text>
            </Box>

            {/* Billing Info */}
            <Box>
              <Text fontSize="sm" fontWeight="medium" mb={2}>Billing Email</Text>
              <Text fontSize="sm" color={textColor}>{billingInfo.email}</Text>
              <Text fontSize="sm" color={textColor} mt={1}>
                Next payment: {billingInfo.nextPayment}
              </Text>
            </Box>
          </SimpleGrid>

          <Button mt={4} colorScheme="blue" variant="outline">
            Manage Billing
          </Button>
        </Box>

        {/* Custom Domain */}
        <Box
          bg={bgColor}
          border="1px"
          borderColor={borderColor}
          borderRadius="lg"
          p={6}
        >
          <HStack justify="space-between" mb={4}>
            <VStack align="start" spacing={1}>
              <HStack>
                <FiGlobe />
                <Heading size="md">Custom Domain</Heading>
              </HStack>
              <Text fontSize="sm" color={textColor}>Set up a custom domain for your account</Text>
            </VStack>
          </HStack>

          <VStack spacing={4} align="stretch">
            <FormControl>
              <FormLabel>Domain</FormLabel>
              <Input
                value={customDomain}
                onChange={(e) => setCustomDomain(e.target.value)}
                placeholder="your-domain.com"
              />
            </FormControl>

            <Button
              onClick={handleSaveCustomDomain}
              colorScheme="blue"
            >
              Save Domain
            </Button>
          </VStack>
        </Box>

        {/* Referral Program */}
        <Box
          bg={bgColor}
          border="1px"
          borderColor={borderColor}
          borderRadius="lg"
          p={6}
        >
          <HStack justify="space-between" mb={4}>
            <VStack align="start" spacing={1}>
              <HStack>
                <FiUsers />
                <Heading size="md">Referral Program</Heading>
              </HStack>
              <Text fontSize="sm" color={textColor}>Earn credits by referring friends</Text>
            </VStack>
          </HStack>

          <VStack spacing={4} align="stretch">
            <Box>
              <Text fontSize="sm" fontWeight="medium" mb={2}>Your Referral Code</Text>
              <HStack>
                <Input
                  value={referralCode}
                  onChange={(e) => setReferralCode(e.target.value)}
                  placeholder="Enter referral code"
                />
                <Button variant="outline">Apply</Button>
              </HStack>
            </Box>

            <Stat>
              <StatLabel>Referrals</StatLabel>
              <StatNumber>0</StatNumber>
              <StatHelpText>Total referrals this month</StatHelpText>
            </Stat>
          </VStack>
        </Box>
      </VStack>
    </Box>
  );
};

export default Settings; 