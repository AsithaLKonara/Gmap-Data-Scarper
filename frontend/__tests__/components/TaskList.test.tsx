import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TaskList from '../../components/TaskList';

// Mock API
jest.mock('../../utils/api', () => ({
  getTasks: jest.fn(() => Promise.resolve([])),
  getTaskStatus: jest.fn(() => Promise.resolve({ status: 'completed' })),
}));

describe('TaskList', () => {
  const mockTasks = [
    {
      id: 'task-1',
      status: 'running',
      created_at: '2025-01-01T00:00:00Z',
      query: 'test query',
    },
    {
      id: 'task-2',
      status: 'completed',
      created_at: '2025-01-01T01:00:00Z',
      query: 'another query',
    },
  ];

  it('renders task list', () => {
    render(<TaskList tasks={mockTasks} />);
    expect(screen.getByText('task-1')).toBeInTheDocument();
  });

  it('displays task status badges', () => {
    render(<TaskList tasks={mockTasks} />);
    expect(screen.getByText(/running/i)).toBeInTheDocument();
    expect(screen.getByText(/completed/i)).toBeInTheDocument();
  });

  it('allows selecting a task', () => {
    const mockOnSelect = jest.fn();
    render(<TaskList tasks={mockTasks} onTaskSelect={mockOnSelect} />);
    
    const taskItem = screen.getByText('task-1');
    fireEvent.click(taskItem);

    expect(mockOnSelect).toHaveBeenCalledWith('task-1');
  });

  it('displays empty state when no tasks', () => {
    render(<TaskList tasks={[]} />);
    expect(screen.getByText(/no tasks/i)).toBeInTheDocument();
  });
});

