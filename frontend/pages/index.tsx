import { useState, useEffect, lazy, Suspense } from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/router';
import LeftPanel from '../components/LeftPanel';
import LogConsole from '../components/LogConsole';
import ConsentNotice from '../components/ConsentNotice';
import ErrorBoundary from '../components/ErrorBoundary';
import { ToastContainer, showToast } from '../utils/toast';
import useWebSocket from '../hooks/useWebSocket';
import GradientBackground from '../components/ui/GradientBackground';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { useUser } from '../contexts/UserContext';
import ProfessionalDashboard from '../components/ProfessionalDashboard';

// Lazy load heavy components with SSR disabled
const RightPanel = lazy(() => import('../components/RightPanel'));

// Disable SSR for this page to avoid browser API issues
function Home() {
  const router = useRouter();
  const { user, loading: userLoading } = useUser();
  const [taskId, setTaskId] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [results, setResults] = useState<any[]>([]);
  const [progress, setProgress] = useState<Record<string, number>>({});
  const [consentGiven, setConsentGiven] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [viewMode, setViewMode] = useState<'dashboard' | 'browser'>('dashboard');

  // Only initialize WebSocket on client side
  useEffect(() => {
    setMounted(true);
  }, []);

  // Redirect to landing if not authenticated (disabled in development for testing)
  useEffect(() => {
    // Allow unauthenticated access in development mode
    const isDevelopment = process.env.NODE_ENV === 'development';
    if (mounted && !userLoading && !user && !isDevelopment) {
      router.push('/landing');
    }
  }, [mounted, userLoading, user, router]);

  // WebSocket connections for real-time updates (with batching for results)
  const apiBaseUrl = typeof window !== 'undefined' 
    ? (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
    : 'http://localhost:8000';
  const wsBaseUrl = apiBaseUrl.replace('http://', 'ws://').replace('https://', 'wss://');
  
  const logMessages = useWebSocket(
    mounted && taskId ? `${wsBaseUrl}/api/scraper/ws/logs/${taskId}` : null,
    { batch: false }
  );
  const progressUpdates = useWebSocket(
    mounted && taskId ? `${wsBaseUrl}/api/scraper/ws/progress/${taskId}` : null,
    { batch: false }
  );
  const resultUpdates = useWebSocket(
    mounted && taskId ? `${wsBaseUrl}/api/scraper/ws/results/${taskId}` : null,
    { batch: true, batchInterval: 100, maxBatchSize: 50 } // Batch results for performance
  );

  // Update logs from WebSocket
  useEffect(() => {
    if (logMessages) {
      try {
        const message = JSON.parse(logMessages);
        if (message.type === 'log' && message.message) {
          setLogs(prev => [...prev, message.message]);
        }
      } catch {
        // If not JSON, treat as plain text
        if (logMessages) {
          setLogs(prev => [...prev, logMessages]);
        }
      }
    }
  }, [logMessages]);

  // Update progress from WebSocket
  useEffect(() => {
    if (progressUpdates) {
      try {
        const update = JSON.parse(progressUpdates);
        if (update.type === 'progress' && update.progress) {
          setProgress(update.progress);
        }
      } catch {
        // Ignore parse errors
      }
    }
  }, [progressUpdates]);

  // Update results from WebSocket
  useEffect(() => {
    if (resultUpdates) {
      try {
        const result = JSON.parse(resultUpdates);
        if (result.type === 'result' && result.data) {
          setResults(prev => [...prev, result.data]);
          showToast('New result found', 'success', 2000);
        } else if (result.type === 'task_completed') {
          showToast('Task completed successfully', 'success', 5000);
        } else if (result.type === 'task_error') {
          showToast(`Task error: ${result.data?.error || 'Unknown error'}`, 'error', 5000);
        } else if (result.type === 'task_started') {
          showToast('Task started', 'info', 3000);
        }
      } catch {
        // Ignore parse errors
      }
    }
  }, [resultUpdates]);

  // Clear logs and results when task stops
  useEffect(() => {
    if (!taskId) {
      setLogs([]);
      setResults([]);
      setProgress({});
    }
  }, [taskId]);

  // Prevent hydration mismatch - wait for client-side mount
  if (!mounted || userLoading) {
    return <LoadingSkeleton />;
  }

  // Allow unauthenticated access in development mode
  const isDevelopment = process.env.NODE_ENV === 'development';
  if (!user && !isDevelopment) {
    return null; // Will redirect via useEffect
  }

  return (
    <ErrorBoundary>
      <GradientBackground variant="clean">
        <ConsentNotice onConsent={() => setConsentGiven(true)} />
        <ToastContainer />
        <div className="flex h-screen">
          {/* Left Panel - Controls */}
          <div className="w-80 overflow-y-auto border-r border-white/10">
            <div className="h-full glass-strong overflow-hidden">
              <LeftPanel
                onStart={(id) => {
                  setTaskId(id);
                  showToast('Scraping task started', 'success');
                }}
                onStop={() => {
                  setTaskId(null);
                  showToast('Scraping task stopped', 'info');
                }}
                taskId={taskId}
                progress={progress}
                totalResults={results.length}
              />
            </div>
          </div>

          {/* Main Content Area */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* View Mode Toggle */}
            {taskId && (
              <div className="flex items-center justify-between px-6 py-3 border-b border-white/10 glass-subtle">
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-2 glass-subtle px-3 py-1.5 rounded-lg">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium">Task Active</span>
                  </div>
                  <div className="text-sm text-gray-400">
                    {Object.entries(progress).map(([platform, count]) => (
                      <span key={platform} className="ml-3">
                        {platform}: <span className="font-semibold text-white">{count}</span>
                      </span>
                    ))}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setViewMode('dashboard')}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                      viewMode === 'dashboard'
                        ? 'glass-strong border border-primary/50 text-primary'
                        : 'glass-subtle border border-white/10 text-gray-400 hover:text-white'
                    }`}
                  >
                    📊 Dashboard
                  </button>
                  <button
                    onClick={() => setViewMode('browser')}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                      viewMode === 'browser'
                        ? 'glass-strong border border-primary/50 text-primary'
                        : 'glass-subtle border border-white/10 text-gray-400 hover:text-white'
                    }`}
                  >
                    🌐 Browser View
                  </button>
                </div>
              </div>
            )}

            {/* Content Area */}
            <div className="flex-1 overflow-hidden">
              {taskId ? (
                viewMode === 'dashboard' ? (
                  <ProfessionalDashboard
                    results={results}
                    progress={progress}
                    taskId={taskId}
                  />
                ) : (
                  <Suspense fallback={<LoadingSkeleton variant="card" className="h-full" />}>
                    <div className="h-full p-4">
                      <RightPanel taskId={taskId} results={results} />
                    </div>
                  </Suspense>
                )
              ) : (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center glass-strong p-12 rounded-2xl border border-white/10 max-w-md">
                    <div className="text-6xl mb-6">🚀</div>
                    <h2 className="text-2xl font-bold text-gradient-primary mb-3">
                      Welcome to Lead Intelligence Platform
                    </h2>
                    <p className="text-gray-400 mb-6">
                      Configure your search parameters on the left and start collecting leads
                    </p>
                    <div className="flex flex-col gap-2 text-sm text-gray-500">
                      <div className="flex items-center gap-2">
                        <span>✓</span>
                        <span>AI-powered lead scoring</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span>✓</span>
                        <span>Multi-platform scraping</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span>✓</span>
                        <span>Real-time results</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Log Console - Always visible at bottom */}
            {taskId && (
              <div className="border-t border-white/10">
                <LogConsole logs={logs} />
              </div>
            )}
          </div>
        </div>
      </GradientBackground>
    </ErrorBoundary>
  );
}

// Export with dynamic to disable SSR - this prevents server-side rendering issues
const DynamicHome = dynamic(() => Promise.resolve(Home), { 
  ssr: false,
  loading: () => <LoadingSkeleton />
});

export default DynamicHome;

