import React, { useEffect, useState } from 'react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { toast } from '../hooks/use-toast';
import { getAffiliateStats, listAffiliateCommissions, requestAffiliatePayout, generateAffiliateCode } from '../api';

interface Affiliate {
  code: string;
  total_earnings: number;
  is_active: boolean;
  created_at: string;
}

interface Commission {
  id: number;
  amount: number;
  status: string;
  created_at: string;
  paid_at?: string;
  notes?: string;
  referred_user_id: number;
}

const AffiliatePortal: React.FC = () => {
  const [affiliate, setAffiliate] = useState<Affiliate | null>(null);
  const [commissions, setCommissions] = useState<Commission[]>([]);
  const [loading, setLoading] = useState(false);
  const [payoutAmount, setPayoutAmount] = useState('');
  const [payoutNotes, setPayoutNotes] = useState('');

  useEffect(() => {
    loadAffiliate();
    loadCommissions();
  }, []);

  const loadAffiliate = async () => {
    setLoading(true);
    try {
      const res = await getAffiliateStats();
      setAffiliate(res);
    } catch (e: any) {
      setAffiliate(null);
    } finally {
      setLoading(false);
    }
  };

  const loadCommissions = async () => {
    try {
      const res = await listAffiliateCommissions();
      setCommissions(res);
    } catch (e) {
      setCommissions([]);
    }
  };

  const handleCopyCode = () => {
    if (affiliate?.code) {
      navigator.clipboard.writeText(affiliate.code);
      toast({ title: 'Copied', status: 'success' });
    }
  };

  const handleCopyLink = () => {
    if (affiliate?.code) {
      navigator.clipboard.writeText(window.location.origin + '/register?aff=' + affiliate.code);
      toast({ title: 'Link copied', status: 'success' });
    }
  };

  const handleGenerateCode = async () => {
    setLoading(true);
    try {
      const res = await generateAffiliateCode();
      setAffiliate(res);
      toast({ title: 'Affiliate code generated', status: 'success' });
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handlePayoutRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!payoutAmount.trim()) return;
    setLoading(true);
    try {
      const data = await requestAffiliatePayout(parseFloat(payoutAmount), payoutNotes);
      toast({ title: data.message, status: data.success ? 'success' : 'error' });
      setPayoutAmount('');
      setPayoutNotes('');
    } catch (e: any) {
      toast({ title: 'Error', description: e.message, status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold text-blue-600 mb-4">Affiliate Program</h1>
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-lg font-semibold text-blue-600 mb-2">Your Affiliate Code</h2>
        {affiliate ? (
          <div className="flex flex-col gap-2 mb-4">
            <div className="flex items-center gap-2">
              <Input value={affiliate.code} readOnly className="w-40 font-mono" />
              <Button onClick={handleCopyCode}>Copy Code</Button>
              <Button onClick={handleCopyLink}>Copy Link</Button>
            </div>
            <div className="text-xs text-gray-500">Share this code or link to earn commissions on paid signups.</div>
            <div className="mt-2 text-sm text-green-700 font-semibold">Total Earnings: ${affiliate.total_earnings.toFixed(2)}</div>
          </div>
        ) : (
          <div className="flex flex-col gap-2 mb-4">
            <div className="text-gray-500">No affiliate account found.</div>
            <Button onClick={handleGenerateCode} disabled={loading}>Generate Affiliate Code</Button>
          </div>
        )}
      </div>
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-lg font-semibold text-blue-600 mb-2">Your Commissions</h2>
        {commissions.length === 0 ? (
          <div className="text-gray-500">No commissions yet.</div>
        ) : (
          <table className="min-w-full border border-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2">Amount</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2">Created</th>
                <th className="px-4 py-2">Paid</th>
                <th className="px-4 py-2">Notes</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {commissions.map((c) => (
                <tr key={c.id}>
                  <td className="px-4 py-2">${c.amount.toFixed(2)}</td>
                  <td className="px-4 py-2">{c.status}</td>
                  <td className="px-4 py-2">{new Date(c.created_at).toLocaleString()}</td>
                  <td className="px-4 py-2">{c.paid_at ? new Date(c.paid_at).toLocaleString() : '-'}</td>
                  <td className="px-4 py-2">{c.notes || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-lg font-semibold text-blue-600 mb-2">Request Payout</h2>
        <form onSubmit={handlePayoutRequest} className="flex flex-col gap-3 max-w-sm">
          <Input
            type="number"
            min="1"
            step="0.01"
            placeholder="Amount (USD)"
            value={payoutAmount}
            onChange={e => setPayoutAmount(e.target.value)}
            required
          />
          <Input
            placeholder="Notes (optional)"
            value={payoutNotes}
            onChange={e => setPayoutNotes(e.target.value)}
          />
          <Button type="submit" disabled={loading}>Request Payout</Button>
        </form>
      </div>
    </div>
  );
};

export default AffiliatePortal; 