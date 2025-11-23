"""Database migration script for new tables."""
from sqlalchemy import create_engine, text
from backend.models.database import Base, get_database_url
from backend.models.team import Team, SharedLeadList, TeamActivity, team_members
from backend.models.workflow import Workflow, WorkflowExecution
from backend.models.scheduled_report import ScheduledReport
import os


def create_migrations():
    """Create all new database tables."""
    database_url = get_database_url()
    engine = create_engine(database_url)
    
    print("Creating database migrations...")
    print(f"Database URL: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    
    try:
        # Create all tables
        print("\n1. Creating team-related tables...")
        Base.metadata.create_all(
            engine,
            tables=[
                Team.__table__,
                SharedLeadList.__table__,
                TeamActivity.__table__,
                team_members
            ]
        )
        print("   ✅ Teams, SharedLeadList, TeamActivity, team_members")
        
        print("\n2. Creating workflow tables...")
        Base.metadata.create_all(
            engine,
            tables=[
                Workflow.__table__,
                WorkflowExecution.__table__
            ]
        )
        print("   ✅ Workflows, WorkflowExecutions")
        
        print("\n3. Creating scheduled report tables...")
        Base.metadata.create_all(
            engine,
            tables=[
                ScheduledReport.__table__
            ]
        )
        print("   ✅ ScheduledReports")
        
        # Verify tables exist
        print("\n4. Verifying tables...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name IN (
                    'teams', 'shared_lead_lists', 'team_activities', 'team_members',
                    'workflows', 'workflow_executions',
                    'scheduled_reports'
                )
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            expected_tables = [
                'teams', 'shared_lead_lists', 'team_activities', 'team_members',
                'workflows', 'workflow_executions',
                'scheduled_reports'
            ]
            
            missing = [t for t in expected_tables if t not in tables]
            if missing:
                print(f"   ⚠️  Missing tables: {missing}")
            else:
                print(f"   ✅ All {len(tables)} tables created successfully")
        
        print("\n✅ Migration complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = create_migrations()
    exit(0 if success else 1)

