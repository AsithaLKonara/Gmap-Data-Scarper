import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { getUserPlan, createCheckoutSession } from '../utils/api';
import UpgradeModal from '../components/UpgradeModal';
import GlassCard from '../components/ui/GlassCard';
import GlassButton from '../components/ui/GlassButton';
import { useUser } from '../contexts/UserContext';

export default function UpgradePage() {
  const router = useRouter();
  const { user, loading } = useUser();
  const [plan, setPlan] = useState<any>(null);
  const [loadingPlan, setLoadingPlan] = useState(true);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/landing');
      return;
    }

    if (user) {
      getUserPlan()
        .then(setPlan)
        .catch(() => {})
        .finally(() => setLoadingPlan(false));
    }
  }, [user, loading, router]);

  // Handle Stripe redirect
  useEffect(() => {
    const { success, canceled, session_id } = router.query;
    
    if (success === 'true' && session_id) {
      // Payment successful - refresh plan
      getUserPlan()
        .then(setPlan)
        .catch(() => {});
    }
  }, [router.query]);

  if (loading || loadingPlan) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Upgrade Your Plan
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Unlock unlimited leads and advanced features
          </p>
        </div>

        {plan && (
          <GlassCard className="mb-8 p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Current Plan: {plan.plan_name}
            </h2>
            <div className="space-y-2 text-gray-700 dark:text-gray-300">
              <p>
                <strong>Status:</strong> {plan.status}
              </p>
              {plan.usage && (
                <p>
                  <strong>Usage Today:</strong>{' '}
                  {plan.usage.is_unlimited ? (
                    <span className="text-green-600 dark:text-green-400">Unlimited</span>
                  ) : (
                    <span>
                      {plan.usage.used_today}/{plan.usage.daily_limit} leads
                      {plan.usage.remaining_today !== null && (
                        <span> ({plan.usage.remaining_today} remaining)</span>
                      )}
                    </span>
                  )}
                </p>
              )}
            </div>
          </GlassCard>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <GlassCard className="p-6">
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Pro Monthly
            </h3>
            <div className="mb-4">
              <span className="text-4xl font-bold text-gray-900 dark:text-white">$29</span>
              <span className="text-gray-600 dark:text-gray-400 ml-1">/month</span>
            </div>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Unlimited leads, all features included
            </p>
            <ul className="space-y-2 mb-6">
              <li className="flex items-start">
                <svg className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-gray-700 dark:text-gray-300">Unlimited leads</span>
              </li>
              <li className="flex items-start">
                <svg className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-gray-700 dark:text-gray-300">All export formats</span>
              </li>
              <li className="flex items-start">
                <svg className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-gray-700 dark:text-gray-300">Priority support</span>
              </li>
            </ul>
            <GlassButton
              variant="primary"
              gradient
              className="w-full"
              onClick={async () => {
                try {
                  const session = await createCheckoutSession('paid_monthly');
                  if (session.url) {
                    window.location.href = session.url;
                  }
                } catch (error: any) {
                  alert(error.message || 'Failed to create checkout session');
                }
              }}
            >
              Upgrade to Monthly
            </GlassButton>
          </GlassCard>

          <GlassCard className="p-6">
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Pay As You Go
            </h3>
            <div className="mb-4">
              <span className="text-4xl font-bold text-gray-900 dark:text-white">$0.50</span>
              <span className="text-gray-600 dark:text-gray-400 ml-1">/lead</span>
            </div>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Flexible pricing, no monthly commitment
            </p>
            <ul className="space-y-2 mb-6">
              <li className="flex items-start">
                <svg className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-gray-700 dark:text-gray-300">Pay only for what you use</span>
              </li>
              <li className="flex items-start">
                <svg className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-gray-700 dark:text-gray-300">No monthly commitment</span>
              </li>
              <li className="flex items-start">
                <svg className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-gray-700 dark:text-gray-300">All Pro features</span>
              </li>
            </ul>
            <GlassButton
              variant="secondary"
              className="w-full"
              onClick={async () => {
                try {
                  const session = await createCheckoutSession('paid_usage');
                  if (session.url) {
                    window.location.href = session.url;
                  }
                } catch (error: any) {
                  alert(error.message || 'Failed to create checkout session');
                }
              }}
            >
              Choose Pay As You Go
            </GlassButton>
          </GlassCard>
        </div>

        <div className="text-center">
          <GlassButton
            variant="secondary"
            onClick={() => router.push('/')}
          >
            Back to Dashboard
          </GlassButton>
        </div>
      </div>
    </div>
  );
}

