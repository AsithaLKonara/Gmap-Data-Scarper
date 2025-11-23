import { useState, useEffect } from 'react';
import { getRetentionStats, runCleanup, optOut } from '../utils/api';
import GlassCard from './ui/GlassCard';
import GlassButton from './ui/GlassButton';
import GlassInput from './ui/GlassInput';
import ErrorDisplay from './ErrorDisplay';
import LoadingSkeleton from './LoadingSkeleton';

interface RetentionStats {
  total_records: number;
  oldest_record_date: string;
  records_to_delete: number;
  next_cleanup_date: string;
}

export default function ComplianceDashboard() {
  const [stats, setStats] = useState<RetentionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [cleaning, setCleaning] = useState(false);
  const [optOutUrl, setOptOutUrl] = useState('');
  const [optOutLoading, setOptOutLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await getRetentionStats();
      setStats(data);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load retention statistics' });
    } finally {
      setLoading(false);
    }
  };

  const handleCleanup = async () => {
    if (!confirm('Are you sure you want to manually purge old records? This action cannot be undone.')) {
      return;
    }

    try {
      setCleaning(true);
      const result = await runCleanup();
      setMessage({
        type: 'success',
        text: `Successfully deleted ${result.records_deleted || 0} records`,
      });
      await loadStats();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to run cleanup' });
    } finally {
      setCleaning(false);
    }
  };

  const handleOptOut = async () => {
    if (!optOutUrl.trim()) {
      setMessage({ type: 'error', text: 'Please enter a profile URL' });
      return;
    }

    try {
      setOptOutLoading(true);
      await optOut(optOutUrl);
      setMessage({ type: 'success', text: 'Record removed successfully' });
      setOptOutUrl('');
      await loadStats();
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to remove record',
      });
    } finally {
      setOptOutLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const calculateDaysUntil = (dateString: string) => {
    if (!dateString) return 0;
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diff = date.getTime() - now.getTime();
      return Math.ceil(diff / (1000 * 60 * 60 * 24));
    } catch {
      return 0;
    }
  };

  return (
    <div className="space-y-6">
      {/* Message Banner */}
      {message && (
        <ErrorDisplay
          error={message.text}
          onDismiss={() => setMessage(null)}
          variant={message.type === 'success' ? 'info' : 'error'}
        />
      )}

      {/* Retention Statistics */}
      <GlassCard>
        <h2 className="text-xl font-semibold mb-4 text-gradient-primary">Data Retention Statistics</h2>
        {loading ? (
          <LoadingSkeleton variant="card" />
        ) : stats ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-600">Total Records</div>
              <div className="text-2xl font-bold">{stats.total_records || 0}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Oldest Record</div>
              <div className="text-lg font-semibold">
                {formatDate(stats.oldest_record_date)}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Records Scheduled for Deletion</div>
              <div className="text-2xl font-bold text-orange-600">
                {stats.records_to_delete || 0}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Next Automatic Cleanup</div>
              <div className="text-lg font-semibold">
                {formatDate(stats.next_cleanup_date)}
                {stats.next_cleanup_date && (
                  <span className="ml-2 text-sm text-gray-500">
                    ({calculateDaysUntil(stats.next_cleanup_date)} days)
                  </span>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-gray-500">No statistics available</div>
        )}
      </GlassCard>

      {/* Manual Cleanup */}
      <GlassCard>
        <h2 className="text-xl font-semibold mb-4 text-gradient-primary">Manual Cleanup</h2>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Manually trigger cleanup of records older than the retention period (default: 6 months).
        </p>
        <GlassButton
          onClick={handleCleanup}
          disabled={cleaning}
          variant="error"
          gradient
        >
          {cleaning ? 'Cleaning...' : 'Run Cleanup Now'}
        </GlassButton>
      </GlassCard>

      {/* Opt-Out Request */}
      <GlassCard>
        <h2 className="text-xl font-semibold mb-4 text-gradient-primary">Opt-Out Request</h2>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Remove a specific record by profile URL. This will delete the record from all CSV files.
        </p>
        <div className="flex gap-2">
          <GlassInput
            type="text"
            value={optOutUrl}
            onChange={(e) => setOptOutUrl(e.target.value)}
            placeholder="Enter profile URL"
            className="flex-1"
          />
          <GlassButton
            onClick={handleOptOut}
            disabled={optOutLoading}
            variant="primary"
            gradient
          >
            {optOutLoading ? 'Removing...' : 'Remove Record'}
          </GlassButton>
        </div>
      </GlassCard>

      {/* Retention Policy Info */}
      <GlassCard className="border-primary/30 bg-primary/10">
        <h3 className="font-semibold text-gradient-primary mb-2">Retention Policy</h3>
        <p className="text-sm text-gray-700 dark:text-gray-300">
          Records are automatically deleted after 6 months (180 days) from the extraction date.
          This ensures compliance with data retention regulations while maintaining useful lead data
          for business purposes.
        </p>
      </GlassCard>
    </div>
  );
}

