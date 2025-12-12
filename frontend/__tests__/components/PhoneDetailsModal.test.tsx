import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import PhoneDetailsModal from '../../components/PhoneDetailsModal';

describe('PhoneDetailsModal', () => {
  const mockPhone = {
    number: '+1234567890',
    confidence: 0.9,
    source: 'DOM',
    coordinates: { x: 100, y: 200 },
  };

  it('renders modal when open', () => {
    render(
      <PhoneDetailsModal
        isOpen={true}
        phone={mockPhone}
        onClose={() => {}}
      />
    );

    expect(screen.getByText('+1234567890')).toBeInTheDocument();
  });

  it('displays phone source information', () => {
    render(
      <PhoneDetailsModal
        isOpen={true}
        phone={mockPhone}
        onClose={() => {}}
      />
    );

    expect(screen.getByText(/source/i)).toBeInTheDocument();
    expect(screen.getByText(/DOM/i)).toBeInTheDocument();
  });

  it('displays confidence score', () => {
    render(
      <PhoneDetailsModal
        isOpen={true}
        phone={mockPhone}
        onClose={() => {}}
      />
    );

    expect(screen.getByText(/confidence/i)).toBeInTheDocument();
    expect(screen.getByText(/90/i)).toBeInTheDocument();
  });

  it('closes modal when close button is clicked', () => {
    const mockOnClose = jest.fn();
    render(
      <PhoneDetailsModal
        isOpen={true}
        phone={mockPhone}
        onClose={mockOnClose}
      />
    );

    const closeButton = screen.getByLabelText(/close/i);
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('does not render when closed', () => {
    render(
      <PhoneDetailsModal
        isOpen={false}
        phone={mockPhone}
        onClose={() => {}}
      />
    );

    expect(screen.queryByText('+1234567890')).not.toBeInTheDocument();
  });
});

