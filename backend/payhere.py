from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Tenant
from database import get_db
import os

router = APIRouter(prefix="/api/payhere", tags=["payhere"])

PAYHERE_MERCHANT_ID = os.getenv('PAYHERE_MERCHANT_ID')
PAYHERE_RETURN_URL = os.getenv('PAYHERE_RETURN_URL', 'https://yourapp.com/payhere/return')
PAYHERE_CANCEL_URL = os.getenv('PAYHERE_CANCEL_URL', 'https://yourapp.com/payhere/cancel')
PAYHERE_NOTIFY_URL = os.getenv('PAYHERE_NOTIFY_URL', 'https://yourapp.com/api/payhere/webhook')

@router.post("/create-session", response_model=dict)
async def create_payhere_session(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    plan = data.get('plan')
    tenant_id = data.get('tenant_id')
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    # Prepare PayHere payment params
    params = {
        'merchant_id': PAYHERE_MERCHANT_ID,
        'return_url': PAYHERE_RETURN_URL,
        'cancel_url': PAYHERE_CANCEL_URL,
        'notify_url': PAYHERE_NOTIFY_URL,
        'order_id': f"tenant-{tenant.id}-{plan}",
        'items': f"{plan} Plan Subscription",
        'amount': '0',  # Set plan price here
        'currency': 'LKR',
        'first_name': tenant.name,
        'last_name': '',
        'email': tenant.billing_email or '',
        'address': '',
        'city': '',
        'country': 'Sri Lanka',
        'custom_1': tenant.id,
    }
    # Return PayHere form URL (or redirect URL)
    payhere_url = f"https://www.payhere.lk/pay/checkout?{'&'.join([f'{k}={v}' for k,v in params.items()])}"
    return {"payhere_url": payhere_url}

@router.post("/webhook", response_model=dict)
async def payhere_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.form()
    order_id = data.get('order_id')
    status_code = data.get('status_code')
    plan = None
    tenant_id = None
    if order_id and order_id.startswith('tenant-'):
        parts = order_id.split('-')
        tenant_id = int(parts[1])
        plan = parts[2]
    if status_code == '2' and tenant_id and plan:
        tenant = db.query(Tenant).get(tenant_id)
        if tenant:
            tenant.plan = plan
            # Optionally set plan_expiry, etc.
            db.commit()
    return {"ok": True} 