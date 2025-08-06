import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Badge,
  Avatar,
  Select,
  useColorModeValue,
  Flex,
  Divider,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';

export type LeadStage = 'to_contact' | 'in_progress' | 'converted';

export interface User {
  id: string;
  name: string;
  avatarUrl?: string;
}

export interface KanbanLead {
  id: string;
  name: string;
  email?: string;
  company?: string;
  stage: LeadStage;
  owners: string[]; // user IDs
}

const stageLabels: Record<LeadStage, string> = {
  to_contact: 'To Contact',
  in_progress: 'In Progress',
  converted: 'Converted',
};

const stageColors: Record<LeadStage, string> = {
  to_contact: 'yellow',
  in_progress: 'blue',
  converted: 'green',
};

interface LeadKanbanProps {
  leads: KanbanLead[];
  users: User[];
  onStageChange: (leadId: string, newStage: LeadStage) => void;
  onOwnerChange: (leadId: string, owners: string[]) => void;
}

export const LeadKanban: React.FC<LeadKanbanProps> = ({
  leads,
  users,
  onStageChange,
  onOwnerChange,
}) => {
  const { t } = useTranslation();
  const [draggedId, setDraggedId] = useState<string | null>(null);

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  const handleDragStart = (id: string) => setDraggedId(id);
  const handleDragEnd = () => setDraggedId(null);
  const handleDrop = (stage: LeadStage) => {
    if (draggedId) {
      onStageChange(draggedId, stage);
      setDraggedId(null);
    }
  };

  const handleStageChange = (leadId: string, newStage: LeadStage) => {
    onStageChange(leadId, newStage);
  };

  const handleOwnerChange = (leadId: string, owners: string[]) => {
    onOwnerChange(leadId, owners);
  };

  return (
    <Box>
      <Flex gap={4} overflowX="auto" pb={4}>
        {(['to_contact', 'in_progress', 'converted'] as LeadStage[]).map((stage) => (
          <Box
            key={stage}
            flex="1"
            minW="250px"
            bg={`${stageColors[stage]}.50`}
            borderRadius="lg"
            p={4}
            onDragOver={(e) => e.preventDefault()}
            onDrop={() => handleDrop(stage)}
          >
            <VStack spacing={4} align="stretch">
              {/* Column Header */}
              <HStack justify="space-between">
                <Heading size="sm">{stageLabels[stage]}</Heading>
                <Badge colorScheme={stageColors[stage]}>
                  {leads.filter((l) => l.stage === stage).length}
                </Badge>
              </HStack>

              <Divider />

              {/* Lead Cards */}
              <VStack spacing={3} align="stretch">
                {leads
                  .filter((l) => l.stage === stage)
                  .map((lead) => (
                    <Box
                      key={lead.id}
                      bg={bgColor}
                      border="1px"
                      borderColor={borderColor}
                      borderRadius="md"
                      p={3}
                      shadow="sm"
                      cursor="move"
                      opacity={draggedId === lead.id ? 0.5 : 1}
                      draggable
                      onDragStart={() => handleDragStart(lead.id)}
                      onDragEnd={handleDragEnd}
                    >
                      <VStack spacing={2} align="stretch">
                        {/* Lead Name and Owners */}
                        <HStack justify="space-between">
                          <Text fontWeight="medium" fontSize="sm">
                            {lead.name}
                          </Text>
                          <HStack spacing={1}>
                            {lead.owners.map((ownerId) => {
                              const user = users.find((u) => u.id === ownerId);
                              return user ? (
                                <Avatar
                                  key={user.id}
                                  src={user.avatarUrl}
                                  name={user.name}
                                  size="xs"
                                  border="2px"
                                  borderColor="white"
                                />
                              ) : null;
                            })}
                          </HStack>
                        </HStack>

                        {/* Lead Details */}
                        {lead.company && (
                          <Text fontSize="xs" color={textColor}>
                            {lead.company}
                          </Text>
                        )}
                        {lead.email && (
                          <Text fontSize="xs" color={textColor}>
                            {lead.email}
                          </Text>
                        )}

                        {/* Stage Change Dropdown */}
                        <Box>
                          <Select
                            size="xs"
                            value={lead.stage}
                            onChange={(e) =>
                              handleStageChange(lead.id, e.target.value as LeadStage)
                            }
                          >
                            <option value="to_contact">To Contact</option>
                            <option value="in_progress">In Progress</option>
                            <option value="converted">Converted</option>
                          </Select>
                        </Box>

                        {/* Owner Assignment */}
                        <Box>
                          <Select
                            size="xs"
                            multiple
                            value={lead.owners}
                            onChange={(e) => {
                              const selected = Array.from(e.target.selectedOptions).map(
                                (opt) => opt.value
                              );
                              handleOwnerChange(lead.id, selected);
                            }}
                          >
                            {users.map((user) => (
                              <option key={user.id} value={user.id}>
                                {user.name}
                              </option>
                            ))}
                          </Select>
                        </Box>
                      </VStack>
                    </Box>
                  ))}
              </VStack>
            </VStack>
          </Box>
        ))}
      </Flex>
    </Box>
  );
};

export default LeadKanban; 