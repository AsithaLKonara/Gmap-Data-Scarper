from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from models import Tenant, Users
from database import Session, get_db
from auth import create_access_token
from config import SECRET_KEY, ALGORITHM
from fastapi.responses import RedirectResponse, JSONResponse, Response
import logging
import os
import xml.etree.ElementTree as ET
from audit import log_audit_event

# --- SAML SSO Integration (scaffold) ---
# Only enable SAML logic if running in Docker/Linux (not macOS 12)
SAML_ENABLED = os.environ.get('SAML_ENABLED', '1') == '1' and not (os.uname().sysname == 'Darwin' and os.uname().release.startswith('21.'))

try:
    if SAML_ENABLED:
        from onelogin.saml2.auth import OneLogin_Saml2_Auth
        from onelogin.saml2.settings import OneLogin_Saml2_Settings
except ImportError:
    SAML_ENABLED = False

# Utility: Build SAML settings from tenant config
# (In production, load these from t.sso_config)
def build_saml_settings(tenant_config):
    # TODO: Map tenant_config to python3-saml settings dict
    return {
        'strict': True,
        'debug': True,
        'sp': {
            'entityId': tenant_config.get('sp_entity_id'),
            'assertionConsumerService': {
                'url': tenant_config.get('acs_url'),
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
            },
            'singleLogoutService': {
                'url': tenant_config.get('slo_url'),
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
            },
            'x509cert': '',
            'privateKey': '',
        },
        'idp': {
            'entityId': tenant_config.get('idp_entity_id'),
            'singleSignOnService': {
                'url': tenant_config.get('sso_url'),
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
            },
            'singleLogoutService': {
                'url': tenant_config.get('idp_slo_url'),
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
            },
            'x509cert': tenant_config.get('idp_cert'),
        },
    }

router = APIRouter(prefix="/api/auth/sso", tags=["sso"])

logger = logging.getLogger("sso")

# SSO endpoints are placeholders on macOS 12. SAML/SSO is only available in Docker or supported Linux environments.

class SSOLoginRequest(BaseModel):
    tenant: Optional[str] = None

class SSOCallbackRequest(BaseModel):
    saml_response: str
    tenant: Optional[str] = None

@router.get("/metadata", summary="Get SAML SP metadata", response_description="SAML SP metadata XML")
def sso_metadata(tenant: Optional[str] = None, db: Session = Depends(get_db)):
    """Return SAML SP metadata XML for the tenant (for IdP config)."""
    if not tenant:
        raise HTTPException(status_code=400, detail="Tenant slug required for SSO metadata")
    t = db.query(Tenant).filter_by(slug=tenant).first()
    if not t or not t.sso_config:
        raise HTTPException(status_code=404, detail="SSO not configured for this tenant")
    if not SAML_ENABLED:
        logger.info(f"[SSO] SAML not enabled or not supported on this platform.")
        raise HTTPException(status_code=501, detail="SSO not supported on this platform")
    saml_settings = build_saml_settings(t.sso_config)
    # Use python3-saml to generate metadata XML
    saml = OneLogin_Saml2_Settings(settings=saml_settings, sp_validation_only=True)
    metadata = saml.get_sp_metadata()
    errors = saml.validate_metadata(metadata)
    if errors:
        logger.error(f"[SSO] SAML metadata errors: {errors}")
        raise HTTPException(status_code=500, detail=f"SAML metadata error: {errors}")
    return Response(content=metadata, media_type="application/xml")

@router.get("/login", summary="Start SSO login", response_description="Redirect to SSO provider")
def sso_login(request: Request, tenant: Optional[str] = None, db: Session = Depends(get_db)):
    if not tenant:
        log_audit_event(db, None, "sso_login_failed", "sso", {"reason": "missing_tenant"})
        raise HTTPException(status_code=400, detail="Tenant slug required for SSO login")
    t = db.query(Tenant).filter_by(slug=tenant).first()
    if not t or not t.sso_config:
        log_audit_event(db, None, "sso_login_failed", "sso", {"reason": "not_configured", "tenant": tenant})
        raise HTTPException(status_code=404, detail="SSO not configured for this tenant")
    if not SAML_ENABLED:
        logger.info(f"[SSO] SAML not enabled or not supported on this platform.")
        log_audit_event(db, None, "sso_login_failed", "sso", {"reason": "not_supported", "tenant": tenant})
        raise HTTPException(status_code=501, detail="SSO login not supported on this platform")
    try:
        saml_settings = build_saml_settings(t.sso_config)
        saml = OneLogin_Saml2_Auth(request, old_settings=OneLogin_Saml2_Settings(settings=saml_settings, sp_validation_only=True))
        redirect_url = saml.login()
        logger.info(f"[SSO] Redirecting to SAML IdP for tenant: {tenant}")
        log_audit_event(db, None, "sso_login_redirect", "sso", {"tenant": tenant})
        return RedirectResponse(redirect_url)
    except Exception as e:
        logger.exception(f"[SSO] SSO login error: {e}")
        log_audit_event(db, None, "sso_login_failed", "sso", {"reason": str(e), "tenant": tenant})
        raise HTTPException(status_code=500, detail="SSO login failed")

