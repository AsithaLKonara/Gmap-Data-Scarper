import React from 'react';
import { Button } from './ui/button';
import { Card } from './ui/card';

export interface Lead {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  owners?: string[];
}

export interface DuplicateGroup {
  leads: Lead[];
  reason: string; // e.g. 'Same email', 'Similar name'
}

interface DeduplicationPanelProps {
  duplicates: DuplicateGroup[];
  onMerge: (leadIds: string[]) => void;
  onIgnore: (leadIds: string[]) => void;
  onAutoMerge: () => void;
}

export const DeduplicationPanel: React.FC<DeduplicationPanelProps> = ({ duplicates, onMerge, onIgnore, onAutoMerge }) => {
  if (!duplicates.length) return null;
  return (
    <Card className="mb-8 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold">Potential Duplicate Leads</h2>
        <Button variant="secondary" onClick={onAutoMerge}>Auto-merge exact matches</Button>
      </div>
      <div className="space-y-6">
        {duplicates.map((group, idx) => (
          <div key={idx} className="border border-border rounded-lg p-4 bg-muted">
            <div className="mb-2 text-sm text-muted-foreground">Reason: {group.reason}</div>
            <div className="flex flex-col md:flex-row gap-4">
              {group.leads.map(lead => (
                <div key={lead.id} className="flex-1 bg-card border border-border rounded p-3">
                  <div className="font-semibold text-primary mb-1">{lead.name}</div>
                  {lead.email && <div className="text-xs text-muted-foreground">Email: {lead.email}</div>}
                  {lead.phone && <div className="text-xs text-muted-foreground">Phone: {lead.phone}</div>}
                  {lead.company && <div className="text-xs text-muted-foreground">Company: {lead.company}</div>}
                </div>
              ))}
            </div>
            <div className="flex gap-2 mt-3">
              <Button size="sm" onClick={() => onMerge(group.leads.map(l => l.id))}>Merge</Button>
              <Button size="sm" variant="ghost" onClick={() => onIgnore(group.leads.map(l => l.id))}>Ignore</Button>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}; 