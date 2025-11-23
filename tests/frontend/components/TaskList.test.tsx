/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TaskList from '../../../frontend/components/TaskList';

// Mock API functions
jest.mock('../../../frontend/utils/api', () => ({
  listTasks: jest.fn(),
  getQueueStatus: jest.fn(),
  stopScraper: jest.fn(),
  pauseScraper: jest.fn(),
  resumeScraper: jest.fn(),
  bulkStopTasks: jest.fn(),
  bulkPauseTasks: jest.fn(),
  bulkResumeTasks: jest.fn(),
}));

describe('TaskList Component', () => {
  const mockTasks = [
    {
      task_id: 'task-1',
      status: 'running',
      progress: { google_maps: 10 },
      total_results: 10,
      started_at: '2025-01-14T10:00:00Z',
      duration_seconds: 300,
    },
    {
      task_id: 'task-2',
      status: 'paused',
      progress: { facebook: 5 },
      total_results: 5,
      started_at: '2025-01-14T09:00:00Z',
      duration_seconds: 600,
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    const { listTasks, getQueueStatus } = require('../../../frontend/utils/api');
    listTasks.mockResolvedValue(mockTasks);
    getQueueStatus.mockResolvedValue({
      running: 1,
      paused: 1,
      pending: 0,
      estimated_wait_time_seconds: 0,
    });
  });

  it('renders task list', async () => {
    render(<TaskList />);
    
    await waitFor(() => {
      expect(screen.getByText('Task Management')).toBeInTheDocument();
    });
  });

  it('displays task status badges', async () => {
    render(<TaskList />);
    
    await waitFor(() => {
      expect(screen.getByText('RUNNING')).toBeInTheDocument();
      expect(screen.getByText('PAUSED')).toBeInTheDocument();
    });
  });

  it('allows task selection', async () => {
    render(<TaskList />);
    
    await waitFor(() => {
      const checkboxes = screen.getAllByRole('checkbox');
      expect(checkboxes.length).toBeGreaterThan(0);
    });
  });

  it('shows bulk actions when tasks are selected', async () => {
    render(<TaskList />);
    
    await waitFor(() => {
      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[1]); // Select first task
    });
    
    await waitFor(() => {
      expect(screen.getByText(/selected/)).toBeInTheDocument();
    });
  });
});

