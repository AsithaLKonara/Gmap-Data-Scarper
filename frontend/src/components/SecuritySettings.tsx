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
    <div>
      <div className="space-y-6">
        {/* Security Overview */}
        <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <div className="flex items-center justify-between mb-4">
            <span className="text-lg font-bold">Security Overview</span>
            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${securityScore >= 80 ? 'bg-green-100 text-green-700' : securityScore >= 60 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>
              Score: {securityScore}/100
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
            <div className={`${securityScore >= 80 ? 'bg-green-600' : securityScore >= 60 ? 'bg-yellow-500' : 'bg-red-600'} h-2.5 rounded-full transition-all`} style={{ width: `${securityScore}%` }} />
          </div>
            
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
          </div>

        {/* Two-Factor Authentication */}
        <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <div className="flex items-center justify-between mb-4">
            <div>
              <span className="text-lg font-bold block">Two-Factor Authentication</span>
              <span className="text-sm text-gray-600 block">Add an extra layer of security to your account</span>
            </div>
            <input
              type="checkbox"
              checked={securitySettings.twoFactorEnabled}
              onChange={handle2FAToggle}
              className="w-6 h-6 rounded border-gray-300 text-primary focus:ring-primary"
            />
          </div>
          {securitySettings.twoFactorEnabled ? (
            <div className="flex items-start p-4 bg-green-50 border border-green-200 rounded-md mb-4">
              <span className="text-green-500 mr-2">✔️</span>
              <div>
                <span className="font-semibold block">2FA Enabled</span>
                <span className="text-sm text-gray-700 dark:text-gray-300 block">Your account is protected with two-factor authentication.</span>
              </div>
            </div>
          ) : (
            <div className="flex items-start p-4 bg-yellow-50 border border-yellow-200 rounded-md mb-4">
              <span className="text-yellow-500 mr-2">⚠️</span>
              <div>
                <span className="font-semibold block">2FA Disabled</span>
                <span className="text-sm text-gray-700 dark:text-gray-300 block">Enable two-factor authentication for enhanced security.</span>
              </div>
            </div>
          )}
          {securitySettings.twoFactorEnabled && (
            <div className="flex flex-col space-y-2 mt-4">
              <button
                className="inline-flex items-center px-3 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-sm"
                onClick={handleGenerateBackupCodes}
                disabled={loading}
              >
                <span className="mr-2">⬇️</span>Generate Backup Codes
              </button>
              <span className="text-xs text-gray-500">Backup codes allow you to access your account if you lose your 2FA device.</span>
            </div>
          )}
        </div>
        {/* 2FA Setup Modal */}
        {show2FAModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
            <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg w-full max-w-md mx-4 animate-fade-in">
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <span className="text-lg font-bold">Enable Two-Factor Authentication</span>
                <button onClick={() => setShow2FAModal(false)} className="text-gray-400 hover:text-gray-600">&times;</button>
              </div>
              <div className="px-6 py-4 space-y-4">
                <span className="block text-sm text-gray-700">Scan the QR code below with your authenticator app:</span>
                <div className="flex items-center justify-center">
                  {/* QR code image or SVG here */}
                  <span className="bg-gray-200 w-32 h-32 flex items-center justify-center rounded">QR</span>
                </div>
                <input
                  type="text"
                  className="w-full rounded-md border border-gray-300 p-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary"
                  placeholder="Enter verification code"
                  value={verificationCode}
                  onChange={e => setVerificationCode(e.target.value)}
                />
                <button
                  className="w-full inline-flex items-center justify-center px-4 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-sm"
                  onClick={handleVerify2FA}
                  disabled={loading}
                >
                  Verify & Enable
                </button>
              </div>
            </div>
          </div>
        )}
        {/* Backup Codes Modal */}
        {showBackupCodesModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
            <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg w-full max-w-md mx-4 animate-fade-in">
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <span className="text-lg font-bold">Your Backup Codes</span>
                <button onClick={() => setShowBackupCodesModal(false)} className="text-gray-400 hover:text-gray-600">&times;</button>
              </div>
              <div className="px-6 py-4 space-y-2">
                <ul className="grid grid-cols-2 gap-2">
                  {backupCodes.map(code => (
                    <li key={code} className="bg-gray-100 rounded px-3 py-2 text-center font-mono text-sm">{code}</li>
                  ))}
                </ul>
                <span className="block text-xs text-gray-500 mt-2">Store these codes in a safe place. Each code can be used once.</span>
              </div>
            </div>
          </div>
        )}

        {/* Role-Based Access Control */}
        <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <div className="flex items-center justify-between mb-4">
            <span className="text-lg font-bold">Role Management</span>
            <button
              className="inline-flex items-center px-3 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-sm"
              onClick={() => setShowRoleModal(true)}
            >
              Add Role
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm border-separate border-spacing-y-2">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-2 py-1 font-medium text-gray-700 text-left">Role</th>
                  <th className="px-2 py-1 font-medium text-gray-700 text-left">Description</th>
                  <th className="px-2 py-1 font-medium text-gray-700 text-left">Users</th>
                  <th className="px-2 py-1 font-medium text-gray-700 text-left">Permissions</th>
                  <th className="px-2 py-1 font-medium text-gray-700 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                {userRoles.map((role) => (
                  <tr key={role.id} className="even:bg-gray-50">
                    <td className="px-2 py-1">
                      <div className="flex items-center space-x-2">
                        <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-gray-200 text-gray-700 font-bold">{role.name[0]}</span>
                        <span className="font-medium">{role.name}</span>
                      </div>
                    </td>
                    <td className="px-2 py-1">{role.description}</td>
                    <td className="px-2 py-1">{role.userCount}</td>
                    <td className="px-2 py-1">
                      <div className="flex flex-wrap gap-1">
                        {role.permissions.slice(0, 3).map((perm) => (
                          <span key={perm} className="inline-flex items-center px-2 py-0.5 rounded bg-blue-100 text-blue-700 text-xs font-semibold">{perm}</span>
                        ))}
                        {role.permissions.length > 3 && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded bg-gray-100 text-gray-700 text-xs font-semibold">+{role.permissions.length - 3}</span>
                        )}
                      </div>
                    </td>
                    <td className="px-2 py-1">
                      <div className="flex items-center space-x-1">
                        <button aria-label="Edit" className="p-1 rounded hover:bg-gray-200" title="Edit Role">
                          <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path d="M15.232 5.232l3.536 3.536M9 13l6-6 3 3-6 6H9v-3z" /></svg>
                        </button>
                        <button aria-label="Delete" className="p-1 rounded hover:bg-gray-200" title="Delete Role">
                          <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path d="M3 6h18M9 6v12a2 2 0 002 2h2a2 2 0 002-2V6" /></svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        {/* Audit Logs */}
        <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <div className="flex items-center justify-between mb-4">
            <span className="text-lg font-bold">Audit Logs</span>
            <button
              className="inline-flex items-center px-3 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-sm"
            >
              <span className="mr-2">⬇️</span>Export Logs
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm border-separate border-spacing-y-2">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-2 py-1 font-medium text-gray-700 text-left">Timestamp</th>
                  <th className="px-2 py-1 font-medium text-gray-700 text-left">User</th>
                  <th className="px-2 py-1 font-medium text-gray-700 text-left">Action</th>
                  <th className="px-2 py-1 font-medium text-gray-700 text-left">Resource</th>
                  <th className="px-2 py-1 font-medium text-gray-700 text-left">IP Address</th>
                  <th className="px-2 py-1 font-medium text-gray-700 text-left">Status</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map((log) => (
                  <tr key={log.id} className="even:bg-gray-50">
                    <td className="px-2 py-1 text-xs">{new Date(log.timestamp).toLocaleString()}</td>
                    <td className="px-2 py-1 text-xs">{log.user}</td>
                    <td className="px-2 py-1 text-xs">{log.action}</td>
                    <td className="px-2 py-1 text-xs">{log.resource}</td>
                    <td className="px-2 py-1 text-xs">{log.ipAddress}</td>
                    <td className="px-2 py-1">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${getStatusColor(log.status) === 'green' ? 'bg-green-100 text-green-700' : getStatusColor(log.status) === 'red' ? 'bg-red-100 text-red-700' : getStatusColor(log.status) === 'yellow' ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-700'}`}>{log.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        {/* Security Settings */}
        <div className="rounded-lg border bg-white dark:bg-gray-900 p-6 shadow">
          <span className="text-lg font-bold mb-4 block">Security Settings</span>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-medium block">Audit Logging</span>
                <span className="text-sm text-gray-600 block">Track all user activities for security monitoring</span>
              </div>
              <input
                type="checkbox"
                checked={securitySettings.auditLogEnabled}
                onChange={e => setSecuritySettings(prev => ({ ...prev, auditLogEnabled: e.target.checked }))}
                className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary"
              />
            </div>
            <hr />
            <div className="flex items-center justify-between">
              <div>
                <span className="font-medium block">Session Timeout</span>
                <span className="text-sm text-gray-600 block">Automatically log out inactive users</span>
              </div>
              <select
                value={securitySettings.sessionTimeout}
                onChange={e => setSecuritySettings(prev => ({ ...prev, sessionTimeout: Number(e.target.value) }))}
                className="rounded-md border border-gray-300 p-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary w-32"
              >
                <option value={15}>15 minutes</option>
                <option value={30}>30 minutes</option>
                <option value={60}>1 hour</option>
                <option value={120}>2 hours</option>
              </select>
            </div>
            <hr />
            <div className="flex items-center justify-between">
              <div>
                <span className="font-medium block">Account Lockout</span>
                <span className="text-sm text-gray-600 block">Lock account after failed login attempts</span>
              </div>
              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${securitySettings.accountLocked ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>{securitySettings.accountLocked ? 'Locked' : 'Active'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecuritySettings; 