import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SearchTemplates from '../../components/SearchTemplates';

// Mock API
jest.mock('../../utils/api', () => ({
  getTemplates: jest.fn(() => Promise.resolve([
    { id: 'template-1', name: 'ICT Students', query: 'ICT students', platforms: ['google_maps'] },
    { id: 'template-2', name: 'Restaurants', query: 'restaurants', platforms: ['facebook'] },
  ])),
}));

describe('SearchTemplates', () => {
  const mockOnApply = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders template list', async () => {
    render(<SearchTemplates onApply={mockOnApply} />);
    
    await waitFor(() => {
      expect(screen.getByText('ICT Students')).toBeInTheDocument();
    });
  });

  it('applies template when selected', async () => {
    render(<SearchTemplates onApply={mockOnApply} />);
    
    await waitFor(() => {
      const template = screen.getByText('ICT Students');
      fireEvent.click(template);
    });

    expect(mockOnApply).toHaveBeenCalled();
  });

  it('shows template preview', async () => {
    render(<SearchTemplates onApply={mockOnApply} />);
    
    await waitFor(() => {
      expect(screen.getByText(/ICT students/i)).toBeInTheDocument();
    });
  });
});

