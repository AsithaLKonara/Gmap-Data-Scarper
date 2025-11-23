import { renderHook, waitFor } from '@testing-library/react';
import useWebSocket from '../../hooks/useWebSocket';

// Mock WebSocket
global.WebSocket = jest.fn() as unknown as typeof WebSocket;

describe('useWebSocket', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('returns null when url is null', () => {
    const { result } = renderHook(() => useWebSocket(null));
    expect(result.current).toBeNull();
  });

  it('creates WebSocket connection when url is provided', () => {
    const mockWebSocket = {
      addEventListener: jest.fn(),
      close: jest.fn(),
    };
    (global.WebSocket as unknown as jest.Mock).mockImplementation(() => mockWebSocket);

    renderHook(() => useWebSocket('/api/scraper/ws/logs/test-task'));

    expect(global.WebSocket).toHaveBeenCalledWith('ws://localhost:8000/api/scraper/ws/logs/test-task');
  });
});

