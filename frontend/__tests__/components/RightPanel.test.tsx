import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import RightPanel from '../../components/RightPanel';

describe('RightPanel', () => {
  it('renders no stream message when taskId is null', () => {
    render(<RightPanel taskId={null} results={[]} />);
    expect(screen.getByText(/no active stream/i)).toBeInTheDocument();
  });

  it('renders stream image when taskId is provided', () => {
    render(<RightPanel taskId="test-task-123" results={[]} />);
    const img = screen.getByAltText(/live browser stream/i);
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('src', 'http://localhost:8000/live_feed/test-task-123');
  });

  it('renders results table', () => {
    const mockResults = [
      {
        display_name: 'Test Business',
        phones: [{
          raw_phone: '555-123-4567',
          normalized_e164: '+15551234567',
          confidence_score: 90,
          phone_source: 'tel_link'
        }],
        field_of_study: 'ICT',
        platform: 'google_maps'
      }
    ];

    render(<RightPanel taskId="test-task-123" results={mockResults} />);
    expect(screen.getByText(/test business/i)).toBeInTheDocument();
  });
});

