import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Button,
  SimpleGrid,
  useColorModeValue,
  IconButton,
  useToast,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import {
  FiGrid,
  FiBarChart2,
  FiUsers,
  FiTrendingUp,
  FiCheckSquare,
  FiEye,
  FiEyeOff,
  FiMove,
} from 'react-icons/fi';

interface Widget {
  id: string;
  label: string;
  icon: React.ReactElement;
  content: React.ReactElement;
  hidden?: boolean;
}

const defaultWidgets: Widget[] = [
  {
    id: 'stats',
    label: 'Statistics',
    icon: <FiBarChart2 />,
    content: (
      <VStack spacing={4} align="stretch">
        <HStack justify="space-between">
          <Text fontWeight="medium">Total Leads</Text>
          <Text fontSize="lg" fontWeight="bold" color="blue.500">1,247</Text>
        </HStack>
        <HStack justify="space-between">
          <Text fontWeight="medium">Conversion Rate</Text>
          <Text fontSize="lg" fontWeight="bold" color="green.500">12.5%</Text>
        </HStack>
        <HStack justify="space-between">
          <Text fontWeight="medium">Revenue</Text>
          <Text fontSize="lg" fontWeight="bold" color="purple.500">$45,230</Text>
        </HStack>
      </VStack>
    ),
  },
  {
    id: 'leads',
    label: 'Recent Leads',
    icon: <FiUsers />,
    content: (
      <VStack spacing={3} align="stretch">
        <Box p={3} bg="gray.50" borderRadius="md">
          <Text fontWeight="medium">John Doe</Text>
          <Text fontSize="sm" color="gray.600">john@example.com</Text>
          <Text fontSize="sm" color="gray.600">Tech Corp</Text>
        </Box>
        <Box p={3} bg="gray.50" borderRadius="md">
          <Text fontWeight="medium">Jane Smith</Text>
          <Text fontSize="sm" color="gray.600">jane@example.com</Text>
          <Text fontSize="sm" color="gray.600">Design Studio</Text>
        </Box>
        <Box p={3} bg="gray.50" borderRadius="md">
          <Text fontWeight="medium">Mike Johnson</Text>
          <Text fontSize="sm" color="gray.600">mike@example.com</Text>
          <Text fontSize="sm" color="gray.600">Marketing Agency</Text>
        </Box>
      </VStack>
    ),
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: <FiTrendingUp />,
    content: (
      <VStack spacing={4} align="stretch">
        <Box>
          <Text fontWeight="medium" mb={2}>Lead Growth</Text>
          <Box h="100px" bg="gray.100" borderRadius="md" display="flex" alignItems="end" p={2}>
            <Box w="20%" h="60%" bg="blue.400" borderRadius="sm" mx={1}></Box>
            <Box w="20%" h="80%" bg="blue.400" borderRadius="sm" mx={1}></Box>
            <Box w="20%" h="40%" bg="blue.400" borderRadius="sm" mx={1}></Box>
            <Box w="20%" h="90%" bg="blue.400" borderRadius="sm" mx={1}></Box>
            <Box w="20%" h="70%" bg="blue.400" borderRadius="sm" mx={1}></Box>
          </Box>
        </Box>
        <Text fontSize="sm" color="gray.600" textAlign="center">
          Last 5 days
        </Text>
      </VStack>
    ),
  },
  {
    id: 'tasks',
    label: 'Tasks',
    icon: <FiCheckSquare />,
    content: (
      <VStack spacing={3} align="stretch">
        <HStack justify="space-between" p={2} bg="green.50" borderRadius="md">
          <Text fontSize="sm">Follow up with John Doe</Text>
          <Text fontSize="xs" color="green.600">Today</Text>
        </HStack>
        <HStack justify="space-between" p={2} bg="yellow.50" borderRadius="md">
          <Text fontSize="sm">Review lead scoring</Text>
          <Text fontSize="xs" color="yellow.600">Tomorrow</Text>
        </HStack>
        <HStack justify="space-between" p={2} bg="blue.50" borderRadius="md">
          <Text fontSize="sm">Update CRM data</Text>
          <Text fontSize="xs" color="blue.600">This week</Text>
        </HStack>
      </VStack>
    ),
  },
];

