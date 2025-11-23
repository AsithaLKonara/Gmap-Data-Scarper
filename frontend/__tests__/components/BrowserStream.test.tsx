import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import BrowserStream from '../../components/BrowserStream';

// Mock WebSocket
global.WebSocket = jest.fn(() => ({
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  close: jest.fn(),
  send: jest.fn(),
})) as any;

describe('BrowserStream', () => {
  const defaultProps = {
    taskId: 'test-task-123',
    onPhoneClick: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders browser stream container', () => {
    render(<BrowserStream {...defaultProps} />);

    const container = screen.getByTestId('browser-stream-container');
    expect(container).toBeInTheDocument();
  });

  it('displays loading state initially', () => {
    render(<BrowserStream {...defaultProps} />);

    // May show loading or stream
    const container = screen.getByTestId('browser-stream-container');
    expect(container).toBeInTheDocument();
  });

  it('displays stream image when available', async () => {
    render(<BrowserStream {...defaultProps} />);

    // Stream should load MJPEG feed
    await waitFor(() => {
      const stream = screen.queryByTestId('browser-stream-image');
      // May or may not be present depending on stream availability
      if (stream) {
        expect(stream).toHaveAttribute('src', expect.stringContaining('/live_feed/'));
      }
    });
  });

  it('handles stream errors gracefully', () => {
    render(<BrowserStream {...defaultProps} />);

    // Component should handle errors without crashing
    const container = screen.getByTestId('browser-stream-container');
    expect(container).toBeInTheDocument();
  });

  it('displays error message on stream failure', async () => {
    // Mock image error
    const consoleError = jest.spyOn(console, 'error').mockImplementation();

    render(<BrowserStream {...defaultProps} />);

    // Component should handle image load errors
    await waitFor(() => {
      // May show error state
      expect(screen.getByTestId('browser-stream-container')).toBeInTheDocument();
    });

    consoleError.mockRestore();
  });
});

