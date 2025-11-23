import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import PhoneResultRow from '../../components/PhoneResultRow';

// Mock PhoneDetailsModal
jest.mock('../../components/PhoneDetailsModal', () => {
  return function MockPhoneDetailsModal({ onClose }: any) {
    return <div data-testid="phone-details-modal" onClick={onClose}>Phone Details</div>;
  };
});

// Mock phone utils
jest.mock('../../utils/phone', () => ({
  formatPhone: (phone: string) => phone,
  getConfidenceColor: (score: number) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'yellow';
    return 'red';
  },
  getConfidenceLabel: (score: number) => {
    if (score >= 80) return 'High';
    if (score >= 60) return 'Medium';
    return 'Low';
  },
  copyToClipboard: jest.fn().mockResolvedValue(undefined),
}));

describe('PhoneResultRow', () => {
  const mockResult = {
    display_name: 'Test Business',
    field_of_study: 'Technology',
    platform: 'google_maps',
    phones: [{
      raw_phone: '+1234567890',
      normalized_e164: '+1234567890',
      phone_source: 'tel_link',
      confidence_score: 95,
      validation_status: 'valid',
    }],
  };

  const defaultProps = {
    result: mockResult,
    onPhoneClick: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders result row with phone number', () => {
    render(<PhoneResultRow {...defaultProps} />);

    expect(screen.getByText('Test Business')).toBeInTheDocument();
    expect(screen.getByText('+1234567890')).toBeInTheDocument();
  });

  it('displays phone source', () => {
    render(<PhoneResultRow {...defaultProps} />);

    expect(screen.getByText(/tel_link/i)).toBeInTheDocument();
  });

  it('displays confidence label', () => {
    render(<PhoneResultRow {...defaultProps} />);

    expect(screen.getByText(/High/i)).toBeInTheDocument();
  });

  it('shows high confidence badge for score >= 80', () => {
    render(<PhoneResultRow {...defaultProps} />);

    const badge = screen.getByText(/High/i);
    expect(badge).toHaveClass(expect.stringContaining('green'));
  });

  it('shows medium confidence badge for score 60-79', () => {
    const resultWithMediumConfidence = {
      ...mockResult,
      phones: [{
        ...mockResult.phones[0],
        confidence_score: 70,
      }],
    };

    render(<PhoneResultRow result={resultWithMediumConfidence} onPhoneClick={jest.fn()} />);

    const badge = screen.getByText(/Medium/i);
    expect(badge).toHaveClass(expect.stringContaining('yellow'));
  });

  it('shows low confidence badge for score < 60', () => {
    const resultWithLowConfidence = {
      ...mockResult,
      phones: [{
        ...mockResult.phones[0],
        confidence_score: 50,
      }],
    };

    render(<PhoneResultRow result={resultWithLowConfidence} onPhoneClick={jest.fn()} />);

    const badge = screen.getByText(/Low/i);
    expect(badge).toHaveClass(expect.stringContaining('red'));
  });

  it('opens phone details modal when phone clicked', async () => {
    render(<PhoneResultRow {...defaultProps} />);

    const phoneButton = screen.getByText('+1234567890');
    fireEvent.click(phoneButton);

    await waitFor(() => {
      expect(screen.getByTestId('phone-details-modal')).toBeInTheDocument();
    });
  });

  it('calls onPhoneClick when phone clicked', async () => {
    const mockOnClick = jest.fn();
    render(<PhoneResultRow {...defaultProps} onPhoneClick={mockOnClick} />);

    const phoneButton = screen.getByText('+1234567890');
    fireEvent.click(phoneButton);

    await waitFor(() => {
      expect(mockOnClick).toHaveBeenCalled();
    });
  });

  it('displays normalized phone if available', () => {
    const resultWithNormalized = {
      ...mockResult,
      phones: [{
        ...mockResult.phones[0],
        raw_phone: '(123) 456-7890',
        normalized_e164: '+12345678900',
      }],
    };

    render(<PhoneResultRow result={resultWithNormalized} onPhoneClick={jest.fn()} />);

    expect(screen.getByText('+12345678900')).toBeInTheDocument();
  });

  it('handles result without phone', () => {
    const resultWithoutPhone = {
      ...mockResult,
      phones: [],
    };

    render(<PhoneResultRow result={resultWithoutPhone} onPhoneClick={jest.fn()} />);

    expect(screen.getByText('Test Business')).toBeInTheDocument();
    expect(screen.getByText(/No phone found/i)).toBeInTheDocument();
  });

  it('shows multiple phones indicator', () => {
    const resultWithMultiplePhones = {
      ...mockResult,
      phones: [
        mockResult.phones[0],
        {
          ...mockResult.phones[0],
          raw_phone: '+1987654321',
        },
      ],
    };

    render(<PhoneResultRow result={resultWithMultiplePhones} onPhoneClick={jest.fn()} />);

    expect(screen.getByText(/\+1/i)).toBeInTheDocument(); // Shows "+1" for additional phones
  });
});

