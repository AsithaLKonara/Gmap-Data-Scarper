import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import LogConsole from '../../components/LogConsole';

describe('LogConsole', () => {
  it('renders no logs message when empty', () => {
    render(<LogConsole logs={[]} />);
    expect(screen.getByText(/no logs yet/i)).toBeInTheDocument();
  });

  it('renders log messages', () => {
    const logs = ['[INFO] Starting scraper', '[SUCCESS] Found 10 leads'];
    render(<LogConsole logs={logs} />);
    
    expect(screen.getByText(/starting scraper/i)).toBeInTheDocument();
    expect(screen.getByText(/found 10 leads/i)).toBeInTheDocument();
  });
});

