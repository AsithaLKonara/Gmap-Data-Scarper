import React, { useState, useEffect } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { getTenantSsoConfig } from '../api';
import { login2FA } from '../api';
import { useTranslation } from 'react-i18next';

const Login = () => {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [tenant, setTenant] = useState('');
  const [ssoEnabled, setSsoEnabled] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const { login } = useAuth();
  const navigate = useNavigate();

  // 2FA state
  const [twoFARequired, setTwoFARequired] = useState(false);
  const [twoFAUserId, setTwoFAUserId] = useState<number | null>(null);
  const [twoFACode, setTwoFACode] = useState('');
  const [twoFALoading, setTwoFALoading] = useState(false);
  const [twoFAError, setTwoFAError] = useState<string | null>(null);

  useEffect(() => {
    if (tenant) {
      getTenantSsoConfig(tenant)
        .then(cfg => setSsoEnabled(!!cfg && !!cfg.entity_id && !!cfg.sso_url && !!cfg.cert))
        .catch(() => setSsoEnabled(false));
    } else {
      setSsoEnabled(false);
    }
  }, [tenant]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setFormError(null);
    setTwoFAError(null);
    try {
      if (!tenant) throw new Error(t('login.error.tenantRequired', 'Tenant/Organization is required'));
      localStorage.setItem('tenantSlug', tenant);
      const result = await login(email, password);
      if (result.type === 'success') {
        navigate('/dashboard');
      } else if (result.type === '2fa') {
        setTwoFARequired(true);
        setTwoFAUserId(result.userId);
      }
    } catch (error) {
      let message = t('login.error.invalidCredentials', 'Invalid credentials');
      if (error instanceof Error) message = error.message;
      setFormError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handle2FASubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setTwoFALoading(true);
    setTwoFAError(null);
    try {
      if (!twoFAUserId) throw new Error('Missing user ID for 2FA');
      const data = await login2FA(twoFAUserId, twoFACode);
      navigate('/dashboard');
    } catch (error) {
      let message = t('login.error.invalid2FACode', 'Invalid 2FA code');
      if (error instanceof Error) message = error.message;
      setTwoFAError(message);
    } finally {
      setTwoFALoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-64px)] py-20 bg-gray-100 dark:bg-gray-900">
      <div className="max-w-md mx-auto">
        <div className="flex flex-col items-center space-y-4 text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/80 bg-clip-text text-transparent">
            {t('login.heading', 'Welcome Back')}
          </h1>
          <p className="text-gray-400 text-lg">
            {t('login.subtitle', 'Sign in to your LeadTap account')}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 w-full">
          {!twoFARequired ? (
            <form onSubmit={handleSubmit}>
              {formError && (
                <div className="text-red-500 text-sm text-center mb-4">{formError}</div>
              )}
              <div className="flex flex-col space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('login.email', 'Email')}</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder={t('login.emailPlaceholder', 'Enter your email')}
                    className="w-full rounded-md border border-gray-300 p-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary bg-gray-50 dark:bg-gray-900"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('login.password', 'Password')}</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder={t('login.passwordPlaceholder', 'Enter your password')}
                    className="w-full rounded-md border border-gray-300 p-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary bg-gray-50 dark:bg-gray-900"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('login.tenant', 'Organization/Tenant')}</label>
                  <input
                    value={tenant}
                    onChange={(e) => setTenant(e.target.value)}
                    placeholder={t('login.tenantPlaceholder', 'Enter your organization/tenant slug')}
                    className="w-full rounded-md border border-gray-300 p-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary bg-gray-50 dark:bg-gray-900"
                    required
                  />
                </div>
                {ssoEnabled && (
                  <button
                    type="button"
                    className="w-full inline-flex items-center justify-center rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white shadow transition-colors hover:bg-purple-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-purple-500 focus-visible:ring-offset-2"
                    onClick={() => {
                      // Store tenant for callback use
                      localStorage.setItem('tenantSlug', tenant);
                      window.location.assign(`/api/auth/sso/login?tenant=${tenant}`);
                    }}
                  >
                    {t('login.sso', 'Sign in with SSO')}
                  </button>
                )}
                <button
                  type="submit"
                  className="w-full inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-lg font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50"
                  disabled={isLoading}
                >
                  {isLoading ? t('login.signingIn', 'Signing in...') : t('login.signIn', 'Sign In')}
                </button>
              </div>
            </form>
          ) : (
            <form onSubmit={handle2FASubmit}>
              {twoFAError && (
                <div className="text-red-500 text-sm text-center mb-4">{twoFAError}</div>
              )}
              <div className="flex flex-col space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('login.2faCode', 'Two-Factor Code')}</label>
                  <input
                    type="text"
                    value={twoFACode}
                    onChange={(e) => setTwoFACode(e.target.value)}
                    placeholder={t('login.2faCodePlaceholder', 'Enter your 2FA code')}
                    className="w-full rounded-md border border-gray-300 p-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary bg-gray-50 dark:bg-gray-900"
                    required
                  />
                </div>
                <button
                  type="submit"
                  className="w-full inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-lg font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50"
                  disabled={twoFALoading}
                >
                  {twoFALoading ? t('login.verifying', 'Verifying...') : t('login.verify2FA', 'Verify 2FA')}
                </button>
              </div>
            </form>
          )}
        </div>
        <div className="text-gray-400 text-center mt-6">
          {t('login.noAccount', "Don't have an account?")}{' '}
          <RouterLink to="/register" className="text-primary font-semibold hover:underline">
            {t('login.signUpHere', 'Sign up here')}
          </RouterLink>
        </div>
      </div>
    </div>
  );
};

export default Login; 