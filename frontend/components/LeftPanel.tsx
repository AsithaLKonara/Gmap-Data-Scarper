import { useState, useEffect } from 'react';
import { startScraper, stopScraper, getTaskStatus, getPlatforms, getUsageStats, getLeadObjectives, UserPlan, LeadObjective } from '../utils/api';
import {
  optimizeQueriesAdvanced,
  extractLocationFromQuery,
  extractFieldFromQuery,
  extractContextFromQuery,
  validateQuery,
  scoreQuery,
  type QueryContext,
  type OptimizedQuery,
  type QueryIntent,
  queryLearning,
} from '../utils/queryOptimizer';
import GlassCard from './ui/GlassCard';
import GlassButton from './ui/GlassButton';
import GlassInput from './ui/GlassInput';
import ErrorDisplay from './ErrorDisplay';
import LoadingSkeleton from './LoadingSkeleton';
import TaskList from './TaskList';
import PushNotificationService from './PushNotificationService';
import UpgradeModal from './UpgradeModal';
import AILeadFinder from './AILeadFinder';
import SearchTemplates from './SearchTemplates';

// Loading spinner component
function Spinner() {
  return (
    <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
  );
}

interface LeftPanelProps {
  onStart: (taskId: string) => void;
  onStop: () => void;
  taskId: string | null;
  progress: Record<string, number>;
  totalResults: number;
}

