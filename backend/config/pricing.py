"""Pricing configuration for plans."""
from typing import Dict, Any
import os

# Plan configurations
PLAN_CONFIGS: Dict[str, Dict[str, Any]] = {
    'free': {
        'name': 'Free',
        'daily_lead_limit': 10,
        'monthly_price': None,
        'price_per_lead': None,
        'features': [
            '10 leads per day',
            'Basic scraping',
            'Phone extraction',
            'CSV export',
            'Email support',
        ],
    },
    'paid_monthly': {
        'name': 'Pro Monthly',
        'daily_lead_limit': None,  # Unlimited
        'monthly_price': 29.0,
        'price_per_lead': None,
        'stripe_price_id': os.getenv('STRIPE_PRICE_ID_MONTHLY', ''),
        'features': [
            'Unlimited leads',
            'Advanced scraping',
            'Phone & email extraction',
            'Data enrichment',
            'All export formats',
            'Priority support',
            'API access',
        ],
    },
    'paid_usage': {
        'name': 'Pay As You Go',
        'daily_lead_limit': None,  # Unlimited
        'monthly_price': None,
        'price_per_lead': 0.50,
        'stripe_price_id': os.getenv('STRIPE_PRICE_ID_USAGE_BASED', ''),
        'features': [
            'Pay only for what you use',
            'No monthly commitment',
            'All Pro features',
            'Volume discounts available',
            'Priority support',
            'API access',
        ],
    },
}


def get_plan_config(plan_type: str) -> Dict[str, Any]:
    """Get configuration for a plan type."""
    return PLAN_CONFIGS.get(plan_type, PLAN_CONFIGS['free'])


def get_stripe_price_id(plan_type: str) -> str:
    """Get Stripe price ID for a plan type."""
    config = get_plan_config(plan_type)
    return config.get('stripe_price_id', '')

