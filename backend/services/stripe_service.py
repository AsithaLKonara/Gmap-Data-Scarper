"""Stripe service for payment processing."""
import os
from typing import Optional, Dict, Any, List

# Optional Stripe import - handle gracefully if not installed
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    stripe = None  # type: ignore

# Initialize Stripe if available
if STRIPE_AVAILABLE:
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')
else:
    # Create a mock stripe object for when it's not available
    class MockStripe:
        api_key = None
    stripe = MockStripe()


class StripeService:
    """Service for managing Stripe payments and subscriptions."""
    
    def __init__(self):
        """Initialize Stripe service."""
        if not STRIPE_AVAILABLE:
            print("⚠️  Stripe package not installed. Payment features will be disabled.")
        elif not stripe.api_key:
            print("⚠️  Stripe API key not configured. Payment features will be disabled.")
    
    def create_customer(self, email: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a Stripe customer.
        
        Args:
            email: Customer email
            name: Customer name (optional)
            
        Returns:
            Stripe customer object
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")
        
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={
                'source': 'lead_intelligence_platform'
            }
        )
        
        return {
            'customer_id': customer.id,
            'email': customer.email,
            'name': customer.name,
        }
    
    def create_checkout_session(
        self,
        price_id: str,
        user_id: str,
        customer_id: Optional[str] = None,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe checkout session.
        
        Args:
            price_id: Stripe price ID
            user_id: User ID
            customer_id: Existing Stripe customer ID (optional)
            success_url: Success redirect URL
            cancel_url: Cancel redirect URL
            
        Returns:
            Checkout session object
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")
        
        base_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        default_success = f"{base_url}/upgrade?success=true&session_id={{CHECKOUT_SESSION_ID}}"
        default_cancel = f"{base_url}/upgrade?canceled=true"
        
        session_params = {
            'payment_method_types': ['card'],
            'line_items': [{
                'price': price_id,
                'quantity': 1,
            }],
            'mode': 'subscription' if 'monthly' in price_id.lower() else 'payment',
            'success_url': success_url or default_success,
            'cancel_url': cancel_url or default_cancel,
            'metadata': {
                'user_id': user_id,
            },
        }
        
        if customer_id:
            session_params['customer'] = customer_id
        
        session = stripe.checkout.Session.create(**session_params)
        
        return {
            'session_id': session.id,
            'url': session.url,
            'customer_id': session.customer,
        }
    
    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        plan_type: str
    ) -> Dict[str, Any]:
        """
        Create a Stripe subscription.
        
        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            plan_type: Plan type ('paid_monthly' or 'paid_usage')
            
        Returns:
            Subscription object
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")
        
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{
                'price': price_id,
            }],
            metadata={
                'plan_type': plan_type,
            }
        )
        
        return {
            'subscription_id': subscription.id,
            'customer_id': subscription.customer,
            'status': subscription.status,
            'current_period_end': subscription.current_period_end,
        }
    
    def handle_webhook(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Stripe webhook events.
        
        Args:
            event: Stripe webhook event
            
        Returns:
            Processing result
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")
        
        event_type = event.get('type')
        event_data = event.get('data', {}).get('object', {})
        
        result = {
            'processed': False,
            'event_type': event_type,
            'message': 'Event not processed',
        }
        
        if event_type == 'checkout.session.completed':
            # Payment successful, update user plan
            session = event_data
            user_id = session.get('metadata', {}).get('user_id')
            customer_id = session.get('customer')
            
            if user_id and customer_id:
                # Determine plan type from price
                price_id = session.get('line_items', {}).get('data', [{}])[0].get('price', {}).get('id', '')
                plan_type = 'paid_monthly' if 'monthly' in price_id.lower() else 'paid_usage'
                
                result = {
                    'processed': True,
                    'event_type': event_type,
                    'user_id': user_id,
                    'customer_id': customer_id,
                    'plan_type': plan_type,
                    'message': 'Checkout completed, plan should be updated',
                }
        
        elif event_type == 'customer.subscription.created':
            # Subscription created
            subscription = event_data
            result = {
                'processed': True,
                'event_type': event_type,
                'subscription_id': subscription.get('id'),
                'customer_id': subscription.get('customer'),
                'message': 'Subscription created',
            }
        
        elif event_type == 'customer.subscription.updated':
            # Subscription updated
            subscription = event_data
            result = {
                'processed': True,
                'event_type': event_type,
                'subscription_id': subscription.get('id'),
                'status': subscription.get('status'),
                'message': 'Subscription updated',
            }
        
        elif event_type == 'customer.subscription.deleted':
            # Subscription cancelled
            subscription = event_data
            result = {
                'processed': True,
                'event_type': event_type,
                'subscription_id': subscription.get('id'),
                'message': 'Subscription cancelled',
            }
        
        return result
    
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Cancel a Stripe subscription.
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            Cancellation result
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")
        
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
        
        return {
            'subscription_id': subscription.id,
            'status': subscription.status,
            'cancel_at_period_end': subscription.cancel_at_period_end,
            'current_period_end': subscription.current_period_end,
        }
    
    def update_subscription(
        self,
        subscription_id: str,
        new_price_id: str
    ) -> Dict[str, Any]:
        """
        Update subscription to new price.
        
        Args:
            subscription_id: Stripe subscription ID
            new_price_id: New Stripe price ID
            
        Returns:
            Updated subscription
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")
        
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Update subscription items
        stripe.Subscription.modify(
            subscription_id,
            items=[{
                'id': subscription['items']['data'][0].id,
                'price': new_price_id,
            }],
            proration_behavior='create_prorations'
        )
        
        updated = stripe.Subscription.retrieve(subscription_id)
        
        return {
            'subscription_id': updated.id,
            'status': updated.status,
            'current_period_end': updated.current_period_end,
        }
    
    def upgrade_subscription(
        self,
        subscription_id: str,
        new_price_id: str,
        prorate: bool = True
    ) -> Dict[str, Any]:
        """
        Upgrade subscription to a higher tier.
        
        Args:
            subscription_id: Stripe subscription ID
            new_price_id: New price ID for upgrade
            prorate: Whether to prorate the charge
            
        Returns:
            Updated subscription
        """
        return self.update_subscription(subscription_id, new_price_id)
    
    def downgrade_subscription(
        self,
        subscription_id: str,
        new_price_id: str,
        schedule_at_period_end: bool = True
    ) -> Dict[str, Any]:
        """
        Downgrade subscription to a lower tier.
        
        Args:
            subscription_id: Stripe subscription ID
            new_price_id: New price ID for downgrade
            schedule_at_period_end: Schedule change at period end (no proration)
            
        Returns:
            Updated subscription
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")
        
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        if schedule_at_period_end:
            # Schedule change at period end
            stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': new_price_id,
                }],
                proration_behavior='none'
            )
        else:
            # Immediate change with proration
            return self.update_subscription(subscription_id, new_price_id)
        
        updated = stripe.Subscription.retrieve(subscription_id)
        return {
            'subscription_id': updated.id,
            'status': updated.status,
            'current_period_end': updated.current_period_end,
            'scheduled_change': schedule_at_period_end,
        }
    
    def create_usage_record(
        self,
        subscription_item_id: str,
        quantity: int,
        timestamp: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Record usage for metered billing.
        
        Args:
            subscription_item_id: Stripe subscription item ID
            quantity: Usage quantity
            timestamp: Unix timestamp (defaults to now)
            
        Returns:
            Usage record
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")
        
        usage_record = stripe.UsageRecord.create(
            subscription_item=subscription_item_id,
            quantity=quantity,
            timestamp=timestamp or int(stripe.util.current_unix_timestamp())
        )
        
        return {
            'id': usage_record.id,
            'quantity': usage_record.quantity,
            'timestamp': usage_record.timestamp,
        }
    
    def get_invoice_history(
        self,
        customer_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get invoice history for a customer.
        
        Args:
            customer_id: Stripe customer ID
            limit: Number of invoices to retrieve
            
        Returns:
            List of invoices
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")
        
        invoices = stripe.Invoice.list(
            customer=customer_id,
            limit=limit
        )
        
        return [
            {
                'id': inv.id,
                'amount_paid': inv.amount_paid / 100,  # Convert from cents
                'currency': inv.currency,
                'status': inv.status,
                'created': inv.created,
                'invoice_pdf': inv.invoice_pdf,
                'hosted_invoice_url': inv.hosted_invoice_url,
            }
            for inv in invoices.data
        ]


# Global instance
_stripe_service: Optional[StripeService] = None


def get_stripe_service() -> StripeService:
    """Get global Stripe service instance."""
    global _stripe_service
    if _stripe_service is None:
        _stripe_service = StripeService()
    return _stripe_service

