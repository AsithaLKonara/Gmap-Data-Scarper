import React, { useState } from 'react';
import {
  Box,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Text,
  VStack,
  HStack,
  Input,
  Button,
  FormControl,
  FormLabel,
  Select,
  Textarea,
  useToast,
  useColorModeValue,
  Badge,
  Progress,
  Alert,
  AlertIcon,
  SimpleGrid,
  Divider,
} from '@chakra-ui/react';
import { FiSearch, FiMapPin, FiFilter, FiPlay } from 'react-icons/fi';

interface SearchFilters {
  location: string;
  category: string;
  radius: string;
  maxResults: number;
  includePhone: boolean;
  includeWebsite: boolean;
}

const LeadSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({
    location: '',
    category: '',
    radius: '10',
    maxResults: 100,
    includePhone: true,
    includeWebsite: true,
  });
  const [isSearching, setIsSearching] = useState(false);
  const [searchProgress, setSearchProgress] = useState(0);
  const [searchResults, setSearchResults] = useState<any[]>([]);

  const toast = useToast();
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const categories = [
    'Restaurants',
    'Auto Parts',
    'Salons',
    'Furniture',
    'Electronics',
    'Healthcare',
    'Education',
    'Real Estate',
    'Automotive',
    'Beauty & Spa',
  ];

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast({
        title: 'Search Query Required',
        description: 'Please enter a search query to continue.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsSearching(true);
    setSearchProgress(0);
    setSearchResults([]);

    // Simulate search progress
    const interval = setInterval(() => {
      setSearchProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsSearching(false);
          
          // Mock results
          const mockResults = Array.from({ length: 25 }, (_, i) => ({
            id: i + 1,
            name: `${searchQuery} Business ${i + 1}`,
            category: filters.category || 'General',
            address: `${Math.floor(Math.random() * 100)} Main St, ${filters.location || 'City'}`,
            phone: `+94 ${Math.floor(Math.random() * 90000000) + 10000000}`,
            website: `www.business${i + 1}.lk`,
            rating: (Math.random() * 2 + 3).toFixed(1),
            reviews: Math.floor(Math.random() * 500) + 10,
          }));

          setSearchResults(mockResults);
          
          toast({
            title: 'Search Completed',
            description: `Found ${mockResults.length} leads for "${searchQuery}"`,
            status: 'success',
            duration: 5000,
            isClosable: true,
          });
          
          return 100;
        }
        return prev + 10;
      });
    }, 500);
  };

  const handleFilterChange = (field: keyof SearchFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  return (
    <Box>
      {/* Page Header */}
      <Box mb={6}>
        <Heading size="lg" mb={2}>
          Lead Search
        </Heading>
        <Text color="gray.600">
          Search Google Maps for business leads with advanced filtering options.
        </Text>
      </Box>

      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
        {/* Search Form */}
        <Card bg={cardBg} border="1px" borderColor={borderColor}>
          <CardHeader>
            <Heading size="md">Search Configuration</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4}>
              {/* Search Query */}
              <FormControl>
                <FormLabel>Search Query</FormLabel>
                <Input
                  placeholder="e.g., restaurants in Colombo, auto parts in Kandy"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  size="lg"
                />
              </FormControl>

              {/* Location */}
              <FormControl>
                <FormLabel>Location</FormLabel>
                <Input
                  placeholder="City, Country"
                  value={filters.location}
                  onChange={(e) => handleFilterChange('location', e.target.value)}
                />
              </FormControl>

              {/* Category */}
              <FormControl>
                <FormLabel>Business Category</FormLabel>
                <Select
                  value={filters.category}
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                  placeholder="Select category"
                >
                  {categories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </Select>
              </FormControl>

              {/* Search Radius */}
              <FormControl>
                <FormLabel>Search Radius (km)</FormLabel>
                <Select
                  value={filters.radius}
                  onChange={(e) => handleFilterChange('radius', e.target.value)}
                >
                  <option value="5">5 km</option>
                  <option value="10">10 km</option>
                  <option value="25">25 km</option>
                  <option value="50">50 km</option>
                  <option value="100">100 km</option>
                </Select>
              </FormControl>

              {/* Max Results */}
              <FormControl>
                <FormLabel>Maximum Results</FormLabel>
                <Select
                  value={filters.maxResults}
                  onChange={(e) => handleFilterChange('maxResults', parseInt(e.target.value))}
                >
                  <option value={50}>50 results</option>
                  <option value={100}>100 results</option>
                  <option value={200}>200 results</option>
                  <option value={500}>500 results</option>
                </Select>
              </FormControl>

              {/* Search Button */}
              <Button
                leftIcon={<FiPlay />}
                colorScheme="blue"
                size="lg"
                w="100%"
                onClick={handleSearch}
                isLoading={isSearching}
                loadingText="Searching..."
              >
                Start Search
              </Button>
            </VStack>
          </CardBody>
        </Card>

        {/* Search Progress & Results */}
        <VStack spacing={6}>
          {/* Search Progress */}
          {isSearching && (
            <Card bg={cardBg} border="1px" borderColor={borderColor} w="100%">
              <CardBody>
                <VStack spacing={4}>
                  <HStack>
                    <FiSearch />
                    <Text fontWeight="medium">Searching Google Maps...</Text>
                  </HStack>
                  <Progress value={searchProgress} colorScheme="blue" w="100%" />
                  <Text fontSize="sm" color="gray.600">
                    {searchProgress}% complete
                  </Text>
                </VStack>
              </CardBody>
            </Card>
          )}

          {/* Search Results */}
          {searchResults.length > 0 && (
            <Card bg={cardBg} border="1px" borderColor={borderColor} w="100%">
              <CardHeader>
                <HStack justify="space-between">
                  <Heading size="md">Search Results</Heading>
                  <Badge colorScheme="green" fontSize="sm">
                    {searchResults.length} leads found
                  </Badge>
                </HStack>
              </CardHeader>
              <CardBody>
                <VStack spacing={3} maxH="400px" overflowY="auto">
                  {searchResults.slice(0, 10).map((result) => (
                    <Box
                      key={result.id}
                      w="100%"
                      p={3}
                      border="1px"
                      borderColor={borderColor}
                      borderRadius="lg"
                    >
                      <VStack align="start" spacing={2}>
                        <HStack justify="space-between" w="100%">
                          <Text fontWeight="medium" fontSize="sm">
                            {result.name}
                          </Text>
                          <Badge colorScheme="blue" fontSize="xs">
                            {result.rating} ⭐ ({result.reviews})
                          </Badge>
                        </HStack>
                        <Text fontSize="sm" color="gray.600">
                          {result.category}
                        </Text>
                        <Text fontSize="sm" color="gray.600">
                          📍 {result.address}
                        </Text>
                        {result.phone && (
                          <Text fontSize="sm" color="gray.600">
                            📞 {result.phone}
                          </Text>
                        )}
                        {result.website && (
                          <Text fontSize="sm" color="blue.600">
                            🌐 {result.website}
                          </Text>
                        )}
                      </VStack>
                    </Box>
                  ))}
                </VStack>
                
                {searchResults.length > 10 && (
                  <Box mt={4} textAlign="center">
                    <Text fontSize="sm" color="gray.600">
                      Showing 10 of {searchResults.length} results
                    </Text>
                    <Button size="sm" variant="outline" mt={2}>
                      View All Results
                    </Button>
                  </Box>
                )}
              </CardBody>
            </Card>
          )}

          {/* Quick Actions */}
          {searchResults.length > 0 && (
            <Card bg={cardBg} border="1px" borderColor={borderColor} w="100%">
              <CardHeader>
                <Heading size="md">Quick Actions</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={3}>
                  <Button colorScheme="green" w="100%" size="sm">
                    Export to CSV
                  </Button>
                  <Button colorScheme="blue" w="100%" size="sm">
                    Save to Collection
                  </Button>
                  <Button colorScheme="purple" w="100%" size="sm">
                    Run Lead Scoring
                  </Button>
                </VStack>
              </CardBody>
            </Card>
          )}
        </VStack>
      </SimpleGrid>
    </Box>
  );
};

export default LeadSearch; 