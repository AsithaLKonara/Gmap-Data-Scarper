import React, { useEffect, useState } from 'react';
import { adminGetAuditLogs } from '../api';
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from '../components/ui/table';

const PAGE_SIZE = 20;

const AdminAuditLog: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [action, setAction] = useState('');
  const [adminEmail, setAdminEmail] = useState('');
  const [targetType, setTargetType] = useState('');

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await adminGetAuditLogs({ page, pageSize: PAGE_SIZE, action, adminEmail, targetType });
      setLogs(res.results || []);
      setTotal(res.total || 0);
    } catch (e: any) {
      setError(e.message || 'Failed to load logs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchLogs(); }, [page, action, adminEmail, targetType]);

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <div className="bg-white dark:bg-gray-900 p-8 rounded-lg shadow-md">
        <h1 className="text-2xl font-bold mb-4">Admin Audit Log</h1>
        <div className="flex gap-2 mb-4">
          <input
            className="border px-2 py-1 rounded"
            placeholder="Action"
            value={action}
            onChange={e => { setAction(e.target.value); setPage(1); }}
          />
          <input
            className="border px-2 py-1 rounded"
            placeholder="User Email"
            value={adminEmail}
            onChange={e => { setAdminEmail(e.target.value); setPage(1); }}
          />
          <input
            className="border px-2 py-1 rounded"
            placeholder="Target Type"
            value={targetType}
            onChange={e => { setTargetType(e.target.value); setPage(1); }}
          />
          <button className="bg-blue-500 text-white px-3 py-1 rounded" onClick={() => fetchLogs()}>Search</button>
        </div>
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : error ? (
          <div className="flex items-center p-4 mb-4 text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400">
            {error}
          </div>
        ) : logs.length === 0 ? (
          <p className="text-gray-500">No audit logs found.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Action</TableHead>
                <TableHead>User</TableHead>
                <TableHead>Target</TableHead>
                <TableHead>Details</TableHead>
                <TableHead>Timestamp</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {logs.map(log => (
                <TableRow key={log.id}>
                  <TableCell>{log.action}</TableCell>
                  <TableCell>{log.user_email || '-'}</TableCell>
                  <TableCell>{log.target_type}{log.target_id ? ` #${log.target_id}` : ''}</TableCell>
                  <TableCell><pre className="whitespace-pre-wrap text-xs">{log.details}</pre></TableCell>
                  <TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
        {/* Pagination */}
        <div className="flex gap-2 mt-4 justify-end">
          <button
            className="px-3 py-1 rounded bg-gray-200"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >Prev</button>
          <span>Page {page} / {Math.ceil(total / PAGE_SIZE) || 1}</span>
          <button
            className="px-3 py-1 rounded bg-gray-200"
            onClick={() => setPage(p => p + 1)}
            disabled={page >= Math.ceil(total / PAGE_SIZE)}
          >Next</button>
        </div>
      </div>
    </div>
  );
};

export default AdminAuditLog; 