from fastapi import APIRouter, Request, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from config import FRONTEND_URL
from models import User
from database import get_db
from auth import get_current_user
import os
import hashlib
import hmac

router = APIRouter(prefix="/api/payhere", tags=["payhere"])

PAYHERE_MERCHANT_ID = os.getenv('PAYHERE_MERCHANT_ID', '121XXXX')
PAYHERE_MERCHANT_SECRET = os.getenv('PAYHERE_MERCHANT_SECRET', 'sandboxSecret')
PAYHERE_BASE_URL = os.getenv('PAYHERE_BASE_URL', 'https://sandbox.payhere.lk/pay/checkout')

PLANS = {
    'pro': {'amount': 9, 'name': 'Pro'},
    'business': {'amount': 49, 'name': 'Business'}
}

@router.post("/create-session")
def create_payhere_session(plan: str = Form(...), user=Depends(get_current_user)):
    if plan not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    order_id = f"{user.id}-{plan}-{os.urandom(4).hex()}"
    amount = PLANS[plan]['amount']
    payload = {
        'merchant_id': PAYHERE_MERCHANT_ID,
        'return_url': f'{FRONTEND_URL}/payment-success',
        'cancel_url': f'{FRONTEND_URL}/payment-cancel',
        'notify_url': f'{FRONTEND_URL}/api/payhere/notify',
        'order_id': order_id,
        'items': PLANS[plan]['name'],
        'currency': 'USD',
        'amount': amount,
        'first_name': user.email.split('@')[0],
        'last_name': 'User',
        'email': user.email,
        'phone': '0000000000',
        'address': 'N/A',
        'city': 'N/A',
        'country': 'Sri Lanka',
    }
    # The frontend should POST this payload to PayHere
    return {'payhere_url': PAYHERE_BASE_URL, 'payload': payload}

@router.post("/notify")
def payhere_notify(
    merchant_id: str = Form(...),
    order_id: str = Form(...),
    payment_id: str = Form(...),
    payhere_amount: str = Form(...),
    payhere_currency: str = Form(...),
    status_code: str = Form(...),
    md5sig: str = Form(...),
    method: str = Form(None),
    db: Session = Depends(get_db)
):
    # Validate signature
    local_md5sig = hashlib.md5((merchant_id + order_id + payhere_amount + payhere_currency + status_code + PAYHERE_MERCHANT_SECRET).encode()).hexdigest().upper()
    if md5sig != local_md5sig:
        raise HTTPException(status_code=400, detail="Invalid signature")
    # Only process completed payments
    if status_code == '2':
        # Extract user_id and plan from order_id
        try:
            user_id, plan, _ = order_id.split('-', 2)
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user and plan in PLANS:
                user.plan = plan
                db.commit()
        except Exception:
            pass
    return {"status": "ok"} 