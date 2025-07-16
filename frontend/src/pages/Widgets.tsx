import React, { useEffect, useState } from 'react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { toast } from '../hooks/use-toast';
import { Copy } from 'lucide-react';

interface Widget {
  id: number;
  type: string;
  config?: Record<string, any>;
  embed_code?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

const WIDGET_TYPES = [
  { value: 'lead_capture', label: 'Lead Capture Form' },
  { value: 'testimonial', label: 'Testimonial Widget' },
  { value: 'metrics', label: 'Metrics Badge' },
];

const Widgets: React.FC = () => {
  const [widgets, setWidgets] = useState<Widget[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [newType, setNewType] = useState('lead_capture');
  const [newConfig, setNewConfig] = useState('');
  const [editModal, setEditModal] = useState<{ open: boolean; widget: Widget | null }>({ open: false, widget: null });
  const [editConfig, setEditConfig] = useState('');
  const [deleteModal, setDeleteModal] = useState<{ open: boolean; widget: Widget | null }>({ open: false, widget: null });
  const [previewModal, setPreviewModal] = useState<{ open: boolean; widget: Widget | null }>({ open: false, widget: null });

  useEffect(() => {
    loadWidgets();
  }, []);

  const loadWidgets = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/widgets', { credentials: 'include' });
      if (!res.ok) throw new Error(await res.text());
      setWidgets(await res.json());
    } catch (e) {
      setWidgets([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const configObj = newConfig ? JSON.parse(newConfig) : undefined;
      const res = await fetch('/api/widgets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ type: newType, config: configObj })
      });
      if (!res.ok) throw new Error(await res.text());
      toast({ title: 'Widget created', status: 'success' });
      setShowModal(false);
      setNewConfig('');
      loadWidgets();
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (widget: Widget) => {
    setEditConfig(widget.config ? JSON.stringify(widget.config, null, 2) : '');
    setEditModal({ open: true, widget });
  };
  const handleEditSave = async () => {
    if (!editModal.widget) return;
    setLoading(true);
    try {
      const configObj = editConfig ? JSON.parse(editConfig) : undefined;
      const res = await fetch(`/api/widgets/${editModal.widget.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ config: configObj })
      });
      if (!res.ok) throw new Error(await res.text());
      toast({ title: 'Widget updated', status: 'success' });
      setEditModal({ open: false, widget: null });
      loadWidgets();
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };
  const handleDelete = async () => {
    if (!deleteModal.widget) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/widgets/${deleteModal.widget.id}`, {
        method: 'DELETE',
        credentials: 'include',
      });
      if (!res.ok) throw new Error(await res.text());
      toast({ title: 'Widget deleted', status: 'success' });
      setDeleteModal({ open: false, widget: null });
      loadWidgets();
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold text-blue-600 mb-4">Widget Management</h1>
      <div className="flex justify-end mb-4">
        <Button onClick={() => setShowModal(true)}>Create Widget</Button>
      </div>
      {widgets.length === 0 ? (
        <div className="text-gray-500">No widgets yet.</div>
      ) : (
        <div className="space-y-4">
          {widgets.map((w) => (
            <div key={w.id} className="bg-white rounded-lg shadow p-4 flex flex-col gap-2">
              <div className="flex items-center gap-4">
                <span className="font-semibold text-blue-600">{WIDGET_TYPES.find(t => t.value === w.type)?.label || w.type}</span>
                <span className={`text-xs px-2 py-1 rounded ${w.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-600'}`}>{w.is_active ? 'Active' : 'Inactive'}</span>
                <span className="text-xs text-gray-400">Created: {new Date(w.created_at).toLocaleString()}</span>
                <Button size="sm" variant="outline" onClick={() => setPreviewModal({ open: true, widget: w })}>Preview</Button>
                <Button size="sm" variant="outline" onClick={() => handleEdit(w)}>Edit</Button>
                <Button size="sm" variant="danger" onClick={() => setDeleteModal({ open: true, widget: w })}>Delete</Button>
              </div>
              <div className="text-xs text-gray-500">Widget ID: {w.id}</div>
              {w.embed_code && (
                <div className="flex items-center gap-2 mt-2">
                  <Input value={w.embed_code} readOnly className="font-mono" />
                  <button onClick={() => {navigator.clipboard.writeText(w.embed_code || ''); toast({ title: 'Copied', status: 'success' });}} className="p-2 rounded hover:bg-gray-100" aria-label="Copy embed code"><Copy size={16} /></button>
                </div>
              )}
              {w.config && <pre className="bg-gray-50 rounded p-2 text-xs mt-2">{JSON.stringify(w.config, null, 2)}</pre>}
            </div>
          ))}
        </div>
      )}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full p-6 relative">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl font-bold"
              onClick={() => setShowModal(false)}
              aria-label="Close"
            >
              &times;
            </button>
            <h2 className="text-xl font-bold mb-4 text-blue-600">Create Widget</h2>
            <form onSubmit={handleCreate} className="flex flex-col gap-3">
              <label className="font-semibold">Type</label>
              <select value={newType} onChange={e => setNewType(e.target.value)} className="border border-gray-300 rounded px-2 py-1">
                {WIDGET_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
              <label className="font-semibold">Config (JSON)</label>
              <textarea
                value={newConfig}
                onChange={e => setNewConfig(e.target.value)}
                placeholder='{"title":"Contact Us","fields":["name","email"]}'
                className="border border-gray-300 rounded px-2 py-1 min-h-[80px] font-mono"
              />
              <div className="flex justify-end gap-2 mt-6">
                <Button type="button" onClick={() => setShowModal(false)} variant="outline">Cancel</Button>
                <Button type="submit" disabled={loading}>{loading ? 'Creating...' : 'Create'}</Button>
              </div>
            </form>
          </div>
        </div>
      )}
      {editModal.open && editModal.widget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full p-6 relative">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl font-bold"
              onClick={() => setEditModal({ open: false, widget: null })}
              aria-label="Close"
            >
              &times;
            </button>
            <h2 className="text-xl font-bold mb-4 text-blue-600">Edit Widget</h2>
            <form onSubmit={e => { e.preventDefault(); handleEditSave(); }} className="flex flex-col gap-3">
              <label className="font-semibold">Config (JSON)</label>
              <textarea
                value={editConfig}
                onChange={e => setEditConfig(e.target.value)}
                className="border border-gray-300 rounded px-2 py-1 min-h-[80px] font-mono"
              />
              <div className="flex justify-end gap-2 mt-6">
                <Button type="button" onClick={() => setEditModal({ open: false, widget: null })} variant="outline">Cancel</Button>
                <Button type="submit" disabled={loading}>{loading ? 'Saving...' : 'Save'}</Button>
              </div>
            </form>
          </div>
        </div>
      )}
      {deleteModal.open && deleteModal.widget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full p-6 relative">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl font-bold"
              onClick={() => setDeleteModal({ open: false, widget: null })}
              aria-label="Close"
            >
              &times;
            </button>
            <h2 className="text-xl font-bold mb-4 text-red-600">Delete Widget</h2>
            <p>Are you sure you want to delete this widget?</p>
            <div className="flex justify-end gap-2 mt-6">
              <Button type="button" onClick={() => setDeleteModal({ open: false, widget: null })} variant="outline">Cancel</Button>
              <Button type="button" onClick={handleDelete} variant="danger" disabled={loading}>{loading ? 'Deleting...' : 'Delete'}</Button>
            </div>
          </div>
        </div>
      )}
      {previewModal.open && previewModal.widget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full p-6 relative">
            <button
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-2xl font-bold"
              onClick={() => setPreviewModal({ open: false, widget: null })}
              aria-label="Close"
            >
              &times;
            </button>
            <h2 className="text-xl font-bold mb-4 text-blue-600">Widget Preview</h2>
            <pre className="bg-gray-50 rounded p-2 text-xs mt-2">{JSON.stringify(previewModal.widget.config, null, 2)}</pre>
            <div className="flex justify-end gap-2 mt-6">
              <Button type="button" onClick={() => setPreviewModal({ open: false, widget: null })} variant="outline">Close</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Widgets; 