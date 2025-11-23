"""Consent management endpoints."""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from backend.services.consent_service import consent_service

router = APIRouter(prefix="/api/consent", tags=["consent"])


class ConsentRequest(BaseModel):
    """Consent request model."""
    user_id: str = None
    consent_version: str = "1.0"


class WithdrawalRequest(BaseModel):
    """Consent withdrawal request model."""
    user_id: str = None
    reason: str = None


@router.post("/record")
async def record_consent(request: Request, consent_req: ConsentRequest):
    """Record user consent."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    success = consent_service.record_consent(
        user_id=consent_req.user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        consent_version=consent_req.consent_version
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to record consent")
    
    return {"status": "success", "message": "Consent recorded"}


@router.post("/withdraw")
async def withdraw_consent(withdrawal_req: WithdrawalRequest):
    """Record consent withdrawal."""
    success = consent_service.record_withdrawal(
        user_id=withdrawal_req.user_id,
        reason=withdrawal_req.reason
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to record withdrawal")
    
    return {"status": "success", "message": "Withdrawal recorded"}


@router.get("/check")
async def check_consent(user_id: str = None):
    """Check if user has given consent."""
    has_consent = consent_service.has_consent(user_id=user_id)
    return {"has_consent": has_consent}


@router.get("/stats")
async def get_consent_stats():
    """Get consent statistics."""
    stats = consent_service.get_consent_stats()
    return stats

