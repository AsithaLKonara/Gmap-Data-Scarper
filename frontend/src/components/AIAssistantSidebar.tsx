import React, { useState } from 'react';
import { Card, CardHeader, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Sparkles } from 'lucide-react';
import { Select } from './ui/input';

const examplePrompts = [
  'What are my top 5 leads this week?',
  'Summarize contact history for John Doe.',
  'Generate a follow-up email.',
  'Show leads likely to convert soon.',
  'Who should I contact next?'
];

const smartRecommendations = [
  { name: 'Alice Smith', reason: 'High engagement, not contacted in 7 days' },
  { name: 'Bob Lee', reason: 'Recently opened your email' },
  { name: 'Carol Jones', reason: 'Scored as Hot Lead' },
];

const predictiveAnalytics = [
  { name: 'Alice Smith', churn: 'Low', conversion: 'High' },
  { name: 'Bob Lee', churn: 'Medium', conversion: 'Medium' },
  { name: 'Carol Jones', churn: 'High', conversion: 'Low' },
];

const leadsList = [
  { id: '1', name: 'Alice Smith' },
  { id: '2', name: 'Bob Lee' },
  { id: '3', name: 'Carol Jones' },
];

export const AIAssistantSidebar: React.FC = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<{ role: 'user' | 'ai'; text: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedLeadId, setSelectedLeadId] = useState('');
  const [summary, setSummary] = useState('');
  const [summarizing, setSummarizing] = useState(false);

  const sendPrompt = async (prompt: string) => {
    setMessages(msgs => [...msgs, { role: 'user', text: prompt }]);
    setLoading(true);
    // TODO: Integrate with backend AI API
    setTimeout(() => {
      setMessages(msgs => [...msgs, { role: 'ai', text: 'AI response for: ' + prompt }]);
      setLoading(false);
    }, 1200);
  };

  const handleSummarize = () => {
    if (!selectedLeadId) return;
    setSummarizing(true);
    setTimeout(() => {
      setSummary('Summary for ' + (leadsList.find(l => l.id === selectedLeadId)?.name || '') + ': This lead has high engagement and recently responded to your outreach.');
      setSummarizing(false);
    }, 1200);
  };

  return (
    <Card className="w-80 min-h-full flex flex-col">
      <CardHeader className="flex items-center gap-2">
        <Sparkles className="text-yellow-500" />
        <span className="font-semibold">CRM Copilot</span>
        <Badge variant="secondary">AI</Badge>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col gap-2">
        <div className="mb-4">
          <div className="font-semibold mb-1">Smart Recommendations</div>
          <div className="space-y-1">
            {smartRecommendations.map((rec, i) => (
              <div key={i} className="bg-muted rounded p-2 text-sm">
                <span className="font-medium">{rec.name}</span> <span className="text-muted-foreground">- {rec.reason}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="mb-4">
          <div className="font-semibold mb-1">Predictive Analytics</div>
          <div className="space-y-1">
            {predictiveAnalytics.map((p, i) => (
              <div key={i} className="bg-muted rounded p-2 text-sm flex items-center gap-2">
                <span className="font-medium">{p.name}</span>
                <span className={`text-xs rounded px-2 py-0.5 ${p.churn === 'High' ? 'bg-red-200 text-red-800' : p.churn === 'Medium' ? 'bg-yellow-200 text-yellow-800' : 'bg-green-200 text-green-800'}`}>Churn: {p.churn}</span>
                <span className={`text-xs rounded px-2 py-0.5 ${p.conversion === 'High' ? 'bg-green-200 text-green-800' : p.conversion === 'Medium' ? 'bg-yellow-200 text-yellow-800' : 'bg-red-200 text-red-800'}`}>Conversion: {p.conversion}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="mb-4">
          <div className="font-semibold mb-1">Auto-Summary</div>
          <div className="flex gap-2 items-center mb-2">
            <select
              className="border rounded px-2 py-1 text-sm"
              value={selectedLeadId}
              onChange={e => setSelectedLeadId(e.target.value)}
            >
              <option value="">Select Lead</option>
              {leadsList.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
            </select>
            <Button size="sm" onClick={handleSummarize} disabled={!selectedLeadId || summarizing}>Summarize</Button>
          </div>
          {summarizing && <div className="text-xs text-muted-foreground">Generating summary...</div>}
          {summary && <div className="bg-muted rounded p-2 text-sm mt-1">{summary}</div>}
        </div>
        <div className="flex flex-col gap-2 mb-2">
          {examplePrompts.map((p, i) => (
            <Button key={i} variant="outline" size="sm" onClick={() => sendPrompt(p)}>{p}</Button>
          ))}
        </div>
        <div className="flex-1 overflow-y-auto bg-muted rounded p-2 mb-2">
          {messages.length === 0 && <div className="text-muted-foreground text-sm">Ask the AI assistant about your leads, CRM, or next steps.</div>}
          {messages.map((m, i) => (
            <div key={i} className={`mb-2 ${m.role === 'ai' ? 'text-blue-600' : 'text-foreground'}`}>{m.role === 'ai' ? '🤖 ' : '🧑‍💼 '}{m.text}</div>
          ))}
          {loading && <div className="text-muted-foreground text-xs">AI is thinking...</div>}
        </div>
        <form className="flex gap-2" onSubmit={e => { e.preventDefault(); if (input.trim()) { sendPrompt(input); setInput(''); } }}>
          <Input value={input} onChange={e => setInput(e.target.value)} placeholder="Ask anything..." />
          <Button type="submit" disabled={loading || !input.trim()}>Send</Button>
        </form>
      </CardContent>
    </Card>
  );
}; 