const CustomDashboard: React.FC = () => {
  const { t } = useTranslation();
  const toast = useToast();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  const [widgets, setWidgets] = useState<Widget[]>(() => {
    const saved = localStorage.getItem('dashboard_widgets');
    return saved ? JSON.parse(saved) : defaultWidgets;
  });
  const [draggedId, setDraggedId] = useState<string | null>(null);

  useEffect(() => {
    localStorage.setItem('dashboard_widgets', JSON.stringify(widgets));
  }, [widgets]);

  const onDragStart = (id: string) => setDraggedId(id);
  
  const onDragOver = (id: string) => {
    if (draggedId && draggedId !== id) {
      const fromIdx = widgets.findIndex((w) => w.id === draggedId);
      const toIdx = widgets.findIndex((w) => w.id === id);
      const newWidgets = [...widgets];
      const [moved] = newWidgets.splice(fromIdx, 1);
      newWidgets.splice(toIdx, 0, moved);
      setWidgets(newWidgets);
    }
  };
  
  const onDragEnd = () => setDraggedId(null);

  const toggleWidget = (id: string) => {
    setWidgets((widgets) =>
      widgets.map((w) => (w.id === id ? { ...w, hidden: !w.hidden } : w))
    );
    toast({
      title: 'Widget visibility updated',
      status: 'success',
      duration: 2000,
    });
  };

  const resetLayout = () => {
    setWidgets(defaultWidgets);
    toast({
      title: 'Layout reset to default',
      status: 'info',
      duration: 3000,
    });
  };

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <VStack align="start" spacing={1}>
            <Heading size="lg">Custom Dashboard</Heading>
            <Text color={textColor}>
              Customize your dashboard layout and widgets
            </Text>
          </VStack>
          <Button
            leftIcon={<FiGrid />}
            variant="outline"
            onClick={resetLayout}
          >
            Reset Layout
          </Button>
        </HStack>

        {/* Widget Controls */}
        <Box>
          <Text fontWeight="medium" mb={3}>Widget Controls</Text>
          <HStack spacing={2} flexWrap="wrap">
            {widgets.map((widget) => (
              <Button
                key={widget.id}
                size="sm"
                variant={widget.hidden ? 'outline' : 'solid'}
                leftIcon={widget.hidden ? <FiEyeOff /> : <FiEye />}
                onClick={() => toggleWidget(widget.id)}
              >
                {widget.hidden ? `Show ${widget.label}` : `Hide ${widget.label}`}
              </Button>
            ))}
          </HStack>
        </Box>

        {/* Widget Grid */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
          {widgets
            .filter((w) => !w.hidden)
            .map((widget) => (
              <Box
                key={widget.id}
                bg={bgColor}
                border="1px"
                borderColor={borderColor}
                borderRadius="lg"
                p={4}
                shadow="md"
                draggable
                onDragStart={() => onDragStart(widget.id)}
                onDragOver={() => onDragOver(widget.id)}
                onDragEnd={onDragEnd}
                opacity={draggedId === widget.id ? 0.5 : 1}
                cursor="move"
                _hover={{ shadow: 'lg' }}
                transition="all 0.2s"
              >
                <VStack spacing={4} align="stretch">
                  {/* Widget Header */}
                  <HStack justify="space-between">
                    <HStack>
                      {widget.icon}
                      <Text fontWeight="medium">{widget.label}</Text>
                    </HStack>
                    <IconButton
                      size="sm"
                      variant="ghost"
                      icon={<FiMove />}
                      aria-label="Drag widget"
                    />
                  </HStack>

                  {/* Widget Content */}
                  <Box>{widget.content}</Box>
                </VStack>
              </Box>
            ))}
        </SimpleGrid>

        {/* Empty State */}
        {widgets.filter((w) => !w.hidden).length === 0 && (
          <Box
            textAlign="center"
            py={12}
            border="2px dashed"
            borderColor={borderColor}
            borderRadius="lg"
          >
            <VStack spacing={4}>
              <FiGrid size={48} color="gray" />
              <Text fontSize="lg" fontWeight="medium" color={textColor}>
                No widgets visible
              </Text>
              <Text color={textColor}>
                Use the controls above to show widgets
              </Text>
            </VStack>
          </Box>
        )}
      </VStack>
    </Box>
  );
};

export default CustomDashboard; 