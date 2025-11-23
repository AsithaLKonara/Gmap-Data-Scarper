import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

interface ConsentModalProps {
  onAccept: () => void;
  onDecline: () => void;
}

export default function ConsentModal({ onAccept, onDecline }: ConsentModalProps) {
  const [showModal, setShowModal] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Check if user has already given consent
    const consentGiven = localStorage.getItem('data_consent_given');
    if (!consentGiven) {
      setShowModal(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('data_consent_given', 'true');
    localStorage.setItem('data_consent_timestamp', new Date().toISOString());
    setShowModal(false);
    onAccept();
  };

  const handleDecline = () => {
    // Redirect to policy page or home
    router.push('/policy');
    onDecline();
  };

  const handleViewPolicy = () => {
    router.push('/policy');
  };

  if (!showModal) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">Data Collection Consent</h2>
        
        <div className="space-y-4 mb-6">
          <p className="text-gray-700">
            This platform collects publicly available business and individual contact information 
            from Google Maps and social media platforms for lead generation purposes.
          </p>
          
          <div>
            <h3 className="font-semibold mb-2">What We Collect:</h3>
            <ul className="list-disc list-inside space-y-1 text-gray-600">
              <li>Business names, addresses, and contact information</li>
              <li>Phone numbers (publicly listed)</li>
              <li>Social media profiles and handles</li>
              <li>Business categories and descriptions</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-2">How We Use It:</h3>
            <ul className="list-disc list-inside space-y-1 text-gray-600">
              <li>B2B lead generation and outreach</li>
              <li>Business intelligence and market research</li>
              <li>Contact database building (B2B only)</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-2">Your Rights:</h3>
            <ul className="list-disc list-inside space-y-1 text-gray-600">
              <li>Request data deletion (opt-out)</li>
              <li>Access your data (if applicable)</li>
              <li>Withdraw consent at any time</li>
            </ul>
          </div>
          
          <div className="bg-blue-50 border border-blue-200 rounded p-3">
            <p className="text-sm text-blue-800">
              <strong>Data Retention:</strong> Records are automatically deleted after 6 months 
              (180 days) from collection date, unless you request earlier deletion.
            </p>
          </div>
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={handleAccept}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            I Accept
          </button>
          <button
            onClick={handleViewPolicy}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
          >
            View Full Policy
          </button>
          <button
            onClick={handleDecline}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Decline
          </button>
        </div>
        
        <p className="text-xs text-gray-500 mt-4 text-center">
          By clicking "I Accept", you consent to our data collection and usage as described above.
        </p>
      </div>
    </div>
  );
}

