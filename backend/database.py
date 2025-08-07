from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from config import DATABASE_URL
import logging
import os

logger = logging.getLogger(__name__)

# Database engine configuration for production
def create_database_engine():
    """Create database engine with production optimizations"""
    try:
        # Parse database URL to determine type
        if DATABASE_URL.startswith('postgresql://'):
            # PostgreSQL configuration
            engine = create_engine(
                DATABASE_URL,
                poolclass=QueuePool,
                pool_size=20,  # Number of connections to maintain
                max_overflow=30,  # Additional connections when pool is full
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,  # Recycle connections every hour
                echo=False  # Set to True for SQL logging in development
            )
            logger.info("✅ PostgreSQL database engine created successfully")
        elif DATABASE_URL.startswith('mysql://'):
            # MySQL configuration
            engine = create_engine(
                DATABASE_URL,
                poolclass=QueuePool,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            logger.info("✅ MySQL database engine created successfully")
        else:
            # SQLite configuration (development)
            engine = create_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False},
                echo=False
            )
            logger.info("✅ SQLite database engine created successfully")
        
        return engine
    except Exception as e:
        logger.error(f"❌ Failed to create database engine: {e}")
        raise

# Create engine instance
engine = create_database_engine()

# Session configuration
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False  # Prevent expired object access issues
)

Base = declarative_base()

def get_db():
    """Database dependency with proper error handling and connection management"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"❌ Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def test_database_connection():
    """Test database connectivity"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("✅ Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

def get_database_info():
    """Get database information for monitoring"""
    try:
        db = SessionLocal()
        if DATABASE_URL.startswith('postgresql://'):
            result = db.execute("SELECT version()").fetchone()
            db_type = "PostgreSQL"
            version = result[0] if result else "Unknown"
        elif DATABASE_URL.startswith('mysql://'):
            result = db.execute("SELECT VERSION()").fetchone()
            db_type = "MySQL"
            version = result[0] if result else "Unknown"
        else:
            db_type = "SQLite"
            version = "3.x"
        
        db.close()
        return {
            "type": db_type,
            "version": version,
            "url": DATABASE_URL.split('@')[0] + "@***" if '@' in DATABASE_URL else DATABASE_URL
        }
    except Exception as e:
        logger.error(f"❌ Failed to get database info: {e}")
        return {"type": "Unknown", "version": "Unknown", "url": "Unknown"} 