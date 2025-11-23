import React, { useMemo } from 'react';
import { FixedSizeList as List } from 'react-window';
import { formatPhone, getConfidenceColor, getConfidenceLabel, copyToClipboard } from '../utils/phone';

interface VirtualizedResultsTableProps {
  results: any[];
  onPhoneClick: (phone: any) => void;
  height?: number;
}

interface RowProps {
  index: number;
  style: React.CSSProperties;
  data: {
    results: any[];
    onPhoneClick: (phone: any) => void;
  };
}

const Row = ({ index, style, data }: RowProps) => {
  const result = data.results[index];
  if (!result) return null;

  const phones: any[] = result.phones || [];
  const primaryPhone = phones.length > 0 ? phones[0] : null;

  const handlePhoneClick = (phone: any) => {
    if (data.onPhoneClick) {
      data.onPhoneClick(phone);
    }
  };

  const handleCopyPhone = async (phone: string) => {
    try {
      await copyToClipboard(phone);
    } catch (error) {
      console.error('Failed to copy phone:', error);
    }
  };

  // Lead score for rows without phones too
  const leadScore = result.lead_score;
  const leadScoreCategory = result.lead_score_category || (leadScore >= 80 ? 'hot' : leadScore >= 50 ? 'warm' : 'low');
  const getLeadScoreEmoji = (category: string) => {
    if (category === 'hot') return '🔥';
    if (category === 'warm') return '🟡';
    return '⚪';
  };
  const getLeadScoreColor = (category: string) => {
    if (category === 'hot') return 'text-red-600 dark:text-red-400';
    if (category === 'warm') return 'text-yellow-600 dark:text-yellow-400';
    return 'text-gray-500 dark:text-gray-400';
  };

  if (!primaryPhone) {
    return (
      <div style={style} className="grid grid-cols-5 gap-2 px-2 py-2 border-b border-white/5 hover:glass-subtle">
        <div className="text-sm flex items-center gap-2">
          {result.display_name || 'N/A'}
          {leadScore !== undefined && (
            <span className={`text-xs font-semibold ${getLeadScoreColor(leadScoreCategory)}`} title={`Lead Score: ${leadScore}/100`}>
              {getLeadScoreEmoji(leadScoreCategory)} {leadScore}
            </span>
          )}
        </div>
        <div className="text-sm text-gray-400">No phone found</div>
        <div className="text-sm">{result.field_of_study || 'N/A'}</div>
        <div className="text-sm">{result.platform || 'N/A'}</div>
        <div className="text-sm text-gray-500 dark:text-gray-400">{result.location || result.city || 'N/A'}</div>
      </div>
    );
  }

  const confidenceColor = getConfidenceColor(primaryPhone.confidence_score);
  const confidenceLabel = getConfidenceLabel(primaryPhone.confidence_score);
  const displayPhone = primaryPhone.normalized_e164 || primaryPhone.raw_phone;

  return (
    <div style={style} className="grid grid-cols-5 gap-2 px-2 py-2 border-b border-white/5 hover:glass-subtle cursor-pointer">
      <div className="text-sm flex items-center gap-2">
        {result.display_name || 'N/A'}
        {leadScore !== undefined && (
          <span className={`text-xs font-semibold ${getLeadScoreColor(leadScoreCategory)}`} title={`Lead Score: ${leadScore}/100`}>
            {getLeadScoreEmoji(leadScoreCategory)} {leadScore}
          </span>
        )}
      </div>
      <div className="text-sm flex items-center gap-2">
        <button
          onClick={() => handlePhoneClick(primaryPhone)}
          className="text-blue-600 hover:text-blue-800 underline"
        >
          {formatPhone(displayPhone)}
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleCopyPhone(displayPhone);
          }}
          className="text-gray-400 hover:text-gray-600"
          title="Copy phone number"
        >
          📋
        </button>
        <span
          className={`px-1.5 py-0.5 text-xs rounded ${
            confidenceColor === 'green'
              ? 'bg-green-100 text-green-800'
              : confidenceColor === 'yellow'
              ? 'bg-yellow-100 text-yellow-800'
              : 'bg-red-100 text-red-800'
          }`}
          title={`Confidence: ${primaryPhone.confidence_score}%`}
        >
          {confidenceLabel}
        </span>
        {phones.length > 1 && (
          <span className="px-1.5 py-0.5 text-xs rounded bg-blue-100 text-blue-800">
            +{phones.length - 1}
          </span>
        )}
      </div>
      <div className="text-sm flex items-center">{result.field_of_study || 'N/A'}</div>
      <div className="text-sm flex items-center">{result.platform || 'N/A'}</div>
      <div className="text-sm flex items-center text-gray-500 dark:text-gray-400">{result.location || result.city || 'N/A'}</div>
    </div>
  );
};

export default function VirtualizedResultsTable({
  results,
  onPhoneClick,
  height = 400,
}: VirtualizedResultsTableProps) {
  const itemData = useMemo(
    () => ({ results, onPhoneClick }),
    [results, onPhoneClick]
  );

  if (results.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
        No results yet
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* Table Header */}
      <div className="glass-subtle sticky top-0 z-10 grid grid-cols-5 gap-2 px-2 py-2 text-sm font-semibold border-b border-white/10">
        <div className="text-left">Name / Score</div>
        <div className="text-left">Phone</div>
        <div className="text-left">Field of Study</div>
        <div className="text-left">Platform</div>
        <div className="text-left">Location</div>
      </div>
      
      {/* Virtualized List */}
      <List
        height={height}
        itemCount={results.length}
        itemSize={60} // Estimated row height
        itemData={itemData}
        width="100%"
        className="virtualized-list"
      >
        {Row}
      </List>
    </div>
  );
}

