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
  Textarea,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  IconButton,
  useColorModeValue,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import {
  FiPlus,
  FiEdit,
  FiTrash2,
  FiEye,
  FiCopy,
  FiCode,
  FiGlobe,
} from 'react-icons/fi';

interface Widget {
  id: number;
  type: string;
  config?: Record<string, any>;
  embed_code?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

const WIDGET_TYPES = [
  { value: 'lead_capture', label: 'Lead Capture Form' },
  { value: 'testimonial', label: 'Testimonial Widget' },
  { value: 'metrics', label: 'Metrics Badge' },
  { value: 'contact_form', label: 'Contact Form' },
  { value: 'newsletter', label: 'Newsletter Signup' },
];

const Widgets: React.FC = () => {
  const { t } = useTranslation();
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  const [widgets, setWidgets] = useState<Widget[]>([]);
  const [loading, setLoading] = useState(false);
  const [newType, setNewType] = useState('lead_capture');
  const [newConfig, setNewConfig] = useState('');
  const [editingWidget, setEditingWidget] = useState<Widget | null>(null);
  const [editConfig, setEditConfig] = useState('');

  // Mock data - replace with actual API calls
  useEffect(() => {
    const mockWidgets: Widget[] = [
      {
        id: 1,
        type: 'lead_capture',
        config: {
          title: 'Get Your Free Leads',
          buttonText: 'Download Now',
          fields: ['name', 'email', 'company'],
        },
        embed_code: '<script src="https://leadtap.com/widget.js?id=1"></script>',
        is_active: true,
        created_at: '2024-01-10T09:00:00Z',
      },
      {
        id: 2,
        type: 'testimonial',
        config: {
          title: 'What Our Customers Say',
          testimonials: [
            { name: 'John Doe', company: 'Tech Corp', text: 'Amazing results!' },
          ],
        },
        embed_code: '<script src="https://leadtap.com/widget.js?id=2"></script>',
        is_active: false,
        created_at: '2024-01-12T14:30:00Z',
      },
    ];
    setWidgets(mockWidgets);
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      
      const configObj = newConfig ? JSON.parse(newConfig) : {};
      const newWidget: Widget = {
        id: Date.now(),
        type: newType,
        config: configObj,
        embed_code: `<script src="https://leadtap.com/widget.js?id=${Date.now()}"></script>`,
        is_active: true,
        created_at: new Date().toISOString(),
      };
      
      setWidgets([...widgets, newWidget]);
      toast({
        title: 'Widget created',
        status: 'success',
        duration: 3000,
      });
      onClose();
      setNewConfig('');
      setNewType('lead_capture');
    } catch (error) {
      toast({
        title: 'Error creating widget',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (widget: Widget) => {
    setEditingWidget(widget);
    setEditConfig(widget.config ? JSON.stringify(widget.config, null, 2) : '');
    onOpen();
  };

  const handleEditSave = async () => {
    if (!editingWidget) return;
    
    setLoading(true);
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      
      const configObj = editConfig ? JSON.parse(editConfig) : {};
      const updatedWidgets = widgets.map((w) =>
        w.id === editingWidget.id ? { ...w, config: configObj } : w
      );
      
      setWidgets(updatedWidgets);
      toast({
        title: 'Widget updated',
        status: 'success',
        duration: 3000,
      });
      setEditingWidget(null);
      onClose();
    } catch (error) {
      toast({
        title: 'Error updating widget',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (widgetId: number) => {
    if (!window.confirm('Delete this widget?')) return;
    
    setLoading(true);
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 500));
      
      setWidgets(widgets.filter((w) => w.id !== widgetId));
      toast({
        title: 'Widget deleted',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error deleting widget',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (widget: Widget) => {
    try {
      // Mock API call
      await new Promise((resolve) => setTimeout(resolve, 500));
      
      const updatedWidgets = widgets.map((w) =>
        w.id === widget.id ? { ...w, is_active: !w.is_active } : w
      );
      
      setWidgets(updatedWidgets);
      toast({
        title: `Widget ${widget.is_active ? 'deactivated' : 'activated'}`,
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error updating widget',
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

  const getWidgetTypeLabel = (type: string) => {
    const widgetType = WIDGET_TYPES.find((wt) => wt.value === type);
    return widgetType ? widgetType.label : type;
  };

  return (
    <Box>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <VStack align="start" spacing={1}>
            <Heading size="lg">Widgets</Heading>
            <Text color={textColor}>
              Create and manage embeddable widgets for your website
            </Text>
          </VStack>
          <Button
            leftIcon={<FiPlus />}
            colorScheme="blue"
            onClick={() => {
              setEditingWidget(null);
              setNewConfig('');
              setNewType('lead_capture');
              onOpen();
            }}
          >
            Create Widget
          </Button>
        </HStack>

        {/* Widgets Table */}
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
                <Th>Type</Th>
                <Th>Status</Th>
                <Th>Created</Th>
                <Th>Embed Code</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {widgets.map((widget) => (
                <Tr key={widget.id}>
                  <Td>
                    <VStack align="start" spacing={1}>
                      <Text fontWeight="medium">
                        {getWidgetTypeLabel(widget.type)}
                      </Text>
                      <Text fontSize="sm" color={textColor}>
                        ID: {widget.id}
                      </Text>
                    </VStack>
                  </Td>
                  <Td>
                    <Badge colorScheme={widget.is_active ? 'green' : 'gray'}>
                      {widget.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </Td>
                  <Td>
                    <Text fontSize="sm">
                      {new Date(widget.created_at).toLocaleDateString()}
                    </Text>
                  </Td>
                  <Td>
                    <HStack spacing={2}>
                      <Text fontSize="sm" fontFamily="mono" maxW="200px" isTruncated>
                        {widget.embed_code}
                      </Text>
                      <IconButton
                        size="sm"
                        variant="ghost"
                        icon={<FiCopy />}
                        onClick={() => copyToClipboard(widget.embed_code || '')}
                        aria-label="Copy embed code"
                      />
                    </HStack>
                  </Td>
                  <Td>
                    <HStack spacing={1}>
                      <IconButton
                        size="sm"
                        variant="ghost"
                        icon={<FiEdit />}
                        onClick={() => handleEdit(widget)}
                        aria-label="Edit widget"
                      />
                      <IconButton
                        size="sm"
                        variant="ghost"
                        icon={<FiEye />}
                        onClick={() => copyToClipboard(widget.embed_code || '')}
                        aria-label="View embed code"
                      />
                      <IconButton
                        size="sm"
                        variant="ghost"
                        colorScheme="red"
                        icon={<FiTrash2 />}
                        onClick={() => handleDelete(widget.id)}
                        aria-label="Delete widget"
                      />
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>

        {/* Create/Edit Widget Modal */}
        <Modal isOpen={isOpen} onClose={onClose} size="lg">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>
              {editingWidget ? 'Edit Widget' : 'Create New Widget'}
            </ModalHeader>
            <form onSubmit={editingWidget ? handleEditSave : handleCreate}>
              <ModalBody>
                <VStack spacing={4}>
                  <FormControl isRequired>
                    <FormLabel>Widget Type</FormLabel>
                    <Select
                      value={editingWidget ? editingWidget.type : newType}
                      onChange={(e) =>
                        editingWidget
                          ? setEditingWidget({ ...editingWidget, type: e.target.value })
                          : setNewType(e.target.value)
                      }
                      isDisabled={!!editingWidget}
                    >
                      {WIDGET_TYPES.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </Select>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Configuration (JSON)</FormLabel>
                    <Textarea
                      value={editingWidget ? editConfig : newConfig}
                      onChange={(e) =>
                        editingWidget
                          ? setEditConfig(e.target.value)
                          : setNewConfig(e.target.value)
                      }
                      placeholder='{"title": "Widget Title", "buttonText": "Click Me"}'
                      rows={6}
                    />
                    <Text fontSize="xs" color={textColor} mt={1}>
                      Enter valid JSON configuration for the widget
                    </Text>
                  </FormControl>
                </VStack>
              </ModalBody>

              <ModalFooter>
                <Button variant="ghost" mr={3} onClick={onClose}>
                  Cancel
                </Button>
                <Button
                  type="submit"
                  isLoading={loading}
                  colorScheme="blue"
                >
                  {editingWidget ? 'Update' : 'Create'} Widget
                </Button>
              </ModalFooter>
            </form>
          </ModalContent>
        </Modal>
      </VStack>
    </Box>
  );
};

export default Widgets; 