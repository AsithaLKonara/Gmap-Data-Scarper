import React, { useState } from 'react';
import { Card, CardHeader, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

export type LeadStage = 'to_contact' | 'in_progress' | 'converted';

export interface KanbanLead {
  id: string;
  name: string;
  email?: string;
  company?: string;
  stage: LeadStage;
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
  onStageChange: (leadId: string, newStage: LeadStage) => void;
}

export const LeadKanban: React.FC<LeadKanbanProps> = ({ leads, onStageChange }) => {
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
                    <div className="font-medium">{lead.name}</div>
                    {lead.company && <div className="text-xs text-muted-foreground">{lead.company}</div>}
                    {lead.email && <div className="text-xs text-muted-foreground">{lead.email}</div>}
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