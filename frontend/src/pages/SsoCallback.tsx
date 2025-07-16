import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

const SsoCallback: React.FC = () => {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const samlResponse = searchParams.get('SAMLResponse');
    const tenant = searchParams.get('tenant');
    if (!samlResponse || !tenant) {
      setError('Missing SAML response or tenant.');
      setLoading(false);
      return;
    }
    // Call backend SSO callback
    fetch('/api/auth/sso/callback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ saml_response: samlResponse, tenant }),
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text());
        return res.json();
      })
      .then((data) => {
        if (data.access_token) {
          localStorage.setItem('token', data.access_token);
          window.location.href = '/dashboard';
        } else {
          setError('SSO login failed.');
        }
      })
      .catch((e) => {
        setError(e.message || 'SSO login failed.');
      })
      .finally(() => setLoading(false));
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100">
      <div className="bg-white rounded-lg shadow p-8 max-w-md w-full text-center">
        <h1 className="text-2xl font-bold mb-4">SSO Login</h1>
        {loading && <div>Processing SSO login...</div>}
        {error && <div className="text-red-500">{error}</div>}
      </div>
    </div>
  );
};

export default SsoCallback; 