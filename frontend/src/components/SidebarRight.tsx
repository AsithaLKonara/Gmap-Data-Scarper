import React, { useEffect, useState } from 'react';
import * as api from '../api';

interface SidebarRightProps {
  jobId: number | null;
}

const SidebarRight: React.FC<SidebarRightProps> = ({ jobId }) => {
  const [status, setStatus] = useState<string>('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [csvReady, setCsvReady] = useState(false);

  useEffect(() => {
    if (!jobId) return;
    
    setLoading(true);
    setStatus('pending');
    setResults([]);
    setCsvReady(false);
    
    const interval = setInterval(async () => {
      try {
        const s = await api.getJobStatus(jobId);
        setStatus(s.status);
        
        if (s.status === 'completed') {
          const r = await api.getJobResults(jobId);
          setResults(r.result);
          setCsvReady(true);
          setLoading(false);
          clearInterval(interval);
        } else if (s.status === 'failed') {
          setStatus('failed');
          setLoading(false);
          clearInterval(interval);
        }
      } catch {
        setStatus('error');
        setLoading(false);
        clearInterval(interval);
      }
    }, 2000);
    
    return () => clearInterval(interval);
  }, [jobId]);

  return (
    <div className="w-full md:w-[350px] p-4 bg-gray-100 min-h-screen border-l border-gray-200">
      <h3 className="text-lg font-semibold mb-4">Collected Data</h3>
      
      {loading && (
        <span 
          className="inline-block w-6 h-6 border-2 border-gray-300 border-t-primary rounded-full animate-spin mb-2" 
          aria-label="Loading" 
        />
      )}
      
      {status === 'completed' && results.length > 0 && (
        <div className="overflow-x-auto mb-2 rounded-md shadow-sm bg-white">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                {Object.keys(results[0]).map(key => (
                  <th key={key} className="px-2 py-1 font-medium text-gray-700 text-left">
                    {key}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {results.map((row, i) => (
                <tr key={i} className="even:bg-gray-50">
                  {Object.values(row).map((val, j) => (
                    <td key={j} className="px-2 py-1">
                      {String(val)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {status === 'pending' && (
        <span className="text-gray-700">Scraping in progress...</span>
      )}
      
      {status === 'failed' && (
        <span className="text-red-600">Scraping failed.</span>
      )}
      
      <a
        className="mt-4 w-full inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 disabled:bg-gray-300 disabled:text-gray-500 text-center"
        href={jobId && csvReady ? api.getJobCSV(jobId) : undefined}
        download
        tabIndex={csvReady ? 0 : -1}
        aria-disabled={!csvReady}
        style={{ 
          pointerEvents: csvReady ? 'auto' : 'none', 
          opacity: csvReady ? 1 : 0.5 
        }}
      >
        Download CSV
      </a>
    </div>
  );
};

export default SidebarRight;
