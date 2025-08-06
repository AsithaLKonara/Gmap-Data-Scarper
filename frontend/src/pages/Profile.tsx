import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  useToast,
  Spinner,
  Avatar,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Select,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  useColorModeValue,
  Alert,
  AlertIcon,
  Divider,
  Badge,
  Flex,
  IconButton,
  Tooltip,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import {
  FiEdit,
  FiCheck,
  FiX,
  FiUser,
  FiMail,
  FiPhone,
  FiGlobe,
  FiHome,
  FiCalendar,
  FiTrendingUp,
  FiUsers,
  FiTarget,
  FiMapPin,
  FiSettings,
  FiShield,
  FiCreditCard,
  FiBell,
  FiLogOut,
} from 'react-icons/fi';

interface UserProfile {
  id: number;
  user_id: number;
  first_name?: string;
  last_name?: string;
  avatar?: string;
  phone?: string;
  company?: string;
  website?: string;
  bio?: string;
  timezone: string;
  created_at: string;
  updated_at: string;
}

interface UserInfo {
  id: number;
  email: string;
  plan: string;
  created_at: string;
  profile?: UserProfile;
}

interface UserStats {
  total_jobs: number;
  completed_jobs: number;
  success_rate: number;
  total_leads: number;
  account_age_days: number;
}

