"""SQLAlchemy database models for lead storage."""
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Text, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from datetime import datetime
from typing import Optional, Dict, Any, List
import os

Base = declarative_base()


class Lead(Base):
    """Lead data model."""
    __tablename__ = "leads"
    
    # Soft delete field
    deleted_at = Column(DateTime, nullable=True, index=True)
    
    # Audit fields
    created_by = Column(String, nullable=True)
    modified_by = Column(String, nullable=True)
    modified_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, index=True, nullable=False)
    search_query = Column(String, index=True, nullable=False)
    platform = Column(String, index=True, nullable=False)
    profile_url = Column(String, nullable=False)
    handle = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    bio_about = Column(Text, nullable=True)
    website = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True, index=True)
    phone_normalized = Column(String, nullable=True, index=True)
    followers = Column(String, nullable=True)
    location = Column(String, nullable=True)
    
    # Phone extraction data (JSON)
    phones_data = Column(JSON, nullable=True)
    
    # v2.0+ fields
    business_type = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    city = Column(String, nullable=True, index=True)
    region = Column(String, nullable=True)
    country = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    seniority_level = Column(String, nullable=True)
    education_level = Column(String, nullable=True)
    institution_name = Column(String, nullable=True)
    
    # v3.0+ fields
    lead_type = Column(String, nullable=True)  # individual or business
    field_of_study = Column(String, nullable=True, index=True)
    degree_program = Column(String, nullable=True)
    graduation_year = Column(Integer, nullable=True)
    
    # Phase 2: Intelligence features
    lead_score = Column(Integer, nullable=True, index=True)  # 0-100 score
    lead_score_category = Column(String, nullable=True)  # hot, warm, low
    keywords = Column(JSON, nullable=True)  # Extracted keywords
    estimated_revenue = Column(String, nullable=True)  # Revenue estimate
    employee_count = Column(Integer, nullable=True)  # Estimated employee count
    
    # Metadata
    extracted_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_task_platform', 'task_id', 'platform'),
        Index('idx_phone_extracted', 'phone', 'extracted_at'),
        Index('idx_field_location', 'field_of_study', 'city'),
        Index('idx_extracted_at', 'extracted_at'),  # For archival queries
        Index('idx_profile_url', 'profile_url'),  # For duplicate detection
        Index('idx_email', 'email'),  # For duplicate detection
        Index('idx_platform_extracted', 'platform', 'extracted_at'),  # For platform analytics
    )


class Task(Base):
    """Task tracking model."""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=True)
    status = Column(String, nullable=False, default="running")  # running, paused, stopped, completed, error
    queries = Column(JSON, nullable=False)  # List of queries
    platforms = Column(JSON, nullable=False)  # List of platforms
    progress = Column(JSON, nullable=True)  # Progress counts per platform
    total_results = Column(Integer, default=0)
    current_query = Column(String, nullable=True)
    current_platform = Column(String, nullable=True)
    lead_objective = Column(String, nullable=True, index=True)  # Phase 1: Global Lead Types
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    
    # Soft delete field
    deleted_at = Column(DateTime, nullable=True, index=True)
    
    # Audit fields
    created_by = Column(String, nullable=True)
    modified_by = Column(String, nullable=True)
    modified_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)


# Database connection
# Use SQLite for local development if PostgreSQL is not available
_database_url = os.getenv(
    "DATABASE_URL",
    "sqlite:///./lead_intelligence.db"  # SQLite for local development
)

_engine = None
_SessionLocal = None


def get_engine():
    """Get or create database engine with optimized connection pooling."""
    global _engine
    if _engine is None:
        # SQLite doesn't support connection pooling the same way as PostgreSQL
        if "sqlite" in _database_url:
            _engine = create_engine(
                _database_url,
                poolclass=None,  # SQLite doesn't need pooling
                connect_args={
                    "check_same_thread": False,  # SQLite specific
                },
                echo=False,
            )
        else:
            # Optimized pool settings for PostgreSQL
            pool_size = int(os.getenv("DB_POOL_SIZE", "20"))
            max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "40"))
            pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
            pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))
            
            _engine = create_engine(
                _database_url,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_timeout=pool_timeout,
                pool_recycle=pool_recycle,
                pool_pre_ping=True,
                echo=False,
                connect_args={
                    "connect_timeout": 10,
                    "application_name": "lead_intelligence"
                } if "postgresql" in _database_url else {}
            )
    return _engine


def get_session() -> Session:
    """Get database session."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine()
        )
    return _SessionLocal()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=get_engine())


def close_db():
    """Close database connections."""
    global _engine
    if _engine:
        _engine.dispose()
        _engine = None

