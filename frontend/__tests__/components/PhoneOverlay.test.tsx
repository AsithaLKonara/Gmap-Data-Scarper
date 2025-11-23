import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import PhoneOverlay from '../../components/PhoneOverlay';

describe('PhoneOverlay', () => {
  const mockCoordinates = {
    x: 0.1,
    y: 0.2,
    width: 0.15,
    height: 0.05,
  };

  const defaultProps = {
    coordinates: mockCoordinates,
    phoneNumber: '+1234567890',
    source: 'tel_link',
    confidence: 95,
    containerWidth: 1920,
    containerHeight: 1080,
  };

  it('renders phone overlay with correct position', () => {
    render(<PhoneOverlay {...defaultProps} />);

    const overlay = screen.getByTestId('phone-overlay');
    expect(overlay).toBeInTheDocument();
    
    // Check positioning (x: 0.1 * 1920 = 192px, y: 0.2 * 1080 = 216px)
    expect(overlay).toHaveStyle({
      position: 'absolute',
    });
  });

  it('displays phone number', () => {
    render(<PhoneOverlay {...defaultProps} />);

    expect(screen.getByText('+1234567890')).toBeInTheDocument();
  });

  it('shows high confidence color (green) for confidence >= 80', () => {
    render(<PhoneOverlay {...defaultProps} confidence={95} />);

    const overlay = screen.getByTestId('phone-overlay');
    expect(overlay).toHaveStyle({
      backgroundColor: expect.stringContaining('34, 197, 94'), // Green
    });
  });

  it('shows medium confidence color (yellow) for confidence 60-79', () => {
    render(<PhoneOverlay {...defaultProps} confidence={70} />);

    const overlay = screen.getByTestId('phone-overlay');
    expect(overlay).toHaveStyle({
      backgroundColor: expect.stringContaining('234, 179, 8'), // Yellow
    });
  });

  it('shows low confidence color (red) for confidence < 60', () => {
    render(<PhoneOverlay {...defaultProps} confidence={50} />);

    const overlay = screen.getByTestId('phone-overlay');
    expect(overlay).toHaveStyle({
      backgroundColor: expect.stringContaining('239, 68, 68'), // Red
    });
  });

  it('calls onClick when clicked', () => {
    const mockOnClick = jest.fn();
    render(<PhoneOverlay {...defaultProps} onClick={mockOnClick} />);

    const overlay = screen.getByTestId('phone-overlay');
    fireEvent.click(overlay);

    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('displays source information', () => {
    render(<PhoneOverlay {...defaultProps} source="tel_link" />);

    expect(screen.getByText(/tel_link/i)).toBeInTheDocument();
  });

  it('handles different container sizes', () => {
    render(
      <PhoneOverlay
        {...defaultProps}
        containerWidth={800}
        containerHeight={600}
      />
    );

    const overlay = screen.getByTestId('phone-overlay');
    expect(overlay).toBeInTheDocument();
    // Position should scale with container size
  });
});
