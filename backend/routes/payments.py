"""Payment endpoints for Stripe integration."""
from fastapi import APIRouter, HTTPException, Depends, Header, Request, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
# Import stripe service - handle gracefully if not available
try:
    from backend.services.stripe_service import get_stripe_service
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    def get_stripe_service():
        return None
from backend.services.plan_service import get_plan_service
from backend.config.pricing import get_stripe_price_id, get_plan_config
from backend.middleware.auth import get_current_user
import os

# Optional stripe import
try:
    import stripe
    STRIPE_MODULE_AVAILABLE = True
except ImportError:
    STRIPE_MODULE_AVAILABLE = False
    stripe = None  # type: ignore

router = APIRouter(prefix="/api/payments", tags=["payments"])


class CreateCheckoutRequest(BaseModel):
    """Create checkout session request."""
    plan_type: str  # 'paid_monthly' or 'paid_usage'


@router.post("/create-checkout")
async def create_checkout(
    request: CreateCheckoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create Stripe checkout session.
    
    Args:
        request: Checkout request with plan_type
        current_user: Authenticated user
        
    Returns:
        Checkout session URL
    """
    try:
        stripe_service = get_stripe_service()
        user_id = current_user["user_id"]
        email = current_user.get("email", "")
        
        # Get Stripe price ID for plan
        price_id = get_stripe_price_id(request.plan_type)
        if not price_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe price ID not configured for plan: {request.plan_type}"
            )
        
        # Create or get Stripe customer
        from backend.dependencies import get_db
        from fastapi import Depends
        from sqlalchemy.orm import Session
        
        # Note: This endpoint doesn't use dependency injection yet due to complex logic
        # Will be updated in a future refactor
        from backend.models.database import get_session
        db = get_session()
        try:
            plan_service = get_plan_service(db)
            user_plan = plan_service.get_user_plan(user_id)
        finally:
            db.close()
        customer_id = user_plan.stripe_customer_id if user_plan else None
        
        if not customer_id:
            # Create new customer
            customer = stripe_service.create_customer(email=email)
            customer_id = customer['customer_id']
        
        # Create checkout session
        session = stripe_service.create_checkout_session(
            price_id=price_id,
            user_id=user_id,
            customer_id=customer_id
        )
        
        return {
            "session_id": session["session_id"],
            "url": session["url"],
            "customer_id": customer_id,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature")
):
    """
    Handle Stripe webhook events.
    
    Args:
        request: FastAPI request
        stripe_signature: Stripe signature header
        
    Returns:
        Webhook processing result
    """
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    
    if not webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe webhook secret not configured"
        )
    
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature"
        )
    
    try:
        body = await request.body()
        if not STRIPE_MODULE_AVAILABLE or stripe is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stripe service is not available"
            )
        event = stripe.Webhook.construct_event(
            body, stripe_signature, webhook_secret
        )
        
        stripe_service = get_stripe_service()
        result = stripe_service.handle_webhook(event)
        
        # Update user plan if checkout completed
        if result.get('processed') and result.get('event_type') == 'checkout.session.completed':
            user_id = result.get('user_id')
            plan_type = result.get('plan_type')
            customer_id = result.get('customer_id')
            
            if user_id and plan_type:
                from backend.models.database import get_session
                db = get_session()
                try:
                    plan_service = get_plan_service(db)
                    plan_service.update_user_plan(
                        user_id=user_id,
                        plan_type=plan_type,
                        stripe_customer_id=customer_id,
                        stripe_subscription_id=result.get('subscription_id')
                    )
                finally:
                    db.close()
        
        return {"status": "success", "result": result}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid webhook: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )


@router.get("/subscription-status")
async def get_subscription_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's subscription status.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Subscription status and plan information
    """
    try:
        from backend.models.database import get_session
        db = get_session()
        try:
            plan_service = get_plan_service(db)
            user_id = current_user["user_id"]
            
            user_plan = plan_service.get_user_plan(user_id)
            usage_stats = plan_service.get_usage_stats(user_id)
        finally:
            db.close()
        
        plan_config = get_plan_config(user_plan.plan_type)
        
        return {
            "plan_type": user_plan.plan_type,
            "plan_name": plan_config.get('name', ''),
            "status": user_plan.status,
            "daily_limit": user_plan.daily_lead_limit,
            "monthly_price": user_plan.monthly_price,
            "price_per_lead": user_plan.price_per_lead,
            "stripe_subscription_id": user_plan.stripe_subscription_id,
            "stripe_customer_id": user_plan.stripe_customer_id,
            "usage": usage_stats,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription status: {str(e)}"
        )


@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel user's subscription.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Cancellation confirmation
    """
    try:
        plan_service = get_plan_service()
        stripe_service = get_stripe_service()
        user_id = current_user["user_id"]
        
        user_plan = plan_service.get_user_plan(user_id)
        
        if not user_plan.stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active subscription to cancel"
            )
        
        # Cancel in Stripe
        result = stripe_service.cancel_subscription(user_plan.stripe_subscription_id)
        
        # Update plan to free
        from backend.models.database import get_session
        db = get_session()
        try:
            plan_service = get_plan_service(db)
            plan_service.update_user_plan(user_id, 'free')
        finally:
            db.close()
        
        return {
            "status": "success",
            "message": "Subscription cancelled. Will remain active until period end.",
            "cancel_at_period_end": result.get('cancel_at_period_end'),
            "current_period_end": result.get('current_period_end'),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )

