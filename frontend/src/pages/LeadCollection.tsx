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
  Badge,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Input,
  Select,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  FormControl,
  FormLabel,
  Textarea,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Grid,
  GridItem,
  IconButton,
  Tooltip,
  Alert,
  AlertIcon,
  Flex,
  useColorModeValue,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Card,
  CardBody,
  SimpleGrid,
  Tag,
  TagLabel,
  TagCloseButton,
} from '@chakra-ui/react';
import { AddIcon, EditIcon, DeleteIcon, ViewIcon, SearchIcon } from '@chakra-ui/icons';
import * as api from '../api';
import { useAuth } from '../hooks/useAuth';
import { useTranslation } from 'react-i18next';

interface LeadSource {
  id: number;
  name: string;
  type: string;
  config: any;
}

interface LeadCollection {
  id: number;
  name: string;
  description: string;
  source_id: number;
  status: string;
  last_run: string;
  next_run: string;
  created_at: string;
}

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

const LeadCollection: React.FC = () => {
  const { t } = useTranslation();
  const [sources, setSources] = useState<LeadSource[]>([]);
  const [collections, setCollections] = useState<LeadCollection[]>([]);
  const [leads, setLeads] = useState<SocialMediaLead[]>([]);
  const [loading, setLoading] = useState(false);
  const [sourcesLoading, setSourcesLoading] = useState(false);
  const [collectionsLoading, setCollectionsLoading] = useState(false);
  const [leadsLoading, setLeadsLoading] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState('facebook');
  const [filterStatus, setFilterStatus] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [collectionModalOpen, setCollectionModalOpen] = useState(false);
  const [collectionForm, setCollectionForm] = useState({
    name: '',
    description: '',
    source_id: 0,
    config: {}
  });
  const [facebookForm, setFacebookForm] = useState({
    keywords: '',
    location: '',
    max_results: 100
  });
  const [instagramForm, setInstagramForm] = useState({
    hashtags: '',
    location: '',
    max_results: 100
  });
  const [whatsappForm, setWhatsappForm] = useState({
    phone_numbers: '',
    keywords: ''
  });
  const [collecting, setCollecting] = useState(false);
  
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const { user } = useAuth();

  useEffect(() => {
    loadSources();
    loadCollections();
    loadLeads();
  }, []);

  const loadSources = async () => {
    setSourcesLoading(true);
    try {
      const response = await api.getLeadSources();
      setSources(response);
    } catch (error: any) {
      console.error(error);
      toast({
        title: t('error', 'Error'),
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    } finally {
      setSourcesLoading(false);
    }
  };

  const loadCollections = async () => {
    setCollectionsLoading(true);
    try {
      const response = await api.getLeadCollections();
      setCollections(response);
    } catch (error: any) {
      console.error(error);
      toast({
        title: t('error', 'Error'),
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    } finally {
      setCollectionsLoading(false);
    }
  };

  const loadLeads = async () => {
    setLeadsLoading(true);
    try {
      const response = await api.getSocialMediaLeads({
        platform: selectedPlatform !== 'all' ? selectedPlatform : undefined,
        status: filterStatus || undefined
      });
      setLeads(response);
    } catch (error: any) {
      console.error(error);
      toast({
        title: t('error', 'Error'),
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLeadsLoading(false);
    }
  };

  const handleFacebookCollection = async () => {
    if (!facebookForm.keywords.trim()) {
      toast({
        title: t('error', 'Error'),
        description: t('leadCollection.facebook.keywordsError', 'Please enter keywords'),
        status: 'error',
        duration: 3000,
      });
      return;
    }

    setCollecting(true);
    try {
      const keywords = facebookForm.keywords.split(',').map(k => k.trim()).filter(k => k);
      const response = await api.collectFacebookLeads({
        keywords,
        location: facebookForm.location || undefined,
        max_results: facebookForm.max_results
      });
      
      toast({
        title: t('leadCollection.collectionStarted', 'Collection Started'),
        description: t('leadCollection.facebook.collectionStartedDescription', 'Facebook lead collection has been started'),
        status: 'success',
        duration: 3000,
      });
      
      setFacebookForm({ keywords: '', location: '', max_results: 100 });
      loadCollections();
    } catch (error: any) {
      toast({
        title: t('error', 'Error'),
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    } finally {
      setCollecting(false);
    }
  };

  const handleInstagramCollection = async () => {
    if (!instagramForm.hashtags.trim()) {
      toast({
        title: t('error', 'Error'),
        description: t('leadCollection.instagram.hashtagsError', 'Please enter hashtags'),
        status: 'error',
        duration: 3000,
      });
      return;
    }

    setCollecting(true);
    try {
      const hashtags = instagramForm.hashtags.split(',').map(h => h.trim()).filter(h => h);
      const response = await api.collectInstagramLeads({
        hashtags,
        location: instagramForm.location || undefined,
        max_results: instagramForm.max_results
      });
      
      toast({
        title: t('leadCollection.collectionStarted', 'Collection Started'),
        description: t('leadCollection.instagram.collectionStartedDescription', 'Instagram lead collection has been started'),
        status: 'success',
        duration: 3000,
      });
      
      setInstagramForm({ hashtags: '', location: '', max_results: 100 });
      loadCollections();
    } catch (error: any) {
      toast({
        title: t('error', 'Error'),
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    } finally {
      setCollecting(false);
    }
  };

  const handleWhatsAppCollection = async () => {
    if (!whatsappForm.keywords.trim() || !whatsappForm.phone_numbers.trim()) {
      toast({
        title: t('error', 'Error'),
        description: t('leadCollection.whatsapp.keywordsError', 'Please enter both keywords and phone numbers'),
        status: 'error',
        duration: 3000,
      });
      return;
    }

    setCollecting(true);
    try {
      const keywords = whatsappForm.keywords.split(',').map(k => k.trim()).filter(k => k);
      const phoneNumbers = whatsappForm.phone_numbers.split(',').map(p => p.trim()).filter(p => p);
      const response = await api.collectWhatsAppLeads({
        keywords,
        phone_numbers: phoneNumbers
      });
      
      toast({
        title: t('leadCollection.collectionStarted', 'Collection Started'),
        description: t('leadCollection.whatsapp.collectionStartedDescription', 'WhatsApp lead collection has been started'),
        status: 'success',
        duration: 3000,
      });
      
      setWhatsappForm({ keywords: '', phone_numbers: '' });
      loadCollections();
    } catch (error: any) {
      toast({
        title: t('error', 'Error'),
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    } finally {
      setCollecting(false);
    }
  };

  const filteredLeads = leads.filter(lead => {
    const matchesSearch = !searchTerm || 
      lead.display_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.bio?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = !filterStatus || lead.status === filterStatus;
    
    return matchesSearch && matchesStatus;
  });

  // Plan-based gating logic
  const canAccessFacebook = user && (user.plan === 'pro' || user.plan === 'business');
  const canAccessInstagram = user && (user.plan === 'pro' || user.plan === 'business');
  const canAccessWhatsApp = user && user.plan === 'business';
  const handleTabChange = (index: number) => {
    if ((index === 0 && !canAccessFacebook) || (index === 1 && !canAccessInstagram) || (index === 2 && !canAccessWhatsApp)) {
      toast({ title: t('leadCollection.upgradeRequired', 'Upgrade Required'), description: t('leadCollection.upgradeRequiredDescription', 'Upgrade your plan to access this lead source.'), status: 'info' });
      return false;
    }
    return true;
  };

  return (
    <Box minH="100vh" bg={useColorModeValue('gray.100', 'gray.800')}>
      <Container maxW="container.xl" py={8}>
        <Heading size="lg" mb={6} className="gradient-text">{t('leadCollection.title', 'Multi-Source Lead Collection')}</Heading>
        
        <Tabs variant="enclosed" mb={8} onChange={handleTabChange}>
          <TabList>
            <Tab isDisabled={!canAccessFacebook}>{t('leadCollection.tabs.facebook', 'Facebook')} {canAccessFacebook ? '' : <Badge ml={2} colorScheme="blue">{t('leadCollection.pro', 'Pro')}</Badge>}</Tab>
            <Tab isDisabled={!canAccessInstagram}>{t('leadCollection.tabs.instagram', 'Instagram')} {canAccessInstagram ? '' : <Badge ml={2} colorScheme="blue">{t('leadCollection.pro', 'Pro')}</Badge>}</Tab>
            <Tab isDisabled={!canAccessWhatsApp}>{t('leadCollection.tabs.whatsapp', 'WhatsApp')} {canAccessWhatsApp ? '' : <Badge ml={2} colorScheme="green">{t('leadCollection.business', 'Business')}</Badge>}</Tab>
            <Tab>{t('leadCollection.tabs.collections', 'Collections')}</Tab>
            <Tab>{t('leadCollection.tabs.leads', 'Leads')}</Tab>
          </TabList>

          <TabPanels>
            {/* Facebook Collection */}
            <TabPanel>
              <Card bg={bgColor} border="1px" borderColor={borderColor}>
                <CardBody>
                  <Heading size="md" mb={4}>{t('leadCollection.facebookLeadCollection', 'Facebook Lead Collection')}</Heading>
                  <Text fontSize="sm" color="gray.600" mb={6}>
                    {t('leadCollection.facebookLeadCollectionDescription', 'Collect leads from Facebook pages and groups based on keywords and location.')}
                  </Text>
                  
                  <VStack spacing={4} align="stretch">
                    <FormControl>
                      <FormLabel>{t('leadCollection.facebook.keywordsLabel', 'Keywords (comma-separated)')}</FormLabel>
                      <Input
                        placeholder={t('leadCollection.facebook.keywordsPlaceholder', 'restaurant, cafe, business')}
                        value={facebookForm.keywords}
                        onChange={(e) => setFacebookForm({...facebookForm, keywords: e.target.value})}
                      />
                    </FormControl>
                    
                    <FormControl>
                      <FormLabel>{t('leadCollection.facebook.locationLabel', 'Location (optional)')}</FormLabel>
                      <Input
                        placeholder={t('leadCollection.facebook.locationPlaceholder', 'New York, NY')}
                        value={facebookForm.location}
                        onChange={(e) => setFacebookForm({...facebookForm, location: e.target.value})}
                      />
                    </FormControl>
                    
                    <FormControl>
                      <FormLabel>{t('leadCollection.facebook.maxResultsLabel', 'Max Results')}</FormLabel>
                      <Input
                        type="number"
                        value={facebookForm.max_results}
                        onChange={(e) => setFacebookForm({...facebookForm, max_results: parseInt(e.target.value)})}
                        min={1}
                        max={1000}
                      />
                    </FormControl>
                    
                    <Button
                      colorScheme="blue"
                      onClick={handleFacebookCollection}
                      isLoading={collecting}
                      loadingText={t('leadCollection.facebook.collectingLeadsLoadingText', 'Collecting Leads')}
                    >
                      {t('leadCollection.facebook.startCollectionButton', 'Start Facebook Collection')}
                    </Button>
                  </VStack>
                </CardBody>
              </Card>
            </TabPanel>

            {/* Instagram Collection */}
            <TabPanel>
              <Card bg={bgColor} border="1px" borderColor={borderColor}>
                <CardBody>
                  <Heading size="md" mb={4}>{t('leadCollection.instagramLeadCollection', 'Instagram Lead Collection')}</Heading>
                  <Text fontSize="sm" color="gray.600" mb={6}>
                    {t('leadCollection.instagramLeadCollectionDescription', 'Collect leads from Instagram based on hashtags and location.')}
                  </Text>
                  
                  <VStack spacing={4} align="stretch">
                    <FormControl>
                      <FormLabel>{t('leadCollection.instagram.hashtagsLabel', 'Hashtags (comma-separated)')}</FormLabel>
                      <Input
                        placeholder={t('leadCollection.instagram.hashtagsPlaceholder', '#business, #entrepreneur, #startup')}
                        value={instagramForm.hashtags}
                        onChange={(e) => setInstagramForm({...instagramForm, hashtags: e.target.value})}
                      />
                    </FormControl>
                    
                    <FormControl>
                      <FormLabel>{t('leadCollection.instagram.locationLabel', 'Location (optional)')}</FormLabel>
                      <Input
                        placeholder={t('leadCollection.instagram.locationPlaceholder', 'Los Angeles, CA')}
                        value={instagramForm.location}
                        onChange={(e) => setInstagramForm({...instagramForm, location: e.target.value})}
                      />
                    </FormControl>
                    
                    <FormControl>
                      <FormLabel>{t('leadCollection.instagram.maxResultsLabel', 'Max Results')}</FormLabel>
                      <Input
                        type="number"
                        value={instagramForm.max_results}
                        onChange={(e) => setInstagramForm({...instagramForm, max_results: parseInt(e.target.value)})}
                        min={1}
                        max={1000}
                      />
                    </FormControl>
                    
                    <Button
                      colorScheme="purple"
                      onClick={handleInstagramCollection}
                      isLoading={collecting}
                      loadingText={t('leadCollection.instagram.collectingLeadsLoadingText', 'Collecting Leads')}
                    >
                      {t('leadCollection.instagram.startCollectionButton', 'Start Instagram Collection')}
                    </Button>
                  </VStack>
                </CardBody>
              </Card>
            </TabPanel>

            {/* WhatsApp Collection */}
            <TabPanel>
              <Card bg={bgColor} border="1px" borderColor={borderColor}>
                <CardBody>
                  <Heading size="md" mb={4}>{t('leadCollection.whatsAppBusinessLeadCollection', 'WhatsApp Business Lead Collection')}</Heading>
                  <Text fontSize="sm" color="gray.600" mb={6}>
                    {t('leadCollection.whatsAppBusinessLeadCollectionDescription', 'Collect leads from WhatsApp Business accounts. Business plan required.')}
                  </Text>
                  
                  <VStack spacing={4} align="stretch">
                    <FormControl>
                      <FormLabel>{t('leadCollection.whatsApp.phoneNumbersLabel', 'Phone Numbers (comma-separated)')}</FormLabel>
                      <Input
                        placeholder={t('leadCollection.whatsApp.phoneNumbersPlaceholder', '+1234567890, +0987654321')}
                        value={whatsappForm.phone_numbers}
                        onChange={(e) => setWhatsappForm({...whatsappForm, phone_numbers: e.target.value})}
                      />
                    </FormControl>
                    
                    <FormControl>
                      <FormLabel>{t('leadCollection.whatsApp.keywordsLabel', 'Keywords (comma-separated)')}</FormLabel>
                      <Input
                        placeholder={t('leadCollection.whatsApp.keywordsPlaceholder', 'business, services, products')}
                        value={whatsappForm.keywords}
                        onChange={(e) => setWhatsappForm({...whatsappForm, keywords: e.target.value})}
                      />
                    </FormControl>
                    
                    <Button
                      colorScheme="green"
                      onClick={handleWhatsAppCollection}
                      isLoading={collecting}
                      loadingText={t('leadCollection.whatsApp.collectingLeadsLoadingText', 'Collecting Leads')}
                    >
                      {t('leadCollection.whatsApp.startCollectionButton', 'Start WhatsApp Collection')}
                    </Button>
                  </VStack>
                </CardBody>
              </Card>
            </TabPanel>

            {/* Collections */}
            <TabPanel>
              <Card bg={bgColor} border="1px" borderColor={borderColor}>
                <CardBody>
                  <HStack justify="space-between" mb={4}>
                    <Heading size="md">{t('leadCollection.leadCollections', 'Lead Collections')}</Heading>
                    <Button size="sm" colorScheme="blue" onClick={() => setCollectionModalOpen(true)}>{t('leadCollection.createCollection', 'Create Collection')}</Button>
                  </HStack>
                  
                  {collectionsLoading ? (
                    <Spinner />
                  ) : collections.length === 0 ? (
                    <Text color="gray.500">{t('leadCollection.noCollectionsMessage', 'No collections yet. Start collecting leads to see them here.')}</Text>
                  ) : (
                    <Table size="sm">
                      <Thead>
                        <Tr>
                          <Th>{t('leadCollection.collectionName', 'Name')}</Th>
                          <Th>{t('leadCollection.source', 'Source')}</Th>
                          <Th>{t('leadCollection.status', 'Status')}</Th>
                          <Th>{t('leadCollection.lastRun', 'Last Run')}</Th>
                          <Th>{t('leadCollection.actions', 'Actions')}</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {collections.map((collection) => (
                          <Tr key={collection.id}>
                            <Td>{collection.name}</Td>
                            <Td>{sources.find(s => s.id === collection.source_id)?.name || t('leadCollection.unknownSource', 'Unknown')}</Td>
                            <Td>
                              <Badge colorScheme={collection.status === 'completed' ? 'green' : 'yellow'}>
                                {collection.status}
                              </Badge>
                            </Td>
                            <Td>{collection.last_run ? new Date(collection.last_run).toLocaleString() : t('leadCollection.neverRun', 'Never')}</Td>
                            <Td>
                              <Button size="xs" colorScheme="blue">{t('leadCollection.view', 'View')}</Button>
                            </Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  )}
                </CardBody>
              </Card>
            </TabPanel>

            {/* Leads */}
            <TabPanel>
              <Card bg={bgColor} border="1px" borderColor={borderColor}>
                <CardBody>
                  <HStack justify="space-between" mb={4}>
                    <Heading size="md">{t('leadCollection.collectedLeads', 'Collected Leads')}</Heading>
                    <HStack spacing={2}>
                      <Select
                        placeholder={t('leadCollection.allPlatforms', 'All Platforms')}
                        value={selectedPlatform}
                        onChange={(e) => setSelectedPlatform(e.target.value)}
                        size="sm"
                        w="150px"
                      >
                        <option value="all">{t('leadCollection.allPlatforms', 'All Platforms')}</option>
                        <option value="facebook">{t('leadCollection.facebook', 'Facebook')}</option>
                        <option value="instagram">{t('leadCollection.instagram', 'Instagram')}</option>
                        <option value="whatsapp">{t('leadCollection.whatsApp', 'WhatsApp')}</option>
                      </Select>
                      <Select
                        placeholder={t('leadCollection.allStatus', 'All Status')}
                        value={filterStatus}
                        onChange={(e) => setFilterStatus(e.target.value)}
                        size="sm"
                        w="120px"
                      >
                        <option value="">{t('leadCollection.allStatus', 'All Status')}</option>
                        <option value="new">{t('leadCollection.new', 'New')}</option>
                        <option value="contacted">{t('leadCollection.contacted', 'Contacted')}</option>
                        <option value="qualified">{t('leadCollection.qualified', 'Qualified')}</option>
                        <option value="converted">{t('leadCollection.converted', 'Converted')}</option>
                      </Select>
                      <Input
                        placeholder={t('leadCollection.searchLeads', 'Search leads...')}
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        size="sm"
                        w="200px"
                      />
                    </HStack>
                  </HStack>
                  
                  {leadsLoading ? (
                    <Spinner />
                  ) : filteredLeads.length === 0 ? (
                    <Text color="gray.500">{t('leadCollection.noLeadsFound', 'No leads found. Start collecting leads to see them here.')}</Text>
                  ) : (
                    <Table size="sm">
                      <Thead>
                        <Tr>
                          <Th>{t('leadCollection.platform', 'Platform')}</Th>
                          <Th>{t('leadCollection.name', 'Name')}</Th>
                          <Th>{t('leadCollection.contact', 'Contact')}</Th>
                          <Th>{t('leadCollection.followers', 'Followers')}</Th>
                          <Th>{t('leadCollection.location', 'Location')}</Th>
                          <Th>{t('leadCollection.status', 'Status')}</Th>
                          <Th>{t('leadCollection.actions', 'Actions')}</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {filteredLeads.map((lead) => (
                          <Tr key={lead.id}>
                            <Td>
                              <Badge colorScheme={
                                lead.platform === 'facebook' ? 'blue' :
                                lead.platform === 'instagram' ? 'purple' :
                                lead.platform === 'whatsapp' ? 'green' : 'gray'
                              }>
                                {lead.platform}
                              </Badge>
                            </Td>
                            <Td>
                              <VStack align="start" spacing={1}>
                                <Text fontWeight="bold">{lead.display_name}</Text>
                                <Text fontSize="xs" color="gray.500">@{lead.username}</Text>
                              </VStack>
                            </Td>
                            <Td>
                              <VStack align="start" spacing={1}>
                                {lead.email && <Text fontSize="xs">{lead.email}</Text>}
                                {lead.phone && <Text fontSize="xs">{lead.phone}</Text>}
                              </VStack>
                            </Td>
                            <Td>
                              {lead.followers_count ? (
                                <Text fontSize="sm">{lead.followers_count.toLocaleString()}</Text>
                              ) : '-'}
                            </Td>
                            <Td>
                              {lead.location || '-'}
                            </Td>
                            <Td>
                              <Badge colorScheme={
                                lead.status === 'new' ? 'blue' :
                                lead.status === 'contacted' ? 'yellow' :
                                lead.status === 'qualified' ? 'orange' :
                                lead.status === 'converted' ? 'green' : 'gray'
                              }>
                                {lead.status}
                              </Badge>
                            </Td>
                            <Td>
                              <HStack spacing={1}>
                                <Button size="xs" colorScheme="blue">{t('leadCollection.view', 'View')}</Button>
                                <Button size="xs" colorScheme="green">{t('leadCollection.addToCrm', 'Add to CRM')}</Button>
                              </HStack>
                            </Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  )}
                </CardBody>
              </Card>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </Container>
    </Box>
  );
};

export default LeadCollection; 