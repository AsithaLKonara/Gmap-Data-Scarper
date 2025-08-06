#!/usr/bin/env python3
"""
Simple test script to debug backend startup issues
"""

import sys
import traceback

def test_imports():
    """Test all imports step by step"""
    print("🔍 Testing imports...")
    
    try:
        print("  ✅ Testing basic imports...")
        import os
        import fastapi
        print(f"  ✅ FastAPI version: {fastapi.__version__}")
        
        print("  ✅ Testing SQLAlchemy...")
        import sqlalchemy
        print(f"  ✅ SQLAlchemy version: {sqlalchemy.__version__}")
        
        print("  ✅ Testing database config...")
        from config import DATABASE_URL
        print(f"  ✅ Database URL: {DATABASE_URL}")
        
        print("  ✅ Testing database connection...")
        from database import engine, Base
        print("  ✅ Database engine created")
        
        print("  ✅ Testing main app...")
        from main import app
        print("  ✅ Main app imported successfully!")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        print(f"  📍 Location: {traceback.format_exc()}")
        return False

def test_endpoints():
    """Test basic endpoints"""
    print("\n🔍 Testing endpoints...")
    
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        print(f"  ✅ Root endpoint: {response.status_code}")
        
        # Test health endpoint
        response = client.get("/api/health")
        print(f"  ✅ Health endpoint: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Backend Test Script")
    print("=" * 50)
    
    success = test_imports()
    
    if success:
        test_endpoints()
        print("\n✅ All tests passed! Backend is ready.")
    else:
        print("\n❌ Tests failed. Check the errors above.")
        sys.exit(1) 
 
"""
Simple test script to debug backend startup issues
"""

import sys
import traceback

def test_imports():
    """Test all imports step by step"""
    print("🔍 Testing imports...")
    
    try:
        print("  ✅ Testing basic imports...")
        import os
        import fastapi
        print(f"  ✅ FastAPI version: {fastapi.__version__}")
        
        print("  ✅ Testing SQLAlchemy...")
        import sqlalchemy
        print(f"  ✅ SQLAlchemy version: {sqlalchemy.__version__}")
        
        print("  ✅ Testing database config...")
        from config import DATABASE_URL
        print(f"  ✅ Database URL: {DATABASE_URL}")
        
        print("  ✅ Testing database connection...")
        from database import engine, Base
        print("  ✅ Database engine created")
        
        print("  ✅ Testing main app...")
        from main import app
        print("  ✅ Main app imported successfully!")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        print(f"  📍 Location: {traceback.format_exc()}")
        return False

def test_endpoints():
    """Test basic endpoints"""
    print("\n🔍 Testing endpoints...")
    
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        print(f"  ✅ Root endpoint: {response.status_code}")
        
        # Test health endpoint
        response = client.get("/api/health")
        print(f"  ✅ Health endpoint: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Backend Test Script")
    print("=" * 50)
    
    success = test_imports()
    
    if success:
        test_endpoints()
        print("\n✅ All tests passed! Backend is ready.")
    else:
        print("\n❌ Tests failed. Check the errors above.")
        sys.exit(1) 
 
"""
Simple test script to debug backend startup issues
"""

import sys
import traceback

def test_imports():
    """Test all imports step by step"""
    print("🔍 Testing imports...")
    
    try:
        print("  ✅ Testing basic imports...")
        import os
        import fastapi
        print(f"  ✅ FastAPI version: {fastapi.__version__}")
        
        print("  ✅ Testing SQLAlchemy...")
        import sqlalchemy
        print(f"  ✅ SQLAlchemy version: {sqlalchemy.__version__}")
        
        print("  ✅ Testing database config...")
        from config import DATABASE_URL
        print(f"  ✅ Database URL: {DATABASE_URL}")
        
        print("  ✅ Testing database connection...")
        from database import engine, Base
        print("  ✅ Database engine created")
        
        print("  ✅ Testing main app...")
        from main import app
        print("  ✅ Main app imported successfully!")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        print(f"  📍 Location: {traceback.format_exc()}")
        return False

def test_endpoints():
    """Test basic endpoints"""
    print("\n🔍 Testing endpoints...")
    
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        print(f"  ✅ Root endpoint: {response.status_code}")
        
        # Test health endpoint
        response = client.get("/api/health")
        print(f"  ✅ Health endpoint: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Backend Test Script")
    print("=" * 50)
    
    success = test_imports()
    
    if success:
        test_endpoints()
        print("\n✅ All tests passed! Backend is ready.")
    else:
        print("\n❌ Tests failed. Check the errors above.")
        sys.exit(1) 
 