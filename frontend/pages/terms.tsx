import { useRouter } from 'next/router';

export default function TermsOfServicePage() {
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
          <h1 className="text-3xl font-bold">Terms of Service</h1>

          <section>
            <p className="text-gray-700 mb-4">
              <strong>Effective Date:</strong> January 13, 2025
            </p>
            <p className="text-gray-700">
              By using the Lead Intelligence Platform, you agree to these Terms of Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">1. Acceptance of Terms</h2>
            <p className="text-gray-700">
              By accessing or using this platform, you agree to be bound by these Terms. 
              If you disagree, do not use the service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">2. Use of Service</h2>
            <p className="text-gray-700 mb-4">You agree to:</p>
            <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
              <li>Use the service only for lawful B2B purposes</li>
              <li>Not use the service for spam or unsolicited communications</li>
              <li>Respect rate limits and platform terms of service</li>
              <li>Not attempt to circumvent security measures</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">3. Data Collection</h2>
            <p className="text-gray-700">
              The platform collects publicly available information. By using the service, you acknowledge 
              that collected data is from public sources and used for B2B lead generation purposes.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">4. User Responsibilities</h2>
            <p className="text-gray-700 mb-4">You are responsible for:</p>
            <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
              <li>Compliance with applicable laws (GDPR, CAN-SPAM, etc.)</li>
              <li>Obtaining necessary consents for outreach</li>
              <li>Accurate representation of your business</li>
              <li>Maintaining account security</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">5. Prohibited Uses</h2>
            <p className="text-gray-700 mb-4">You may NOT:</p>
            <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
              <li>Use data for spam or unsolicited bulk communications</li>
              <li>Violate platform terms of service (Google, Facebook, etc.)</li>
              <li>Resell or redistribute collected data</li>
              <li>Use automated systems to abuse the service</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">6. Service Availability</h2>
            <p className="text-gray-700">
              We strive for 99.9% uptime but do not guarantee uninterrupted service. The service may be 
              temporarily unavailable for maintenance or updates.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">7. Limitation of Liability</h2>
            <p className="text-gray-700">
              The service is provided "as is". We are not liable for any damages arising from use of 
              the platform or collected data.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">8. Termination</h2>
            <p className="text-gray-700">
              We reserve the right to terminate access for violation of these terms. You may stop 
              using the service at any time.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">9. Changes to Terms</h2>
            <p className="text-gray-700">
              We may update these terms periodically. Continued use after changes constitutes acceptance.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">10. Contact</h2>
            <p className="text-gray-700">
              Questions about these terms: <strong>legal@leadintelligence.com</strong>
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}

