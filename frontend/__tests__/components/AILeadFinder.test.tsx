import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AILeadFinder from '../../components/AILeadFinder';

// Mock API
jest.mock('../../utils/api', () => ({
  generateQueries: jest.fn(() => Promise.resolve({
    queries: ['ICT students in Toronto', 'IT professionals in Toronto'],
  })),
}));

describe('AILeadFinder', () => {
  const mockOnApply = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders AI lead finder component', () => {
    render(<AILeadFinder onApply={mockOnApply} />);
    expect(screen.getByPlaceholderText(/describe your ideal leads/i)).toBeInTheDocument();
  });

  it('generates queries when input is submitted', async () => {
    render(<AILeadFinder onApply={mockOnApply} />);
    
    const input = screen.getByPlaceholderText(/describe your ideal leads/i);
    fireEvent.change(input, { target: { value: 'ICT students in Toronto' } });
    
    const generateButton = screen.getByText(/generate queries/i);
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(screen.getByText('ICT students in Toronto')).toBeInTheDocument();
    });
  });

  it('applies generated queries', async () => {
    render(<AILeadFinder onApply={mockOnApply} />);
    
    const input = screen.getByPlaceholderText(/describe your ideal leads/i);
    fireEvent.change(input, { target: { value: 'ICT students' } });
    
    const generateButton = screen.getByText(/generate queries/i);
    fireEvent.click(generateButton);

    await waitFor(() => {
      const applyButton = screen.getByText(/apply/i);
      fireEvent.click(applyButton);
    });

    expect(mockOnApply).toHaveBeenCalled();
  });

  it('shows loading state during query generation', async () => {
    const { generateQueries } = require('../../utils/api');
    generateQueries.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(<AILeadFinder onApply={mockOnApply} />);
    
    const input = screen.getByPlaceholderText(/describe your ideal leads/i);
    fireEvent.change(input, { target: { value: 'test' } });
    
    const generateButton = screen.getByText(/generate queries/i);
    fireEvent.click(generateButton);

    expect(screen.getByText(/generating/i)).toBeInTheDocument();
  });
});

