import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import LeftPanel from '../../components/LeftPanel';

// Mock API
jest.mock('../../utils/api', () => ({
  startScraper: jest.fn(),
  stopScraper: jest.fn(),
  getPlatforms: jest.fn(() => Promise.resolve(['google_maps', 'facebook'])),
}));

describe('LeftPanel', () => {
  const mockOnStart = jest.fn();
  const mockOnStop = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders search query input', () => {
    render(
      <LeftPanel
        onStart={mockOnStart}
        onStop={mockOnStop}
        taskId={null}
        progress={{}}
        totalResults={0}
      />
    );

    expect(screen.getByPlaceholderText(/e.g., ICT students/i)).toBeInTheDocument();
  });

  it('renders platform checkboxes', async () => {
    render(
      <LeftPanel
        onStart={mockOnStart}
        onStop={mockOnStop}
        taskId={null}
        progress={{}}
        totalResults={0}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/google maps/i)).toBeInTheDocument();
    });
  });

  it('calls onStart when start button is clicked', async () => {
    const { startScraper } = require('../../utils/api');
    startScraper.mockResolvedValue({ task_id: 'test-task-123' });

    render(
      <LeftPanel
        onStart={mockOnStart}
        onStop={mockOnStop}
        taskId={null}
        progress={{}}
        totalResults={0}
      />
    );

    const startButton = screen.getByText(/start scraping/i);
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(mockOnStart).toHaveBeenCalledWith('test-task-123');
    });
  });

  it('shows stop button when task is running', () => {
    render(
      <LeftPanel
        onStart={mockOnStart}
        onStop={mockOnStop}
        taskId="test-task-123"
        progress={{}}
        totalResults={0}
      />
    );

    expect(screen.getByText(/stop scraping/i)).toBeInTheDocument();
  });

  it('disables export button when no results', () => {
    render(
      <LeftPanel
        onStart={mockOnStart}
        onStop={mockOnStop}
        taskId={null}
        progress={{}}
        totalResults={0}
      />
    );

    const exportButton = screen.getByText(/export csv/i);
    expect(exportButton).toBeDisabled();
  });
});

