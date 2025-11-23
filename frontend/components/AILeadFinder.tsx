import { useState } from 'react';
import GlassCard from './ui/GlassCard';
import GlassButton from './ui/GlassButton';
import GlassInput from './ui/GlassInput';
import LoadingSkeleton from './LoadingSkeleton';

interface AIGeneratedConfig {
  queries: string[];
  platforms: string[];
  filters: {
    business_type?: string[];
    location?: string;
    [key: string]: any;
  };
  expected_results: 'high' | 'medium' | 'low';
  confidence: number;
  reasoning: string;
}

interface AILeadFinderProps {
  onApplyConfig: (config: AIGeneratedConfig) => void;
}

export default function AILeadFinder({ onApplyConfig }: AILeadFinderProps) {
  const [input, setInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedConfig, setGeneratedConfig] = useState<AIGeneratedConfig | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!input.trim()) {
      setError('Please enter a search request');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setGeneratedConfig(null);

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/ai/generate-search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: input }),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate search: ${response.statusText}`);
      }

      const config = await response.json();
      setGeneratedConfig(config);
    } catch (err: any) {
      setError(err.message || 'Failed to generate search configuration');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <GlassCard>
      <h2 className="font-semibold mb-4 text-lg text-gradient-primary">AI Lead Finder</h2>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Describe what you're looking for in natural language, and AI will generate the optimal search configuration.
      </p>

      <div className="space-y-3">
        <GlassInput
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g., Find me 500 Shopify stores in Canada doing paid ads"
          className="w-full"
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !isGenerating) {
              handleGenerate();
            }
          }}
        />

        <GlassButton
          onClick={handleGenerate}
          disabled={isGenerating || !input.trim()}
          variant="primary"
          gradient
          className="w-full"
        >
          {isGenerating ? (
            <>
              <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Generating...
            </>
          ) : (
            'Generate Search Configuration'
          )}
        </GlassButton>

        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-sm text-red-600 dark:text-red-400">
            {error}
          </div>
        )}

        {generatedConfig && (
          <div className="mt-4 space-y-3">
            <div className="p-4 glass-subtle rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold">Generated Configuration</span>
                <span className="text-xs text-gray-500">
                  Confidence: {generatedConfig.confidence}%
                </span>
              </div>
              
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                {generatedConfig.reasoning}
              </div>

              <div className="mb-2">
                <strong className="text-xs">Queries:</strong>
                <ul className="list-disc list-inside text-xs mt-1">
                  {generatedConfig.queries.map((q, idx) => (
                    <li key={idx}>{q}</li>
                  ))}
                </ul>
              </div>

              <div className="mb-2">
                <strong className="text-xs">Platforms:</strong>
                <span className="text-xs ml-2">
                  {generatedConfig.platforms.join(', ')}
                </span>
              </div>

              <div className="mb-2">
                <strong className="text-xs">Expected Results:</strong>
                <span className={`text-xs ml-2 ${
                  generatedConfig.expected_results === 'high' ? 'text-green-600' :
                  generatedConfig.expected_results === 'medium' ? 'text-yellow-600' :
                  'text-red-600'
                }`}>
                  {generatedConfig.expected_results.toUpperCase()}
                </span>
              </div>

              <GlassButton
                onClick={() => onApplyConfig(generatedConfig)}
                variant="success"
                gradient
                className="w-full mt-3"
                size="sm"
              >
                Apply Configuration
              </GlassButton>
            </div>
          </div>
        )}
      </div>
    </GlassCard>
  );
}

