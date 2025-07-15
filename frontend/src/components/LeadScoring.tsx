import React, { useState } from 'react';
import { LeadScoringCriteriaBuilder, ScoringRule } from './LeadScoringCriteriaBuilder';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Tooltip } from './ui/tooltip';

interface Lead {
  id: number;
  name: string;
  email: string;
  phone?: string;
  company?: string;
  website?: string;
  source: string;
  status: string;
  score: number;
  enriched: boolean;
  last_contacted?: string;
  engagement_level: 'high' | 'medium' | 'low';
  conversion_probability: number;
  tags: string[];
  notes?: string;
}

interface LeadScoringProps {
  leads: Lead[];
  onLeadUpdate: (leadId: number, updates: Partial<Lead>) => void;
}

const scoreBadge = (score: number) => {
  if (score >= 80) return <Badge className="bg-green-100 text-green-700">Hot</Badge>;
  if (score >= 60) return <Badge className="bg-blue-100 text-blue-700">Warm</Badge>;
  if (score >= 40) return <Badge className="bg-yellow-100 text-yellow-800">Cold</Badge>;
  return <Badge className="bg-gray-100 text-gray-700">Poor</Badge>;
};

const LeadScoring: React.FC<LeadScoringProps> = ({ leads, onLeadUpdate }) => {
  const [filter, setFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [scoringRules, setScoringRules] = useState<ScoringRule[]>([
    { id: 'email', field: 'email', label: 'Has Email', points: 15 },
    { id: 'phone', field: 'phone', label: 'Has Phone', points: 10 },
    { id: 'website', field: 'website', label: 'Has Website', points: 5 },
    { id: 'company', field: 'company', label: 'Has Company', points: 10 },
    { id: 'enriched', field: 'enriched', label: 'Is Enriched', points: 15 },
  ]);

  // Calculate lead score based on user-defined rules
  const calculateLeadScore = (lead: Lead): number => {
    let score = 0;
    scoringRules.forEach(rule => {
      if (rule.field === 'email' && lead.email) score += rule.points;
      if (rule.field === 'phone' && lead.phone) score += rule.points;
      if (rule.field === 'website' && lead.website) score += rule.points;
      if (rule.field === 'company' && lead.company) score += rule.points;
      if (rule.field === 'enriched' && lead.enriched) score += rule.points;
      if (rule.field === 'recent_contact' && lead.last_contacted) {
        const daysSince = Math.floor((Date.now() - new Date(lead.last_contacted).getTime()) / (1000 * 60 * 60 * 24));
        if (daysSince <= 7) score += rule.points;
      }
      if (rule.field === 'engagement_high' && lead.engagement_level === 'high') score += rule.points;
      if (rule.field === 'source_facebook' && lead.source === 'facebook') score += rule.points;
      if (rule.field === 'source_gmaps' && lead.source === 'google_maps') score += rule.points;
      if (rule.field === 'source_whatsapp' && lead.source === 'whatsapp') score += rule.points;
    });
    return Math.min(score, 100);
  };

  // Filter leads by score
  const filteredLeads = leads.filter(lead => {
    const score = calculateLeadScore(lead);
    if (filter === 'high') return score >= 80;
    if (filter === 'medium') return score >= 60 && score < 80;
    if (filter === 'low') return score < 60;
    return true;
  });

  // Calculate statistics
  const totalLeads = leads.length;
  const highScoreLeads = leads.filter(lead => calculateLeadScore(lead) >= 80).length;
  const mediumScoreLeads = leads.filter(lead => {
    const score = calculateLeadScore(lead);
    return score >= 60 && score < 80;
  }).length;
  const lowScoreLeads = leads.filter(lead => calculateLeadScore(lead) < 60).length;
  const averageScore = leads.length > 0 
    ? leads.reduce((sum, lead) => sum + calculateLeadScore(lead), 0) / leads.length 
    : 0;

  return (
    <div className="space-y-8">
      <LeadScoringCriteriaBuilder rules={scoringRules} onChange={setScoringRules} />
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="p-4">
          <div className="font-semibold text-sm text-muted-foreground">Total Leads</div>
          <div className="text-2xl font-bold">{totalLeads}</div>
          <div className="text-xs text-muted-foreground">All leads in your CRM</div>
        </Card>
        <Card className="p-4">
          <div className="font-semibold text-sm text-muted-foreground">Hot Leads</div>
          <div className="text-2xl font-bold text-green-600">{highScoreLeads}</div>
          <div className="text-xs text-muted-foreground">Score ≥ 80</div>
        </Card>
        <Card className="p-4">
          <div className="font-semibold text-sm text-muted-foreground">Warm Leads</div>
          <div className="text-2xl font-bold text-blue-600">{mediumScoreLeads}</div>
          <div className="text-xs text-muted-foreground">Score 60-79</div>
        </Card>
        <Card className="p-4">
          <div className="font-semibold text-sm text-muted-foreground">Average Score</div>
          <div className="text-2xl font-bold">{averageScore.toFixed(0)}</div>
          <div className="text-xs text-muted-foreground">Overall lead quality</div>
        </Card>
      </div>
      {/* Filter Controls */}
      <div className="flex gap-2 mb-4 items-center">
        <span className="text-sm font-medium">Filter by Score:</span>
        <Button size="sm" variant={filter === 'all' ? 'default' : 'outline'} onClick={() => setFilter('all')}>All ({totalLeads})</Button>
        <Button size="sm" variant={filter === 'high' ? 'default' : 'outline'} className="text-green-700" onClick={() => setFilter('high')}>Hot ({highScoreLeads})</Button>
        <Button size="sm" variant={filter === 'medium' ? 'default' : 'outline'} className="text-blue-700" onClick={() => setFilter('medium')}>Warm ({mediumScoreLeads})</Button>
        <Button size="sm" variant={filter === 'low' ? 'default' : 'outline'} className="text-yellow-800" onClick={() => setFilter('low')}>Cold ({lowScoreLeads})</Button>
      </div>
      {/* Leads Table */}
      <Card className="p-0 overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="bg-muted">
              <th className="p-3 text-left font-semibold">Lead</th>
              <th className="p-3 text-left font-semibold">Source</th>
              <th className="p-3 text-left font-semibold">Score
                <Tooltip content="Lead score is calculated based on your criteria.">
                  <span className="ml-1 text-xs text-muted-foreground cursor-help">?</span>
                </Tooltip>
              </th>
              <th className="p-3 text-left font-semibold">Status</th>
              <th className="p-3 text-left font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredLeads.map(lead => {
              const score = calculateLeadScore(lead);
              return (
                <tr key={lead.id} className="border-b last:border-0">
                  <td className="p-3">
                    <div className="font-medium">{lead.name}</div>
                    <div className="text-xs text-muted-foreground">{lead.email}</div>
                  </td>
                  <td className="p-3">{lead.source}</td>
                  <td className="p-3">{scoreBadge(score)}</td>
                  <td className="p-3">{lead.status}</td>
                  <td className="p-3">
                    <Button size="sm" variant="outline" onClick={() => onLeadUpdate(lead.id, { enriched: true })}>Enrich</Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Card>
    </div>
  );
};

export default LeadScoring;