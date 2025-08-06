import React, { useEffect, useState } from 'react';
import {
  Box, Heading, VStack, HStack, Button, Input, Table, Thead, Tr, Th, Tbody, Td, Select, useToast, Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalFooter, ModalCloseButton, Spinner, Badge, Text
} from '@chakra-ui/react';
import {
  getTeams, createTeam, inviteToTeam, listTeamMembers, removeTeamMember, changeTeamMemberRole, transferTeamOwnership, acceptTeamInvite, declineTeamInvite, getUser
} from '../api';
import { useTranslation } from 'react-i18next';

const TeamManagement: React.FC = () => {
  const { t } = useTranslation();
  const [teams, setTeams] = useState<any[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<any>(null);
  const [members, setMembers] = useState<any[]>([]);
  const [teamName, setTeamName] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('member');
  const [modalOpen, setModalOpen] = useState(false);
  const [transferUserId, setTransferUserId] = useState('');
  const toast = useToast();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [invites, setInvites] = useState<any[]>([]);
  const [myUserId, setMyUserId] = useState<number | null>(null);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    getUser().then(setUser);
    loadTeams();
  }, []);

  const loadTeams = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getTeams();
      setTeams(data);
      if (data.length > 0) {
        setSelectedTeam(data[0]);
        loadMembers(data[0].id);
      }
    } catch (e: any) {
      setError(e.message || t('teamManagement.error.failedToLoadTeams', 'Failed to load teams'));
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const loadMembers = async (teamId: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await listTeamMembers(teamId);
      setMembers(data);
    } catch (e: any) {
      setError(e.message || t('teamManagement.error.failedToLoadMembers', 'Failed to load members'));
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTeam = async () => {
    if (!teamName.trim()) return;
    setLoading(true);
    setError(null);
    try {
      await createTeam({ name: teamName });
      setTeamName('');
      loadTeams();
      toast({ title: t('teamManagement.success.teamCreated', 'Team created'), status: 'success' });
    } catch (e: any) {
      setError(e.message || t('teamManagement.error.failedToCreateTeam', 'Failed to create team'));
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async () => {
    if (!inviteEmail.trim()) return;
    setLoading(true);
    setError(null);
    try {
      await inviteToTeam(selectedTeam.id, { email: inviteEmail, role: inviteRole });
      setInviteEmail('');
      setInviteRole('member');
      loadMembers(selectedTeam.id);
      toast({ title: t('teamManagement.success.userInvited', 'User invited'), status: 'success' });
    } catch (e: any) {
      setError(e.message || t('teamManagement.error.failedToInviteUser', 'Failed to invite user'));
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (memberId: number) => {
    setLoading(true);
    setError(null);
    try {
      await removeTeamMember(selectedTeam.id, memberId);
      loadMembers(selectedTeam.id);
      toast({ title: t('teamManagement.info.memberRemoved', 'Member removed'), status: 'info' });
    } catch (e: any) {
      setError(e.message || t('teamManagement.error.failedToRemoveMember', 'Failed to remove member'));
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleChangeRole = async (memberId: number, role: string) => {
    setLoading(true);
    setError(null);
    try {
      await changeTeamMemberRole(selectedTeam.id, memberId, role);
      loadMembers(selectedTeam.id);
      toast({ title: t('teamManagement.success.roleUpdated', 'Role updated'), status: 'success' });
    } catch (e: any) {
      setError(e.message || t('teamManagement.error.failedToUpdateRole', 'Failed to update role'));
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleTransferOwnership = async () => {
    if (!transferUserId) return;
    setLoading(true);
    setError(null);
    try {
      await transferTeamOwnership(selectedTeam.id, Number(transferUserId));
      setModalOpen(false);
      loadTeams();
      toast({ title: t('teamManagement.success.ownershipTransferred', 'Ownership transferred'), status: 'success' });
    } catch (e: any) {
      setError(e.message || t('teamManagement.error.failedToTransferOwnership', 'Failed to transfer ownership'));
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptInvite = async (membershipId: number) => {
    setLoading(true);
    setError(null);
    try {
      await acceptTeamInvite(membershipId);
      loadTeams();
      toast({ title: t('teamManagement.success.inviteAccepted', 'Invite accepted'), status: 'success' });
    } catch (e: any) {
      setError(e.message || t('teamManagement.error.failedToAcceptInvite', 'Failed to accept invite'));
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleDeclineInvite = async (membershipId: number) => {
    setLoading(true);
    setError(null);
    try {
      await declineTeamInvite(membershipId);
      loadTeams();
      toast({ title: t('teamManagement.info.inviteDeclined', 'Invite declined'), status: 'info' });
    } catch (e: any) {
      setError(e.message || t('teamManagement.error.failedToDeclineInvite', 'Failed to decline invite'));
      toast({ title: t('error', 'Error'), description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  if (user && user.plan !== 'pro' && user.plan !== 'business') {
    return (
      <Box p={8}>
        <Heading size="lg" mb={6}>{t('teamManagement.heading', 'Team Management')}</Heading>
        <Text color="red.500" mb={4}>{t('teamManagement.proOnly', 'Team features are only available on Pro and Business plans.')}</Text>
        <Button colorScheme="blue" as="a" href="/upgrade">{t('teamManagement.upgradePlan', 'Upgrade Plan')}</Button>
      </Box>
    );
  }

  return (
    <Box p={8} data-tour="team-main">
      <Heading size="lg" mb={6} data-tour="team-title">{t('teamManagement.heading', 'Team Management')}</Heading>
      {loading && <Spinner data-tour="team-loading" />}
      {error && <Text color="red.500" data-tour="team-error">{error}</Text>}
      <VStack align="stretch" spacing={6} data-tour="team-content">
        <Box data-tour="team-create">
          <HStack>
            <Input placeholder={t('teamManagement.newTeamName', 'New team name')} value={teamName} onChange={e => setTeamName(e.target.value)} data-tour="team-name-input" />
            <Button colorScheme="blue" onClick={handleCreateTeam} isLoading={loading} data-tour="team-create-btn">{t('teamManagement.createTeam', 'Create Team')}</Button>
          </HStack>
        </Box>
        <Box data-tour="team-select">
          <Select value={selectedTeam?.id || ''} onChange={e => {
            const t = teams.find(t => t.id === Number(e.target.value));
            setSelectedTeam(t);
            loadMembers(t.id);
          }} placeholder={t('teamManagement.selectTeam', 'Select a team')} data-tour="team-select-dropdown">
            {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
          </Select>
        </Box>
        {invites.length > 0 && (
          <Box>
            <Heading size="sm" mb={2}>{t('teamManagement.pendingInvites', 'Pending Invites')}</Heading>
            <Table size="sm">
              <Thead>
                <Tr>
                  <Th>{t('teamManagement.team', 'Team')}</Th>
                  <Th>{t('teamManagement.role', 'Role')}</Th>
                  <Th>{t('teamManagement.status', 'Status')}</Th>
                  <Th>{t('teamManagement.invitedAt', 'Invited At')}</Th>
                  <Th>{t('teamManagement.actions', 'Actions')}</Th>
                </Tr>
              </Thead>
              <Tbody>
                {invites.map(invite => (
                  <Tr key={invite.id}>
                    <Td>{invite.team_name}</Td>
                    <Td><Badge>{invite.role}</Badge></Td>
                    <Td>{invite.status}</Td>
                    <Td>{new Date(invite.invited_at).toLocaleString()}</Td>
                    <Td>
                      {invite.status === 'invited' && (
                        <>
                          <Button size="xs" colorScheme="green" onClick={() => handleAcceptInvite(invite.id)}>{t('teamManagement.acceptInvite', 'Accept')}</Button>
                          <Button size="xs" colorScheme="red" onClick={() => handleDeclineInvite(invite.id)}>{t('teamManagement.declineInvite', 'Decline')}</Button>
                        </>
                      )}
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
        )}
        {selectedTeam && (
          <Box>
            <Heading size="md" mb={4}>{t('teamManagement.members', 'Members')}</Heading>
            {members.length === 0 ? (
              <Text color="gray.500">{t('teamManagement.noMembers', 'No members yet.')}</Text>
            ) : (
              <Table size="sm">
                <Thead>
                  <Tr>
                    <Th>{t('teamManagement.userId', 'User ID')}</Th>
                    <Th>{t('teamManagement.email', 'Email')}</Th>
                    <Th>{t('teamManagement.role', 'Role')}</Th>
                    <Th>{t('teamManagement.status', 'Status')}</Th>
                    <Th>{t('teamManagement.invitedAt', 'Invited At')}</Th>
                    <Th>{t('teamManagement.actions', 'Actions')}</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {members.map(m => (
                    <Tr key={m.id} bg={m.user_id === selectedTeam.owner_id ? 'yellow.50' : undefined}>
                      <Td>{m.user_id}{m.user_id === selectedTeam.owner_id && <Badge ml={2} colorScheme="yellow">{t('teamManagement.owner', 'Owner')}</Badge>}</Td>
                      <Td>
                        <Text color="blue.500" cursor="pointer">
                          {m.email}
                        </Text>
                      </Td>
                      <Td><Badge colorScheme={m.role === 'admin' ? 'blue' : m.role === 'member' ? 'green' : 'gray'}>{m.role}</Badge></Td>
                      <Td>{m.status}</Td>
                      <Td>{new Date(m.invited_at).toLocaleString()}</Td>
                      <Td>
                        <Button size="xs" colorScheme="red" onClick={() => handleRemove(m.user_id)} isDisabled={m.user_id === selectedTeam.owner_id}>{t('teamManagement.removeMember', 'Remove')}</Button>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            )}
            <HStack mt={4}>
              <Input placeholder={t('teamManagement.inviteEmail', 'Invite email')} value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} />
              <Select value={inviteRole} onChange={e => setInviteRole(e.target.value)} w="120px">
                <option value="member">{t('teamManagement.roleMember', 'Member')}</option>
                <option value="admin">{t('teamManagement.roleAdmin', 'Admin')}</option>
                <option value="viewer">{t('teamManagement.roleViewer', 'Viewer')}</option>
              </Select>
              <Button colorScheme="blue" onClick={handleInvite} isLoading={loading}>{t('teamManagement.inviteUser', 'Invite')}</Button>
            </HStack>
            <Button mt={4} colorScheme="yellow" onClick={() => setModalOpen(true)}>{t('teamManagement.transferOwnership', 'Transfer Ownership')}</Button>
            <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)}>
              <ModalOverlay />
              <ModalContent>
                <ModalHeader>{t('teamManagement.transferOwnership', 'Transfer Ownership')}</ModalHeader>
                <ModalCloseButton />
                <ModalBody>
                  <Select placeholder={t('teamManagement.selectNewOwner', 'Select new owner')} value={transferUserId} onChange={e => setTransferUserId(e.target.value)}>
                    {members.filter(m => m.user_id !== selectedTeam.owner_id).map(m => (
                      <option key={m.user_id} value={m.user_id}>{m.user_id}</option>
                    ))}
                  </Select>
                </ModalBody>
                <ModalFooter>
                  <Button variant="ghost" mr={3} onClick={() => setModalOpen(false)}>{t('teamManagement.cancel', 'Cancel')}</Button>
                  <Button colorScheme="yellow" onClick={handleTransferOwnership} isLoading={loading}>{t('teamManagement.transfer', 'Transfer')}</Button>
                </ModalFooter>
              </ModalContent>
            </Modal>
          </Box>
        )}
      </VStack>
    </Box>
  );
};

export default TeamManagement; 