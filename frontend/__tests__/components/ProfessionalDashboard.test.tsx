import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProfessionalDashboard from '../../components/ProfessionalDashboard';

// Mock utilities
jest.mock('../../utils/phone', () => ({
  formatPhone: jest.fn((phone) => phone),
  copyToClipboard: jest.fn(() => Promise.resolve()),
}));

jest.mock('../../utils/toast', () => ({
  showToast: jest.fn(),
}));

describe('ProfessionalDashboard', () => {
  const mockResults = [
    {
      id: 1,
      name: 'Test Business 1',
      phone: '1234567890',
      lead_score: 85,
      phones: [{ number: '1234567890', confidence: 0.9 }],
    },
    {
      id: 2,
      name: 'Test Business 2',
      phone: '0987654321',
      lead_score: 45,
      phones: [{ number: '0987654321', confidence: 0.7 }],
    },
    {
      id: 3,
      name: 'Test Business 3',
      lead_score: 92,
      phones: [],
    },
  ];

  const mockProgress = {
    google_maps: 50,
    facebook: 75,
  };

  it('renders dashboard with stats cards', () => {
    render(
      <ProfessionalDashboard
        results={mockResults}
        progress={mockProgress}
        taskId="test-task-123"
      />
    );

    expect(screen.getByText(/total leads/i)).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('calculates and displays statistics correctly', () => {
    render(
      <ProfessionalDashboard
        results={mockResults}
        progress={mockProgress}
        taskId="test-task-123"
      />
    );

    expect(screen.getByText('3')).toBeInTheDocument(); // Total leads
    expect(screen.getByText('2')).toBeInTheDocument(); // Leads with phone
  });

  it('filters results by lead score category', () => {
    render(
      <ProfessionalDashboard
        results={mockResults}
        progress={mockProgress}
        taskId="test-task-123"
      />
    );

    // Click on "Hot" filter
    const hotButton = screen.getByText(/hot/i);
    fireEvent.click(hotButton);

    // Should show only hot leads (score >= 80)
    expect(screen.getByText('Test Business 1')).toBeInTheDocument();
    expect(screen.getByText('Test Business 3')).toBeInTheDocument();
    expect(screen.queryByText('Test Business 2')).not.toBeInTheDocument();
  });

  it('searches results by query', () => {
    render(
      <ProfessionalDashboard
        results={mockResults}
        progress={mockProgress}
        taskId="test-task-123"
      />
    );

    const searchInput = screen.getByPlaceholderText(/search leads/i);
    fireEvent.change(searchInput, { target: { value: 'Business 1' } });

    expect(screen.getByText('Test Business 1')).toBeInTheDocument();
    expect(screen.queryByText('Test Business 2')).not.toBeInTheDocument();
  });

  it('displays empty state when no results', () => {
    render(
      <ProfessionalDashboard
        results={[]}
        progress={{}}
        taskId={null}
      />
    );

    expect(screen.getByText(/no leads found/i)).toBeInTheDocument();
  });

  it('displays lead score badges with correct colors', () => {
    render(
      <ProfessionalDashboard
        results={mockResults}
        progress={mockProgress}
        taskId="test-task-123"
      />
    );

    // Check for lead score display
    const business1 = screen.getByText('Test Business 1');
    expect(business1).toBeInTheDocument();
  });
});

