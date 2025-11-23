import { useState, useEffect } from 'react';
import GlassCard from '../ui/GlassCard';
import GlassButton from '../ui/GlassButton';
import { createTeam, getTeams, getTeamMembers, getTeamActivities, Team, TeamMember, TeamActivity } from '../../utils/teamsApi';

export default function TeamWorkspace() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [activities, setActivities] = useState<TeamActivity[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTeamName, setNewTeamName] = useState('');

  useEffect(() => {
    loadTeams();
  }, []);

  useEffect(() => {
    if (selectedTeam) {
      loadTeamDetails(selectedTeam.team_id);
    }
  }, [selectedTeam]);

  const loadTeams = async () => {
    try {
      const data = await getTeams();
      setTeams(data);
      if (data.length > 0 && !selectedTeam) {
        setSelectedTeam(data[0]);
      }
    } catch (err) {
      console.error('Failed to load teams:', err);
    }
  };

  const loadTeamDetails = async (teamId: string) => {
    try {
      const [membersData, activitiesData] = await Promise.all([
        getTeamMembers(teamId),
        getTeamActivities(teamId)
      ]);
      setMembers(membersData);
      setActivities(activitiesData);
    } catch (err) {
      console.error('Failed to load team details:', err);
    }
  };

  const handleCreateTeam = async () => {
    if (!newTeamName.trim()) return;
    
    setIsLoading(true);
    try {
      const newTeam = await createTeam(newTeamName);
      setTeams([...teams, newTeam]);
      setSelectedTeam(newTeam);
      setShowCreateModal(false);
      setNewTeamName('');
    } catch (err) {
      console.error('Failed to create team:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gradient-primary">Team Workspace</h1>
        <GlassButton
          onClick={() => setShowCreateModal(true)}
          variant="primary"
          gradient
        >
          + Create Team
        </GlassButton>
      </div>

      {showCreateModal && (
        <GlassCard>
          <h2 className="text-xl font-semibold mb-4">Create New Team</h2>
          <div className="space-y-3">
            <input
              type="text"
              value={newTeamName}
              onChange={(e) => setNewTeamName(e.target.value)}
              placeholder="Team name"
              className="input-glass w-full"
            />
            <div className="flex gap-2">
              <GlassButton
                onClick={handleCreateTeam}
                disabled={isLoading}
                variant="primary"
                gradient
              >
                {isLoading ? 'Creating...' : 'Create'}
              </GlassButton>
              <GlassButton
                onClick={() => {
                  setShowCreateModal(false);
                  setNewTeamName('');
                }}
                variant="secondary"
              >
                Cancel
              </GlassButton>
            </div>
          </div>
        </GlassCard>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Teams List */}
        <GlassCard>
          <h2 className="text-xl font-semibold mb-4">Your Teams</h2>
          <div className="space-y-2">
            {teams.map((team) => (
              <div
                key={team.team_id}
                onClick={() => setSelectedTeam(team)}
                className={`p-3 rounded-lg cursor-pointer transition-all ${
                  selectedTeam?.team_id === team.team_id
                    ? 'glass-subtle border-2 border-blue-500'
                    : 'hover:glass-subtle'
                }`}
              >
                <div className="font-semibold">{team.name}</div>
                <div className="text-sm text-gray-500">
                  {team.member_count} members
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Team Details */}
        {selectedTeam && (
          <>
            <GlassCard>
              <h2 className="text-xl font-semibold mb-4">Team Members</h2>
              <div className="space-y-2">
                {members.map((member) => (
                  <div key={member.user_id} className="p-2 glass-subtle rounded">
                    <div className="font-medium">{member.name || member.email}</div>
                    <div className="text-xs text-gray-500 capitalize">{member.role}</div>
                  </div>
                ))}
              </div>
            </GlassCard>

            <GlassCard>
              <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {activities.map((activity) => (
                  <div key={activity.activity_id} className="p-2 text-sm">
                    <div className="font-medium">{activity.title}</div>
                    <div className="text-xs text-gray-500">
                      {new Date(activity.created_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </GlassCard>
          </>
        )}
      </div>
    </div>
  );
}

