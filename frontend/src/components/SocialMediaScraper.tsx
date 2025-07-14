import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  VStack,
  HStack,
  Input,
  Select,
  Textarea,
  Badge,
  Progress,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  useToast,
  useColorModeValue,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  IconButton,
  Tooltip,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
  Switch,
  FormControl,
  FormLabel,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  StatGroup,
  Grid,
  GridItem,
  Flex,
  Spacer,
  Divider
} from '@chakra-ui/react';
import { 
  FaFacebook, 
  FaInstagram, 
  FaTwitter, 
  FaLinkedin, 
  FaTiktok,
  FaPlay,
  FaPause,
  FaStop,
  FaDownload,
  FaFilter,
  FaChartLine,
  FaUsers,
  FaEnvelope,
  FaPhone,
  FaGlobe,
  FaCheck,
  FaTimes,
  FaEye,
  FaEdit,
  FaTrash
} from 'react-icons/fa';
import { api } from '../api';

interface SocialMediaLead {
  id: number;
  platform: string;
  platform_id: string;
  username?: string;
  display_name?: string;
  email?: string;
  phone?: string;
  bio?: string;
  followers_count?: number;
  following_count?: number;
  posts_count?: number;
  location?: string;
  website?: string;
  profile_url?: string;
  avatar_url?: string;
  verified: boolean;
  business_category?: string;
  engagement_score?: number;
  status: string;
  tags: string[];
  notes?: string;
  created_at: string;
  updated_at: string;
}

interface ScrapingRequest {
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
}

interface ScrapingAnalytics {
  platform_counts: Record<string, number>;
  engagement_stats: {
    average: number;
    maximum: number;
    minimum: number;
  };
  status_distribution: Record<string, number>;
  total_leads: number;
}

