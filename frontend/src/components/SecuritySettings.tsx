import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Card,
  CardBody,
  Button,
  Switch,
  Badge,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  Input,
  FormControl,
  FormLabel,
  Select,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Avatar,
  IconButton,
  Tooltip,
  useColorModeValue,
  Divider,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
} from '@chakra-ui/react';
import {
  LockIcon,
  DownloadIcon,
  CheckIcon,
  CloseIcon,
} from '@chakra-ui/icons';
import { FiEye, FiEyeOff, FiRefreshCw, FiShield, FiUser } from 'react-icons/fi';
import { MdQrCode } from 'react-icons/md';
import * as api from '../api';

interface SecuritySettings {
  twoFactorEnabled: boolean;
  backupCodesGenerated: boolean;
  lastPasswordChange: string;
  failedLoginAttempts: number;
  accountLocked: boolean;
  sessionTimeout: number;
  ipWhitelist: string[];
  auditLogEnabled: boolean;
}

interface UserRole {
  id: string;
  name: string;
  permissions: string[];
  description: string;
  userCount: number;
}

interface AuditLog {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  resource: string;
  ipAddress: string;
  userAgent: string;
  status: 'success' | 'failed' | 'warning';
}

const SecuritySettings: React.FC = () => {
  const [securitySettings, setSecuritySettings] = useState<SecuritySettings>({
    twoFactorEnabled: false,
    backupCodesGenerated: false,
    lastPasswordChange: '2024-01-15',
    failedLoginAttempts: 0,
    accountLocked: false,
    sessionTimeout: 30,
    ipWhitelist: [],
    auditLogEnabled: true,
  });

  const [show2FAModal, setShow2FAModal] = useState(false);
  const [showBackupCodesModal, setShowBackupCodesModal] = useState(false);
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [qrCode, setQrCode] = useState('');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [verificationCode, setVerificationCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [userRoles, setUserRoles] = useState<UserRole[]>([]);

  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Remove mock data useEffect and replace with real API calls
  useEffect(() => {
    async function fetchSecurityData() {
      try {
        const logs = await api.getMyAuditLogs();
        setAuditLogs(logs || []);
        // TODO: Replace with real API call for user roles if available
        // setUserRoles(await api.getUserRoles());
      } catch (e) {
        setAuditLogs([]);
      }
    }
    fetchSecurityData();
  }, []);

  const handle2FAToggle = async () => {
    if (!securitySettings.twoFactorEnabled) {
      setShow2FAModal(true);
    } else {
      // Disable 2FA
      setSecuritySettings(prev => ({ ...prev, twoFactorEnabled: false }));
      toast({
        title: '2FA Disabled',
        description: 'Two-factor authentication has been disabled.',
        status: 'info',
        duration: 3000,
      });
    }
  };

  const handleGenerateBackupCodes = async () => {
    setLoading(true);
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      const codes = Array.from({ length: 10 }, () => 
        Math.random().toString(36).substring(2, 8).toUpperCase()
      );
      setBackupCodes(codes);
      setShowBackupCodesModal(true);
      setSecuritySettings(prev => ({ ...prev, backupCodesGenerated: true }));
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to generate backup codes.',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleVerify2FA = async () => {
    if (!verificationCode.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter the verification code.',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    setLoading(true);
    try {
      // Mock verification
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (verificationCode === '123456') { // Mock valid code
        setSecuritySettings(prev => ({ ...prev, twoFactorEnabled: true }));
        setShow2FAModal(false);
        setVerificationCode('');
        toast({
          title: '2FA Enabled',
          description: 'Two-factor authentication has been enabled successfully.',
          status: 'success',
          duration: 3000,
        });
      } else {
        toast({
          title: 'Invalid Code',
          description: 'Please enter a valid verification code.',
          status: 'error',
          duration: 3000,
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to verify code.',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const getSecurityScore = () => {
    let score = 0;
    if (securitySettings.twoFactorEnabled) score += 30;
    if (securitySettings.backupCodesGenerated) score += 15;
    if (securitySettings.auditLogEnabled) score += 20;
    if (securitySettings.ipWhitelist.length > 0) score += 15;
    if (securitySettings.sessionTimeout <= 30) score += 20;
    return Math.min(score, 100);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'green';
      case 'failed': return 'red';
      case 'warning': return 'yellow';
      default: return 'gray';
    }
  };

  const securityScore = getSecurityScore();

  return (
    <Box>
      <VStack spacing={6} align="stretch">
        {/* Security Overview */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <HStack justify="space-between" mb={4}>
              <Text fontSize="lg" fontWeight="bold">Security Overview</Text>
              <Badge colorScheme={securityScore >= 80 ? 'green' : securityScore >= 60 ? 'yellow' : 'red'}>
                Score: {securityScore}/100
              </Badge>
            </HStack>
            
            <Progress value={securityScore} colorScheme={securityScore >= 80 ? 'green' : securityScore >= 60 ? 'yellow' : 'red'} mb={4} />
            
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
              <Stat>
                <StatLabel>Last Password Change</StatLabel>
                <StatNumber fontSize="sm">{securitySettings.lastPasswordChange}</StatNumber>
                <StatHelpText>30 days ago</StatHelpText>
              </Stat>
              <Stat>
                <StatLabel>Failed Login Attempts</StatLabel>
                <StatNumber fontSize="sm">{securitySettings.failedLoginAttempts}</StatNumber>
                <StatHelpText>Last 24 hours</StatHelpText>
              </Stat>
              <Stat>
                <StatLabel>Session Timeout</StatLabel>
                <StatNumber fontSize="sm">{securitySettings.sessionTimeout} min</StatNumber>
                <StatHelpText>Auto-logout</StatHelpText>
              </Stat>
            </SimpleGrid>
          </CardBody>
        </Card>

        {/* Two-Factor Authentication */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <HStack justify="space-between" mb={4}>
              <Box>
                <Text fontSize="lg" fontWeight="bold">Two-Factor Authentication</Text>
                <Text fontSize="sm" color="gray.600">
                  Add an extra layer of security to your account
                </Text>
              </Box>
              <Switch
                isChecked={securitySettings.twoFactorEnabled}
                onChange={handle2FAToggle}
                colorScheme="blue"
                size="lg"
              />
            </HStack>
            
            {securitySettings.twoFactorEnabled ? (
              <Alert status="success" borderRadius="md">
                <AlertIcon />
                <Box>
                  <AlertTitle>2FA Enabled</AlertTitle>
                  <AlertDescription>
                    Your account is protected with two-factor authentication.
                  </AlertDescription>
                </Box>
              </Alert>
            ) : (
              <Alert status="warning" borderRadius="md">
                <AlertIcon />
                <Box>
                  <AlertTitle>2FA Disabled</AlertTitle>
                  <AlertDescription>
                    Enable two-factor authentication for enhanced security.
                  </AlertDescription>
                </Box>
              </Alert>
            )}

            {securitySettings.twoFactorEnabled && (
              <VStack spacing={4} mt={4}>
                <Button
                  size="sm"
                  leftIcon={<DownloadIcon />}
                  onClick={handleGenerateBackupCodes}
                  isLoading={loading}
                >
                  Generate Backup Codes
                </Button>
                <Text fontSize="xs" color="gray.500">
                  Backup codes allow you to access your account if you lose your 2FA device.
                </Text>
              </VStack>
            )}
          </CardBody>
        </Card>

        {/* Role-Based Access Control */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <HStack justify="space-between" mb={4}>
              <Text fontSize="lg" fontWeight="bold">Role Management</Text>
              <Button size="sm" onClick={() => setShowRoleModal(true)}>
                Add Role
              </Button>
            </HStack>
            
            <Table variant="simple" size="sm">
              <Thead>
                <Tr>
                  <Th>Role</Th>
                  <Th>Description</Th>
                  <Th>Users</Th>
                  <Th>Permissions</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {userRoles.map((role) => (
                  <Tr key={role.id}>
                    <Td>
                      <HStack>
                        <Avatar size="sm" name={role.name} />
                        <Text fontWeight="medium">{role.name}</Text>
                      </HStack>
                    </Td>
                    <Td>{role.description}</Td>
                    <Td>{role.userCount}</Td>
                    <Td>
                      <HStack spacing={1}>
                        {role.permissions.slice(0, 3).map((perm) => (
                          <Badge key={perm} size="sm" colorScheme="blue">
                            {perm}
                          </Badge>
                        ))}
                        {role.permissions.length > 3 && (
                          <Badge size="sm" colorScheme="gray">
                            +{role.permissions.length - 3}
                          </Badge>
                        )}
                      </HStack>
                    </Td>
                    <Td>
                      <HStack spacing={1}>
                        <Tooltip label="Edit Role">
                          <IconButton size="xs" aria-label="Edit" icon={<FiEye />} />
                        </Tooltip>
                        <Tooltip label="Delete Role">
                          <IconButton size="xs" aria-label="Delete" icon={<CloseIcon />} />
                        </Tooltip>
                      </HStack>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </CardBody>
        </Card>

        {/* Audit Logs */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <HStack justify="space-between" mb={4}>
              <Text fontSize="lg" fontWeight="bold">Audit Logs</Text>
              <Button size="sm" leftIcon={<DownloadIcon />}>
                Export Logs
              </Button>
            </HStack>
            
            <Table variant="simple" size="sm">
              <Thead>
                <Tr>
                  <Th>Timestamp</Th>
                  <Th>User</Th>
                  <Th>Action</Th>
                  <Th>Resource</Th>
                  <Th>IP Address</Th>
                  <Th>Status</Th>
                </Tr>
              </Thead>
              <Tbody>
                {auditLogs.map((log) => (
                  <Tr key={log.id}>
                    <Td fontSize="xs">{new Date(log.timestamp).toLocaleString()}</Td>
                    <Td fontSize="xs">{log.user}</Td>
                    <Td fontSize="xs">{log.action}</Td>
                    <Td fontSize="xs">{log.resource}</Td>
                    <Td fontSize="xs">{log.ipAddress}</Td>
                    <Td>
                      <Badge colorScheme={getStatusColor(log.status)} size="sm">
                        {log.status}
                      </Badge>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </CardBody>
        </Card>

        {/* Security Settings */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Text fontSize="lg" fontWeight="bold" mb={4}>Security Settings</Text>
            
            <VStack spacing={4} align="stretch">
              <HStack justify="space-between">
                <Box>
                  <Text fontWeight="medium">Audit Logging</Text>
                  <Text fontSize="sm" color="gray.600">
                    Track all user activities for security monitoring
                  </Text>
                </Box>
                <Switch
                  isChecked={securitySettings.auditLogEnabled}
                  onChange={(e) => setSecuritySettings(prev => ({ ...prev, auditLogEnabled: e.target.checked }))}
                  colorScheme="blue"
                />
              </HStack>

              <Divider />

              <HStack justify="space-between">
                <Box>
                  <Text fontWeight="medium">Session Timeout</Text>
                  <Text fontSize="sm" color="gray.600">
                    Automatically log out inactive users
                  </Text>
                </Box>
                <Select
                  value={securitySettings.sessionTimeout}
                  onChange={(e) => setSecuritySettings(prev => ({ ...prev, sessionTimeout: Number(e.target.value) }))}
                  size="sm"
                  width="120px"
                >
                  <option value={15}>15 minutes</option>
                  <option value={30}>30 minutes</option>
                  <option value={60}>1 hour</option>
                  <option value={120}>2 hours</option>
                </Select>
              </HStack>

              <Divider />

              <HStack justify="space-between">
                <Box>
                  <Text fontWeight="medium">Account Lockout</Text>
                  <Text fontSize="sm" color="gray.600">
                    Lock account after failed login attempts
                  </Text>
                </Box>
                <Badge colorScheme={securitySettings.accountLocked ? 'red' : 'green'}>
                  {securitySettings.accountLocked ? 'Locked' : 'Active'}
                </Badge>
              </HStack>
            </VStack>
          </CardBody>
        </Card>
      </VStack>

      {/* 2FA Setup Modal */}
      <Modal isOpen={show2FAModal} onClose={() => setShow2FAModal(false)} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Setup Two-Factor Authentication</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={6}>
              <Alert status="info">
                <AlertIcon />
                <Box>
                  <AlertTitle>Setup Instructions</AlertTitle>
                  <AlertDescription>
                    1. Scan the QR code with your authenticator app<br/>
                    2. Enter the 6-digit code to verify setup
                  </AlertDescription>
                </Box>
              </Alert>

              <Box textAlign="center" p={4} border="1px" borderColor={borderColor} borderRadius="md">
                <MdQrCode boxSize={8} mb={2} />
                <Text fontSize="sm" color="gray.600">
                  QR Code will appear here
                </Text>
                <Text fontSize="xs" color="gray.500">
                  Use Google Authenticator, Authy, or similar app
                </Text>
              </Box>

              <FormControl>
                <FormLabel>Verification Code</FormLabel>
                <Input
                  placeholder="Enter 6-digit code"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  maxLength={6}
                />
              </FormControl>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => setShow2FAModal(false)}>
              Cancel
            </Button>
            <Button
              colorScheme="blue"
              onClick={handleVerify2FA}
              isLoading={loading}
              isDisabled={!verificationCode.trim()}
            >
              Verify & Enable
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Backup Codes Modal */}
      <Modal isOpen={showBackupCodesModal} onClose={() => setShowBackupCodesModal(false)} size="md">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Backup Codes</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Alert status="warning" mb={4}>
              <AlertIcon />
              <AlertTitle>Important</AlertTitle>
              <AlertDescription>
                Save these codes in a secure location. Each code can only be used once.
              </AlertDescription>
            </Alert>

            <Box
              p={4}
              bg="gray.50"
              borderRadius="md"
              fontFamily="mono"
              fontSize="sm"
              textAlign="center"
            >
              {backupCodes.map((code, index) => (
                <Text key={index} mb={2}>
                  {code}
                </Text>
              ))}
            </Box>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => setShowBackupCodesModal(false)}>
              Close
            </Button>
            <Button
              colorScheme="blue"
              onClick={() => {
                navigator.clipboard.writeText(backupCodes.join('\n'));
                toast({
                  title: 'Copied',
                  description: 'Backup codes copied to clipboard',
                  status: 'success',
                  duration: 3000,
                });
              }}
            >
              Copy Codes
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default SecuritySettings; 