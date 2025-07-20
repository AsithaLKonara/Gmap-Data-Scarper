#!/usr/bin/env python3
"""
Database initialization script for LeadTap
Creates all tables and seeds initial data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal
from models import Base, Users, Plans, Jobs, Leads, ApiKeys, Webhooks, SavedQueries, Notifications, Analytics, Payments, Teams, TeamMembers, Integrations, AuditLogs, Referrals, AffiliateLinks, Widgets, SSOConfigs, Branding, SocialMediaAccounts, WhatsAppWorkflows, ROIProjects, LeadScoringRules, ShowcaseProjects
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import hashlib
import secrets

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")

def seed_default_plans():
    """Seed default subscription plans"""
    print("Seeding default plans...")
    db = SessionLocal()
    try:
        # Check if plans already exist
        existing_plans = db.query(Plans).count()
        if existing_plans > 0:
            print("Plans already exist, skipping...")
            return

        plans = [
            Plans(
                name="Free",
                type="free",
                price=0.0,
                max_queries_per_day=10,
                max_results_per_query=50,
                max_leads=100,
                features={
                    "csv_export": True,
                    "basic_analytics": True,
                    "email_support": False,
                    "api_access": False,
                    "webhooks": False,
                    "team_management": False,
                    "advanced_filters": False,
                    "priority_support": False
                }
            ),
            Plans(
                name="Pro",
                type="pro",
                price=29.99,
                max_queries_per_day=100,
                max_results_per_query=200,
                max_leads=1000,
                features={
                    "csv_export": True,
                    "json_export": True,
                    "xlsx_export": True,
                    "basic_analytics": True,
                    "advanced_analytics": True,
                    "email_support": True,
                    "api_access": True,
                    "webhooks": True,
                    "team_management": False,
                    "advanced_filters": True,
                    "priority_support": False
                }
            ),
            Plans(
                name="Business",
                type="business",
                price=99.99,
                max_queries_per_day=500,
                max_results_per_query=500,
                max_leads=5000,
                features={
                    "csv_export": True,
                    "json_export": True,
                    "xlsx_export": True,
                    "pdf_export": True,
                    "basic_analytics": True,
                    "advanced_analytics": True,
                    "enhanced_analytics": True,
                    "email_support": True,
                    "phone_support": True,
                    "api_access": True,
                    "webhooks": True,
                    "team_management": True,
                    "advanced_filters": True,
                    "priority_support": True,
                    "sso": True,
                    "custom_branding": True
                }
            ),
            Plans(
                name="Enterprise",
                type="enterprise",
                price=299.99,
                max_queries_per_day=2000,
                max_results_per_query=1000,
                max_leads=20000,
                features={
                    "csv_export": True,
                    "json_export": True,
                    "xlsx_export": True,
                    "pdf_export": True,
                    "basic_analytics": True,
                    "advanced_analytics": True,
                    "enhanced_analytics": True,
                    "email_support": True,
                    "phone_support": True,
                    "dedicated_support": True,
                    "api_access": True,
                    "webhooks": True,
                    "team_management": True,
                    "advanced_filters": True,
                    "priority_support": True,
                    "sso": True,
                    "custom_branding": True,
                    "white_label": True,
                    "custom_integrations": True
                }
            )
        ]
        
        db.add_all(plans)
        db.commit()
        print("✅ Default plans seeded successfully!")
    except Exception as e:
        print(f"❌ Error seeding plans: {e}")
        db.rollback()
    finally:
        db.close()

def seed_sample_data():
    """Seed sample data for testing"""
    print("Seeding sample data...")
    db = SessionLocal()
    try:
        # Create a sample user
        sample_user = Users(
            email="demo@leadtap.com",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KqQKqK",  # password: demo123
            full_name="Demo User",
            role="user",
            is_active=True,
            is_verified=True,
            plan_id=2,  # Pro plan
            tenant_id="demo-tenant-001"
        )
        db.add(sample_user)
        db.commit()
        
        # Create sample jobs
        sample_jobs = [
            Jobs(
                user_id=sample_user.id,
                status="completed",
                queries=["restaurants in New York", "coffee shops in Manhattan"],
                results_count=45,
                completed_at=datetime.now() - timedelta(days=1)
            ),
            Jobs(
                user_id=sample_user.id,
                status="completed",
                queries=["dentists in Los Angeles", "orthodontists in Beverly Hills"],
                results_count=32,
                completed_at=datetime.now() - timedelta(days=2)
            ),
            Jobs(
                user_id=sample_user.id,
                status="running",
                queries=["lawyers in Chicago", "attorneys in downtown Chicago"],
                results_count=0
            )
        ]
        db.add_all(sample_jobs)
        db.commit()
        
        # Create sample leads
        sample_leads = [
            Leads(
                user_id=sample_user.id,
                name="Joe's Pizza",
                email="contact@joespizza.com",
                phone="+1-555-0123",
                company="Joe's Pizza & Restaurant",
                website="https://joespizza.com",
                status="new",
                source="gmaps",
                score=85.5,
                notes="Popular pizza place with good reviews"
            ),
            Leads(
                user_id=sample_user.id,
                name="Starbucks Coffee",
                email="manager@starbucks.com",
                phone="+1-555-0456",
                company="Starbucks Corporation",
                website="https://starbucks.com",
                status="contacted",
                source="gmaps",
                score=92.0,
                notes="Major coffee chain, high potential"
            ),
            Leads(
                user_id=sample_user.id,
                name="Dr. Sarah Johnson",
                email="sarah.johnson@dentalcare.com",
                phone="+1-555-0789",
                company="Dental Care Associates",
                website="https://dentalcareassociates.com",
                status="qualified",
                source="gmaps",
                score=78.5,
                notes="Experienced dentist with good patient reviews"
            )
        ]
        db.add_all(sample_leads)
        db.commit()
        
        # Create sample API key
        api_key = ApiKeys(
            user_id=sample_user.id,
            key_hash=hashlib.sha256(f"demo-api-key-{secrets.token_urlsafe(32)}".encode()).hexdigest(),
            name="Demo API Key",
            is_active=True,
            last_used=datetime.now() - timedelta(hours=2)
        )
        db.add(api_key)
        db.commit()
        
        # Create sample webhook
        webhook = Webhooks(
            user_id=sample_user.id,
            url="https://demo-app.com/webhooks/leadtap",
            secret=secrets.token_urlsafe(32),
            events=["job_completed", "lead_added"],
            is_active=True
        )
        db.add(webhook)
        db.commit()
        
        # Create sample notifications
        notifications = [
            Notifications(
                user_id=sample_user.id,
                type="job_completed",
                title="Job Completed",
                message="Your job 'restaurants in New York' has been completed successfully.",
                is_read=False
            ),
            Notifications(
                user_id=sample_user.id,
                type="plan_upgrade",
                title="Plan Upgrade Available",
                message="Upgrade to Business plan for unlimited queries and advanced features.",
                is_read=True
            )
        ]
        db.add_all(notifications)
        db.commit()
        
        print("✅ Sample data seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding sample data: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main initialization function"""
    print("🚀 Initializing LeadTap Database...")
    
    try:
        create_tables()
        seed_default_plans()
        seed_sample_data()
        
        print("\n🎉 Database initialization completed successfully!")
        print("\n📊 Summary:")
        print("- All tables created")
        print("- Default plans seeded")
        print("- Sample data added")
        print("\n🔗 You can now start the application!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 