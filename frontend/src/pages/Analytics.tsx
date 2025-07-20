import React, { useState } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/tabs';
import { Download, Star, Mail } from 'lucide-react';
// Assume Chart components are available or stubbed
import Chart from '../components/ui/charts';

const DUMMY_REPORTS = [
  { id: 'r1', name: 'Leads by Source', type: 'bar' },
  { id: 'r2', name: 'Conversion Rate Over Time', type: 'line' },
  { id: 'r3', name: 'Lead Status Distribution', type: 'pie' },
];

const AnalyticsDashboard: React.FC = () => {
  const [pinned, setPinned] = useState<string[]>([]);
  const [compare, setCompare] = useState(false);
  const [email, setEmail] = useState('');
  const [scheduled, setScheduled] = useState(false);
  const [tab, setTab] = useState('r1');

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center gap-4 justify-between">
        <h1 className="text-2xl font-bold">Analytics Dashboard</h1>
        <div className="flex gap-2">
          <Button variant={compare ? 'default' : 'outline'} onClick={() => setCompare(v => !v)}>
            {compare ? 'Comparing: This vs Last Period' : 'Compare Time Series'}
          </Button>
          <Button variant="outline" onClick={() => setScheduled(true)}><Mail className="w-4 h-4 mr-1" /> Schedule Email</Button>
        </div>
      </div>
      {/* Chart Tabs */}
      <Tabs defaultValue="r1" value={tab} onValueChange={setTab}>
        <TabsList>
          {DUMMY_REPORTS.map(r => (
            <TabsTrigger key={r.id} value={r.id}>
              {r.name}
              <Button size="icon" variant={pinned.includes(r.id) ? 'default' : 'ghost'} className="ml-2" onClick={e => { e.stopPropagation(); setPinned(p => p.includes(r.id) ? p.filter(id => id !== r.id) : [...p, r.id]); }}>
                <Star className={pinned.includes(r.id) ? 'text-yellow-500' : ''} />
              </Button>
            </TabsTrigger>
          ))}
        </TabsList>
        <TabsContent value="r1">
          <Card className="p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold">Leads by Source</span>
              <div className="flex gap-2">
                <Button size="sm" variant="outline"><Download className="w-4 h-4 mr-1" /> PDF</Button>
                <Button size="sm" variant="outline"><Download className="w-4 h-4 mr-1" /> CSV</Button>
              </div>
            </div>
            <Chart title="Leads by Source" />
          </Card>
        </TabsContent>
        <TabsContent value="r2">
          <Card className="p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold">Conversion Rate Over Time</span>
              <div className="flex gap-2">
                <Button size="sm" variant="outline"><Download className="w-4 h-4 mr-1" /> PDF</Button>
                <Button size="sm" variant="outline"><Download className="w-4 h-4 mr-1" /> CSV</Button>
              </div>
            </div>
            <Chart title="Conversion Rate Over Time" />
          </Card>
        </TabsContent>
        <TabsContent value="r3">
          <Card className="p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold">Lead Status Distribution</span>
              <div className="flex gap-2">
                <Button size="sm" variant="outline"><Download className="w-4 h-4 mr-1" /> PDF</Button>
                <Button size="sm" variant="outline"><Download className="w-4 h-4 mr-1" /> CSV</Button>
              </div>
            </div>
            <Chart title="Lead Status Distribution" />
          </Card>
        </TabsContent>
      </Tabs>
      {/* Email Scheduler Modal */}
      {scheduled && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <Card className="p-6 w-full max-w-md">
            <h2 className="font-bold text-lg mb-2">Schedule Analytics Report Email</h2>
            <form onSubmit={e => { e.preventDefault(); setScheduled(false); }} className="space-y-4">
              <Input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Recipient email" required />
              <Button type="submit" className="w-full">Schedule</Button>
              <Button type="button" variant="ghost" className="w-full" onClick={() => setScheduled(false)}>Cancel</Button>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard; 