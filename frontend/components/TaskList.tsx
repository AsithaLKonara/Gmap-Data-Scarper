import React, { useState, useEffect } from 'react';
import { 
  listTasks, 
  getQueueStatus, 
  stopScraper, 
  pauseScraper, 
  resumeScraper,
  bulkStopTasks,
  bulkPauseTasks,
  bulkResumeTasks
} from '../utils/api';
import GlassCard from './ui/GlassCard';
import GlassButton from './ui/GlassButton';
import LoadingSkeleton from './LoadingSkeleton';
import ErrorDisplay from './ErrorDisplay';
import TaskDetailsModal from './TaskDetailsModal';

interface Task {
  task_id: string;
  status: string;
  progress: Record<string, number>;
  total_results: number;
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
}

export default function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [queueStatus, setQueueStatus] = useState<any>(null);
  const [selectedTaskIds, setSelectedTaskIds] = useState<Set<string>>(new Set());
  const [bulkActionLoading, setBulkActionLoading] = useState(false);

  useEffect(() => {
    fetchTasks();
    fetchQueueStatus();
    const interval = setInterval(() => {
      fetchTasks();
      fetchQueueStatus();
    }, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, [statusFilter]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const status = statusFilter === 'all' ? undefined : statusFilter;
      const data = await listTasks(status);
      setTasks(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const fetchQueueStatus = async () => {
    try {
      const status = await getQueueStatus();
      setQueueStatus(status);
    } catch (err) {
      // Ignore queue status errors
    }
  };

  const handleStop = async (taskId: string) => {
    try {
      await stopScraper(taskId);
      await fetchTasks();
    } catch (err: any) {
      setError(err.message || 'Failed to stop task');
    }
  };

  const handlePause = async (taskId: string) => {
    try {
      await pauseScraper(taskId);
      await fetchTasks();
    } catch (err: any) {
      setError(err.message || 'Failed to pause task');
    }
  };

  const handleResume = async (taskId: string) => {
    try {
      await resumeScraper(taskId);
      await fetchTasks();
    } catch (err: any) {
      setError(err.message || 'Failed to resume task');
    }
  };

  const handleBulkStop = async () => {
    if (selectedTaskIds.size === 0) return;
    if (!confirm(`Stop ${selectedTaskIds.size} task(s)?`)) return;
    
    try {
      setBulkActionLoading(true);
      const result = await bulkStopTasks(Array.from(selectedTaskIds));
      setSelectedTaskIds(new Set());
      if (result.errors && result.errors.length > 0) {
        setError(`Some tasks failed to stop: ${result.errors.join(', ')}`);
      }
      await fetchTasks();
    } catch (err: any) {
      setError(err.message || 'Failed to stop tasks');
    } finally {
      setBulkActionLoading(false);
    }
  };

  const handleBulkPause = async () => {
    if (selectedTaskIds.size === 0) return;
    if (!confirm(`Pause ${selectedTaskIds.size} task(s)?`)) return;
    
    try {
      setBulkActionLoading(true);
      const result = await bulkPauseTasks(Array.from(selectedTaskIds));
      setSelectedTaskIds(new Set());
      if (result.errors && result.errors.length > 0) {
        setError(`Some tasks failed to pause: ${result.errors.join(', ')}`);
      }
      await fetchTasks();
    } catch (err: any) {
      setError(err.message || 'Failed to pause tasks');
    } finally {
      setBulkActionLoading(false);
    }
  };

  const handleBulkResume = async () => {
    if (selectedTaskIds.size === 0) return;
    if (!confirm(`Resume ${selectedTaskIds.size} task(s)?`)) return;
    
    try {
      setBulkActionLoading(true);
      const result = await bulkResumeTasks(Array.from(selectedTaskIds));
      setSelectedTaskIds(new Set());
      if (result.errors && result.errors.length > 0) {
        setError(`Some tasks failed to resume: ${result.errors.join(', ')}`);
      }
      await fetchTasks();
    } catch (err: any) {
      setError(err.message || 'Failed to resume tasks');
    } finally {
      setBulkActionLoading(false);
    }
  };

  const toggleTaskSelection = (taskId: string) => {
    const newSelection = new Set(selectedTaskIds);
    if (newSelection.has(taskId)) {
      newSelection.delete(taskId);
    } else {
      newSelection.add(taskId);
    }
    setSelectedTaskIds(newSelection);
  };

  const toggleSelectAll = () => {
    if (selectedTaskIds.size === filteredTasks.length) {
      setSelectedTaskIds(new Set());
    } else {
      setSelectedTaskIds(new Set(filteredTasks.map(t => t.task_id)));
    }
  };

  const calculateQueuePosition = (task: Task): number | null => {
    if (task.status !== 'running' && task.status !== 'paused') return null;
    if (!queueStatus) return null;
    
    // Calculate position based on start time (earlier tasks have lower position)
    const runningTasks = filteredTasks.filter(t => 
      (t.status === 'running' || t.status === 'paused') && 
      t.started_at && 
      task.started_at &&
      new Date(t.started_at) < new Date(task.started_at)
    );
    
    return runningTasks.length + 1;
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      running: 'bg-green-100 text-green-800',
      paused: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-blue-100 text-blue-800',
      error: 'bg-red-100 text-red-800',
      stopped: 'bg-gray-100 text-gray-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
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

  const filteredTasks = statusFilter === 'all' 
    ? tasks 
    : tasks.filter(t => t.status === statusFilter);

  return (
    <GlassCard>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gradient-primary">Task Management</h2>
        {queueStatus && (
          <div className="flex gap-2 text-sm">
            <div className="glass-subtle px-3 py-1 rounded-lg">
              Running: <span className="font-semibold text-green-600">{queueStatus.running}</span>
            </div>
            <div className="glass-subtle px-3 py-1 rounded-lg">
              Paused: <span className="font-semibold text-yellow-600">{queueStatus.paused || 0}</span>
            </div>
            {queueStatus.estimated_wait_time_seconds > 0 && (
              <div className="glass-subtle px-3 py-1 rounded-lg">
                Est. Wait: <span className="font-semibold">{Math.ceil(queueStatus.estimated_wait_time_seconds / 60)}m</span>
              </div>
            )}
          </div>
        )}
      </div>

      {error && (
        <ErrorDisplay
          error={error}
          onDismiss={() => setError(null)}
          variant="error"
        />
      )}

      {/* Status Filter and Bulk Actions */}
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <div className="flex gap-2 flex-wrap">
          {['all', 'running', 'paused', 'completed', 'error', 'stopped'].map((status) => (
            <GlassButton
              key={status}
              size="sm"
              variant={statusFilter === status ? 'primary' : 'secondary'}
              gradient={statusFilter === status}
              onClick={() => setStatusFilter(status)}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </GlassButton>
          ))}
        </div>
        
        {/* Bulk Actions */}
        {selectedTaskIds.size > 0 && (
          <div className="flex gap-2 items-center">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {selectedTaskIds.size} selected
            </span>
            <GlassButton
              size="sm"
              variant="secondary"
              onClick={handleBulkPause}
              disabled={bulkActionLoading}
            >
              Pause All
            </GlassButton>
            <GlassButton
              size="sm"
              variant="success"
              onClick={handleBulkResume}
              disabled={bulkActionLoading}
            >
              Resume All
            </GlassButton>
            <GlassButton
              size="sm"
              variant="error"
              onClick={handleBulkStop}
              disabled={bulkActionLoading}
            >
              Stop All
            </GlassButton>
          </div>
        )}
      </div>

      {/* Tasks List */}
      {loading ? (
        <LoadingSkeleton variant="card" className="h-64" />
      ) : filteredTasks.length === 0 ? (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          No tasks found
        </div>
      ) : (
        <div className="space-y-2">
          {/* Select All Checkbox */}
          {filteredTasks.length > 0 && (
            <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/10">
              <label className="flex items-center gap-2 text-sm glass-subtle px-3 py-1 rounded-lg cursor-pointer hover:glass transition-all">
                <input
                  type="checkbox"
                  checked={selectedTaskIds.size === filteredTasks.length && filteredTasks.length > 0}
                  onChange={toggleSelectAll}
                  className="w-4 h-4 rounded accent-primary"
                />
                <span>Select All ({filteredTasks.length})</span>
              </label>
            </div>
          )}
          
          {filteredTasks.map((task) => {
            const queuePosition = calculateQueuePosition(task);
            return (
            <div
              key={task.task_id}
              className="glass-subtle rounded-lg p-4 hover:glass transition-all"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  {/* Selection Checkbox */}
                  <label className="flex items-center cursor-pointer" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={selectedTaskIds.has(task.task_id)}
                      onChange={() => toggleTaskSelection(task.task_id)}
                      onClick={(e) => e.stopPropagation()}
                      className="w-4 h-4 rounded accent-primary"
                    />
                  </label>
                  
                  <div className="flex-1 cursor-pointer" onClick={() => setSelectedTask(task)}>
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`px-2 py-1 text-xs rounded font-semibold ${getStatusBadge(task.status)}`}>
                        {task.status.toUpperCase()}
                      </span>
                      <span className="text-sm font-mono text-gray-600 dark:text-gray-400">
                        {task.task_id.substring(0, 8)}...
                      </span>
                      {queuePosition && (
                        <span className="text-xs glass-subtle px-2 py-1 rounded">
                          Queue: #{queuePosition}
                        </span>
                      )}
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">Results: </span>
                        <span className="font-semibold text-gradient-primary">{task.total_results}</span>
                      </div>
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">Duration: </span>
                        <span className="font-semibold">{formatDuration(task.duration_seconds)}</span>
                      </div>
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">Started: </span>
                        <span className="font-semibold">
                          {task.started_at 
                            ? new Date(task.started_at).toLocaleString()
                            : 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  {task.status === 'running' && (
                    <>
                      <GlassButton
                        size="sm"
                        variant="secondary"
                        onClick={(e) => {
                          e.stopPropagation();
                          handlePause(task.task_id);
                        }}
                      >
                        Pause
                      </GlassButton>
                      <GlassButton
                        size="sm"
                        variant="error"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleStop(task.task_id);
                        }}
                      >
                        Stop
                      </GlassButton>
                    </>
                  )}
                  {task.status === 'paused' && (
                    <GlassButton
                      size="sm"
                      variant="success"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleResume(task.task_id);
                      }}
                    >
                      Resume
                    </GlassButton>
                  )}
                </div>
              </div>
            </div>
            );
          })}
        </div>
      )}

      {/* Task Details Modal */}
      {selectedTask && (
        <TaskDetailsModal
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
        />
      )}
    </GlassCard>
  );
}
