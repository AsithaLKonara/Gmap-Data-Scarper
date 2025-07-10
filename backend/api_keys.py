from tenant_utils import get_tenant_record_or_403

@router.get("/api_keys/{key_id}", ...)
def get_api_key(key_id: int, request: Request, db: Session = Depends(get_db)):
    tenant = get_tenant_from_request(request, db)
    key = get_tenant_record_or_403(ApiKey, key_id, tenant.id, db)
    return key 