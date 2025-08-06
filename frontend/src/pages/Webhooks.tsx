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
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Select,
  Switch,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  IconButton,
  useColorModeValue,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import {
  FiPlus,
  FiEdit,
  FiTrash2,
  FiEye,
  FiCopy,
  FiPlay,
  FiToggleLeft,
  FiToggleRight,
} from 'react-icons/fi';

interface Webhook {
  id: number;
  url: string;
  event: string;
  is_active: boolean;
  secret?: string;
  last_delivery_status?: string;
  last_delivery_at?: string;
  created_at: string;
  updated_at?: string;
}

const EVENT_OPTIONS = [
  { value: 'job.completed', label: 'Job Completed' },
  { value: 'lead.created', label: 'Lead Created' },
  { value: 'lead.updated', label: 'Lead Updated' },
  { value: 'lead.converted', label: 'Lead Converted' },
];

const Webhooks: React.FC = () => {
  const { t } = useTranslation();
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  const [webhooks, setWebhooks] = useState<Webhook[]>([]);
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState<Webhook | null>(null);
  const [form, setForm] = useState({
    url: '',
    event: EVENT_OPTIONS[0].value,
    secret: '',
  });

  // Mock data - replace with actual API calls
  useEffect(() => {
    const mockWebhooks: Webhook[] = [
      {
        id: 1,
        url: 'https://api.example.com/webhook',
        event: 'lead.created',
        is_active: true,
        secret: 'whsec_123456789',
        last_delivery_status: 'success',
        last_delivery_at: '2024-01-15T10:30:00Z',
        created_at: '2024-01-10T09:00:00Z',
      },
      {
        id: 2,
        url: 'https://crm.example.com/webhook',
        event: 'job.completed',
        is_active: false,
        secret: 'whsec_987654321',
        last_delivery_status: 'failed',
        last_delivery_at: '2024-01-14T15:45:00Z',
        created_at: '2024-01-08T14:30:00Z',
      },
    ];
    setWebhooks(mockWebhooks);
  }, []);

  const handleOpenModal = (webhook?: Webhook) => {
    setEditing(webhook || null);
    setForm(
      webhook
        ? { url: webhook.url, event: webhook.event, secret: webhook.secret || '' }
        : { url: '', event: EVENT_OPTIONS[0].value, secret: '' }
    );
    onOpen();
  };

  const handleSave = async () => {
    if (!form.url) {
      toast({
        title: 'URL required',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    setLoading(true);
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      if (editing) {
        // Update existing webhook
        setWebhooks(
          webhooks.map((wh) =>
            wh.id === editing.id ? { ...wh, ...form } : wh
          )
        );
        toast({
          title: 'Webhook updated',
          status: 'success',
          duration: 3000,
        });
      } else {
        // Create new webhook
        const newWebhook: Webhook = {
          id: Date.now(),
          url: form.url,
          event: form.event,
          is_active: true,
          secret: form.secret,
          created_at: new Date().toISOString(),
        };
        setWebhooks([...webhooks, newWebhook]);
        toast({
          title: 'Webhook created',
          status: 'success',
          duration: 3000,
        });
      }
      onClose();
    } catch (error) {
      toast({
        title: 'Error saving webhook',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this webhook?')) return;

    setLoading(true);
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setWebhooks(webhooks.filter((wh) => wh.id !== id));
      toast({
        title: 'Webhook deleted',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error deleting webhook',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (webhook: Webhook) => {
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 500));
      setWebhooks(
        webhooks.map((wh) =>
          wh.id === webhook.id ? { ...wh, is_active: !wh.is_active } : wh
        )
      );
      toast({
        title: `Webhook ${webhook.is_active ? 'deactivated' : 'activated'}`,
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error updating webhook',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleTest = async (webhook: Webhook) => {
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 2000));
      toast({
        title: 'Test webhook sent',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error testing webhook',
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

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'success':
        return 'green';
      case 'failed':
        return 'red';
      case 'pending':
        return 'yellow';
      default:
        return 'gray';
    }
  };

  return (
    <Box>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <VStack align="start" spacing={1}>
            <Heading size="lg">Webhooks</Heading>
            <Text color={textColor}>
              Configure webhooks to receive real-time notifications
            </Text>
          </VStack>
          <Button
            leftIcon={<FiPlus />}
            colorScheme="blue"
            onClick={() => handleOpenModal()}
          >
            Add Webhook
          </Button>
        </HStack>

        {/* Webhooks Table */}
        <Box
          bg={bgColor}
          border="1px"
          borderColor={borderColor}
          borderRadius="lg"
          overflow="hidden"
        >
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>URL</Th>
                <Th>Event</Th>
                <Th>Status</Th>
                <Th>Last Delivery</Th>
                <Th>Created</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {webhooks.map((webhook) => (
                <Tr key={webhook.id}>
                  <Td>
                    <Text fontSize="sm" maxW="200px" isTruncated>
                      {webhook.url}
                    </Text>
                  </Td>
                  <Td>
                    <Badge colorScheme="blue" variant="subtle">
                      {webhook.event}
                    </Badge>
                  </Td>
                  <Td>
                    <HStack spacing={2}>
                      <Switch
                        isChecked={webhook.is_active}
                        onChange={() => handleToggleActive(webhook)}
                        size="sm"
                      />
                      <Badge
                        colorScheme={webhook.is_active ? 'green' : 'gray'}
                        variant="subtle"
                      >
                        {webhook.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </HStack>
                  </Td>
                  <Td>
                    {webhook.last_delivery_at ? (
                      <VStack align="start" spacing={1}>
                        <Text fontSize="xs">
                          {new Date(webhook.last_delivery_at).toLocaleDateString()}
                        </Text>
                        <Badge
                          colorScheme={getStatusColor(webhook.last_delivery_status)}
                          size="sm"
                        >
                          {webhook.last_delivery_status}
                        </Badge>
                      </VStack>
                    ) : (
                      <Text fontSize="xs" color={textColor}>
                        Never
                      </Text>
                    )}
                  </Td>
                  <Td>
                    <Text fontSize="xs">
                      {new Date(webhook.created_at).toLocaleDateString()}
                    </Text>
                  </Td>
                  <Td>
                    <HStack spacing={1}>
                      <IconButton
                        size="sm"
                        variant="ghost"
                        icon={<FiPlay />}
                        aria-label="Test webhook"
                        onClick={() => handleTest(webhook)}
                      />
                      <IconButton
                        size="sm"
                        variant="ghost"
                        icon={<FiEdit />}
                        aria-label="Edit webhook"
                        onClick={() => handleOpenModal(webhook)}
                      />
                      <IconButton
                        size="sm"
                        variant="ghost"
                        colorScheme="red"
                        icon={<FiTrash2 />}
                        aria-label="Delete webhook"
                        onClick={() => handleDelete(webhook.id)}
                      />
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>

        {/* Add/Edit Webhook Modal */}
        <Modal isOpen={isOpen} onClose={onClose} size="lg">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>
              {editing ? 'Edit Webhook' : 'Add New Webhook'}
            </ModalHeader>
            <ModalBody>
              <VStack spacing={4}>
                <FormControl isRequired>
                  <FormLabel>Webhook URL</FormLabel>
                  <Input
                    value={form.url}
                    onChange={(e) => setForm({ ...form, url: e.target.value })}
                    placeholder="https://your-domain.com/webhook"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Event Type</FormLabel>
                  <Select
                    value={form.event}
                    onChange={(e) => setForm({ ...form, event: e.target.value })}
                  >
                    {EVENT_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>Secret Key (Optional)</FormLabel>
                  <Input
                    value={form.secret}
                    onChange={(e) => setForm({ ...form, secret: e.target.value })}
                    placeholder="whsec_your_secret_key"
                  />
                </FormControl>
              </VStack>
            </ModalBody>

            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onClose}>
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                isLoading={loading}
                colorScheme="blue"
              >
                {editing ? 'Update' : 'Create'} Webhook
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Box>
  );
};

export default Webhooks; 