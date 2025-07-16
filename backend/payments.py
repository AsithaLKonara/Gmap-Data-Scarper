import os
import stripe
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from models import User
from database import SessionLocal
from auth import get_current_user

STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter(prefix='/api/payments', tags=['payments'])

@router.post('/create-checkout-session')
def create_checkout_session(plan: str, user: User = Depends(get_current_user)):
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
        return {'checkout_url': session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/webhook')
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        return JSONResponse(status_code=400, content={'error': str(e)})
    # Handle event types
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata'].get('user_id')
        plan = session['metadata'].get('plan')
        db = SessionLocal()
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user:
            user.plan = plan
            user.stripe_customer_id = session.get('customer')
            user.stripe_subscription_id = session.get('subscription')
            db.commit()
        db.close()
    # Add more event handling as needed
    return {'status': 'success'}

@router.get('/plan-status')
def get_plan_status(user: User = Depends(get_current_user)):
    return {'plan': user.plan, 'stripe_customer_id': user.stripe_customer_id, 'stripe_subscription_id': user.stripe_subscription_id} 