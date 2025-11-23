import { useState, useEffect } from 'react';

interface ConsentNoticeProps {
  onConsent: () => void;
}

export default function ConsentNotice({ onConsent }: ConsentNoticeProps) {
  const [show, setShow] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Check if user has already consented (only on client side)
    if (typeof window !== 'undefined') {
      const hasConsented = localStorage.getItem('data_consent');
      if (!hasConsented) {
        setShow(true);
      }
    }
  }, []);

  const handleAgree = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('data_consent', 'true');
      localStorage.setItem('data_consent_timestamp', new Date().toISOString());
    }
    setShow(false);
    onConsent();
  };

  const handleDisagree = () => {
    // User must agree to use the service
    alert('You must agree to the data usage policy to use this service.');
  };

  if (!mounted || !show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
        <div className="p-6">
          <h2 className="text-2xl font-bold mb-4">Data Usage Consent</h2>
          
          <div className="space-y-4 mb-6 text-sm text-gray-700">
            <p>
              <strong>Important:</strong> This tool collects publicly available information from Google Maps and social media platforms.
            </p>
            
            <div>
              <h3 className="font-semibold mb-2">What We Collect:</h3>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>Publicly displayed business information (name, address, phone, website)</li>
                <li>Public social media profiles and posts</li>
                <li>Contact information that is publicly visible</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-2">How We Use This Data:</h3>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>For B2B lead generation and outreach purposes only</li>
                <li>To help you find potential customers or partners</li>
                <li>Data is stored locally on your device</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-2">Data Retention:</h3>
              <p>
                Collected data is automatically deleted after 6 months. You can also request immediate removal of any record.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-2">Your Rights:</h3>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>You can request removal of any collected data</li>
                <li>You can export your data at any time</li>
                <li>You can opt-out of specific platforms</li>
              </ul>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
              <p className="text-xs">
                <strong>Legal Notice:</strong> This tool only collects publicly available information. 
                Use this data responsibly and in compliance with local privacy laws (GDPR, CCPA, etc.). 
                Do not use collected data for spam or unsolicited communications.
              </p>
            </div>
          </div>

          <div className="flex gap-3 justify-end">
            <button
              onClick={handleDisagree}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
            >
              Disagree
            </button>
            <button
              onClick={handleAgree}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              I Agree
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

