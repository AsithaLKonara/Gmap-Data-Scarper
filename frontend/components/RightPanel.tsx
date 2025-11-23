import { useEffect, useState, useRef } from 'react';
import PhoneOverlay from './PhoneOverlay';
import VirtualizedResultsTable from './VirtualizedResultsTable';

interface PhoneData {
  raw_phone: string;
  normalized_e164?: string;
  validation_status: string;
  confidence_score: number;
  phone_source: string;
  phone_element_selector?: string;
  phone_screenshot_path?: string;
  phone_timestamp?: string;
  phone_coordinates?: {
    x: number;
    y: number;
    width: number;
    height: number;
    absolute_x?: number;
    absolute_y?: number;
    viewport_width?: number;
    viewport_height?: number;
    scroll_x?: number;
    scroll_y?: number;
  };
  viewport_info?: {
    width: number;
    height: number;
    scroll_x: number;
    scroll_y: number;
  };
}

interface RightPanelProps {
  taskId: string | null;
  results: any[];
}

export default function RightPanel({ taskId, results }: RightPanelProps) {
  const [streamUrl, setStreamUrl] = useState<string | null>(null);
  const [highlightedPhones, setHighlightedPhones] = useState<Map<string, PhoneData>>(new Map());
  const streamContainerRef = useRef<HTMLDivElement>(null);
  const resultsTableRef = useRef<HTMLDivElement>(null);
  const [containerSize, setContainerSize] = useState({ width: 0, height: 0 });
  const [showOnlyNew, setShowOnlyNew] = useState(false);
  const [lastResultCount, setLastResultCount] = useState(0);
  const [resultRate, setResultRate] = useState(0);
  const [resultRateHistory, setResultRateHistory] = useState<number[]>([]);

  useEffect(() => {
    if (taskId) {
      // MJPEG stream URL
      setStreamUrl(`http://localhost:8000/live_feed/${taskId}`);
    } else {
      setStreamUrl(null);
    }
  }, [taskId]);

  // Update container size on resize
  useEffect(() => {
    const updateSize = () => {
      if (streamContainerRef.current) {
        setContainerSize({
          width: streamContainerRef.current.clientWidth,
          height: streamContainerRef.current.clientHeight,
        });
      }
    };

    updateSize();
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, []);

  // Extract all phones with coordinates from results
  useEffect(() => {
    const phonesMap = new Map<string, PhoneData>();
    
    results.forEach((result) => {
      if (result.phones && Array.isArray(result.phones)) {
        result.phones.forEach((phone: PhoneData) => {
          if (phone.phone_coordinates && phone.phone_element_selector) {
            // Use selector as key to avoid duplicates
            phonesMap.set(phone.phone_element_selector, phone);
          }
        });
      }
    });
    
    setHighlightedPhones(phonesMap);
  }, [results]);

  // Calculate result rate and auto-scroll
  useEffect(() => {
    const newCount = results.length;
    if (newCount > lastResultCount) {
      const delta = newCount - lastResultCount;
      const now = Date.now();
      
      // Update result rate (results per minute)
      setResultRateHistory(prev => {
        const updated = [...prev, now];
        // Keep only last 60 seconds
        const oneMinuteAgo = now - 60000;
        return updated.filter(timestamp => timestamp > oneMinuteAgo);
      });
      
      setResultRate(resultRateHistory.length);
      
      // Auto-scroll to bottom when new results arrive
      if (resultsTableRef.current && showOnlyNew === false) {
        resultsTableRef.current.scrollTop = resultsTableRef.current.scrollHeight;
      }
    }
    setLastResultCount(newCount);
  }, [results.length, lastResultCount, showOnlyNew, resultRateHistory.length]);

  // Filter results for "Show Only New"
  const displayedResults = showOnlyNew 
    ? results.slice(lastResultCount)
    : results;

  const handlePhoneClick = (phone: PhoneData) => {
    // Toggle highlight for this phone
    const newMap = new Map(highlightedPhones);
    if (newMap.has(phone.phone_element_selector || '')) {
      newMap.delete(phone.phone_element_selector || '');
    } else if (phone.phone_coordinates && phone.phone_element_selector) {
      newMap.set(phone.phone_element_selector, phone);
    }
    setHighlightedPhones(newMap);
  };

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Live Browser View with Phone Highlighting */}
      <div className="flex-1 relative glass-subtle rounded-lg overflow-hidden" ref={streamContainerRef}>
        {streamUrl ? (
          <>
            <img
              src={streamUrl}
              alt="Live browser stream"
              className="w-full h-full object-contain"
              style={{ imageRendering: 'pixelated' }}
            />
            {/* Phone Highlighting Overlays */}
            {containerSize.width > 0 && containerSize.height > 0 && (
              <div className="absolute inset-0 pointer-events-none">
                {Array.from(highlightedPhones.values()).map((phone, idx) => {
                  if (!phone.phone_coordinates) return null;
                  
                  return (
                    <PhoneOverlay
                      key={phone.phone_element_selector || idx}
                      coordinates={phone.phone_coordinates}
                      phoneNumber={phone.normalized_e164 || phone.raw_phone}
                      source={phone.phone_source}
                      confidence={phone.confidence_score}
                      onClick={() => handlePhoneClick(phone)}
                      containerWidth={containerSize.width}
                      containerHeight={containerSize.height}
                    />
                  );
                })}
              </div>
            )}
          </>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400 dark:text-gray-500">
            No active stream
          </div>
        )}
      </div>

      {/* Results Table with Controls */}
      <div className="glass-strong rounded-lg mt-4 overflow-hidden">
        {/* Controls Bar */}
        <div className="flex items-center justify-between px-4 py-3 glass-subtle border-b border-white/10">
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm glass-subtle px-3 py-1 rounded-lg cursor-pointer hover:glass transition-all">
              <input
                type="checkbox"
                checked={showOnlyNew}
                onChange={(e) => setShowOnlyNew(e.target.checked)}
                className="w-4 h-4 rounded accent-primary"
              />
              <span>Show Only New</span>
            </label>
            <div className="text-sm glass-subtle px-3 py-1 rounded-lg">
              Results: <span className="font-semibold text-gradient-primary">{results.length}</span> | Rate: <span className="font-semibold">{resultRate}/min</span>
            </div>
          </div>
          <div className="text-xs glass-subtle px-3 py-1 rounded-lg">
            {displayedResults.length} displayed
          </div>
        </div>
        
        {/* Results Table with Virtual Scrolling */}
        <div ref={resultsTableRef} className="h-64">
          <VirtualizedResultsTable
            results={displayedResults}
            onPhoneClick={handlePhoneClick}
            height={256} // h-64 = 256px
          />
        </div>
      </div>
    </div>
  );
}

