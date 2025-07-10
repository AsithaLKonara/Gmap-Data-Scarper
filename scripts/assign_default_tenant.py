from backend.database import SessionLocal
from backend.models import Tenant, User, Job, Lead, CRMRecord, AnalyticsEvent, Notification, SavedQuery, SupportTicket, ApiKey

def main():
    db = SessionLocal()
    # 1. Create Default Tenant if not exists
    default_slug = 'default'
    default_tenant = db.query(Tenant).filter_by(slug=default_slug).first()
    if not default_tenant:
        default_tenant = Tenant(name='Default Tenant', slug=default_slug)
        db.add(default_tenant)
        db.commit()
        db.refresh(default_tenant)
        print('Created Default Tenant')
    else:
        print('Default Tenant already exists')
    # 2. Assign orphaned records
    models = [User, Job, Lead, CRMRecord, AnalyticsEvent, Notification, SavedQuery, SupportTicket, ApiKey]
    for model in models:
        orphaned = db.query(model).filter((model.tenant_id == None) | (model.tenant_id == 0)).all()
        for record in orphaned:
            record.tenant_id = default_tenant.id
        if orphaned:
            db.commit()
        print(f'Assigned {len(orphaned)} {model.__name__} records to Default Tenant')
    db.close()

if __name__ == '__main__':
    main() 