export default function LeftPanel({
  onStart,
  onStop,
  taskId,
  progress,
  totalResults,
}: LeftPanelProps) {
  const [queries, setQueries] = useState<string[]>(['']);
  const [platforms, setPlatforms] = useState<string[]>(['google_maps']);
  const [availablePlatforms, setAvailablePlatforms] = useState<string[]>([]);
  const [leadObjective, setLeadObjective] = useState<string>('');
  const [leadObjectives, setLeadObjectives] = useState<LeadObjective[]>([]);
  const [fieldOfStudy, setFieldOfStudy] = useState('');
  const [studentOnly, setStudentOnly] = useState(false);
  const [phoneOnly, setPhoneOnly] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState<'csv' | 'json' | 'excel'>('csv');
  const [error, setError] = useState<string | null>(null);
  const [usageStats, setUsageStats] = useState<UserPlan['usage'] | null>(null);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  
  // Query optimization states
  const [optimizeQueriesEnabled, setOptimizeQueriesEnabled] = useState(true);
  const [optimizedQueries, setOptimizedQueries] = useState<string[]>([]);
  const [showOptimizedQueries, setShowOptimizedQueries] = useState(false);
  const [optimizationResults, setOptimizationResults] = useState<{
    queries: OptimizedQuery[];
    intent: QueryIntent;
    analytics: {
      totalGenerated: number;
      afterDeduplication: number;
      afterScoring: number;
      avgQualityScore: number;
    };
  } | null>(null);
  const [queryValidation, setQueryValidation] = useState<{
    isValid: boolean;
    issues: string[];
    suggestions: string[];
    estimatedResults: 'high' | 'medium' | 'low';
  } | null>(null);
  const [generatedConfig, setGeneratedConfig] = useState<any>(null);

  useEffect(() => {
    getPlatforms()
      .then((platforms) => {
        // Ensure we always set an array
        setAvailablePlatforms(Array.isArray(platforms) ? platforms : []);
      })
      .catch(err => {
        console.error('Failed to load platforms:', err);
        setError('Failed to load platforms');
        setAvailablePlatforms([]); // Set empty array on error
      });
    
    getLeadObjectives()
      .then((objectives) => {
        // Ensure we always set an array
        setLeadObjectives(Array.isArray(objectives) ? objectives : []);
      })
      .catch(err => {
        console.error('Failed to load lead objectives:', err);
        setLeadObjectives([]); // Set empty array on error
      });
    
    // Load usage stats
    getUsageStats()
      .then(setUsageStats)
      .catch(err => {
        console.error('Failed to load usage stats:', err);
      });
  }, []);
  
  // Refresh usage stats periodically
  useEffect(() => {
    const interval = setInterval(() => {
      getUsageStats()
        .then(setUsageStats)
        .catch(() => {});
    }, 30000); // Every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  // Query optimization effect
  useEffect(() => {
    if (optimizeQueriesEnabled && queries.length > 0 && queries[0].trim()) {
      const baseQuery = queries[0].trim();
      
      // Extract context from query
      const extractedContext = extractContextFromQuery(baseQuery);
      const context: QueryContext = {
        location: extractedContext.location || undefined,
        fieldOfStudy: fieldOfStudy || extractedContext.fieldOfStudy || undefined,
        studentOnly: studentOnly || extractedContext.studentOnly || false,
      };
      
      // Validate query
      const validation = validateQuery(baseQuery, context);
      setQueryValidation(validation);
      
      // Optimize queries
      try {
        const result = optimizeQueriesAdvanced(
          [baseQuery],
          context,
          platforms,
          {
            enableLearning: true,
            enablePlatformOptimization: true,
            maxQueries: 15,
            minQualityScore: 50
          }
        );
        
        setOptimizationResults(result);
        setOptimizedQueries(result.queries.map(q => q.query));
      } catch (err) {
        console.error('Query optimization failed:', err);
      }
    } else {
      setOptimizationResults(null);
      setOptimizedQueries([]);
      setQueryValidation(null);
    }
  }, [queries, fieldOfStudy, studentOnly, platforms, optimizeQueriesEnabled]);

  const handleStart = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Use optimized queries if enabled, otherwise use original
      const queriesToUse = optimizeQueriesEnabled && optimizedQueries.length > 0
        ? optimizedQueries
        : queries.filter(q => q.trim());
      
      const response = await startScraper({
        queries: queriesToUse,
        platforms,
        lead_objective: leadObjective || undefined,
        field_of_study: fieldOfStudy || undefined,
        student_only: studentOnly || undefined,
        phone_only: phoneOnly || undefined,
      });
      onStart(response.task_id);
      
      // Update usage stats from response if available
      if (response.usage) {
        setUsageStats({
          plan_type: usageStats?.plan_type || 'free',
          daily_limit: response.usage.limit,
          used_today: response.usage.used,
          remaining_today: response.usage.remaining,
          is_unlimited: false,
        });
      } else {
        // Refresh usage stats
        getUsageStats().then(setUsageStats).catch(() => {});
      }
      
      // Record query analytics (will be updated when results come in)
      if (optimizeQueriesEnabled && optimizedQueries.length > 0) {
        // We'll update this when we get results count
        optimizedQueries.forEach(query => {
          queryLearning.recordQuery(query, 0, platforms);
        });
      }
    } catch (error: any) {
      console.error('Failed to start scraper:', error);
      const errorMessage = error.message || 'Failed to start scraper';
      setError(errorMessage);
      
      // Check if it's a limit exceeded error
      if (errorMessage.includes('limit exceeded') || errorMessage.includes('Daily lead limit')) {
        setShowUpgradeModal(true);
        // Refresh usage stats to show current limit
        getUsageStats().then(setUsageStats).catch(() => {});
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleStop = async () => {
    if (taskId) {
      try {
        await stopScraper(taskId);
        onStop();
      } catch (error) {
        console.error('Failed to stop scraper:', error);
      }
    }
  };

  const [showTaskList, setShowTaskList] = useState(false);

  return (
    <div className="p-6 space-y-5 bg-transparent">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gradient-primary mb-1">Lead Intelligence</h1>
          <p className="text-xs text-gray-400">Configure & Start</p>
        </div>
        <GlassButton
          size="sm"
          variant="secondary"
          onClick={() => setShowTaskList(!showTaskList)}
          className="text-xs"
        >
          {showTaskList ? 'Hide' : 'Show'} Tasks
        </GlassButton>
      </div>

      {/* Usage Display */}
      {usageStats && (
        <GlassCard className="border-blue-500/30 bg-blue-500/10">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-sm mb-1">Daily Usage</h3>
              {usageStats.is_unlimited ? (
                <p className="text-sm text-green-600 dark:text-green-400">Unlimited leads</p>
              ) : (
                <p className="text-sm">
                  <span className={usageStats.remaining_today === 0 ? 'text-red-600 dark:text-red-400 font-bold' : 'text-gray-700 dark:text-gray-300'}>
                    {usageStats.used_today}/{usageStats.daily_limit}
                  </span>
                  {' '}leads used today
                  {usageStats.remaining_today !== null && (
                    <span className="text-gray-600 dark:text-gray-400">
                      {' '}({usageStats.remaining_today} remaining)
                    </span>
                  )}
                </p>
              )}
            </div>
            {!usageStats.is_unlimited && usageStats.remaining_today !== null && usageStats.remaining_today <= 2 && (
              <GlassButton
                size="sm"
                variant="primary"
                gradient
                onClick={() => setShowUpgradeModal(true)}
              >
                Upgrade
              </GlassButton>
            )}
          </div>
        </GlassCard>
      )}

      {/* Task List Section */}
      {showTaskList && (
        <div className="mb-4">
          <TaskList />
        </div>
      )}

      {/* Push Notifications Section */}
      <PushNotificationService />

      {/* Upgrade Modal */}
      {showUpgradeModal && (
        <UpgradeModal
          onClose={() => setShowUpgradeModal(false)}
          onUpgrade={() => {
            setShowUpgradeModal(false);
            // Refresh usage stats after upgrade
            getUsageStats().then(setUsageStats).catch(() => {});
          }}
        />
      )}

      {/* Search Templates */}
      <SearchTemplates
        onSelectTemplate={(template) => {
          // Apply template configuration
          if (template.queries) {
            setQueries(template.queries);
          }
          if (template.platforms) {
            setPlatforms(template.platforms);
          }
          if (template.lead_objective) {
            setLeadObjective(template.lead_objective);
          }
        }}
      />

      {/* AI Lead Finder */}
      <AILeadFinder
        onApplyConfig={(config) => {
          // Apply generated configuration
          setQueries(config.queries);
          setPlatforms(config.platforms);
          if (config.filters.location) {
            // Note: location filter would need to be added to state if not already present
          }
          setGeneratedConfig(config);
        }}
      />

      {/* Lead Objective */}
      <GlassCard>
        <h2 className="font-semibold mb-4 text-lg">Lead Objective</h2>
        <select
          value={leadObjective}
          onChange={(e) => {
            setLeadObjective(e.target.value);
          }}
          className="input-glass w-full text-sm mb-2"
        >
          <option value="">Select lead objective (optional)</option>
          {Array.isArray(leadObjectives) && leadObjectives.map((obj) => (
            <option key={obj.value} value={obj.value}>
              {obj.label}
            </option>
          ))}
        </select>
        {leadObjective && (
          <p className="text-xs text-gray-500 mt-1">
            Filters and platforms will be auto-configured based on your selection
          </p>
        )}
      </GlassCard>

      {/* Search Queries */}
      <GlassCard>
        <h2 className="font-semibold mb-4 text-lg">Search Queries</h2>
        <div className="space-y-3">
          {queries.map((query, idx) => (
            <div key={idx} className="flex gap-2">
              <GlassInput
                type="text"
                value={query}
                onChange={(e) => {
                  const newQueries = [...queries];
                  newQueries[idx] = e.target.value;
                  setQueries(newQueries);
                }}
                placeholder="e.g., ICT students in Toronto"
                className="flex-1"
              />
              {queries.length > 1 && (
                <GlassButton
                  variant="error"
                  size="sm"
                  onClick={() => setQueries(queries.filter((_, i) => i !== idx))}
                  className="px-3"
                >
                  ×
                </GlassButton>
              )}
            </div>
          ))}
          <GlassButton
            variant="secondary"
            size="sm"
            onClick={() => setQueries([...queries, ''])}
            className="w-full"
          >
            + Add Query
          </GlassButton>
        </div>
      </GlassCard>

      {/* Platform Selection */}
      <GlassCard>
        <h2 className="font-semibold mb-4 text-lg">Platforms</h2>
        <div className="space-y-2">
          {Array.isArray(availablePlatforms) && availablePlatforms.map((platform) => (
            <label key={platform} className="flex items-center gap-3 p-2 glass-subtle rounded-lg hover:glass cursor-pointer transition-all">
              <input
                type="checkbox"
                checked={platforms.includes(platform)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setPlatforms([...platforms, platform]);
                  } else {
                    setPlatforms(platforms.filter(p => p !== platform));
                  }
                }}
                className="w-4 h-4 rounded accent-primary"
              />
              <span className="capitalize flex-1">{platform.replace('_', ' ')}</span>
            </label>
          ))}
        </div>
      </GlassCard>

      {/* Education/Career Filters */}
      <GlassCard>
        <h2 className="font-semibold mb-4 text-lg">Education/Career Filters</h2>
        <GlassInput
          type="text"
          value={fieldOfStudy}
          onChange={(e) => setFieldOfStudy(e.target.value)}
          placeholder="Field of Study (e.g., ICT, Computer Science)"
          className="mb-4"
        />
        <div className="space-y-3">
          <label className="flex items-center gap-3 p-2 glass-subtle rounded-lg hover:glass cursor-pointer transition-all">
            <input
              type="checkbox"
              checked={studentOnly}
              onChange={(e) => setStudentOnly(e.target.checked)}
              className="w-4 h-4 rounded accent-primary"
            />
            <span>Students Only</span>
          </label>
          <label className="flex items-center gap-3 p-2 glass-subtle rounded-lg hover:glass cursor-pointer transition-all">
            <input
              type="checkbox"
              checked={phoneOnly}
              onChange={(e) => setPhoneOnly(e.target.checked)}
              className="w-4 h-4 rounded accent-primary"
            />
            <span>Only Leads with Phone Numbers</span>
          </label>
        </div>
      </GlassCard>

      {/* Query Optimization Section */}
      <GlassCard>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-lg">Query Optimization</h2>
          <label className="flex items-center gap-2 text-sm glass-subtle px-3 py-1 rounded-lg cursor-pointer hover:glass transition-all">
            <input
              type="checkbox"
              checked={optimizeQueriesEnabled}
              onChange={(e) => setOptimizeQueriesEnabled(e.target.checked)}
              className="w-4 h-4 rounded accent-primary"
            />
            <span>Enable</span>
          </label>
        </div>
        
        {optimizeQueriesEnabled && queries[0]?.trim() && (
          <>
            {/* Query Validation */}
            {queryValidation && (
              <GlassCard className={`mb-4 text-xs ${
                queryValidation.isValid
                  ? 'border-success/30 bg-success/10'
                  : 'border-warning/30 bg-warning/10'
              }`}>
                <div className="font-semibold mb-1">
                  Query Quality: {queryValidation.estimatedResults.toUpperCase()}
                </div>
                {queryValidation.issues.length > 0 && (
                  <div className="mb-1">
                    <strong>Issues:</strong>
                    <ul className="list-disc list-inside ml-2">
                      {queryValidation.issues.map((issue, idx) => (
                        <li key={idx}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {queryValidation.suggestions.length > 0 && (
                  <div>
                    <strong>Suggestions:</strong>
                    <ul className="list-disc list-inside ml-2">
                      {queryValidation.suggestions.map((suggestion, idx) => (
                        <li key={idx}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </GlassCard>
            )}

            {/* Optimization Results */}
            {optimizationResults && (
              <GlassCard className="mb-4 border-primary/30 bg-primary/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-blue-800">
                    Optimization Insights
                  </span>
                  <span className="text-xs text-blue-600">
                    Avg Quality: {optimizationResults.analytics.avgQualityScore}/100
                  </span>
                </div>
                
                <div className="text-xs text-blue-700 mb-2 space-y-1">
                  <div>
                    <strong>Intent:</strong> {optimizationResults.intent.type.replace('_', ' ')} 
                    ({optimizationResults.intent.confidence}% confidence)
                  </div>
                  <div>
                    <strong>Generated:</strong> {optimizationResults.analytics.totalGenerated} queries → 
                    {optimizationResults.analytics.afterScoring} high-quality
                  </div>
                  {optimizationResults.intent.entities.location && (
                    <div>
                      <strong>Location:</strong> {optimizationResults.intent.entities.location}
                    </div>
                  )}
                  {optimizationResults.intent.entities.field && (
                    <div>
                      <strong>Field:</strong> {optimizationResults.intent.entities.field}
                    </div>
                  )}
                </div>
                
                <GlassButton
                  size="sm"
                  variant="secondary"
                  onClick={() => setShowOptimizedQueries(!showOptimizedQueries)}
                  className="text-xs w-full"
                >
                  {showOptimizedQueries ? 'Hide' : 'Show'} Optimized Queries ({optimizedQueries.length})
                </GlassButton>
                
                {showOptimizedQueries && (
                  <div className="mt-2 space-y-1 max-h-40 overflow-y-auto glass-subtle p-2 rounded-lg">
                    {optimizationResults.queries.slice(0, 10).map((q, idx) => {
                      const context: QueryContext = {
                        location: extractLocationFromQuery(queries[0]) || undefined,
                        fieldOfStudy: fieldOfStudy || undefined,
                        studentOnly: studentOnly,
                      };
                      const score = scoreQuery(q.query, context, platforms);
                      
                      return (
                        <div key={idx} className="flex items-start justify-between text-xs py-1 border-b border-gray-100 last:border-0">
                          <span className="flex-1 truncate mr-2" title={q.query}>
                            {idx + 1}. {q.query}
                          </span>
                          <div className="flex items-center gap-2 flex-shrink-0">
                            <span className="text-gray-500" title="Quality Score">Q:{score.score}</span>
                            <span className="text-gray-400" title="Priority">P:{q.priority}</span>
                          </div>
                        </div>
                      );
                    })}
                    {optimizationResults.queries.length > 10 && (
                      <div className="text-xs text-gray-500 text-center pt-1">
                        ... and {optimizationResults.queries.length - 10} more
                      </div>
                    )}
                  </div>
                )}
              </GlassCard>
            )}
          </>
        )}
      </GlassCard>

      {/* Error Display */}
      {error && (
        <ErrorDisplay
          error={error}
          onDismiss={() => setError(null)}
          variant="error"
        />
      )}

      {/* Execution Controls */}
      <GlassCard>
        <h2 className="font-semibold mb-4 text-lg">Controls</h2>
        {!taskId ? (
          <GlassButton
            onClick={handleStart}
            disabled={isLoading || queries.filter(q => q.trim()).length === 0}
            variant="primary"
            gradient
            className="w-full"
          >
            {isLoading ? <><Spinner /> Starting...</> : 'Start Scraping'}
          </GlassButton>
        ) : (
          <GlassButton
            onClick={handleStop}
            variant="error"
            gradient
            className="w-full"
          >
            Stop Scraping
          </GlassButton>
        )}
      </GlassCard>

      {/* Results Summary */}
      <GlassCard>
        <h2 className="font-semibold mb-4 text-lg">Results</h2>
        <div className="text-sm space-y-2">
          <div className="glass-subtle p-3 rounded-lg">
            <div className="font-semibold text-lg text-gradient-primary">Total Leads: {totalResults}</div>
          </div>
          {Object.entries(progress).map(([platform, count]) => (
            <div key={platform} className="glass-subtle p-2 rounded-lg flex justify-between">
              <span className="capitalize">{platform.replace('_', ' ')}:</span>
              <span className="font-semibold">{count}</span>
            </div>
          ))}
        </div>
      </GlassCard>

      {/* Export Section */}
      <GlassCard>
        <h2 className="font-semibold mb-4 text-lg">Export</h2>
        <div className="mb-4">
          <label className="block text-sm mb-2 font-medium">Format:</label>
          <select
            value={exportFormat}
            onChange={(e) => setExportFormat(e.target.value as 'csv' | 'json' | 'excel')}
            className="input-glass w-full text-sm"
          >
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
            <option value="excel">Excel (.xlsx)</option>
          </select>
        </div>
        {isExporting && (
          <div className="mb-4">
            <div className="glass-subtle rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Exporting...</span>
                <span className="text-sm text-gray-500">Processing</span>
              </div>
              <div className="w-full glass-subtle rounded-full h-2 overflow-hidden">
                <div className="h-full bg-gradient-primary rounded-full animate-pulse" style={{ width: '100%' }}></div>
              </div>
            </div>
          </div>
        )}
        <GlassButton
          onClick={async () => {
            setIsExporting(true);
            try {
              const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
              const format = exportFormat === 'excel' ? 'excel' : exportFormat;
              const params = new URLSearchParams();
              if (taskId) params.append('task_id', taskId);
              
              const response = await fetch(`${API_BASE_URL}/api/export/${format}?${params}`);
              if (!response.ok) throw new Error(`Export failed: ${response.statusText}`);
              
              const blob = await response.blob();
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              const ext = format === 'excel' ? 'xlsx' : format;
              a.download = `leads_export_${new Date().toISOString().split('T')[0]}.${ext}`;
              document.body.appendChild(a);
              a.click();
              document.body.removeChild(a);
              window.URL.revokeObjectURL(url);
            } catch (error: any) {
              console.error('Export failed:', error);
              setError(error.message || `Failed to export ${exportFormat.toUpperCase()}`);
            } finally {
              setIsExporting(false);
            }
          }}
          variant="success"
          gradient
          className="w-full"
          disabled={totalResults === 0 || isExporting}
        >
          {isExporting ? <><Spinner /> Exporting...</> : `Export ${exportFormat.toUpperCase()}`}
        </GlassButton>
      </GlassCard>
    </div>
  );
}

