/** API functions for team management. */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Team {
  team_id: string;
  name: string;
  description?: string;
  owner_id: string;
  plan?: string;
  member_count: number;
  created_at: string;
}

export interface TeamMember {
  user_id: string;
  email: string;
  name?: string;
  role: 'admin' | 'member' | 'viewer';
  joined_at: string;
}

export interface SharedList {
  list_id: string;
  team_id: string;
  name: string;
  description?: string;
  lead_count: number;
}

export interface TeamActivity {
  activity_id: string;
  activity_type: string;
  title: string;
  description?: string;
  created_at: string;
}

async function getAuthHeaders(): Promise<HeadersInit> {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
}

export async function createTeam(name: string, description?: string, plan?: string): Promise<Team> {
  const response = await fetch(`${API_BASE_URL}/api/teams/`, {
    method: 'POST',
    headers: await getAuthHeaders(),
    body: JSON.stringify({ name, description, plan }),
  });
  if (!response.ok) throw new Error('Failed to create team');
  return response.json();
}

export async function getTeams(): Promise<Team[]> {
  const response = await fetch(`${API_BASE_URL}/api/teams/`, {
    headers: await getAuthHeaders(),
  });
  if (!response.ok) throw new Error('Failed to get teams');
  return response.json();
}

export async function getTeam(teamId: string): Promise<Team> {
  const response = await fetch(`${API_BASE_URL}/api/teams/${teamId}`, {
    headers: await getAuthHeaders(),
  });
  if (!response.ok) throw new Error('Failed to get team');
  return response.json();
}

export async function addTeamMember(teamId: string, userId: string, role: 'admin' | 'member' | 'viewer' = 'member'): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/teams/${teamId}/members`, {
    method: 'POST',
    headers: await getAuthHeaders(),
    body: JSON.stringify({ user_id: userId, role }),
  });
  if (!response.ok) throw new Error('Failed to add member');
}

export async function getTeamMembers(teamId: string): Promise<TeamMember[]> {
  const response = await fetch(`${API_BASE_URL}/api/teams/${teamId}/members`, {
    headers: await getAuthHeaders(),
  });
  if (!response.ok) throw new Error('Failed to get members');
  return response.json();
}

export async function getTeamActivities(teamId: string, limit: number = 50): Promise<TeamActivity[]> {
  const response = await fetch(`${API_BASE_URL}/api/teams/${teamId}/activities?limit=${limit}`, {
    headers: await getAuthHeaders(),
  });
  if (!response.ok) throw new Error('Failed to get activities');
  return response.json();
}

