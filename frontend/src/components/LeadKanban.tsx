import React, { useState } from 'react';
import { Card, CardHeader, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Avatar } from './ui/avatar';
import { Select } from './ui/select';

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
  to_contact: 'bg-yellow-100',
  in_progress: 'bg-blue-100',
  converted: 'bg-green-100',
};

interface LeadKanbanProps {
  leads: KanbanLead[];
  users: User[];
  onStageChange: (leadId: string, newStage: LeadStage) => void;
  onOwnerChange: (leadId: string, owners: string[]) => void;
}

export const LeadKanban: React.FC<LeadKanbanProps> = ({ leads, users, onStageChange, onOwnerChange }) => {
  const [draggedId, setDraggedId] = useState<string | null>(null);

  const handleDragStart = (id: string) => setDraggedId(id);
  const handleDragEnd = () => setDraggedId(null);
  const handleDrop = (stage: LeadStage) => {
    if (draggedId) {
      onStageChange(draggedId, stage);
      setDraggedId(null);
    }
  };

  return (
    <div className="flex gap-4 w-full overflow-x-auto">
      {(['to_contact', 'in_progress', 'converted'] as LeadStage[]).map(stage => (
        <div
          key={stage}
          className={`flex-1 min-w-[250px] ${stageColors[stage]} rounded-lg p-2`}
          onDragOver={e => e.preventDefault()}
          onDrop={() => handleDrop(stage)}
        >
          <Card>
            <CardHeader className="flex items-center justify-between">
              <span className="font-semibold">{stageLabels[stage]}</span>
              <Badge>{leads.filter(l => l.stage === stage).length}</Badge>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {leads.filter(l => l.stage === stage).map(lead => (
                  <div
                    key={lead.id}
                    className={`bg-white rounded shadow p-2 cursor-move border ${draggedId === lead.id ? 'opacity-50' : ''}`}
                    draggable
                    onDragStart={() => handleDragStart(lead.id)}
                    onDragEnd={handleDragEnd}
                  >
                    <div className="font-medium flex items-center gap-2">
                      {lead.name}
                      <div className="flex -space-x-2">
                        {lead.owners.map(ownerId => {
                          const user = users.find(u => u.id === ownerId);
                          return user ? (
                            <Avatar key={user.id} src={user.avatarUrl} alt={user.name} className="w-6 h-6 border-2 border-white" />
                          ) : null;
                        })}
                      </div>
                    </div>
                    {lead.company && <div className="text-xs text-muted-foreground">{lead.company}</div>}
                    {lead.email && <div className="text-xs text-muted-foreground">{lead.email}</div>}
                    {/* Owner assignment dropdown */}
                    <div className="mt-2">
                      <Select
                        multiple
                        value={lead.owners}
                        onChange={e => {
                          const selected = Array.from(e.target.selectedOptions).map(opt => opt.value);
                          onOwnerChange(lead.id, selected);
                        }}
                        className="w-full text-xs"
                        aria-label="Assign owners"
                      >
                        {users.map(user => (
                          <option key={user.id} value={user.id}>{user.name}</option>
                        ))}
                      </Select>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      ))}
    </div>
  );
}; 