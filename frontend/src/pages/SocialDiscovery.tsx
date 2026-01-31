
import React, { useState } from 'react';
import {
    Box,
    Heading,
    Text,
    VStack,
    HStack,
    Input,
    Button,
    FormControl,
    FormLabel,
    SimpleGrid,
    useToast,
    Badge,
    Progress,
    Icon,
    Avatar,
    Flex,
    Spacer,
    Tag,
    TagLabel,
} from '@chakra-ui/react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    FiTarget,
    FiPlay,
    FiLinkedin,
    FiFacebook,
    FiInstagram,
    FiCheckCircle,
    FiCpu,
    FiZap,
    FiUserPlus
} from 'react-icons/fi';

const MotionBox = motion(Box);

const SocialDiscovery: React.FC = () => {
    const [isDiscovering, setIsDiscovering] = useState(false);
    const [leadsFound, setLeadsFound] = useState<any[]>([]);
    const toast = useToast();

    const startDiscovery = () => {
        setIsDiscovering(true);
        toast({
            title: 'X-Ray Engine Initialized',
            description: 'High-priority undergraduate scan is now active.',
            status: 'info',
            duration: 3000,
        });

        // Simulate finding leads
        setTimeout(() => {
            setLeadsFound([
                { name: 'Kavindu Perera', university: 'UoM', skills: ['Python', 'AI'], platform: 'linkedin', phone: '077 123 4567' },
                { name: 'Asha Fernando', university: 'SLIIT', skills: ['React', 'UX'], platform: 'facebook', phone: '071 987 6543' },
                { name: 'Dilshan Silva', university: 'IIT', skills: ['Java', 'Cloud'], platform: 'linkedin', phone: '075 444 3210' },
            ]);
        }, 2000);
    };

    return (
        <Box p={6}>
            <VStack spacing={10} align="stretch">
                <Flex align="center">
                    <VStack align="start" spacing={0}>
                        <HStack>
                            <Box bg="vibrant.gradient" p={2} borderRadius="12px">
                                <Icon as={FiTarget} color="white" boxSize={6} />
                            </Box>
                            <Heading size="lg" fontWeight="900" letterSpacing="-1px">Discovery Engine.</Heading>
                        </HStack>
                        <Text color="gray.500" ml={12}>Precise undergraduate targeting across social networks.</Text>
                    </VStack>
                </Flex>

                <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={10}>
                    {/* Configuration */}
                    <VStack spacing={6} align="stretch">
                        <Box
                            bg="rgba(255,255,255,0.03)" border="1px solid rgba(255,255,255,0.08)"
                            p={8} borderRadius="30px" backdropFilter="blur(20px)"
                        >
                            <VStack spacing={6}>
                                <FormControl>
                                    <FormLabel fontSize="xs" fontWeight="bold" color="gray.500" letterSpacing="1px">SCAN TARGETS</FormLabel>
                                    <HStack spacing={4}>
                                        <Icon as={FiLinkedin} boxSize={6} color="blue.400" cursor="pointer" opacity={1} />
                                        <Icon as={FiFacebook} boxSize={6} color="blue.600" cursor="pointer" opacity={0.3} />
                                        <Icon as={FiInstagram} boxSize={6} color="pink.500" cursor="pointer" opacity={0.3} />
                                    </HStack>
                                </FormControl>

                                <FormControl>
                                    <FormLabel fontSize="xs" fontWeight="bold" color="gray.500" letterSpacing="1px">SKILLSET KEYWORDS</FormLabel>
                                    <Input variant="filled" placeholder="e.g. Java, React, Marketing" />
                                </FormControl>

                                <FormControl>
                                    <FormLabel fontSize="xs" fontWeight="bold" color="gray.500" letterSpacing="1px">INSTITUTIONS</FormLabel>
                                    <Input variant="filled" placeholder="e.g. SLIIT, Moratuwa" />
                                </FormControl>

                                <Button
                                    variant="glow" w="100%" h="60px" size="lg"
                                    leftIcon={<FiPlay />} onClick={startDiscovery}
                                    isLoading={isDiscovering}
                                    loadingText="ENGAGING ENGINE"
                                >
                                    START DISCOVERY
                                </Button>
                            </VStack>
                        </Box>

                        {isDiscovering && (
                            <MotionBox
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                bg="rgba(139, 92, 246, 0.1)" border="1px solid rgba(139, 92, 246, 0.2)"
                                p={6} borderRadius="24px"
                            >
                                <HStack mb={4}>
                                    <Icon as={FiCpu} color="vibrant.purple" />
                                    <Text fontSize="sm" fontWeight="bold" color="vibrant.purple">ENGINE STATUS: ACTIVE</Text>
                                </HStack>
                                <Progress value={leadsFound.length > 0 ? 100 : 35} size="xs" colorScheme="purple" borderRadius="full" isIndeterminate={leadsFound.length === 0} />
                                <Text fontSize="xs" color="gray.500" mt={3}>Analyzing LinkedIn X-Ray results for "Undergraduate" + "React"...</Text>
                            </MotionBox>
                        )}
                    </VStack>

                    {/* Results Feed */}
                    <Box gridColumn={{ lg: 'span 2' }}>
                        <VStack align="stretch" spacing={6}>
                            <HStack justify="space-between">
                                <Heading size="md" fontWeight="800">Live Lead Feed.</Heading>
                                <Badge colorScheme="blue" borderRadius="full" px={3}>{leadsFound.length} Detected</Badge>
                            </HStack>

                            <AnimatePresence>
                                {leadsFound.map((lead, i) => (
                                    <MotionBox
                                        key={i}
                                        initial={{ opacity: 0, x: 20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: i * 0.1 }}
                                        bg="rgba(255, 255, 255, 0.02)"
                                        border="1px solid rgba(255, 255, 255, 0.05)"
                                        p={5} borderRadius="24px"
                                        _hover={{ bg: 'rgba(255, 255, 255, 0.04)', borderColor: 'rgba(255,255,255,0.1)' }}
                                    >
                                        <Flex align="center">
                                            <Avatar name={lead.name} src={`https://i.pravatar.cc/100?u=${lead.name}`} borderRadius="16px" mr={4} />
                                            <VStack align="start" spacing={0}>
                                                <HStack>
                                                    <Text fontWeight="bold" fontSize="lg">{lead.name}</Text>
                                                    <Icon as={FiCheckCircle} color="green.400" boxSize={4} />
                                                </HStack>
                                                <Text color="gray.500" fontSize="sm">{lead.university} • {lead.skills.join(', ')}</Text>
                                            </VStack>
                                            <Spacer />
                                            <VStack align="end" spacing={2}>
                                                <HStack>
                                                    <Tag size="sm" colorScheme="green" variant="subtle" borderRadius="full">
                                                        <TagLabel>{lead.phone}</TagLabel>
                                                    </Tag>
                                                    <Icon as={lead.platform === 'linkedin' ? FiLinkedin : FiFacebook} color="gray.600" />
                                                </HStack>
                                                <Button size="xs" variant="glass" leftIcon={<FiUserPlus />}>Add to CRM</Button>
                                            </VStack>
                                        </Flex>
                                    </MotionBox>
                                ))}
                            </AnimatePresence>

                            {leadsFound.length === 0 && !isDiscovering && (
                                <VStack py={20} spacing={4}>
                                    <Icon as={FiZap} boxSize={12} color="gray.700" />
                                    <Text color="gray.600">Enter parameters and start the discovery engine to find leads.</Text>
                                </VStack>
                            )}
                        </VStack>
                    </Box>
                </SimpleGrid>
            </VStack>
        </Box>
    );
};

export default SocialDiscovery;
