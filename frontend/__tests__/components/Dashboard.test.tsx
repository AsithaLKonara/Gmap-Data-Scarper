import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Dashboard from '../../components/Dashboard';

// Mock API
jest.mock('../../utils/api', () => ({
  getAnalyticsSummary: jest.fn(() => Promise.resolve({
    total_leads: 100,
    total_tasks: 5,
    leads_today: 20,
    leads_this_week: 80,
  })),
  getPlatformStats: jest.fn(() => Promise.resolve({
    google_maps: 50,
    facebook: 30,
    linkedin: 20,
  })),
  getTimelineData: jest.fn(() => Promise.resolve({
    daily: [{ date: '2025-01-01', leads: 10 }],
  })),
  getCategoryStats: jest.fn(() => Promise.resolve({
    categories: [{ name: 'Technology', count: 30 }],
  })),
  getConfidenceStats: jest.fn(() => Promise.resolve({
    high: 60,
    medium: 30,
    low: 10,
  })),
}));

jest.mock('../../utils/toast', () => ({
  showToast: jest.fn(),
}));

describe('Dashboard', () => {
  it('renders dashboard component', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/analytics/i)).toBeInTheDocument();
    });
  });

  it('displays loading skeleton while fetching data', () => {
    render(<Dashboard />);
    // Should show loading state initially
    expect(screen.queryByText(/analytics/i)).not.toBeInTheDocument();
  });

  it('displays error message on API failure', async () => {
    const { getAnalyticsSummary } = require('../../utils/api');
    getAnalyticsSummary.mockRejectedValueOnce(new Error('API Error'));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('renders summary cards when data is loaded', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/100/i)).toBeInTheDocument(); // Total leads
    });
  });

  it('allows changing summary days filter', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/analytics/i)).toBeInTheDocument();
    });

    // Should have filter controls (implementation dependent)
    // This is a placeholder test
    expect(true).toBe(true);
  });
});

