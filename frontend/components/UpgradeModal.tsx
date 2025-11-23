import { useState, useEffect } from 'react';
import { createCheckoutSession, getUserPlan } from '../utils/api';
import GlassCard from './ui/GlassCard';
import GlassButton from './ui/GlassButton';
import { showToast } from '../utils/toast';

interface UpgradeModalProps {
  onClose: () => void;
  onUpgrade: () => void;
}

export default function UpgradeModal({ onClose, onUpgrade }: UpgradeModalProps) {
  const [loading, setLoading] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<'paid_monthly' | 'paid_usage' | null>(null);
  const [currentPlan, setCurrentPlan] = useState<string>('free');

  useEffect(() => {
    getUserPlan()
      .then(plan => setCurrentPlan(plan.plan_type))
      .catch(() => {});
  }, []);

  const handleUpgrade = async (planType: 'paid_monthly' | 'paid_usage') => {
    if (loading) return;
    
    setLoading(true);
    try {
      const session = await createCheckoutSession(planType);
      
      // Redirect to Stripe Checkout
      if (session.url) {
        window.location.href = session.url;
      } else {
        throw new Error('No checkout URL received');
      }
    } catch (error: any) {
      showToast(error.message || 'Failed to create checkout session', 'error');
      setLoading(false);
    }
  };

  const plans = [
    {
      id: 'paid_monthly' as const,
      name: 'Pro Monthly',
      price: '$29',
      period: '/month',
      description: 'Unlimited leads, all features',
      features: [
        'Unlimited leads per day',
        'Advanced scraping',
        'Phone & email extraction',
        'Data enrichment',
        'All export formats',
        'Priority support',
        'API access',
      ],
    },
    {
      id: 'paid_usage' as const,
      name: 'Pay As You Go',
      price: '$0.50',
      period: '/lead',
      description: 'Flexible pricing, pay only for what you use',
      features: [
        'Pay only for what you use',
        'No monthly commitment',
        'All Pro features',
        'Volume discounts available',
        'Priority support',
        'API access',
      ],
    },
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 backdrop-blur-sm">
      <GlassCard className="max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Upgrade Your Plan
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 text-2xl"
          >
            ×
          </button>
        </div>

        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Choose a plan that works for you. You can change or cancel anytime.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`glass-strong p-6 rounded-xl cursor-pointer transition-all ${
                selectedPlan === plan.id
                  ? 'ring-2 ring-blue-500 scale-105'
                  : 'hover:scale-102'
              }`}
              onClick={() => setSelectedPlan(plan.id)}
            >
              <div className="text-center mb-4">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  {plan.name}
                </h3>
                <div className="mb-2">
                  <span className="text-3xl font-bold text-gray-900 dark:text-white">
                    {plan.price}
                  </span>
                  <span className="text-gray-600 dark:text-gray-400 ml-1">
                    {plan.period}
                  </span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {plan.description}
                </p>
              </div>
              <ul className="space-y-2 mb-4">
                {plan.features.map((feature, idx) => (
                  <li key={idx} className="flex items-start text-sm">
                    <svg
                      className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span className="text-gray-700 dark:text-gray-300">{feature}</span>
                  </li>
                ))}
              </ul>
              <GlassButton
                variant={selectedPlan === plan.id ? 'primary' : 'secondary'}
                gradient={selectedPlan === plan.id}
                className="w-full"
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedPlan(plan.id);
                }}
              >
                {selectedPlan === plan.id ? 'Selected' : 'Select'}
              </GlassButton>
            </div>
          ))}
        </div>

        <div className="flex gap-4">
          <GlassButton
            variant="secondary"
            className="flex-1"
            onClick={onClose}
            disabled={loading}
          >
            Cancel
          </GlassButton>
          <GlassButton
            variant="primary"
            gradient
            className="flex-1"
            onClick={() => selectedPlan && handleUpgrade(selectedPlan)}
            disabled={!selectedPlan || loading}
          >
            {loading ? 'Processing...' : 'Continue to Payment'}
          </GlassButton>
        </div>

        <p className="text-xs text-gray-500 dark:text-gray-400 mt-4 text-center">
          Secure payment powered by Stripe. Your subscription can be cancelled anytime.
        </p>
      </GlassCard>
    </div>
  );
}

