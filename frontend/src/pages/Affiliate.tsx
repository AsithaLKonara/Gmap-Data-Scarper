import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Input,
  VStack,
  HStack,
  Heading,
  Text,
  useToast,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  FormControl,
  FormLabel,
  Textarea,
  useColorModeValue,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  IconButton,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import {
  FiUsers,
  FiDollarSign,
  FiCopy,
  FiLink,
  FiRefreshCw,
  FiDownload,
  FiTrendingUp,
  FiGift,
} from 'react-icons/fi';

interface Affiliate {
  code: string;
  total_earnings: number;
  is_active: boolean;
  created_at: string;
}

interface Commission {
  id: number;
  amount: number;
  status: string;
  created_at: string;
  paid_at?: string;
  notes?: string;
  referred_user_id: number;
}

const AffiliatePortal: React.FC = () => {
  const { t } = useTranslation();
  const toast = useToast();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  const [affiliate, setAffiliate] = useState<Affiliate | null>(null);
  const [commissions, setCommissions] = useState<Commission[]>([]);
  const [loading, setLoading] = useState(false);
  const [payoutAmount, setPayoutAmount] = useState('');
  const [payoutNotes, setPayoutNotes] = useState('');

  // Mock data - replace with actual API calls
  useEffect(() => {
    const mockAffiliate: Affiliate = {
      code: 'AFF2024',
      total_earnings: 1250.50,
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
    };

    const mockCommissions: Commission[] = [
      {
        id: 1,
        amount: 50.00,
        status: 'paid',
        created_at: '2024-01-15T10:30:00Z',
        paid_at: '2024-01-20T14:00:00Z',
        referred_user_id: 123,
      },
      {
        id: 2,
        amount: 75.00,
        status: 'pending',
        created_at: '2024-01-18T15:45:00Z',
        referred_user_id: 124,
      },
      {
        id: 3,
        amount: 100.00,
        status: 'paid',
        created_at: '2024-01-10T09:15:00Z',
        paid_at: '2024-01-15T11:30:00Z',
        referred_user_id: 125,
      },
    ];

    setAffiliate(mockAffiliate);
    setCommissions(mockCommissions);
  }, []);

  const loadAffiliate = async () => {
    setLoading(true);
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
    } catch (error) {
      toast({
        title: 'Error loading affiliate data',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const loadCommissions = async () => {
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 500));
    } catch (error) {
      toast({
        title: 'Error loading commissions',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleCopyCode = () => {
    if (affiliate?.code) {
      navigator.clipboard.writeText(affiliate.code);
      toast({
        title: 'Affiliate code copied',
        status: 'success',
        duration: 2000,
      });
    }
  };

  const handleCopyLink = () => {
    if (affiliate?.code) {
      const link = `${window.location.origin}/register?aff=${affiliate.code}`;
      navigator.clipboard.writeText(link);
      toast({
        title: 'Affiliate link copied',
        status: 'success',
        duration: 2000,
      });
    }
  };

  const handleGenerateCode = async () => {
    setLoading(true);
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      const newCode = `AFF${Date.now().toString().slice(-6)}`;
      setAffiliate(affiliate ? { ...affiliate, code: newCode } : null);
      toast({
        title: 'New affiliate code generated',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error generating code',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePayoutRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!payoutAmount.trim()) {
      toast({
        title: 'Please enter payout amount',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    setLoading(true);
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      toast({
        title: 'Payout request submitted',
        status: 'success',
        duration: 3000,
      });
      setPayoutAmount('');
      setPayoutNotes('');
    } catch (error) {
      toast({
        title: 'Error submitting payout request',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid':
        return 'green';
      case 'pending':
        return 'yellow';
      case 'cancelled':
        return 'red';
      default:
        return 'gray';
    }
  };

  if (!affiliate) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minH="400px">
        <VStack spacing={4}>
          <FiGift size={48} color="gray" />
          <Text fontSize="lg" fontWeight="medium">
            You need to be an affiliate to access this page
          </Text>
          <Button colorScheme="blue">Become an Affiliate</Button>
        </VStack>
      </Box>
    );
  }

  return (
    <Box>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>Affiliate Portal</Heading>
          <Text color={textColor}>
            Earn money by referring customers to LeadTap
          </Text>
        </Box>

        {/* Stats */}
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
          <Stat>
            <StatLabel>Total Earnings</StatLabel>
            <StatNumber color="green.500">${affiliate.total_earnings.toFixed(2)}</StatNumber>
            <StatHelpText>All time</StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Total Referrals</StatLabel>
            <StatNumber>{commissions.length}</StatNumber>
            <StatHelpText>Successful referrals</StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Commission Rate</StatLabel>
            <StatNumber color="blue.500">15%</StatNumber>
            <StatHelpText>Per successful referral</StatHelpText>
          </Stat>
        </SimpleGrid>

        {/* Affiliate Code Section */}
        <Box
          bg={bgColor}
          border="1px"
          borderColor={borderColor}
          borderRadius="lg"
          p={6}
        >
          <VStack spacing={4} align="stretch">
            <HStack justify="space-between">
              <Heading size="md">Your Affiliate Code</Heading>
              <Button
                leftIcon={<FiRefreshCw />}
                onClick={handleGenerateCode}
                isLoading={loading}
                size="sm"
              >
                Generate New Code
              </Button>
            </HStack>

            <Box
              bg="gray.50"
              p={4}
              borderRadius="md"
              border="1px"
              borderColor="gray.200"
            >
              <HStack justify="space-between">
                <Text fontFamily="mono" fontSize="lg" fontWeight="bold">
                  {affiliate.code}
                </Text>
                <HStack spacing={2}>
                  <IconButton
                    icon={<FiCopy />}
                    onClick={handleCopyCode}
                    aria-label="Copy affiliate code"
                    size="sm"
                  />
                  <IconButton
                    icon={<FiLink />}
                    onClick={handleCopyLink}
                    aria-label="Copy affiliate link"
                    size="sm"
                  />
                </HStack>
              </HStack>
            </Box>

            <Alert status="info" borderRadius="md">
              <AlertIcon />
              <Box>
                <AlertTitle>How it works</AlertTitle>
                <AlertDescription>
                  Share your affiliate link with potential customers. You'll earn 15% commission
                  on their first month's subscription.
                </AlertDescription>
              </Box>
            </Alert>
          </VStack>
        </Box>

        {/* Payout Request */}
        <Box
          bg={bgColor}
          border="1px"
          borderColor={borderColor}
          borderRadius="lg"
          p={6}
        >
          <Heading size="md" mb={4}>Request Payout</Heading>
          <form onSubmit={handlePayoutRequest}>
            <VStack spacing={4} align="stretch">
              <FormControl isRequired>
                <FormLabel>Payout Amount ($)</FormLabel>
                <Input
                  type="number"
                  value={payoutAmount}
                  onChange={(e) => setPayoutAmount(e.target.value)}
                  placeholder="Enter amount"
                  min="10"
                  step="0.01"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Notes (Optional)</FormLabel>
                <Textarea
                  value={payoutNotes}
                  onChange={(e) => setPayoutNotes(e.target.value)}
                  placeholder="Any additional notes..."
                  rows={3}
                />
              </FormControl>

              <Button
                type="submit"
                leftIcon={<FiDownload />}
                isLoading={loading}
                colorScheme="blue"
              >
                Request Payout
              </Button>
            </VStack>
          </form>
        </Box>

        {/* Commissions Table */}
        <Box
          bg={bgColor}
          border="1px"
          borderColor={borderColor}
          borderRadius="lg"
          overflow="hidden"
        >
          <Box p={6} borderBottom="1px" borderColor={borderColor}>
            <Heading size="md">Commission History</Heading>
          </Box>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Date</Th>
                <Th>Amount</Th>
                <Th>Status</Th>
                <Th>Paid Date</Th>
              </Tr>
            </Thead>
            <Tbody>
              {commissions.map((commission) => (
                <Tr key={commission.id}>
                  <Td>{new Date(commission.created_at).toLocaleDateString()}</Td>
                  <Td>${commission.amount.toFixed(2)}</Td>
                  <Td>
                    <Badge colorScheme={getStatusColor(commission.status)}>
                      {commission.status}
                    </Badge>
                  </Td>
                  <Td>
                    {commission.paid_at
                      ? new Date(commission.paid_at).toLocaleDateString()
                      : '-'}
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      </VStack>
    </Box>
  );
};

export default AffiliatePortal; 