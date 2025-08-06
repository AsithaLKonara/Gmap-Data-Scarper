import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Button,
  Badge,
  useColorModeValue,
  Divider,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import {
  FiUsers,
  FiGitMerge,
  FiX,
  FiCheck,
  FiAlertTriangle,
} from 'react-icons/fi';

export interface Lead {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  owners?: string[];
}

export interface DuplicateGroup {
  leads: Lead[];
  reason: string; // e.g. 'Same email', 'Similar name'
}

interface DeduplicationPanelProps {
  duplicates: DuplicateGroup[];
  onMerge: (leadIds: string[]) => void;
  onIgnore: (leadIds: string[]) => void;
  onAutoMerge: () => void;
}

export const DeduplicationPanel: React.FC<DeduplicationPanelProps> = ({
  duplicates,
  onMerge,
  onIgnore,
  onAutoMerge,
}) => {
  const { t } = useTranslation();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  if (!duplicates.length) {
    return (
      <Box
        bg={bgColor}
        border="1px"
        borderColor={borderColor}
        borderRadius="lg"
        p={6}
        textAlign="center"
      >
        <VStack spacing={4}>
          <FiCheck size={48} color="green" />
          <Heading size="md" color="green.500">No Duplicates Found</Heading>
          <Text color={textColor}>
            Your lead database is clean and free of duplicates!
          </Text>
        </VStack>
      </Box>
    );
  }

  return (
    <Box
      bg={bgColor}
      border="1px"
      borderColor={borderColor}
      borderRadius="lg"
      p={6}
    >
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <VStack align="start" spacing={1}>
            <HStack>
              <FiAlertTriangle color="orange" />
              <Heading size="md">Potential Duplicate Leads</Heading>
            </HStack>
            <Text color={textColor}>
              Found {duplicates.length} groups of potential duplicates
            </Text>
          </VStack>
          <Button
            leftIcon={<FiGitMerge />}
            colorScheme="blue"
            variant="outline"
            onClick={onAutoMerge}
          >
            Auto-merge Exact Matches
          </Button>
        </HStack>

        <Divider />

        {/* Duplicate Groups */}
        <VStack spacing={4} align="stretch">
          {duplicates.map((group, idx) => (
            <Box
              key={idx}
              border="1px"
              borderColor={borderColor}
              borderRadius="lg"
              p={4}
              bg="gray.50"
            >
              <VStack spacing={4} align="stretch">
                {/* Reason */}
                <HStack justify="space-between">
                  <Badge colorScheme="orange" variant="subtle">
                    {group.reason}
                  </Badge>
                  <Text fontSize="sm" color={textColor}>
                    {group.leads.length} leads
                  </Text>
                </HStack>

                {/* Lead Cards */}
                <Box
                  display="grid"
                  gridTemplateColumns={{ base: '1fr', md: 'repeat(auto-fit, minmax(250px, 1fr))' }}
                  gap={4}
                >
                  {group.leads.map((lead) => (
                    <Box
                      key={lead.id}
                      bg={bgColor}
                      border="1px"
                      borderColor={borderColor}
                      borderRadius="md"
                      p={3}
                    >
                      <VStack spacing={2} align="stretch">
                        <Text fontWeight="medium" fontSize="sm">
                          {lead.name}
                        </Text>
                        {lead.email && (
                          <Text fontSize="xs" color={textColor}>
                            Email: {lead.email}
                          </Text>
                        )}
                        {lead.phone && (
                          <Text fontSize="xs" color={textColor}>
                            Phone: {lead.phone}
                          </Text>
                        )}
                        {lead.company && (
                          <Text fontSize="xs" color={textColor}>
                            Company: {lead.company}
                          </Text>
                        )}
                        {lead.owners && lead.owners.length > 0 && (
                          <Text fontSize="xs" color={textColor}>
                            Owners: {lead.owners.join(', ')}
                          </Text>
                        )}
                      </VStack>
                    </Box>
                  ))}
                </Box>

                {/* Action Buttons */}
                <HStack spacing={2} justify="end">
                  <Button
                    size="sm"
                    leftIcon={<FiGitMerge />}
                    colorScheme="blue"
                    onClick={() => onMerge(group.leads.map((l) => l.id))}
                  >
                    Merge Leads
                  </Button>
                  <Button
                    size="sm"
                    leftIcon={<FiX />}
                    variant="outline"
                    onClick={() => onIgnore(group.leads.map((l) => l.id))}
                  >
                    Ignore
                  </Button>
                </HStack>
              </VStack>
            </Box>
          ))}
        </VStack>

        {/* Summary */}
        <Alert status="info" borderRadius="md">
          <AlertIcon />
          <Box>
            <AlertTitle>Duplicate Detection</AlertTitle>
            <AlertDescription>
              Review each group carefully before merging. Merged leads will combine all information
              and keep the most recent data.
            </AlertDescription>
          </Box>
        </Alert>
      </VStack>
    </Box>
  );
};

export default DeduplicationPanel; 