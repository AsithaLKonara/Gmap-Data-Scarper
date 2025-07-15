import React, { useState } from 'react';
import { Card, CardHeader, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Sparkles } from 'lucide-react';

const examplePrompts = [
  'What are my top 5 leads this week?',
  'Summarize contact history for John Doe.',
  'Generate a follow-up email.',
  'Show leads likely to convert soon.',
  'Who should I contact next?'
];

export const AIAssistantSidebar: React.FC = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<{ role: 'user' | 'ai'; text: string }[]>([]);
  const [loading, setLoading] = useState(false);

  const sendPrompt = async (prompt: string) => {
    setMessages(msgs => [...msgs, { role: 'user', text: prompt }]);
    setLoading(true);
    // TODO: Integrate with backend AI API
    setTimeout(() => {
      setMessages(msgs => [...msgs, { role: 'ai', text: 'AI response for: ' + prompt }]);
      setLoading(false);
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