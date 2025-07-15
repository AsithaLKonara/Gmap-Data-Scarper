import React, { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Sparkles, Loader2 } from 'lucide-react';

interface AICopilotSidebarProps {
  leadCount: number;
  onPrompt: (prompt: string) => Promise<string>;
}

const EXAMPLE_PROMPTS = [
  'Who are my top 5 leads to follow up with this week?',
  'Summarize contact history for John Doe.',
  'Generate a follow-up email for a warm lead.',
  'What is the conversion chance for my current pipeline?',
  'Show leads at risk of churn.',
];

export const AICopilotSidebar: React.FC<AICopilotSidebarProps> = ({ leadCount, onPrompt }) => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<string | null>(null);

  const handlePrompt = async (prompt: string) => {
    setLoading(true);
    setResponse(null);
    try {
      const res = await onPrompt(prompt);
      setResponse(res);
    } finally {
      setLoading(false);
    }
  };

  return (
    <aside className="fixed top-20 right-0 w-80 max-w-full h-[calc(100vh-5rem)] bg-card border-l border-border shadow-lg z-40 flex flex-col p-4 gap-4">
      <div className="flex items-center gap-2 mb-2">
        <Sparkles className="text-primary" />
        <span className="font-bold text-lg">AI Copilot</span>
      </div>
      <div className="text-xs text-muted-foreground mb-2">{leadCount} leads loaded. Ask anything about your CRM or try a suggestion below:</div>
      <div className="flex flex-col gap-2 mb-2">
        {EXAMPLE_PROMPTS.map(p => (
          <Button key={p} variant="ghost" size="sm" className="justify-start" onClick={() => handlePrompt(p)}>
            {p}
          </Button>
        ))}
      </div>
      <form
        className="flex gap-2 mb-2"
        onSubmit={e => {
          e.preventDefault();
          if (input.trim()) handlePrompt(input.trim());
        }}
      >
        <Input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask Copilot..."
          className="flex-1"
        />
        <Button type="submit" size="sm" disabled={loading || !input.trim()}>Ask</Button>
      </form>
      <Card className="flex-1 p-3 overflow-y-auto bg-muted">
        {loading ? (
          <div className="flex items-center gap-2 text-muted-foreground"><Loader2 className="animate-spin" /> Generating...</div>
        ) : response ? (
          <div className="whitespace-pre-line text-sm text-foreground">{response}</div>
        ) : (
          <div className="text-xs text-muted-foreground">AI suggestions and summaries will appear here.</div>
        )}
      </Card>
    </aside>
  );
}; 