import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { X, Plus, ChevronLeft, ChevronRight } from 'lucide-react';

const SidebarLeft = ({ onJobCreated }: { onJobCreated: (jobId: number) => void }) => {
  const [query, setQuery] = useState('');
  const [queries, setQueries] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [collapsed, setCollapsed] = useState(false);

  const addQuery = () => {
    if (query.trim() && !queries.includes(query.trim())) {
      setQueries([query.trim(), ...queries]);
      setQuery('');
    }
  };

  const removeQuery = (q: string) => {
    setQueries(queries.filter(item => item !== q));
  };

  const handleSubmit = async () => {
    if (!queries.length) return;
    setLoading(true);
    setError(null);
    try {
      // @ts-ignore
      const res = await import('../api').then(api => api.createJob(queries));
      onJobCreated(res.job_id);
    } catch (e: any) {
      setError(e.message);
    }
    setLoading(false);
  };

  if (collapsed) {
    return (
      <div className="h-full flex flex-col items-center justify-start bg-muted border-r w-12 min-h-screen pt-4">
        <Button variant="ghost" size="icon" onClick={() => setCollapsed(false)} aria-label="Expand sidebar">
          <ChevronRight />
        </Button>
      </div>
    );
  }

  return (
    <aside className="w-full md:w-72 bg-muted border-r min-h-screen p-4 flex flex-col transition-all duration-300">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Search Queries</h3>
        <Button variant="ghost" size="icon" onClick={() => setCollapsed(true)} aria-label="Collapse sidebar">
          <ChevronLeft />
        </Button>
      </div>
      <div className="flex gap-2 mb-4">
        <Input
          placeholder="Enter search query"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && addQuery()}
        />
        <Button type="button" onClick={addQuery} variant="secondary" size="icon" aria-label="Add query">
          <Plus />
        </Button>
      </div>
      <ul className="space-y-2 mb-4">
        {queries.map(q => (
          <li key={q} className="flex items-center justify-between bg-background p-2 rounded-md shadow-sm">
            <span>{q}</span>
            <Button variant="ghost" size="icon" onClick={() => removeQuery(q)} aria-label="Remove query">
              <X className="w-4 h-4" />
            </Button>
          </li>
        ))}
      </ul>
      <Button className="w-full mb-2" onClick={handleSubmit} disabled={!queries.length || loading}>
        {loading ? 'Starting...' : 'Start Scraping'}
      </Button>
      {error && <div className="text-red-500 text-sm mt-2">{error}</div>}
    </aside>
  );
};

export default SidebarLeft; 