import React, { useState, useEffect } from 'react';
import { getTask } from '../utils/api';
import GlassModal from './ui/GlassModal';
import GlassButton from './ui/GlassButton';
import LoadingSkeleton from './LoadingSkeleton';
import { TaskStatus } from '../utils/api';

interface TaskDetailsModalProps {
  task: {
    task_id: string;
    status: string;
    progress: Record<string, number>;
    total_results: number;
    started_at?: string;
    completed_at?: string;
    duration_seconds?: number;
  };
  onClose: () => void;
}

export default function TaskDetailsModal({ task, onClose }: TaskDetailsModalProps) {
  const [taskDetails, setTaskDetails] = useState<TaskStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTaskDetails();
    const interval = setInterval(fetchTaskDetails, 2000); // Refresh every 2 seconds
    return () => clearInterval(interval);
  }, [task.task_id]);

  const fetchTaskDetails = async () => {
    try {
      const details = await getTask(task.task_id);
      setTaskDetails(details);
    } catch (err) {
      console.error('Failed to fetch task details:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  return (
    <GlassModal
      isOpen={true}
      onClose={onClose}
      title={`Task Details: ${task.task_id.substring(0, 8)}...`}
      size="lg"
    >
      {loading ? (
        <LoadingSkeleton variant="card" />
      ) : taskDetails ? (
        <div className="space-y-4">
          {/* Status */}
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-600 dark:text-gray-400">
              Status
            </label>
            <div className="glass-subtle px-3 py-2 rounded-lg">
              <span className="font-semibold text-gradient-primary">{taskDetails.status}</span>
            </div>
          </div>

          {/* Progress */}
          {Object.keys(taskDetails.progress || {}).length > 0 && (
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-600 dark:text-gray-400">
                Progress by Platform
              </label>
              <div className="glass-subtle rounded-lg p-3 space-y-2">
                {Object.entries(taskDetails.progress).map(([platform, count]) => (
                  <div key={platform} className="flex justify-between items-center">
                    <span className="capitalize">{platform.replace('_', ' ')}</span>
                    <span className="font-semibold text-gradient-primary">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Statistics */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-600 dark:text-gray-400">
                Total Results
              </label>
              <div className="glass-subtle px-3 py-2 rounded-lg">
                <span className="font-semibold text-gradient-primary">{taskDetails.total_results}</span>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-600 dark:text-gray-400">
                Current Query
              </label>
              <div className="glass-subtle px-3 py-2 rounded-lg">
                <span className="text-sm">{taskDetails.current_query || 'N/A'}</span>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-600 dark:text-gray-400">
                Current Platform
              </label>
              <div className="glass-subtle px-3 py-2 rounded-lg">
                <span className="text-sm capitalize">
                  {taskDetails.current_platform?.replace('_', ' ') || 'N/A'}
                </span>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-600 dark:text-gray-400">
                Duration
              </label>
              <div className="glass-subtle px-3 py-2 rounded-lg">
                <span className="text-sm">{formatDuration(task.duration_seconds)}</span>
              </div>
            </div>
          </div>

          {/* Timestamps */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-600 dark:text-gray-400">
                Started At
              </label>
              <div className="glass-subtle px-3 py-2 rounded-lg">
                <span className="text-sm">{formatDate(taskDetails.started_at)}</span>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-600 dark:text-gray-400">
                Completed At
              </label>
              <div className="glass-subtle px-3 py-2 rounded-lg">
                <span className="text-sm">{formatDate(taskDetails.completed_at)}</span>
              </div>
            </div>
          </div>

          {/* Error */}
          {taskDetails.error && (
            <div>
              <label className="block text-sm font-medium mb-1 text-red-600">
                Error
              </label>
              <div className="glass-subtle border border-red-500/30 px-3 py-2 rounded-lg">
                <span className="text-sm text-red-600">{taskDetails.error}</span>
              </div>
            </div>
          )}

          <div className="flex justify-end pt-4">
            <GlassButton variant="secondary" onClick={onClose}>
              Close
            </GlassButton>
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          Failed to load task details
        </div>
      )}
    </GlassModal>
  );
}

