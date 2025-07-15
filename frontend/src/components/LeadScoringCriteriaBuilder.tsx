import React, { useState } from 'react';
import { Card, CardHeader, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';

export interface ScoringRule {
  id: string;
  field: string;
  label: string;
  points: number;
}

interface LeadScoringCriteriaBuilderProps {
  rules: ScoringRule[];
  onChange: (rules: ScoringRule[]) => void;
}

const defaultFields = [
  { field: 'email', label: 'Has Email' },
  { field: 'phone', label: 'Has Phone' },
  { field: 'website', label: 'Has Website' },
  { field: 'company', label: 'Has Company' },
  { field: 'enriched', label: 'Is Enriched' },
  { field: 'recent_contact', label: 'Contacted Recently' },
  { field: 'engagement_high', label: 'High Engagement' },
  { field: 'source_facebook', label: 'Source: Facebook' },
  { field: 'source_gmaps', label: 'Source: Google Maps' },
  { field: 'source_whatsapp', label: 'Source: WhatsApp' },
];

export const LeadScoringCriteriaBuilder: React.FC<LeadScoringCriteriaBuilderProps> = ({ rules, onChange }) => {
  const [newField, setNewField] = useState('');
  const [newPoints, setNewPoints] = useState(10);

  const addRule = () => {
    if (!newField) return;
    const fieldObj = defaultFields.find(f => f.field === newField);
    if (!fieldObj) return;
    onChange([
      ...rules,
      { id: Date.now().toString(), field: newField, label: fieldObj.label, points: newPoints }
    ]);
    setNewField('');
    setNewPoints(10);
  };

  const removeRule = (id: string) => {
    onChange(rules.filter(r => r.id !== id));
  };

  return (
    <Card className="mb-6">
      <CardHeader>
        <div className="flex items-center justify-between">
          <span className="font-semibold">Lead Scoring Criteria</span>
          <Badge variant="secondary">Customizable</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {rules.map(rule => (
            <div key={rule.id} className="flex items-center gap-2">
              <span className="flex-1">{rule.label}</span>
              <span className="text-xs text-muted-foreground">+{rule.points} pts</span>
              <Button variant="ghost" size="sm" onClick={() => removeRule(rule.id)}>Remove</Button>
            </div>
          ))}
        </div>
        <div className="flex items-center gap-2 mt-4">
          <select
            className="border rounded px-2 py-1 text-sm"
            value={newField}
            onChange={e => setNewField(e.target.value)}
          >
            <option value="">Select Field</option>
            {defaultFields.filter(f => !rules.some(r => r.field === f.field)).map(f => (
              <option key={f.field} value={f.field}>{f.label}</option>
            ))}
          </select>
          <Input
            type="number"
            min={1}
            max={100}
            value={newPoints}
            onChange={e => setNewPoints(Number(e.target.value))}
            className="w-20"
          />
          <Button size="sm" onClick={addRule}>Add Rule</Button>
        </div>
      </CardContent>
    </Card>
  );
}; 