@router.post("/callback", summary="SSO callback", response_description="Process SSO response and authenticate user")
def sso_callback(data: SSOCallbackRequest, db: Session = Depends(get_db)):
    if not data.tenant:
        log_audit_event(db, None, "sso_callback_failed", "sso", {"reason": "missing_tenant"})
        raise HTTPException(status_code=400, detail="Tenant slug required for SSO callback")
    t = db.query(Tenant).filter_by(slug=data.tenant).first()
    if not t or not t.sso_config:
        log_audit_event(db, None, "sso_callback_failed", "sso", {"reason": "not_configured", "tenant": data.tenant})
        raise HTTPException(status_code=404, detail="SSO not configured for this tenant")
    if not SAML_ENABLED:
        logger.info(f"[SSO] SAML not enabled or not supported on this platform.")
        log_audit_event(db, None, "sso_callback_failed", "sso", {"reason": "not_supported", "tenant": data.tenant})
        raise HTTPException(status_code=501, detail="SSO callback not supported on this platform")
    try:
        saml_settings = build_saml_settings(t.sso_config)
        saml_request = {
            'https': 'on',
            'http_host': 'localhost',
            'script_name': '/api/auth/sso/callback',
            'server_port': '443',
            'get_data': {},
            'post_data': {'SAMLResponse': data.saml_response},
        }
        saml = OneLogin_Saml2_Auth(saml_request, old_settings=OneLogin_Saml2_Settings(settings=saml_settings, sp_validation_only=True))
        saml.process_response()
        errors = saml.get_errors()
        if errors:
            logger.error(f"[SSO] SAML errors: {errors}")
            log_audit_event(db, None, "sso_callback_failed", "sso", {"reason": str(errors), "tenant": data.tenant})
            raise HTTPException(status_code=400, detail=f"SAML error: {errors}")
        if not saml.is_authenticated():
            log_audit_event(db, None, "sso_callback_failed", "sso", {"reason": "not_authenticated", "tenant": data.tenant})
            raise HTTPException(status_code=401, detail="SAML authentication failed")
        user_email = saml.get_nameid()
        if not user_email:
            log_audit_event(db, None, "sso_callback_failed", "sso", {"reason": "no_email", "tenant": data.tenant})
            raise HTTPException(status_code=400, detail="No email in SAML assertion")
        # Enhanced user provisioning: extract name, roles if present
        attributes = saml.get_attributes() if hasattr(saml, 'get_attributes') else {}
        user = db.query(Users).filter_by(email=user_email).first()
        if not user:
            user = Users(email=user_email, role='user', plan=t.plan)
            if attributes:
                user.name = attributes.get('name', [None])[0] or user_email
                # Optionally handle roles/groups
                if 'roles' in attributes:
                    user.roles = attributes['roles']
            db.add(user)
            db.commit()
        else:
            # Optionally update user info from SAML attributes
            updated = False
            if attributes:
                if 'name' in attributes and attributes['name'][0] != user.name:
                    user.name = attributes['name'][0]
                    updated = True
                if 'roles' in attributes:
                    user.roles = attributes['roles']
                    updated = True
            if updated:
                db.commit()
        token = create_access_token({"sub": str(user.id)})
        logger.info(f"[SSO] SAML login success for user: {user_email}")
        log_audit_event(db, user, "sso_login_success", "sso", {"tenant": data.tenant, "email": user_email})
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        logger.exception(f"[SSO] SSO callback error: {e}")
        log_audit_event(db, None, "sso_callback_failed", "sso", {"reason": str(e), "tenant": data.tenant})
        raise HTTPException(status_code=500, detail="SSO callback failed")

@router.get("/config", summary="Get SSO config", response_description="Get SSO configuration for tenant")
def get_sso_config(tenant: Optional[str] = None):
    return {"message": "SSO config not available on macOS 12. Use Docker or Linux for SSO support.", "tenant": tenant} 