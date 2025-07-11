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
  Grid,
  GridItem,
  useColorModeValue,
  Alert,
  AlertIcon,
  Divider,
  Badge,
  Flex,
  IconButton,
  Tooltip,
} from '@chakra-ui/react';
import { EditIcon, CheckIcon, CloseIcon } from '@chakra-ui/icons';
import * as api from '../api';

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
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    company: '',
    website: '',
    bio: '',
    timezone: 'UTC',
  });

  useEffect(() => {
    loadUserInfo();
    loadUserStats();
  }, []);

  const loadUserInfo = async () => {
    setLoading(true);
    try {
      const response = await api.getUserProfile();
      setUserInfo(response);
      if (response.profile) {
        setFormData({
          first_name: response.profile.first_name || '',
          last_name: response.profile.last_name || '',
          phone: response.profile.phone || '',
          company: response.profile.company || '',
          website: response.profile.website || '',
          bio: response.profile.bio || '',
          timezone: response.profile.timezone || 'UTC',
        });
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

  const loadUserStats = async () => {
    setStatsLoading(true);
    try {
      const response = await api.getUserStats();
      setUserStats(response);
    } catch (error: any) {
      console.error(error);
      setUserStats(null);
    } finally {
      setStatsLoading(false);
    }
  };

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

    try {
      const formData = new FormData();
      formData.append('file', avatarFile);
      
      const response = await api.uploadAvatar(formData);
      toast({
        title: 'Success',
        description: 'Avatar uploaded successfully',
        status: 'success',
        duration: 3000,
      });
      
      // Reload user info to get new avatar URL
      loadUserInfo();
      setAvatarFile(null);
      setAvatarPreview(null);
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

  const updateProfile = async () => {
    try {
      await api.updateUserProfile(formData);
      toast({
        title: 'Success',
        description: 'Profile updated successfully',
        status: 'success',
        duration: 3000,
      });
      setEditing(false);
      loadUserInfo();
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

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case 'free': return 'gray';
      case 'pro': return 'blue';
      case 'business': return 'green';
      default: return 'gray';
    }
  };

  if (loading) {
    return (
      <Container maxW="container.xl" py={8}>
        <Flex justify="center" py={8}>
          <Spinner size="lg" />
        </Flex>
      </Container>
    );
  }

  return (
    <Box minH="100vh" bg={useColorModeValue('gray.100', 'gray.800')} data-tour="profile-main">
      <Container maxW="container.md" py={8} data-tour="profile-content">
        <Heading size="lg" mb={6} className="gradient-text" data-tour="profile-title">Profile</Heading>
        <VStack spacing={6} align="stretch">
          <Box data-tour="profile-avatar-section">
            <Avatar size="2xl" name={userInfo?.profile?.first_name} src={userInfo?.profile?.avatar} mb={4} data-tour="profile-avatar" />
            <Button as="label" htmlFor="avatar-upload" colorScheme="blue" data-tour="profile-avatar-upload">Change Avatar</Button>
            <input id="avatar-upload" type="file" accept="image/*" style={{ display: 'none' }} onChange={handleAvatarChange} />
          </Box>
          <Box data-tour="profile-info-section">
            <Text fontSize="lg" fontWeight="bold" data-tour="profile-name">{userInfo?.profile?.first_name} {userInfo?.profile?.last_name}</Text>
            <Text color="gray.500" data-tour="profile-email">{userInfo?.email}</Text>
          </Box>
          <Box data-tour="profile-stats-section">
            {userStats && (
              <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={6}>
                <GridItem>
                  <Stat>
                    <StatLabel>Total Jobs</StatLabel>
                    <StatNumber>{userStats.total_jobs}</StatNumber>
                    <StatHelpText>All time</StatHelpText>
                  </Stat>
                </GridItem>
                <GridItem>
                  <Stat>
                    <StatLabel>Success Rate</StatLabel>
                    <StatNumber>{userStats.success_rate}%</StatNumber>
                    <StatHelpText>Completed jobs</StatHelpText>
                  </Stat>
                </GridItem>
                <GridItem>
                  <Stat>
                    <StatLabel>Total Leads</StatLabel>
                    <StatNumber>{userStats.total_leads}</StatNumber>
                    <StatHelpText>In CRM</StatHelpText>
                  </Stat>
                </GridItem>
                <GridItem>
                  <Stat>
                    <StatLabel>Account Age</StatLabel>
                    <StatNumber>{userStats.account_age_days}</StatNumber>
                    <StatHelpText>Days</StatHelpText>
                  </Stat>
                </GridItem>
              </Grid>
            )}
          </Box>

          <Divider my={6} />

          {/* Profile Information */}
          <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor}>
            <HStack justify="space-between" mb={6}>
              <Heading size="md">Profile Information</Heading>
              <HStack spacing={2}>
                {editing ? (
                  <>
                    <Button size="sm" colorScheme="green" onClick={updateProfile}>
                      <CheckIcon mr={2} />
                      Save
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setEditing(false)}>
                      <CloseIcon mr={2} />
                      Cancel
                    </Button>
                  </>
                ) : (
                  <Button size="sm" onClick={() => setEditing(true)}>
                    <EditIcon mr={2} />
                    Edit
                  </Button>
                )}
              </HStack>
            </HStack>

            <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={6}>
              {/* Avatar Section */}
              <VStack spacing={4} align="start">
                <Text fontWeight="bold">Avatar</Text>
                <HStack spacing={4}>
                  <Avatar
                    size="xl"
                    src={avatarPreview || userInfo?.profile?.avatar}
                    name={`${formData.first_name} ${formData.last_name}`}
                  />
                  <VStack align="start" spacing={2}>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleAvatarChange}
                      style={{ display: 'none' }}
                      id="avatar-upload"
                    />
                    <label htmlFor="avatar-upload">
                      <Button size="sm" as="span">
                        Choose File
                      </Button>
                    </label>
                    {avatarFile && (
                      <Button size="sm" colorScheme="blue" onClick={uploadAvatar}>
                        Upload Avatar
                      </Button>
                    )}
                  </VStack>
                </HStack>
              </VStack>

              {/* Account Info */}
              <VStack spacing={4} align="start">
                <Text fontWeight="bold">Account Information</Text>
                <HStack spacing={4}>
                  <Badge colorScheme={getPlanColor(userInfo?.plan || 'free')}>
                    {userInfo?.plan?.toUpperCase()} PLAN
                  </Badge>
                  <Text fontSize="sm" color="gray.600">
                    Member since {userInfo?.created_at ? new Date(userInfo.created_at).toLocaleDateString() : 'N/A'}
                  </Text>
                </HStack>
                <Text fontSize="sm" color="gray.600">
                  Email: {userInfo?.email}
                </Text>
              </VStack>
            </Grid>

            <Divider my={6} />

            {/* Profile Form */}
            <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={4}>
              <FormControl>
                <FormLabel>First Name</FormLabel>
                <Input
                  value={formData.first_name}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  isDisabled={!editing}
                  placeholder="Enter first name"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Last Name</FormLabel>
                <Input
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  isDisabled={!editing}
                  placeholder="Enter last name"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Phone</FormLabel>
                <Input
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  isDisabled={!editing}
                  placeholder="Enter phone number"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Company</FormLabel>
                <Input
                  value={formData.company}
                  onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                  isDisabled={!editing}
                  placeholder="Enter company name"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Website</FormLabel>
                <Input
                  value={formData.website}
                  onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                  isDisabled={!editing}
                  placeholder="Enter website URL"
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
                  <option value="Europe/London">London</option>
                  <option value="Europe/Paris">Paris</option>
                  <option value="Asia/Tokyo">Tokyo</option>
                </Select>
              </FormControl>
            </Grid>

            <FormControl mt={4}>
              <FormLabel>Bio</FormLabel>
              <Textarea
                value={formData.bio}
                onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                isDisabled={!editing}
                placeholder="Tell us about yourself..."
                rows={3}
              />
            </FormControl>
          </Box>

          {/* Security Section */}
          <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor}>
            <Heading size="md" mb={4}>Security</Heading>
            <Alert status="info">
              <AlertIcon />
              Password changes and security settings are managed through your account settings.
            </Alert>
          </Box>

          {/* Plan Information */}
          <Box bg={bgColor} p={6} borderRadius="lg" border="1px" borderColor={borderColor}>
            <Heading size="md" mb={4}>Plan Information</Heading>
            <VStack spacing={4} align="start">
              <HStack>
                <Text fontWeight="bold">Current Plan:</Text>
                <Badge colorScheme={getPlanColor(userInfo?.plan || 'free')} fontSize="md">
                  {userInfo?.plan?.toUpperCase()}
                </Badge>
              </HStack>
              <Text fontSize="sm" color="gray.600">
                Upgrade your plan to unlock more features and increase your daily limits.
              </Text>
              <Button colorScheme="blue" size="sm">
                Upgrade Plan
              </Button>
            </VStack>
          </Box>
        </VStack>
      </Container>
    </Box>
  );
};

export default Profile; 