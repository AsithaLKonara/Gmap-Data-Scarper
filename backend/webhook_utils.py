import requests
from models import Webhook
from sqlalchemy.orm import Session
from datetime import datetime

def send_webhook_event(event: str, payload: dict, user_id: int, db: Session):
    """
    Send webhooks for a given event and user. POSTs the payload to all active webhooks for the event.
    """
    webhooks = db.query(Webhook).filter_by(user_id=user_id, event=event, is_active=True).all()
    for webhook in webhooks:
        try:
            headers = {"Content-Type": "application/json"}
            if webhook.secret:
                # Simple signature (can be improved)
                import hmac, hashlib
                import json as _json
                body = _json.dumps(payload).encode()
                signature = hmac.new(webhook.secret.encode(), body, hashlib.sha256).hexdigest()
                headers["X-Webhook-Signature"] = signature
            resp = requests.post(webhook.url, json=payload, headers=headers, timeout=5)
            webhook.last_delivery_status = f"{resp.status_code}"
            webhook.last_delivery_at = datetime.utcnow()
        except Exception as e:
            webhook.last_delivery_status = f"error: {e}"
            webhook.last_delivery_at = datetime.utcnow()
        db.commit() 