const Profile: React.FC = () => {
  const { t } = useTranslation();
  const toast = useToast();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    company: '',
    website: '',
    bio: '',
    timezone: 'UTC',
  });

  const [referral, setReferral] = useState<any>(null);
  const [referralStatus, setReferralStatus] = useState<any[]>([]);
  const [applyCode, setApplyCode] = useState('');

  // Mock data - replace with actual API calls
  useEffect(() => {
    const mockUserInfo: UserInfo = {
      id: 1,
      email: 'john.doe@example.com',
      plan: 'Pro',
      created_at: '2024-01-01T00:00:00Z',
      profile: {
        id: 1,
        user_id: 1,
        first_name: 'John',
        last_name: 'Doe',
        avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
        phone: '+1234567890',
        company: 'Tech Corp',
        website: 'https://johndoe.com',
        bio: 'Lead generation specialist with 5+ years of experience.',
        timezone: 'America/New_York',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-15T10:30:00Z',
      },
    };

    const mockUserStats: UserStats = {
      total_jobs: 150,
      completed_jobs: 142,
      success_rate: 94.7,
      total_leads: 2847,
      account_age_days: 15,
    };

    const mockReferral = {
      code: 'JOHN2024',
      total_referrals: 5,
      total_earned: 50,
    };

    setUserInfo(mockUserInfo);
    setUserStats(mockUserStats);
    setReferral(mockReferral);
    
    if (mockUserInfo.profile) {
      setFormData({
        first_name: mockUserInfo.profile.first_name || '',
        last_name: mockUserInfo.profile.last_name || '',
        phone: mockUserInfo.profile.phone || '',
        company: mockUserInfo.profile.company || '',
        website: mockUserInfo.profile.website || '',
        bio: mockUserInfo.profile.bio || '',
        timezone: mockUserInfo.profile.timezone,
      });
    }
  }, []);

  const handleAvatarChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setAvatarFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setAvatarPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const uploadAvatar = async () => {
    if (!avatarFile) return;

    setLoading(true);
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 2000));
      toast({
        title: 'Avatar updated',
        status: 'success',
        duration: 3000,
      });
      setAvatarFile(null);
      setAvatarPreview(null);
    } catch (error) {
      toast({
        title: 'Error uploading avatar',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async () => {
    setLoading(true);
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setEditing(false);
      toast({
        title: 'Profile updated',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error updating profile',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCopyReferral = () => {
    if (referral?.code) {
      navigator.clipboard.writeText(referral.code);
      toast({
        title: 'Referral code copied',
        status: 'success',
        duration: 2000,
      });
    }
  };

  const handleApplyReferral = async () => {
    if (!applyCode) {
      toast({
        title: 'Please enter a referral code',
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
        title: 'Referral code applied',
        status: 'success',
        duration: 3000,
      });
      setApplyCode('');
    } catch (error) {
      toast({
        title: 'Error applying referral code',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const getPlanColor = (plan: string) => {
    switch (plan.toLowerCase()) {
      case 'pro':
        return 'blue';
      case 'business':
        return 'purple';
      case 'enterprise':
        return 'green';
      default:
        return 'gray';
    }
  };

  if (!userInfo) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minH="400px">
        <Spinner size="xl" />
      </Box>
    );
  }

  return (
    <Container maxW="1200px" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>Profile</Heading>
          <Text color={textColor}>Manage your account profile and settings</Text>
        </Box>

        {/* Profile Stats */}
        {userStats && (
          <SimpleGrid columns={{ base: 1, md: 4 }} spacing={6}>
            <Stat>
              <StatLabel>Total Jobs</StatLabel>
              <StatNumber>{userStats.total_jobs}</StatNumber>
              <StatHelpText>All time</StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Success Rate</StatLabel>
              <StatNumber color="green.500">{userStats.success_rate}%</StatNumber>
              <StatHelpText>Completed successfully</StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Total Leads</StatLabel>
              <StatNumber color="blue.500">{userStats.total_leads.toLocaleString()}</StatNumber>
              <StatHelpText>Generated</StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Account Age</StatLabel>
              <StatNumber color="purple.500">{userStats.account_age_days} days</StatNumber>
              <StatHelpText>Member since</StatHelpText>
            </Stat>
          </SimpleGrid>
        )}

        {/* Profile Information */}
        <Box
          bg={bgColor}
          border="1px"
          borderColor={borderColor}
          borderRadius="lg"
          p={6}
        >
          <HStack justify="space-between" mb={6}>
            <Heading size="md">Profile Information</Heading>
            <Button
              leftIcon={editing ? <FiCheck /> : <FiEdit />}
              onClick={editing ? updateProfile : () => setEditing(true)}
              isLoading={loading}
              colorScheme={editing ? 'green' : 'blue'}
            >
              {editing ? 'Save Changes' : 'Edit Profile'}
            </Button>
          </HStack>

          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
            {/* Avatar Section */}
            <VStack spacing={4} align="center">
              <Avatar
                size="2xl"
                src={avatarPreview || userInfo.profile?.avatar}
                name={`${userInfo.profile?.first_name} ${userInfo.profile?.last_name}`}
              />
              {editing && (
                <VStack spacing={2}>
                  <Input
                    type="file"
                    accept="image/*"
                    onChange={handleAvatarChange}
                    size="sm"
                  />
                  {avatarFile && (
                    <Button size="sm" onClick={uploadAvatar} isLoading={loading}>
                      Upload Avatar
                    </Button>
                  )}
                </VStack>
              )}
            </VStack>

            {/* Profile Form */}
            <VStack spacing={4} align="stretch">
              <HStack spacing={4}>
                <FormControl>
                  <FormLabel>First Name</FormLabel>
                  <Input
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    isDisabled={!editing}
                  />
                </FormControl>
                <FormControl>
                  <FormLabel>Last Name</FormLabel>
                  <Input
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    isDisabled={!editing}
                  />
                </FormControl>
              </HStack>

              <FormControl>
                <FormLabel>Email</FormLabel>
                <Input value={userInfo.email} isDisabled />
              </FormControl>

              <FormControl>
                <FormLabel>Phone</FormLabel>
                <Input
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  isDisabled={!editing}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Company</FormLabel>
                <Input
                  value={formData.company}
                  onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                  isDisabled={!editing}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Website</FormLabel>
                <Input
                  value={formData.website}
                  onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                  isDisabled={!editing}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Bio</FormLabel>
                <Textarea
                  value={formData.bio}
                  onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                  isDisabled={!editing}
                  rows={3}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Timezone</FormLabel>
                <Select
                  value={formData.timezone}
                  onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
                  isDisabled={!editing}
                >
                  <option value="UTC">UTC</option>
                  <option value="America/New_York">Eastern Time</option>
                  <option value="America/Chicago">Central Time</option>
                  <option value="America/Denver">Mountain Time</option>
                  <option value="America/Los_Angeles">Pacific Time</option>
                </Select>
              </FormControl>
            </VStack>
          </SimpleGrid>
        </Box>

        {/* Account Information */}
        <Box
          bg={bgColor}
          border="1px"
          borderColor={borderColor}
          borderRadius="lg"
          p={6}
        >
          <Heading size="md" mb={4}>Account Information</Heading>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
            <VStack align="start" spacing={2}>
              <HStack>
                <FiMail />
                <Text fontWeight="medium">Plan</Text>
              </HStack>
              <Badge colorScheme={getPlanColor(userInfo.plan)} size="lg">
                {userInfo.plan}
              </Badge>
            </VStack>
            <VStack align="start" spacing={2}>
              <HStack>
                <FiCalendar />
                <Text fontWeight="medium">Member Since</Text>
              </HStack>
              <Text>{new Date(userInfo.created_at).toLocaleDateString()}</Text>
            </VStack>
          </SimpleGrid>
        </Box>

        {/* Referral Program */}
        {referral && (
          <Box
            bg={bgColor}
            border="1px"
            borderColor={borderColor}
            borderRadius="lg"
            p={6}
          >
            <Heading size="md" mb={4}>Referral Program</Heading>
            <VStack spacing={4} align="stretch">
              <HStack justify="space-between">
                <VStack align="start" spacing={1}>
                  <Text fontWeight="medium">Your Referral Code</Text>
                  <Text fontSize="sm" color={textColor}>
                    Share this code with friends to earn credits
                  </Text>
                </VStack>
                <Button onClick={handleCopyReferral} leftIcon={<FiUsers />}>
                  Copy Code
                </Button>
              </HStack>

              <Box
                bg="gray.50"
                p={4}
                borderRadius="md"
                border="1px"
                borderColor="gray.200"
              >
                <Text fontFamily="mono" fontSize="lg" textAlign="center">
                  {referral.code}
                </Text>
              </Box>

              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                <Stat>
                  <StatLabel>Total Referrals</StatLabel>
                  <StatNumber>{referral.total_referrals}</StatNumber>
                </Stat>
                <Stat>
                  <StatLabel>Total Earned</StatLabel>
                  <StatNumber color="green.500">${referral.total_earned}</StatNumber>
                </Stat>
              </SimpleGrid>
            </VStack>
          </Box>
        )}
      </VStack>
    </Container>
  );
};

export default Profile; 