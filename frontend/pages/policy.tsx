import { useRouter } from 'next/router';

export default function PolicyPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={() => router.push('/')}
          className="text-blue-600 hover:text-blue-800 mb-6"
        >
          ← Back to Dashboard
        </button>

        <div className="bg-white shadow rounded-lg p-8 space-y-8">
          <h1 className="text-3xl font-bold">Data Use Policy</h1>

          <section>
            <h2 className="text-2xl font-semibold mb-4">1. Data Collection</h2>
            <p className="text-gray-700 mb-4">
              The Lead Intelligence Platform collects publicly available information from:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
              <li>Google Maps business listings</li>
              <li>Social media platforms (Facebook, Instagram, LinkedIn, X/Twitter, YouTube, TikTok)</li>
              <li>Public business websites and contact pages</li>
            </ul>
            <p className="text-gray-700 mt-4">
              We only collect information that is publicly visible and accessible without authentication.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">2. Types of Data Collected</h2>
            <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
              <li><strong>Business Information:</strong> Name, address, phone number, website, category</li>
              <li><strong>Contact Details:</strong> Publicly listed phone numbers, email addresses</li>
              <li><strong>Social Media:</strong> Profile URLs, handles, follower counts, bio information</li>
              <li><strong>Metadata:</strong> Collection timestamp, source platform, confidence scores</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">3. How We Use Your Data</h2>
            <p className="text-gray-700 mb-4">
              Collected data is used exclusively for:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
              <li><strong>B2B Lead Generation:</strong> Identifying potential business contacts</li>
              <li><strong>Market Research:</strong> Understanding market trends and business landscapes</li>
              <li><strong>Business Intelligence:</strong> Analyzing industry patterns and opportunities</li>
            </ul>
            <p className="text-gray-700 mt-4">
              <strong>We do NOT:</strong> Sell data to third parties, use data for spam, or contact individuals 
              for personal purposes. All outreach is B2B focused.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">4. Data Retention</h2>
            <p className="text-gray-700 mb-4">
              We automatically delete collected records after <strong>6 months (180 days)</strong> from the 
              date of collection. This ensures compliance with data retention regulations while maintaining 
              useful lead data for business purposes.
            </p>
            <p className="text-gray-700">
              You can request earlier deletion at any time through our opt-out mechanism.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">5. Your Rights (GDPR Compliance)</h2>
            <p className="text-gray-700 mb-4">You have the right to:</p>
            <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
              <li><strong>Access:</strong> Request a copy of your data (if applicable)</li>
              <li><strong>Deletion:</strong> Request removal of your data from our systems</li>
              <li><strong>Rectification:</strong> Request correction of inaccurate data</li>
              <li><strong>Objection:</strong> Object to processing of your data</li>
              <li><strong>Portability:</strong> Request data in a portable format</li>
            </ul>
            <p className="text-gray-700 mt-4">
              To exercise these rights, visit our <a href="/compliance" className="text-blue-600 hover:underline">Compliance Dashboard</a> 
              or contact us directly.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">6. Data Security</h2>
            <p className="text-gray-700 mb-4">
              We implement industry-standard security measures to protect collected data:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
              <li>Encrypted data storage</li>
              <li>Access controls and authentication</li>
              <li>Regular security audits</li>
              <li>Automatic data expiration</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">7. Opt-Out Mechanism</h2>
            <p className="text-gray-700 mb-4">
              If you wish to have your data removed from our systems:
            </p>
            <ol className="list-decimal list-inside space-y-2 text-gray-600 ml-4">
              <li>Visit our <a href="/compliance" className="text-blue-600 hover:underline">Compliance Dashboard</a></li>
              <li>Enter your profile URL in the opt-out form</li>
              <li>Submit the removal request</li>
              <li>Your data will be deleted within 48 hours</li>
            </ol>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">8. Contact Information</h2>
            <p className="text-gray-700">
              For questions, concerns, or data requests, please contact us:
            </p>
            <div className="mt-4 p-4 bg-gray-50 rounded">
              <p className="text-gray-700">
                <strong>Email:</strong> privacy@leadintelligence.com<br />
                <strong>Compliance Dashboard:</strong> <a href="/compliance" className="text-blue-600 hover:underline">/compliance</a>
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">9. Policy Updates</h2>
            <p className="text-gray-700">
              This policy may be updated periodically. We will notify users of significant changes. 
              Continued use of the platform after policy updates constitutes acceptance of the new terms.
            </p>
            <p className="text-gray-500 text-sm mt-2">
              <strong>Last Updated:</strong> January 13, 2025
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}

