from backend.database import SessionLocal
from backend.models import Tenant, Users, SupportTicket

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
    # 2. Assign orphaned records (only models with tenant_id field)
    models = [Users, SupportTicket]
    for model in models:
        orphaned = db.query(model).filter((model.tenant_id == None) | (model.tenant_id == 0)).all()
        for record in orphaned:
            record.tenant_id = default_tenant.id
        db.commit()
        print(f'Assigned {len(orphaned)} orphaned {model.__tablename__} to default tenant')
    db.close()

if __name__ == '__main__':
    main() 