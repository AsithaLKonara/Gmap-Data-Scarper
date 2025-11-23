import { useRouter } from 'next/router';

export default function PrivacyPolicyPage() {
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
          <h1 className="text-3xl font-bold">Privacy Policy</h1>

          <section>
            <p className="text-gray-700 mb-4">
              <strong>Effective Date:</strong> January 13, 2025
            </p>
            <p className="text-gray-700">
              This Privacy Policy describes how the Lead Intelligence Platform ("we", "our", "us") 
              collects, uses, and protects information collected from publicly available sources.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Information We Collect</h2>
            <p className="text-gray-700 mb-4">
              We collect publicly available information from:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
              <li>Google Maps business listings</li>
              <li>Social media platforms (public profiles only)</li>
              <li>Public business websites</li>
            </ul>
            <p className="text-gray-700 mt-4">
              We do not collect private information, require login credentials, or access non-public data.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">How We Use Information</h2>
            <p className="text-gray-700 mb-4">
              Collected information is used for:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
              <li>B2B lead generation and business development</li>
              <li>Market research and business intelligence</li>
              <li>Industry analysis and trend identification</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Data Sharing</h2>
            <p className="text-gray-700">
              We do not sell, rent, or share collected data with third parties except:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4 mt-2">
              <li>When required by law or legal process</li>
              <li>To protect our rights and prevent fraud</li>
              <li>With service providers under strict confidentiality agreements</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Data Security</h2>
            <p className="text-gray-700">
              We implement technical and organizational measures to protect data, including encryption, 
              access controls, and regular security audits.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Your Rights</h2>
            <p className="text-gray-700 mb-4">
              Under GDPR and other privacy laws, you have the right to:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
              <li>Access your data</li>
              <li>Request deletion</li>
              <li>Correct inaccurate data</li>
              <li>Object to processing</li>
              <li>Data portability</li>
            </ul>
            <p className="text-gray-700 mt-4">
              Exercise these rights at our <a href="/compliance" className="text-blue-600 hover:underline">Compliance Dashboard</a>.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Contact Us</h2>
            <p className="text-gray-700">
              For privacy concerns: <strong>privacy@leadintelligence.com</strong>
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}

