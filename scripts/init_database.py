#!/usr/bin/env python3
"""
Initialize database with all models including PushSubscription.
Run this script to ensure all database tables are created.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def init_database():
    """Initialize database with all models."""
    print("🗄️  Initializing database...")
    
    try:
        # Import all models to ensure they're registered with SQLAlchemy
        from backend.models.database import Base, init_db, get_engine
        from backend.models.push_subscription import PushSubscription
        from backend.models.database import Lead, Task
        
        print("✅ All models imported successfully")
        print("   - Lead")
        print("   - Task")
        print("   - PushSubscription")
        
        # Initialize database (creates all tables)
        init_db()
        
        print("✅ Database tables created successfully!")
        
        # Verify tables exist
        from sqlalchemy import inspect
        engine = get_engine()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📊 Found {len(tables)} tables:")
        for table in sorted(tables):
            print(f"   - {table}")
        
        # Check for required tables
        required_tables = ['leads', 'tasks', 'push_subscriptions']
        missing = [t for t in required_tables if t not in tables]
        
        if missing:
            print(f"\n⚠️  Warning: Missing tables: {', '.join(missing)}")
            return False
        else:
            print("\n✅ All required tables exist!")
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)


