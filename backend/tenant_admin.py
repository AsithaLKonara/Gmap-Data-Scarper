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