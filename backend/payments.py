import os
import stripe
from fastapi import APIRouter, Request, HTTPException, Depends, Body, Query
from fastapi.responses import JSONResponse
from models import Users, Affiliates, Commissions
from database import SessionLocal
from auth import get_current_user
from datetime import datetime
from audit import audit_log
from pydantic import BaseModel, Field

STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter(prefix='/api/payments', tags=['payments'])

class CheckoutSessionResponse(BaseModel):
    checkout_url: str = Field(..., description="Stripe Checkout session URL.", example="https://checkout.stripe.com/pay/cs_test_123")

class WebhookResponse(BaseModel):
    status: str = Field(..., description="Status of the webhook processing.", example="success")
    error: str = Field(None, description="Error message if any.", example="Invalid signature")

class PlanStatusResponse(BaseModel):
    plan: str = Field(..., description="Current plan of the user.", example="pro")
    stripe_customer_id: str = Field(None, description="Stripe customer ID.", example="cus_123abc")
    stripe_subscription_id: str = Field(None, description="Stripe subscription ID.", example="sub_456def")

@router.post('/create-checkout-session', response_model=CheckoutSessionResponse, summary="Create Stripe Checkout session", description="Create a Stripe Checkout session for the selected plan.")
@audit_log(action="create_checkout_session", target_type="user")
def create_checkout_session(
    plan: str = Query(..., description="Plan to subscribe to (e.g., free, pro, business)", example="pro"),
    user: Users = Depends(get_current_user)
):
    """Create a Stripe Checkout session for the selected plan."""
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail='Stripe not configured')
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': os.getenv(f'STRIPE_PRICE_{plan.upper()}'),
                'quantity': 1,
            }],
            customer_email=user.email,
            success_url=f'{FRONTEND_URL}/billing/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{FRONTEND_URL}/billing/cancel',
            metadata={'user_id': user.id, 'plan': plan}
        )
        return CheckoutSessionResponse(checkout_url=session.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/webhook', response_model=WebhookResponse, summary="Stripe webhook endpoint", description="Stripe webhook endpoint for payment and subscription events.")
@audit_log(action="stripe_webhook", target_type="user")
async def stripe_webhook(request: Request):
    """Stripe webhook endpoint for payment and subscription events."""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        return WebhookResponse(status="error", error=str(e))
    # Handle event types
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata'].get('user_id')
        plan = session['metadata'].get('plan')
        db = SessionLocal()
        user = db.query(Users).filter(Users.id == int(user_id)).first()
        if user:
            user.plan = plan
            user.stripe_customer_id = session.get('customer')
            user.stripe_subscription_id = session.get('subscription')
            db.commit()
            # Affiliate commission logic
            # Assume user.affiliate_code or user.affiliate_id is set if referred
            affiliate_code = getattr(user, 'affiliate_code', None)
            if affiliate_code:
                affiliate = db.query(Affiliates).filter_by(code=affiliate_code).first()
                if affiliate:
                    commission_amount = 20.0  # USD, fixed for now
                    commission = Commissions(
                        affiliate_id=affiliate.id,
                        referred_user_id=user.id,
                        amount=commission_amount,
                        status='pending',
                        created_at=datetime.utcnow()
                    )
                    db.add(commission)
                    affiliate.total_earnings += commission_amount
                    db.commit()
        db.close()
    # Add more event handling as needed
    return WebhookResponse(status="success")

@router.get('/plan-status', response_model=PlanStatusResponse, summary="Get plan status", description="Get the current user's plan and Stripe subscription status.")
def get_plan_status(user: Users = Depends(get_current_user)):
    """Get the current user's plan and Stripe subscription status."""
    return PlanStatusResponse(
        plan=user.plan,
        stripe_customer_id=user.stripe_customer_id,
        stripe_subscription_id=user.stripe_subscription_id
    ) 