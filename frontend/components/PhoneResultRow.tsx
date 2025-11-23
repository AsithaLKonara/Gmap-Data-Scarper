import { useState } from 'react';
import { formatPhone, getConfidenceColor, getConfidenceLabel, copyToClipboard } from '../utils/phone';
import PhoneDetailsModal from './PhoneDetailsModal';

interface PhoneData {
  raw_phone: string;
  normalized_e164?: string;
  validation_status: string;
  confidence_score: number;
  phone_source: string;
  phone_element_selector?: string;
  phone_screenshot_path?: string;
  phone_timestamp?: string;
}

interface PhoneResultRowProps {
  result: any;
  onPhoneClick?: (phone: PhoneData) => void;
}

export default function PhoneResultRow({ result, onPhoneClick }: PhoneResultRowProps) {
  const [selectedPhone, setSelectedPhone] = useState<PhoneData | null>(null);
  const [showModal, setShowModal] = useState(false);

  const phones: PhoneData[] = result.phones || [];
  const primaryPhone = phones.length > 0 ? phones[0] : null;

  const handlePhoneClick = (phone: PhoneData) => {
    setSelectedPhone(phone);
    setShowModal(true);
    if (onPhoneClick) {
      onPhoneClick(phone);
    }
  };

  const handleCopyPhone = async (phone: string) => {
    try {
      await copyToClipboard(phone);
      // Could add toast notification here
    } catch (error) {
      console.error('Failed to copy phone:', error);
    }
  };

  if (!primaryPhone) {
    return (
      <tr className="border-b hover:bg-gray-50">
        <td className="px-2 py-1">{result.display_name || 'N/A'}</td>
        <td className="px-2 py-1 text-gray-400">No phone found</td>
        <td className="px-2 py-1">{result.field_of_study || 'N/A'}</td>
        <td className="px-2 py-1">{result.platform || 'N/A'}</td>
      </tr>
    );
  }

  const confidenceColor = getConfidenceColor(primaryPhone.confidence_score);
  const confidenceLabel = getConfidenceLabel(primaryPhone.confidence_score);
  const displayPhone = primaryPhone.normalized_e164 || primaryPhone.raw_phone;

  return (
    <>
      <tr className="border-b hover:bg-gray-50 cursor-pointer">
        <td className="px-2 py-1">{result.display_name || 'N/A'}</td>
        <td className="px-2 py-1">
          <div className="flex items-center gap-2">
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
            <span
              className="px-1.5 py-0.5 text-xs rounded bg-gray-100 text-gray-600"
              title={`Source: ${primaryPhone.phone_source}`}
            >
              {primaryPhone.phone_source}
            </span>
            {phones.length > 1 && (
              <span className="px-1.5 py-0.5 text-xs rounded bg-blue-100 text-blue-800">
                +{phones.length - 1}
              </span>
            )}
          </div>
        </td>
        <td className="px-2 py-1">{result.field_of_study || 'N/A'}</td>
        <td className="px-2 py-1">{result.platform || 'N/A'}</td>
      </tr>
      {showModal && selectedPhone && (
        <PhoneDetailsModal
          phone={selectedPhone}
          allPhones={phones}
          result={result}
          onClose={() => setShowModal(false)}
        />
      )}
    </>
  );
}

