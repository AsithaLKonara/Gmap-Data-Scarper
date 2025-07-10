from fastapi import Security

# Placeholder: In production, check tenant admin role

def tenant_admin_required():
    return True

@router.get("/{tenant_id}/sso_config", response_model=dict)
def get_tenant_sso_config(tenant_id: int, db: Session = Depends(get_db), _: bool = Depends(tenant_admin_required)):
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant.sso_config or {}

class SSOConfigUpdate(BaseModel):
    sso_config: dict

@router.put("/{tenant_id}/sso_config", response_model=dict)
def update_tenant_sso_config(tenant_id: int, data: SSOConfigUpdate, db: Session = Depends(get_db), _: bool = Depends(tenant_admin_required)):
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.sso_config = data.sso_config
    db.commit()
    return tenant.sso_config 

class PlanUpdate(BaseModel):
    plan: str
    plan_expiry: Optional[str] = None

@router.get("/{tenant_id}/plan", response_model=dict)
def get_tenant_plan(tenant_id: int, db: Session = Depends(get_db), _: bool = Depends(tenant_admin_required)):
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"plan": tenant.plan, "plan_expiry": tenant.plan_expiry}

@router.put("/{tenant_id}/plan", response_model=dict)
def update_tenant_plan(tenant_id: int, data: PlanUpdate, db: Session = Depends(get_db), _: bool = Depends(tenant_admin_required)):
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.plan = data.plan
    tenant.plan_expiry = data.plan_expiry
    db.commit()
    return {"plan": tenant.plan, "plan_expiry": tenant.plan_expiry}

class BillingUpdate(BaseModel):
    billing_email: Optional[str]
    billing_customer_id: Optional[str]

@router.get("/{tenant_id}/billing", response_model=dict)
def get_tenant_billing(tenant_id: int, db: Session = Depends(get_db), _: bool = Depends(tenant_admin_required)):
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"billing_email": tenant.billing_email, "billing_customer_id": tenant.billing_customer_id}

@router.put("/{tenant_id}/billing", response_model=dict)
def update_tenant_billing(tenant_id: int, data: BillingUpdate, db: Session = Depends(get_db), _: bool = Depends(tenant_admin_required)):
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.billing_email = data.billing_email
    tenant.billing_customer_id = data.billing_customer_id
    db.commit()
    return {"billing_email": tenant.billing_email, "billing_customer_id": tenant.billing_customer_id} 