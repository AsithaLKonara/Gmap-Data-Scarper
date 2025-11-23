import { useState } from 'react';
import Link from 'next/link';
import GlassButton from './ui/GlassButton';

interface Plan {
  name: string;
  price: string;
  priceSubtext?: string;
  description: string;
  features: string[];
  cta: string;
  ctaLink: string;
  popular?: boolean;
  planType: 'free' | 'monthly' | 'usage';
}

export default function PricingSection() {
  const plans: Plan[] = [
    {
      name: 'Free',
      price: '$0',
      description: 'Perfect for trying out the platform',
      features: [
        '10 leads per day',
        'Basic scraping',
        'Phone extraction',
        'CSV export',
        'Email support',
      ],
      cta: 'Get Started',
      ctaLink: '/signup?plan=free',
      planType: 'free',
    },
    {
      name: 'Pro Monthly',
      price: '$29',
      priceSubtext: '/month',
      description: 'For growing businesses',
      features: [
        'Unlimited leads',
        'Advanced scraping',
        'Phone & email extraction',
        'Data enrichment',
        'All export formats',
        'Priority support',
        'API access',
      ],
      cta: 'Start Free Trial',
      ctaLink: '/signup?plan=monthly',
      popular: true,
      planType: 'monthly',
    },
    {
      name: 'Pay As You Go',
      price: '$0.50',
      priceSubtext: '/lead',
      description: 'Flexible pricing for variable usage',
      features: [
        'Pay only for what you use',
        'No monthly commitment',
        'All Pro features',
        'Volume discounts available',
        'Priority support',
        'API access',
      ],
      cta: 'Get Started',
      ctaLink: '/signup?plan=usage',
      planType: 'usage',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      {plans.map((plan) => (
        <div
          key={plan.name}
          className={`bg-white/10 backdrop-blur-xl border border-white/20 p-8 rounded-2xl relative shadow-2xl hover:bg-white/15 hover:scale-105 transition-all duration-300 ${
            plan.popular ? 'ring-2 ring-blue-400 scale-105 shadow-glow' : ''
          }`}
        >
          {plan.popular && (
            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
              <span className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-4 py-1 rounded-full text-sm font-semibold shadow-lg">
                Most Popular
              </span>
            </div>
          )}
          <div className="text-center mb-6">
            <h3 className="text-2xl font-bold text-white mb-2">
              {plan.name}
            </h3>
            <div className="mb-2">
              <span className="text-4xl font-bold text-white">
                {plan.price}
              </span>
              {plan.priceSubtext && (
                <span className="text-white/80 ml-1">
                  {plan.priceSubtext}
                </span>
              )}
            </div>
            <p className="text-white/80 text-sm">
              {plan.description}
            </p>
          </div>
          <ul className="space-y-3 mb-8">
            {plan.features.map((feature, index) => (
              <li key={index} className="flex items-start">
                <svg
                  className="w-5 h-5 text-green-400 mr-2 flex-shrink-0 mt-0.5"
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
                <span className="text-white/90">{feature}</span>
              </li>
            ))}
          </ul>
          <Link href={plan.ctaLink} className="block">
            <GlassButton
              variant={plan.popular ? 'primary' : 'secondary'}
              gradient={plan.popular}
              className="w-full"
            >
              {plan.cta}
            </GlassButton>
          </Link>
        </div>
      ))}
    </div>
  );
}

