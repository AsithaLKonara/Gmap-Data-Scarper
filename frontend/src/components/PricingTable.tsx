import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

// Lucide icons (or use Heroicons if preferred)
const CheckIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"><polyline points="4 11 8 15 16 6" /></svg>
);
const StarIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} viewBox="0 0 20 20" fill="currentColor" className="text-yellow-400"><polygon points="10 2 12.59 7.36 18.51 8.09 14 12.26 15.18 18.09 10 15.27 4.82 18.09 6 12.26 1.49 8.09 7.41 7.36 10 2" /></svg>
);

const PricingTable = () => {
  const { t } = useTranslation();
  const [currentPlan, setCurrentPlan] = useState('');
  const [loadingPlan, setLoadingPlan] = useState(false);
  const [loadingUpgrade, setLoadingUpgrade] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlan = async () => {
      setLoadingPlan(true);
      try {
        const token = localStorage.getItem('token');
        const res = await fetch(`${process.env.REACT_APP_API_URL}/api/payments/plan-status`, {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        });
        const data = await res.json();
        setCurrentPlan(data.plan);
      } catch {}
      setLoadingPlan(false);
    };
    fetchPlan();
  }, []);

  const handleUpgrade = async (plan: string) => {
    setLoadingUpgrade(plan);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${process.env.REACT_APP_API_URL}/api/payments/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ plan }),
      });
      const data = await res.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch {}
    setLoadingUpgrade(null);
  };

  const plans = [
    {
      name: t('plan_free', 'Free'),
      price: '$0',
      period: t('forever', 'forever'),
      queries: t('free_queries', '10 queries/day'),
      features: [
        t('feature_basic_scraping', 'Basic Google Maps scraping'),
        t('feature_csv_export', 'CSV export format'),
        t('feature_email_support', 'Email support'),
        t('feature_basic_filters', 'Basic search filters')
      ],
      popular: false,
      color: 'gray'
    },
    {
      name: t('plan_pro', 'Pro'),
      price: '$9',
      period: t('month', 'month'),
      queries: t('pro_queries', '100 queries/day'),
      features: [
        t('feature_advanced_scraping', 'Advanced scraping capabilities'),
        t('feature_all_exports', 'CSV, JSON, Excel export'),
        t('feature_priority_support', 'Priority email support'),
        t('feature_advanced_filters', 'Advanced search filters'),
        t('feature_api_access', 'API access'),
        t('feature_data_validation', 'Data validation')
      ],
      popular: true,
      color: 'purple'
    },
    {
      name: t('plan_business', 'Business'),
      price: '$49',
      period: t('month', 'month'),
      queries: t('business_queries', 'Unlimited queries'),
      features: [
        t('feature_enterprise_scraping', 'Enterprise-level scraping'),
        t('feature_all_export_formats', 'All export formats'),
        t('feature_phone_support', '24/7 phone support'),
        t('feature_custom_integrations', 'Custom integrations'),
        t('feature_white_label', 'White-label options'),
        t('feature_account_manager', 'Dedicated account manager')
      ],
      popular: false,
      color: 'blue'
    }
  ];

  return (
    <div className="overflow-x-auto fade-in-up">
      <table className="min-w-full text-sm border-separate border-spacing-y-2">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-gray-400 text-md font-medium">{t('plan', 'Plan')}</th>
            <th className="px-4 py-2 text-gray-400 text-md font-medium">{t('price', 'Price')}</th>
            <th className="px-4 py-2 text-gray-400 text-md font-medium">{t('queries', 'Queries')}</th>
            <th className="px-4 py-2 text-gray-400 text-md font-medium">{t('features', 'Features')}</th>
            <th className="px-4 py-2 text-gray-400 text-md font-medium">{t('action', 'Action')}</th>
          </tr>
          {/* Add additional rows for integrations/features as needed, using Tailwind flex/grid for layout */}
        </thead>
        <tbody>
          {plans.map((plan, index) => (
            <tr key={plan.name} className="transition-all hover:bg-gray-100">
              <td className="align-top px-4 py-2">
                <div className="flex flex-col items-start space-y-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-lg">{plan.name}</span>
                    {plan.popular && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded bg-purple-100 text-purple-700 text-xs font-semibold">
                        <StarIcon className="w-3 h-3 mr-1" />
                        {t('popular', 'Popular')}
                      </span>
                    )}
                  </div>
                </div>
              </td>
              <td className="align-top px-4 py-2">
                <div className="flex flex-col items-start space-y-1">
                  <span className="text-2xl font-bold bg-gradient-to-r from-primary to-primary/80 bg-clip-text text-transparent">{plan.price}</span>
                  <span className="text-gray-400 text-sm">
                    {t('per_period', { period: plan.period, defaultValue: `per ${plan.period}` })}
                  </span>
                </div>
              </td>
              <td className="align-top px-4 py-2">
                <span className="text-gray-500 font-medium">{plan.queries}</span>
              </td>
              <td className="align-top px-4 py-2">
                <div className="flex flex-col items-start space-y-2">
                  {plan.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-center space-x-2">
                      <CheckIcon className="w-4 h-4 text-green-500" />
                      <span className="text-gray-400 text-sm">{feature}</span>
                    </div>
                  ))}
                </div>
              </td>
              <td className="align-top px-4 py-2">
                <button
                  className={`inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium shadow transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ${currentPlan === plan.name.toLowerCase() ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-primary text-primary-foreground hover:bg-primary/90'}`}
                  onClick={() => handleUpgrade(plan.name.toLowerCase())}
                  disabled={currentPlan === plan.name.toLowerCase() || loadingUpgrade === plan.name.toLowerCase()}
                >
                  {loadingUpgrade === plan.name.toLowerCase() ? t('loading', 'Loading...') :
                    currentPlan === plan.name.toLowerCase() ? t('current_plan', 'Current Plan') : t('upgrade', 'Upgrade')}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PricingTable; 