const SocialMediaScraper: React.FC = () => {
  const [leads, setLeads] = useState<SocialMediaLead[]>([]);
  const [loading, setLoading] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [analytics, setAnalytics] = useState<ScrapingAnalytics | null>(null);
  const [selectedPlatform, setSelectedPlatform] = useState('facebook');
  const [filterStatus, setFilterStatus] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLeads, setSelectedLeads] = useState<number[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [scrapingRequest, setScrapingRequest] = useState<ScrapingRequest>({
    platform: 'facebook',
    keywords: [],
    location: '',
    max_results: 100,
    filters: {
      min_followers: 0,
      max_followers: 0,
      has_email: false,
      has_phone: false,
      has_website: false,
      verified_only: false
    },
    include_engagement: true,
    include_contact_info: true
  });

  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedLead, setSelectedLead] = useState<SocialMediaLead | null>(null);
  
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    loadLeads();
    loadAnalytics();
  }, []);

  const loadLeads = async () => {
    setLoading(true);
    try {
      const response = await api.getSocialLeads();
      setLeads(response);
    } catch (error: any) {
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

  const loadAnalytics = async () => {
    try {
      const response = await api.getSocialAnalytics();
      setAnalytics(response);
    } catch (error: any) {
      console.error('Error loading analytics:', error);
    }
  };

  const handleStartScraping = async () => {
    if (!scrapingRequest.keywords.length) {
      toast({
        title: 'Error',
        description: 'Please enter at least one keyword',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    setScraping(true);
    try {
      const response = await api.scrapeSocialMedia(scrapingRequest);
      
      toast({
        title: 'Scraping Started',
        description: `${selectedPlatform} scraping has been started`,
        status: 'success',
        duration: 3000,
      });
      
      // Reset form
      setScrapingRequest({
        platform: 'facebook',
        keywords: [],
        location: '',
        max_results: 100,
        filters: {
          min_followers: 0,
          max_followers: 0,
          has_email: false,
          has_phone: false,
          has_website: false,
          verified_only: false
        },
        include_engagement: true,
        include_contact_info: true
      });
      
      // Reload leads after a delay
      setTimeout(() => {
        loadLeads();
        loadAnalytics();
      }, 5000);
      
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    } finally {
      setScraping(false);
    }
  };

  const handleKeywordChange = (value: string) => {
    const keywords = value.split(',').map(k => k.trim()).filter(k => k);
    setScrapingRequest({ ...scrapingRequest, keywords });
  };

  const handleFilterChange = (filter: string, value: any) => {
    setScrapingRequest({
      ...scrapingRequest,
      filters: {
        ...scrapingRequest.filters,
        [filter]: value
      }
    });
  };

  const handleLeadSelection = (leadId: number) => {
    setSelectedLeads(prev => 
      prev.includes(leadId) 
        ? prev.filter(id => id !== leadId)
        : [...prev, leadId]
    );
  };

  const handleViewLead = (lead: SocialMediaLead) => {
    setSelectedLead(lead);
    onOpen();
  };

  const handleExportLeads = async () => {
    if (selectedLeads.length === 0) {
      toast({
        title: 'Error',
        description: 'Please select leads to export',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    try {
      const selectedLeadData = leads.filter(lead => selectedLeads.includes(lead.id));
      const csvContent = generateCSV(selectedLeadData);
      downloadCSV(csvContent, 'social_media_leads.csv');
      
      toast({
        title: 'Export Successful',
        description: `${selectedLeads.length} leads exported`,
        status: 'success',
        duration: 3000,
      });
    } catch (error: any) {
      toast({
        title: 'Export Error',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  const generateCSV = (leads: SocialMediaLead[]): string => {
    const headers = [
      'Platform', 'Username', 'Display Name', 'Email', 'Phone', 'Bio',
      'Followers', 'Following', 'Posts', 'Location', 'Website',
      'Verified', 'Business Category', 'Engagement Score', 'Status'
    ];
    
    const rows = leads.map(lead => [
      lead.platform,
      lead.username || '',
      lead.display_name || '',
      lead.email || '',
      lead.phone || '',
      lead.bio || '',
      lead.followers_count || 0,
      lead.following_count || 0,
      lead.posts_count || 0,
      lead.location || '',
      lead.website || '',
      lead.verified ? 'Yes' : 'No',
      lead.business_category || '',
      lead.engagement_score || 0,
      lead.status
    ]);
    
    return [headers, ...rows].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
  };

  const downloadCSV = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'facebook': return <FaFacebook color="#1877F2" />;
      case 'instagram': return <FaInstagram color="#E4405F" />;
      case 'twitter': return <FaTwitter color="#1DA1F2" />;
      case 'linkedin': return <FaLinkedin color="#0A66C2" />;
      case 'tiktok': return <FaTiktok color="#000000" />;
      default: return <FaUsers />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new': return 'blue';
      case 'contacted': return 'yellow';
      case 'qualified': return 'green';
      case 'converted': return 'purple';
      case 'ignored': return 'red';
      default: return 'gray';
    }
  };

  const filteredLeads = leads.filter(lead => {
    const matchesSearch = !searchTerm || 
      lead.display_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.bio?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = !filterStatus || lead.status === filterStatus;
    const matchesPlatform = selectedPlatform === 'all' || lead.platform === selectedPlatform;
    
    return matchesSearch && matchesStatus && matchesPlatform;
  });

  return (
    <Box p={6}>
      <Heading size="lg" mb={6}>Social Media Lead Scraper</Heading>
      
      {/* Analytics Overview */}
      {analytics && (
        <Card mb={6} bg={bgColor} border="1px" borderColor={borderColor}>
          <CardHeader>
            <Heading size="md">Analytics Overview</Heading>
          </CardHeader>
          <CardBody>
            <StatGroup>
              <Stat>
                <StatLabel>Total Leads</StatLabel>
                <StatNumber>{analytics.total_leads}</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  23.36%
                </StatHelpText>
              </Stat>
              <Stat>
                <StatLabel>Avg Engagement</StatLabel>
                <StatNumber>{analytics.engagement_stats.average.toFixed(1)}</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  12.5%
                </StatHelpText>
              </Stat>
              <Stat>
                <StatLabel>Success Rate</StatLabel>
                <StatNumber>85%</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  8.2%
                </StatHelpText>
              </Stat>
            </StatGroup>
          </CardBody>
        </Card>
      )}

      <Tabs>
        <TabList>
          <Tab>Scrape Leads</Tab>
          <Tab>Manage Leads</Tab>
          <Tab>Analytics</Tab>
        </TabList>

        <TabPanels>
          {/* Scraping Configuration */}
          <TabPanel>
            <Card bg={bgColor} border="1px" borderColor={borderColor}>
              <CardHeader>
                <Heading size="md">Configure Social Media Scraping</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={6} align="stretch">
                  {/* Platform Selection */}
                  <HStack spacing={4}>
                    <FormControl>
                      <FormLabel>Platform</FormLabel>
                      <Select
                        value={scrapingRequest.platform}
                        onChange={(e) => setScrapingRequest({...scrapingRequest, platform: e.target.value})}
                      >
                        <option value="facebook">Facebook</option>
                        <option value="instagram">Instagram</option>
                        <option value="twitter">Twitter</option>
                        <option value="linkedin">LinkedIn</option>
                        <option value="tiktok">TikTok</option>
                      </Select>
                    </FormControl>
                    
                    <FormControl>
                      <FormLabel>Max Results</FormLabel>
                      <NumberInput
                        value={scrapingRequest.max_results}
                        onChange={(value) => setScrapingRequest({...scrapingRequest, max_results: parseInt(value)})}
                        min={1}
                        max={1000}
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    </FormControl>
                  </HStack>

                  {/* Keywords */}
                  <FormControl>
                    <FormLabel>Keywords (comma-separated)</FormLabel>
                    <Textarea
                      placeholder="restaurant, cafe, business, entrepreneur"
                      value={scrapingRequest.keywords.join(', ')}
                      onChange={(e) => handleKeywordChange(e.target.value)}
                    />
                  </FormControl>

                  {/* Location */}
                  <FormControl>
                    <FormLabel>Location (optional)</FormLabel>
                    <Input
                      placeholder="New York, NY"
                      value={scrapingRequest.location}
                      onChange={(e) => setScrapingRequest({...scrapingRequest, location: e.target.value})}
                    />
                  </FormControl>

                  {/* Advanced Filters */}
                  <Box>
                    <Button
                      leftIcon={<FaFilter />}
                      variant="outline"
                      onClick={() => setShowFilters(!showFilters)}
                      mb={4}
                    >
                      Advanced Filters
                    </Button>
                    
                    {showFilters && (
                      <VStack spacing={4} align="stretch" p={4} bg="gray.50" borderRadius="md">
                        <HStack spacing={4}>
                          <FormControl>
                            <FormLabel>Min Followers</FormLabel>
                            <NumberInput
                              value={scrapingRequest.filters?.min_followers || 0}
                              onChange={(value) => handleFilterChange('min_followers', parseInt(value))}
                              min={0}
                            >
                              <NumberInputField />
                            </NumberInput>
                          </FormControl>
                          
                          <FormControl>
                            <FormLabel>Max Followers</FormLabel>
                            <NumberInput
                              value={scrapingRequest.filters?.max_followers || 0}
                              onChange={(value) => handleFilterChange('max_followers', parseInt(value))}
                              min={0}
                            >
                              <NumberInputField />
                            </NumberInput>
                          </FormControl>
                        </HStack>
                        
                        <HStack spacing={4}>
                          <FormControl>
                            <FormLabel>Must have email</FormLabel>
                            <Switch
                              isChecked={scrapingRequest.filters?.has_email}
                              onChange={(e) => handleFilterChange('has_email', e.target.checked)}
                            />
                          </FormControl>
                          
                          <FormControl>
                            <FormLabel>Must have phone</FormLabel>
                            <Switch
                              isChecked={scrapingRequest.filters?.has_phone}
                              onChange={(e) => handleFilterChange('has_phone', e.target.checked)}
                            />
                          </FormControl>
                          
                          <FormControl>
                            <FormLabel>Must have website</FormLabel>
                            <Switch
                              isChecked={scrapingRequest.filters?.has_website}
                              onChange={(e) => handleFilterChange('has_website', e.target.checked)}
                            />
                          </FormControl>
                          
                          <FormControl>
                            <FormLabel>Verified only</FormLabel>
                            <Switch
                              isChecked={scrapingRequest.filters?.verified_only}
                              onChange={(e) => handleFilterChange('verified_only', e.target.checked)}
                            />
                          </FormControl>
                        </HStack>
                      </VStack>
                    )}
                  </Box>

                  {/* Options */}
                  <HStack spacing={4}>
                    <FormControl>
                      <FormLabel>Include engagement scoring</FormLabel>
                      <Switch
                        isChecked={scrapingRequest.include_engagement}
                        onChange={(e) => setScrapingRequest({...scrapingRequest, include_engagement: e.target.checked})}
                      />
                    </FormControl>
                    
                    <FormControl>
                      <FormLabel>Include contact info</FormLabel>
                      <Switch
                        isChecked={scrapingRequest.include_contact_info}
                        onChange={(e) => setScrapingRequest({...scrapingRequest, include_contact_info: e.target.checked})}
                      />
                    </FormControl>
                  </HStack>

                  {/* Start Scraping */}
                  <Button
                    leftIcon={<FaPlay />}
                    colorScheme="blue"
                    size="lg"
                    onClick={handleStartScraping}
                    isLoading={scraping}
                    loadingText="Starting Scraping..."
                  >
                    Start Scraping
                  </Button>
                </VStack>
              </CardBody>
            </Card>
          </TabPanel>

          {/* Lead Management */}
          <TabPanel>
            <Card bg={bgColor} border="1px" borderColor={borderColor}>
              <CardHeader>
                <Flex align="center" justify="space-between">
                  <Heading size="md">Manage Social Media Leads</Heading>
                  <HStack spacing={2}>
                    <Button
                      leftIcon={<FaDownload />}
                      variant="outline"
                      onClick={handleExportLeads}
                      isDisabled={selectedLeads.length === 0}
                    >
                      Export Selected ({selectedLeads.length})
                    </Button>
                    <Button
                      leftIcon={<FaChartLine />}
                      variant="outline"
                      onClick={loadAnalytics}
                    >
                      Refresh Analytics
                    </Button>
                  </HStack>
                </Flex>
              </CardHeader>
              <CardBody>
                {/* Filters */}
                <HStack spacing={4} mb={4}>
                  <FormControl maxW="200px">
                    <FormLabel>Platform</FormLabel>
                    <Select
                      value={selectedPlatform}
                      onChange={(e) => setSelectedPlatform(e.target.value)}
                    >
                      <option value="all">All Platforms</option>
                      <option value="facebook">Facebook</option>
                      <option value="instagram">Instagram</option>
                      <option value="twitter">Twitter</option>
                      <option value="linkedin">LinkedIn</option>
                      <option value="tiktok">TikTok</option>
                    </Select>
                  </FormControl>
                  
                  <FormControl maxW="200px">
                    <FormLabel>Status</FormLabel>
                    <Select
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value)}
                    >
                      <option value="">All Status</option>
                      <option value="new">New</option>
                      <option value="contacted">Contacted</option>
                      <option value="qualified">Qualified</option>
                      <option value="converted">Converted</option>
                      <option value="ignored">Ignored</option>
                    </Select>
                  </FormControl>
                  
                  <FormControl maxW="300px">
                    <FormLabel>Search</FormLabel>
                    <Input
                      placeholder="Search leads..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </FormControl>
                </HStack>

                {/* Leads Table */}
                <Box overflowX="auto">
                  <Table variant="simple">
                    <Thead>
                      <Tr>
                        <Th>
                          <input
                            type="checkbox"
                            checked={selectedLeads.length === filteredLeads.length && filteredLeads.length > 0}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedLeads(filteredLeads.map(lead => lead.id));
                              } else {
                                setSelectedLeads([]);
                              }
                            }}
                          />
                        </Th>
                        <Th>Platform</Th>
                        <Th>Name</Th>
                        <Th>Followers</Th>
                        <Th>Engagement</Th>
                        <Th>Contact</Th>
                        <Th>Status</Th>
                        <Th>Actions</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {filteredLeads.map((lead) => (
                        <Tr key={lead.id}>
                          <Td>
                            <input
                              type="checkbox"
                              checked={selectedLeads.includes(lead.id)}
                              onChange={() => handleLeadSelection(lead.id)}
                            />
                          </Td>
                          <Td>
                            <HStack>
                              {getPlatformIcon(lead.platform)}
                              <Text fontSize="sm">{lead.platform}</Text>
                            </HStack>
                          </Td>
                          <Td>
                            <VStack align="start" spacing={1}>
                              <Text fontWeight="bold">{lead.display_name}</Text>
                              <Text fontSize="sm" color="gray.500">@{lead.username}</Text>
                            </VStack>
                          </Td>
                          <Td>
                            <Text>{lead.followers_count?.toLocaleString() || 'N/A'}</Text>
                          </Td>
                          <Td>
                            <Text>{lead.engagement_score?.toFixed(1) || 'N/A'}</Text>
                          </Td>
                          <Td>
                            <HStack spacing={1}>
                              {lead.email && <FaEnvelope color="green" />}
                              {lead.phone && <FaPhone color="blue" />}
                              {lead.website && <FaGlobe color="purple" />}
                            </HStack>
                          </Td>
                          <Td>
                            <Badge colorScheme={getStatusColor(lead.status)}>
                              {lead.status}
                            </Badge>
                          </Td>
                          <Td>
                            <HStack spacing={1}>
                              <Tooltip label="View Details">
                                <IconButton
                                  aria-label="View lead"
                                  icon={<FaEye />}
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => handleViewLead(lead)}
                                />
                              </Tooltip>
                              <Tooltip label="Edit">
                                <IconButton
                                  aria-label="Edit lead"
                                  icon={<FaEdit />}
                                  size="sm"
                                  variant="ghost"
                                />
                              </Tooltip>
                              <Tooltip label="Delete">
                                <IconButton
                                  aria-label="Delete lead"
                                  icon={<FaTrash />}
                                  size="sm"
                                  variant="ghost"
                                  colorScheme="red"
                                />
                              </Tooltip>
                            </HStack>
                          </Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </Box>

                {filteredLeads.length === 0 && (
                  <Alert status="info" mt={4}>
                    <AlertIcon />
                    <Box>
                      <AlertTitle>No leads found</AlertTitle>
                      <AlertDescription>
                        Try adjusting your filters or start a new scraping job.
                      </AlertDescription>
                    </Box>
                  </Alert>
                )}
              </CardBody>
            </Card>
          </TabPanel>

          {/* Analytics */}
          <TabPanel>
            <Card bg={bgColor} border="1px" borderColor={borderColor}>
              <CardHeader>
                <Heading size="md">Social Media Analytics</Heading>
              </CardHeader>
              <CardBody>
                {analytics ? (
                  <VStack spacing={6} align="stretch">
                    {/* Platform Distribution */}
                    <Box>
                      <Heading size="sm" mb={4}>Platform Distribution</Heading>
                      <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
                        {Object.entries(analytics.platform_counts).map(([platform, count]) => (
                          <GridItem key={platform}>
                            <Card>
                              <CardBody>
                                <HStack>
                                  {getPlatformIcon(platform)}
                                  <VStack align="start" spacing={1}>
                                    <Text fontWeight="bold">{platform}</Text>
                                    <Text fontSize="lg">{count}</Text>
                                  </VStack>
                                </HStack>
                              </CardBody>
                            </Card>
                          </GridItem>
                        ))}
                      </Grid>
                    </Box>

                    {/* Status Distribution */}
                    <Box>
                      <Heading size="sm" mb={4}>Status Distribution</Heading>
                      <Grid templateColumns="repeat(auto-fit, minmax(150px, 1fr))" gap={4}>
                        {Object.entries(analytics.status_distribution).map(([status, count]) => (
                          <GridItem key={status}>
                            <Card>
                              <CardBody>
                                <VStack align="start" spacing={1}>
                                  <Badge colorScheme={getStatusColor(status)}>
                                    {status}
                                  </Badge>
                                  <Text fontSize="lg">{count}</Text>
                                </VStack>
                              </CardBody>
                            </Card>
                          </GridItem>
                        ))}
                      </Grid>
                    </Box>

                    {/* Engagement Statistics */}
                    <Box>
                      <Heading size="sm" mb={4}>Engagement Statistics</Heading>
                      <StatGroup>
                        <Stat>
                          <StatLabel>Average Engagement</StatLabel>
                          <StatNumber>{analytics.engagement_stats.average.toFixed(1)}</StatNumber>
                        </Stat>
                        <Stat>
                          <StatLabel>Maximum Engagement</StatLabel>
                          <StatNumber>{analytics.engagement_stats.maximum.toFixed(1)}</StatNumber>
                        </Stat>
                        <Stat>
                          <StatLabel>Minimum Engagement</StatLabel>
                          <StatNumber>{analytics.engagement_stats.minimum.toFixed(1)}</StatNumber>
                        </Stat>
                      </StatGroup>
                    </Box>
                  </VStack>
                ) : (
                  <Alert status="info">
                    <AlertIcon />
                    <AlertTitle>No analytics data</AlertTitle>
                    <AlertDescription>
                      Start scraping leads to see analytics data.
                    </AlertDescription>
                  </Alert>
                )}
              </CardBody>
            </Card>
          </TabPanel>
        </TabPanels>
      </Tabs>

      {/* Lead Detail Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Lead Details</ModalHeader>
          <ModalBody>
            {selectedLead && (
              <VStack spacing={4} align="stretch">
                <HStack>
                  {getPlatformIcon(selectedLead.platform)}
                  <Text fontWeight="bold">{selectedLead.display_name}</Text>
                  {selectedLead.verified && <FaCheck color="green" />}
                </HStack>
                
                <Box>
                  <Text fontWeight="bold">Contact Information</Text>
                  <VStack align="start" spacing={2} mt={2}>
                    {selectedLead.email && (
                      <HStack>
                        <FaEnvelope />
                        <Text>{selectedLead.email}</Text>
                      </HStack>
                    )}
                    {selectedLead.phone && (
                      <HStack>
                        <FaPhone />
                        <Text>{selectedLead.phone}</Text>
                      </HStack>
                    )}
                    {selectedLead.website && (
                      <HStack>
                        <FaGlobe />
                        <Text>{selectedLead.website}</Text>
                      </HStack>
                    )}
                  </VStack>
                </Box>
                
                {selectedLead.bio && (
                  <Box>
                    <Text fontWeight="bold">Bio</Text>
                    <Text mt={2}>{selectedLead.bio}</Text>
                  </Box>
                )}
                
                <HStack spacing={4}>
                  <Stat>
                    <StatLabel>Followers</StatLabel>
                    <StatNumber>{selectedLead.followers_count?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>Following</StatLabel>
                    <StatNumber>{selectedLead.following_count?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>Posts</StatLabel>
                    <StatNumber>{selectedLead.posts_count?.toLocaleString() || 'N/A'}</StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel>Engagement</StatLabel>
                    <StatNumber>{selectedLead.engagement_score?.toFixed(1) || 'N/A'}</StatNumber>
                  </Stat>
                </HStack>
                
                <Box>
                  <Text fontWeight="bold">Location</Text>
                  <Text mt={2}>{selectedLead.location || 'Not specified'}</Text>
                </Box>
                
                <Box>
                  <Text fontWeight="bold">Business Category</Text>
                  <Text mt={2}>{selectedLead.business_category || 'Not specified'}</Text>
                </Box>
                
                <Box>
                  <Text fontWeight="bold">Status</Text>
                  <Badge colorScheme={getStatusColor(selectedLead.status)} mt={2}>
                    {selectedLead.status}
                  </Badge>
                </Box>
              </VStack>
            )}
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Close
            </Button>
            <Button colorScheme="blue">Add to CRM</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default SocialMediaScraper; 