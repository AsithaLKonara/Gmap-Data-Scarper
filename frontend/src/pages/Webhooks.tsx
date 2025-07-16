import React, { useEffect, useState } from 'react';
import { Dialog } from '../components/ui/dialog';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { toast } from '../hooks/use-toast';
import { Copy } from 'lucide-react';

interface Webhook {
  id: number;
  url: string;
  event: string;
  is_active: boolean;
  secret?: string;
  last_delivery_status?: string;
  last_delivery_at?: string;
  created_at: string;
  updated_at?: string;
}

const EVENT_OPTIONS = [
  { value: 'job.completed', label: 'Job Completed' },
  { value: 'lead.created', label: 'Lead Created' },
];

const Webhooks: React.FC = () => {
  const [webhooks, setWebhooks] = useState<Webhook[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Webhook | null>(null);
  const [form, setForm] = useState({ url: '', event: EVENT_OPTIONS[0].value, secret: '' });
  const [logModalOpen, setLogModalOpen] = useState(false);
  const [logWebhook, setLogWebhook] = useState<Webhook | null>(null);
  const [deliveryLog, setDeliveryLog] = useState<any[]>([]);
  const [testLoading, setTestLoading] = useState<number | null>(null);

  const fetchWebhooks = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/webhooks/', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } });
      const data = await res.json();
      setWebhooks(data);
    } catch (e) {
      toast({ title: 'Error', description: 'Failed to load webhooks', status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchWebhooks(); }, []);

  const handleOpenModal = (wh?: Webhook) => {
    setEditing(wh || null);
    setForm(wh ? { url: wh.url, event: wh.event, secret: wh.secret || '' } : { url: '', event: EVENT_OPTIONS[0].value, secret: '' });
    setModalOpen(true);
  };

  const handleSave = async () => {
    if (!form.url) return toast({ title: 'URL required', status: 'error' });
    setLoading(true);
    try {
      const method = editing ? 'PUT' : 'POST';
      const url = editing ? `/api/webhooks/${editing.id}` : '/api/webhooks/';
      const res = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ ...form })
      });
      if (!res.ok) throw new Error(await res.text());
      setModalOpen(false);
      fetchWebhooks();
      toast({ title: editing ? 'Webhook updated' : 'Webhook created', status: 'success' });
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this webhook?')) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/webhooks/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (!res.ok) throw new Error(await res.text());
      fetchWebhooks();
      toast({ title: 'Webhook deleted', status: 'success' });
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (wh: Webhook) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/webhooks/${wh.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ is_active: !wh.is_active })
      });
      if (!res.ok) throw new Error(await res.text());
      fetchWebhooks();
      toast({ title: `Webhook ${!wh.is_active ? 'enabled' : 'disabled'}`, status: 'success' });
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleTest = async (wh: Webhook) => {
    setTestLoading(wh.id);
    try {
      const res = await fetch('/api/webhooks/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ webhook_id: wh.id })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Test failed');
      toast({ title: 'Test sent', description: data.message || 'Webhook test sent', status: 'success' });
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    } finally {
      setTestLoading(null);
    }
  };

  const handleViewLog = async (wh: Webhook) => {
    setLogModalOpen(true);
    setLogWebhook(wh);
    setDeliveryLog([]);
    try {
      const res = await fetch(`/api/webhooks/${wh.id}/delivery-log`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await res.json();
      setDeliveryLog(data);
    } catch (e) {
      setDeliveryLog([]);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold mb-6">Webhooks</h1>
      <div className="mb-4 flex justify-end">
        <Button onClick={() => handleOpenModal()}>Add Webhook</Button>
      </div>
      <div className="bg-white rounded shadow p-4">
        {loading ? <div>Loading...</div> : (
          <table className="min-w-full text-sm">
            <thead>
              <tr>
                <th className="text-left py-2">Event</th>
                <th className="text-left py-2">URL</th>
                <th className="text-left py-2">Status</th>
                <th className="text-left py-2">Last Delivery</th>
                <th className="text-left py-2">Secret</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {webhooks.map(wh => (
                <tr key={wh.id} className="border-t">
                  <td className="py-2">{EVENT_OPTIONS.find(e => e.value === wh.event)?.label || wh.event}</td>
                  <td className="py-2">{wh.url}</td>
                  <td className="py-2 flex items-center gap-2">
                    <span>{wh.is_active ? 'Active' : 'Inactive'}</span>
                    <Button size="sm" variant="outline" onClick={() => handleToggleActive(wh)} disabled={loading}>
                      {wh.is_active ? 'Disable' : 'Enable'}
                    </Button>
                  </td>
                  <td className="py-2">
                    {wh.last_delivery_status || '-'} {wh.last_delivery_at ? (<span className="text-xs text-gray-500">({new Date(wh.last_delivery_at).toLocaleString()})</span>) : null}
                    <Button size="sm" variant="outline" className="ml-2" onClick={() => handleViewLog(wh)}>View Log</Button>
                  </td>
                  <td className="py-2 flex items-center gap-2">
                    {wh.secret ? (
                      <>
                        <span className="font-mono text-xs">{wh.secret}</span>
                        <button onClick={() => {navigator.clipboard.writeText(wh.secret || ''); toast({ title: 'Copied', status: 'success' });}}><Copy size={14} /></button>
                      </>
                    ) : <span className="text-xs text-gray-400">None</span>}
                  </td>
                  <td className="py-2 flex gap-2">
                    <Button size="sm" variant="outline" onClick={() => handleOpenModal(wh)}>Edit</Button>
                    <Button size="sm" variant="destructive" onClick={() => handleDelete(wh.id)}>Delete</Button>
                    <Button size="sm" variant="outline" onClick={() => handleTest(wh)} disabled={testLoading === wh.id}>{testLoading === wh.id ? 'Testing...' : 'Test'}</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      <div className="mt-4 text-xs text-gray-500">
        <strong>Signature:</strong> If you set a secret, each webhook request will include an <code>X-Webhook-Signature</code> header (HMAC SHA256 of the body).
      </div>
      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full p-6 relative">
            <button className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl font-bold" onClick={() => setModalOpen(false)} aria-label="Close">&times;</button>
            <h2 className="text-xl font-bold mb-4">{editing ? 'Edit Webhook' : 'Add Webhook'}</h2>
            <div className="flex flex-col gap-3">
              <label className="text-sm font-medium">Event</label>
              <select className="border rounded px-2 py-1" value={form.event} onChange={e => setForm(f => ({ ...f, event: e.target.value }))}>
                {EVENT_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
              </select>
              <label className="text-sm font-medium">Webhook URL</label>
              <Input value={form.url} onChange={e => setForm(f => ({ ...f, url: e.target.value }))} placeholder="https://yourapp.com/webhook" />
              <label className="text-sm font-medium">Secret (optional)</label>
              <Input value={form.secret} onChange={e => setForm(f => ({ ...f, secret: e.target.value }))} placeholder="Secret for signing (optional)" />
            </div>
            <div className="flex justify-end gap-2 mt-6">
              <Button variant="outline" onClick={() => setModalOpen(false)} disabled={loading}>Cancel</Button>
              <Button onClick={handleSave} disabled={loading}>{editing ? 'Update' : 'Create'}</Button>
            </div>
          </div>
        </div>
      </Dialog>
      {/* Delivery Log Modal */}
      {logModalOpen && logWebhook && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full p-6 relative">
            <button className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl font-bold" onClick={() => setLogModalOpen(false)} aria-label="Close">&times;</button>
            <h2 className="text-xl font-bold mb-4">Delivery Log</h2>
            {deliveryLog.length === 0 ? <div className="text-gray-500">No delivery log found.</div> : (
              <ul className="text-xs">
                {deliveryLog.map((log, i) => (
                  <li key={i} className="mb-2">
                    <div>Status: <span className="font-mono">{log.status}</span></div>
                    <div>Time: {new Date(log.timestamp).toLocaleString()}</div>
                    {log.response_code && <div>Response Code: {log.response_code}</div>}
                    {log.error && <div className="text-red-500">Error: {log.error}</div>}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Webhooks; 