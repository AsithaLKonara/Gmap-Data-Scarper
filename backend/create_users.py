from database import engine, SessionLocal
from models import User, Base
from auth import get_password_hash

def create_default_users():
    print("🚀 [SETUP] Starting user creation process...")
    
    # Create tables
    print("📋 [SETUP] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ [SETUP] Database tables created successfully")
    
    # Create database session
    print("🔗 [SETUP] Creating database session...")
    db = SessionLocal()
    
    try:
        # Check if users already exist
        print("🔍 [SETUP] Checking for existing users...")
        existing_user = db.query(User).filter(User.email == "user@leadtap.com").first()
        existing_admin = db.query(User).filter(User.email == "admin@leadtap.com").first()
        
        # Create user account
        if not existing_user:
            print("👤 [SETUP] Creating regular user account...")
            user = User(
                email="user@leadtap.com",
                hashed_password=get_password_hash("1234"),
                plan="free"
            )
            db.add(user)
            print("✅ [SETUP] Created user account: user@leadtap.com / 1234")
        else:
            print("ℹ️ [SETUP] User account already exists: user@leadtap.com")
        
        # Create admin account
        if not existing_admin:
            print("👑 [SETUP] Creating admin account...")
            admin = User(
                email="admin@leadtap.com",
                hashed_password=get_password_hash("1234"),
                plan="business"
            )
            db.add(admin)
            print("✅ [SETUP] Created admin account: admin@leadtap.com / 1234")
        else:
            print("ℹ️ [SETUP] Admin account already exists: admin@leadtap.com")
        
        # Commit changes
        print("💾 [SETUP] Committing changes to database...")
        db.commit()
        print("🎉 [SETUP] Default users created successfully!")
        
        # Verify users in database
        print("🔍 [SETUP] Verifying users in database...")
        all_users = db.query(User).all()
        print(f"📊 [SETUP] Total users in database: {len(all_users)}")
        for user in all_users:
            print(f"👤 [SETUP] User - ID: {user.id}, Email: {user.email}, Plan: {user.plan}")
        
    except Exception as e:
        print(f"❌ [SETUP] Error creating users: {e}")
        db.rollback()
    finally:
        print("🔗 [SETUP] Closing database session...")
        db.close()

if __name__ == "__main__":
    create_default_users() 