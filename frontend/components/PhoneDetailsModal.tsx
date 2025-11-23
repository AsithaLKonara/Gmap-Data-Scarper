import { formatPhone, getConfidenceColor, getConfidenceLabel, copyToClipboard } from '../utils/phone';

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

interface PhoneDetailsModalProps {
  phone: PhoneData;
  allPhones: PhoneData[];
  result: any;
  onClose: () => void;
}

export default function PhoneDetailsModal({
  phone,
  allPhones,
  result,
  onClose,
}: PhoneDetailsModalProps) {
  const handleCopy = async (text: string) => {
    try {
      await copyToClipboard(text);
      // Could add toast notification here
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const confidenceColor = getConfidenceColor(phone.confidence_score);
  const confidenceLabel = getConfidenceLabel(phone.confidence_score);
  const displayPhone = phone.normalized_e164 || phone.raw_phone;

  const getSourceLabel = (source: string) => {
    const labels: Record<string, string> = {
      tel_link: 'Tel: Link',
      visible_text: 'Visible Text',
      jsonld: 'JSON-LD',
      ocr: 'OCR (Image)',
      website: 'Website Crawl',
    };
    return labels[source] || source;
  };

  const getValidationBadge = (status: string) => {
    const colors: Record<string, string> = {
      valid: 'bg-green-100 text-green-800',
      possible: 'bg-yellow-100 text-yellow-800',
      invalid: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-xl font-semibold">Phone Number Details</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Primary Phone Info */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-lg">Primary Phone</h3>
              <button
                onClick={() => handleCopy(displayPhone)}
                className="text-blue-600 hover:text-blue-800 text-sm"
              >
                Copy
              </button>
            </div>
            <div className="space-y-2">
              <div>
                <span className="text-sm text-gray-600">Raw:</span>
                <span className="ml-2 font-mono">{phone.raw_phone}</span>
              </div>
              {phone.normalized_e164 && (
                <div>
                  <span className="text-sm text-gray-600">Normalized (E.164):</span>
                  <span className="ml-2 font-mono">{phone.normalized_e164}</span>
                </div>
              )}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Validation:</span>
                <span
                  className={`px-2 py-1 text-xs rounded ${getValidationBadge(
                    phone.validation_status
                  )}`}
                >
                  {phone.validation_status}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Confidence:</span>
                <span
                  className={`px-2 py-1 text-xs rounded ${
                    confidenceColor === 'green'
                      ? 'bg-green-100 text-green-800'
                      : confidenceColor === 'yellow'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {confidenceLabel} ({phone.confidence_score}%)
                </span>
              </div>
              <div>
                <span className="text-sm text-gray-600">Source:</span>
                <span className="ml-2">{getSourceLabel(phone.phone_source)}</span>
              </div>
              {phone.phone_timestamp && (
                <div>
                  <span className="text-sm text-gray-600">Extracted:</span>
                  <span className="ml-2">
                    {new Date(phone.phone_timestamp).toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Source Details */}
          {phone.phone_element_selector && (
            <div>
              <h4 className="font-semibold mb-2">Element Selector</h4>
              <code className="bg-gray-100 p-2 rounded text-sm block">
                {phone.phone_element_selector}
              </code>
            </div>
          )}

          {phone.phone_screenshot_path && (
            <div>
              <h4 className="font-semibold mb-2">Screenshot</h4>
              <img
                src={`http://localhost:8000${phone.phone_screenshot_path}`}
                alt="Phone source screenshot"
                className="max-w-full h-auto border rounded"
              />
            </div>
          )}

          {/* Profile Info */}
          <div className="border-t pt-4">
            <h4 className="font-semibold mb-2">Profile Information</h4>
            <div className="space-y-1 text-sm">
              <div>
                <span className="text-gray-600">Name:</span>
                <span className="ml-2">{result.display_name || 'N/A'}</span>
              </div>
              <div>
                <span className="text-gray-600">Platform:</span>
                <span className="ml-2">{result.platform || 'N/A'}</span>
              </div>
              {result.profile_url && (
                <div>
                  <span className="text-gray-600">Profile URL:</span>
                  <a
                    href={result.profile_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-2 text-blue-600 hover:underline"
                  >
                    {result.profile_url}
                  </a>
                </div>
              )}
            </div>
          </div>

          {/* All Phones */}
          {allPhones.length > 1 && (
            <div className="border-t pt-4">
              <h4 className="font-semibold mb-2">All Phone Numbers ({allPhones.length})</h4>
              <div className="space-y-2">
                {allPhones.map((p, idx) => (
                  <div
                    key={idx}
                    className={`p-2 rounded ${
                      p === phone ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono">
                        {p.normalized_e164 || p.raw_phone}
                      </span>
                      <div className="flex items-center gap-2">
                        <span
                          className={`px-2 py-1 text-xs rounded ${getValidationBadge(
                            p.validation_status
                          )}`}
                        >
                          {p.validation_status}
                        </span>
                        <span className="text-xs text-gray-600">{p.phone_source}</span>
                        <button
                          onClick={() => handleCopy(p.normalized_e164 || p.raw_phone)}
                          className="text-blue-600 hover:text-blue-800 text-sm"
                        >
                          Copy
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Opt-Out Button */}
          {result.profile_url && (
            <div className="border-t pt-4">
              <button
                onClick={async () => {
                  try {
                    const { optOut } = await import('../utils/api');
                    await optOut(result.profile_url);
                    alert('Data removal request submitted successfully');
                    onClose();
                  } catch (error) {
                    console.error('Opt-out failed:', error);
                    alert('Failed to submit removal request. Please try again.');
                  }
                }}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Request Data Removal
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end p-4 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

