import { useState, useEffect } from 'react';
import GlassCard from '../ui/GlassCard';

interface PipelineStage {
  name: string;
  count: number;
  percentage: number;
}

interface PipelineData {
  stages: PipelineStage[];
  conversion_rates: {
    contact_rate: number;
    verification_rate: number;
    quality_rate: number;
    hot_rate: number;
  };
}

export default function PipelineVisualization() {
  const [pipeline, setPipeline] = useState<PipelineData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadPipeline();
  }, []);

  const loadPipeline = async () => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/analytics/pipeline`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setPipeline(data);
      }
    } catch (err) {
      console.error('Failed to load pipeline:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="text-center text-gray-500">Loading pipeline...</div>;
  }

  if (!pipeline) {
    return <div className="text-center text-gray-500">No pipeline data available</div>;
  }

  return (
    <GlassCard>
      <h2 className="text-xl font-semibold mb-6">Lead Pipeline Funnel</h2>
      
      {/* Funnel Visualization */}
      <div className="space-y-4">
        {pipeline.stages.map((stage, idx) => {
          const width = 100 - (idx * 10); // Decreasing width for funnel effect
          return (
            <div key={idx} className="relative">
              <div className="flex items-center gap-4 mb-2">
                <div className="w-40 text-sm font-medium">{stage.name}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <div
                      className="bg-gradient-primary rounded-lg h-8 flex items-center justify-end pr-4 transition-all"
                      style={{ width: `${width}%` }}
                    >
                      <span className="text-white text-sm font-semibold">
                        {stage.count.toLocaleString()}
                      </span>
                    </div>
                    <div className="w-20 text-right text-sm font-semibold">
                      {stage.percentage.toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Conversion rate indicator */}
              {idx > 0 && (
                <div className="text-xs text-gray-500 ml-44">
                  ↓ {((stage.count / pipeline.stages[idx - 1].count) * 100).toFixed(1)}% conversion
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Conversion Rates Summary */}
      <div className="mt-8 pt-6 border-t border-white/10">
        <h3 className="text-lg font-semibold mb-4">Conversion Rates</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-500">
              {pipeline.conversion_rates.contact_rate.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500 mt-1">Contact Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-500">
              {pipeline.conversion_rates.verification_rate.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500 mt-1">Verification Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-500">
              {pipeline.conversion_rates.quality_rate.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500 mt-1">Quality Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-500">
              {pipeline.conversion_rates.hot_rate.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500 mt-1">Hot Lead Rate</div>
          </div>
        </div>
      </div>
    </GlassCard>
  );
}

