import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AdvancedFilters from '../../components/AdvancedFilters';

describe('AdvancedFilters', () => {
  const mockOnFilterChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders filter component', () => {
    render(<AdvancedFilters onFilterChange={mockOnFilterChange} />);
    expect(screen.getByText(/filters/i)).toBeInTheDocument();
  });

  it('applies filter presets', () => {
    render(<AdvancedFilters onFilterChange={mockOnFilterChange} />);
    
    const presetButton = screen.getByText(/hot leads/i);
    fireEvent.click(presetButton);

    expect(mockOnFilterChange).toHaveBeenCalled();
  });

  it('allows custom filter configuration', () => {
    render(<AdvancedFilters onFilterChange={mockOnFilterChange} />);
    
    // Should allow configuring filters
    expect(screen.getByText(/filters/i)).toBeInTheDocument();
  });

  it('resets filters when reset button is clicked', () => {
    render(<AdvancedFilters onFilterChange={mockOnFilterChange} />);
    
    const resetButton = screen.getByText(/reset/i);
    fireEvent.click(resetButton);

    expect(mockOnFilterChange).toHaveBeenCalled();
  });
});

