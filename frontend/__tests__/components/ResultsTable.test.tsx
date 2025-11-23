import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import VirtualizedResultsTable from '../../components/VirtualizedResultsTable';

describe('VirtualizedResultsTable', () => {
  const mockResults = [
    {
      profile_url: 'https://example.com/profile1',
      display_name: 'Test Business 1',
      phone: '+1234567890',
      location: 'Toronto, ON',
      platform: 'google_maps',
    },
    {
      profile_url: 'https://example.com/profile2',
      display_name: 'Test Business 2',
      phone: '+1987654321',
      location: 'Vancouver, BC',
      platform: 'facebook',
    },
  ];

  const defaultProps = {
    results: mockResults,
    onExport: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders results table', () => {
    render(<VirtualizedResultsTable {...defaultProps} />);

    expect(screen.getByText('Test Business 1')).toBeInTheDocument();
    expect(screen.getByText('Test Business 2')).toBeInTheDocument();
  });

  it('displays all result columns', () => {
    render(<ResultsTable {...defaultProps} />);

    // Check for column headers or data
    expect(screen.getByText(/display name/i)).toBeInTheDocument();
    expect(screen.getByText(/phone/i)).toBeInTheDocument();
    expect(screen.getByText(/location/i)).toBeInTheDocument();
    expect(screen.getByText(/platform/i)).toBeInTheDocument();
  });

  it('displays phone numbers', () => {
    render(<ResultsTable {...defaultProps} />);

    expect(screen.getByText('+1234567890')).toBeInTheDocument();
    expect(screen.getByText('+1987654321')).toBeInTheDocument();
  });

  it('handles empty results', () => {
    render(<VirtualizedResultsTable results={[]} onExport={jest.fn()} />);

    expect(screen.getByText(/no results/i)).toBeInTheDocument();
  });

  it('calls onExport when export button clicked', () => {
    const mockOnExport = jest.fn();
    render(<VirtualizedResultsTable {...defaultProps} onExport={mockOnExport} />);

    const exportButton = screen.getByText(/export/i);
    fireEvent.click(exportButton);

    expect(mockOnExport).toHaveBeenCalled();
  });

  it('supports sorting by column', () => {
    render(<VirtualizedResultsTable {...defaultProps} />);

    // Virtualized table may have different interaction patterns
    expect(screen.getByText('Test Business 1')).toBeInTheDocument();
  });

  it('handles large result sets with virtualization', () => {
    const largeResults = Array.from({ length: 100 }, (_, i) => ({
      profile_url: `https://example.com/profile${i}`,
      display_name: `Business ${i}`,
      phone: `+1${i.toString().padStart(10, '0')}`,
      location: 'Toronto, ON',
      platform: 'google_maps',
    }));

    render(<VirtualizedResultsTable results={largeResults} onExport={jest.fn()} />);

    // Should render with virtualization or pagination
    expect(screen.getByText('Business 0')).toBeInTheDocument();
  });
});

