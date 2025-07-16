from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from auth import get_current_user
from security import check_permission
from sqlalchemy.orm import Session
from database import get_db
from audit import audit_log

router = APIRouter(prefix="/api/tenant-admin", tags=["tenant-admin"])

class SSOConfigUpdate(BaseModel):
    sso_config: Dict[str, Any] = Field(..., description="SSO configuration dictionary for the tenant.", example={"provider": "okta", "client_id": "abc123"})

class SSOConfigOut(BaseModel):
    sso_config: Dict[str, Any] = Field(..., description="Current SSO configuration for the tenant.", example={"provider": "okta", "client_id": "abc123"})

@router.get("/{tenant_id}/sso_config", response_model=SSOConfigOut, summary="Get SSO config for tenant", description="Retrieve the SSO (Single Sign-On) configuration for a specific tenant.")
def get_tenant_sso_config(
    tenant_id: int = Field(..., description="ID of the tenant."),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Get the SSO configuration for a tenant."""
    if not check_permission(user, "tenant", "admin", db):
        raise HTTPException(status_code=403, detail="Tenant admin access required")
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"sso_config": tenant.sso_config or {}}

@router.put("/{tenant_id}/sso_config", response_model=SSOConfigOut, summary="Update SSO config for tenant", description="Update the SSO (Single Sign-On) configuration for a specific tenant.")
@audit_log(action="update_tenant_sso_config", target_type="tenant", target_id_param="tenant_id")
def update_tenant_sso_config(
    tenant_id: int = Field(..., description="ID of the tenant."),
    data: SSOConfigUpdate = ...,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Update the SSO configuration for a tenant."""
    if not check_permission(user, "tenant", "admin", db):
        raise HTTPException(status_code=403, detail="Tenant admin access required")
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.sso_config = data.sso_config
    db.commit()
    return {"sso_config": tenant.sso_config}

class PlanUpdate(BaseModel):
    plan: str = Field(..., description="Plan name for the tenant.", example="pro")
    plan_expiry: Optional[str] = Field(None, description="Plan expiry date (ISO format).", example="2024-12-31T23:59:59Z")

class PlanOut(BaseModel):
    plan: str = Field(..., description="Current plan name.", example="pro")
    plan_expiry: Optional[str] = Field(None, description="Plan expiry date (ISO format).", example="2024-12-31T23:59:59Z")

@router.get("/{tenant_id}/plan", response_model=PlanOut, summary="Get tenant plan", description="Retrieve the current subscription plan and expiry for a tenant.")
def get_tenant_plan(
    tenant_id: int = Field(..., description="ID of the tenant."),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Get the current plan and expiry for a tenant."""
    if not check_permission(user, "tenant", "admin", db):
        raise HTTPException(status_code=403, detail="Tenant admin access required")
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"plan": tenant.plan, "plan_expiry": tenant.plan_expiry}

@router.put("/{tenant_id}/plan", response_model=PlanOut, summary="Update tenant plan", description="Update the subscription plan and expiry for a tenant.")
@audit_log(action="update_tenant_plan", target_type="tenant", target_id_param="tenant_id")
def update_tenant_plan(
    tenant_id: int = Field(..., description="ID of the tenant."),
    data: PlanUpdate = ...,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Update the plan and expiry for a tenant."""
    if not check_permission(user, "tenant", "admin", db):
        raise HTTPException(status_code=403, detail="Tenant admin access required")
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.plan = data.plan
    tenant.plan_expiry = data.plan_expiry
    db.commit()
    return {"plan": tenant.plan, "plan_expiry": tenant.plan_expiry}

class BillingUpdate(BaseModel):
    billing_email: Optional[str] = Field(None, description="Billing email address for the tenant.", example="billing@example.com")
    billing_customer_id: Optional[str] = Field(None, description="Billing customer ID (from payment provider).", example="cus_123456789")

class BillingOut(BaseModel):
    billing_email: Optional[str] = Field(None, description="Billing email address for the tenant.", example="billing@example.com")
    billing_customer_id: Optional[str] = Field(None, description="Billing customer ID (from payment provider).", example="cus_123456789")

@router.get("/{tenant_id}/billing", response_model=BillingOut, summary="Get tenant billing info", description="Retrieve the billing information for a tenant.")
def get_tenant_billing(
    tenant_id: int = Field(..., description="ID of the tenant."),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Get the billing information for a tenant."""
    if not check_permission(user, "tenant", "admin", db):
        raise HTTPException(status_code=403, detail="Tenant admin access required")
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"billing_email": tenant.billing_email, "billing_customer_id": tenant.billing_customer_id}

@router.put("/{tenant_id}/billing", response_model=BillingOut, summary="Update tenant billing info", description="Update the billing information for a tenant.")
@audit_log(action="update_tenant_billing", target_type="tenant", target_id_param="tenant_id")
def update_tenant_billing(
    tenant_id: int = Field(..., description="ID of the tenant."),
    data: BillingUpdate = ...,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Update the billing information for a tenant."""
    if not check_permission(user, "tenant", "admin", db):
        raise HTTPException(status_code=403, detail="Tenant admin access required")
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.billing_email = data.billing_email
    tenant.billing_customer_id = data.billing_customer_id
    db.commit()
    return {"billing_email": tenant.billing_email, "billing_customer_id": tenant.billing_customer_id} 