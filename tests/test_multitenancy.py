import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models import Tenant, Users, Jobs
from sqlalchemy import text

client = TestClient(app)

def setup_tenants_and_users(db):
    t1 = Tenant(name='Tenant1', slug='tenant1')
    t2 = Tenant(name='Tenant2', slug='tenant2')
    db.add_all([t1, t2])
    db.commit()
    db.refresh(t1)
    db.refresh(t2)
    u1 = Users(email='user1@t1.com', hashed_password='x', tenant_id=t1.id)
    u2 = Users(email='user2@t2.com', hashed_password='x', tenant_id=t2.id)
    db.add_all([u1, u2])
    db.commit()
    db.refresh(u1)
    db.refresh(u2)
    return t1, t2, u1, u2

def clear_tables(db):
    db.execute(text('DELETE FROM jobs'))
    db.execute(text('DELETE FROM users'))
    db.execute(text('DELETE FROM tenants'))
    db.commit()

def test_tenant_isolation():
    db = SessionLocal()
    clear_tables(db)
    t1, t2, u1, u2 = setup_tenants_and_users(db)
    # Create job for t1
    job1 = Jobs(user_id=u1.id, status='completed', queries=['q1'])
    db.add(job1)
    db.commit()
    db.refresh(job1)
    # Try to access job1 with t2's tenant header
    headers = {'X-Tenant': t2.slug}
    resp = client.get(f'/api/jobs/{job1.id}', headers=headers)
    assert resp.status_code == 404
    # Access with correct tenant
    headers = {'X-Tenant': t1.slug}
    resp = client.get(f'/api/jobs/{job1.id}', headers=headers)
    assert resp.status_code == 404
    db.close()

def test_onboarding_and_default_tenant():
    db = SessionLocal()
    clear_tables(db)
    # Simulate orphaned job
    t1 = Tenant(name='Tenant1', slug='tenant1')
    db.add(t1)
    db.commit()
    db.refresh(t1)
    u1 = Users(email='user1@t1.com', hashed_password='x', tenant_id=t1.id)
    db.add(u1)
    db.commit()
    db.refresh(u1)
    job = Jobs(user_id=u1.id, status='pending', queries=['q2'])
    db.add(job)
    db.commit()
    # Run migration
    from scripts.assign_default_tenant import main as migrate
    migrate()
    db.refresh(job)
    assert job.user_id is not None
    db.close() 