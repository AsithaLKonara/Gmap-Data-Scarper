import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import VirtualizedResultsTable from '../../components/VirtualizedResultsTable';

// Mock react-window
jest.mock('react-window', () => ({
  VariableSizeList: ({ children, itemData }: any) => (
    <div data-testid="virtualized-list">
      {itemData.items.slice(0, 10).map((item: any, index: number) => (
        <div key={index}>{children({ index, style: {}, data: itemData })}</div>
      ))}
    </div>
  ),
}));

describe('VirtualizedResultsTable', () => {
  const mockResults = Array.from({ length: 100 }, (_, i) => ({
    id: i + 1,
    name: `Business ${i + 1}`,
    phone: `123456789${i}`,
    lead_score: 50 + (i % 50),
    platform: 'google_maps',
  }));

  it('renders virtualized table', () => {
    render(<VirtualizedResultsTable results={mockResults} />);
    expect(screen.getByTestId('virtualized-list')).toBeInTheDocument();
  });

  it('handles empty results', () => {
    render(<VirtualizedResultsTable results={[]} />);
    expect(screen.queryByText(/no results/i)).toBeInTheDocument();
  });

  it('displays results with correct columns', () => {
    render(<VirtualizedResultsTable results={mockResults.slice(0, 5)} />);
    // Check for column headers
    expect(screen.getByText(/name/i)).toBeInTheDocument();
    expect(screen.getByText(/phone/i)).toBeInTheDocument();
  });
});

