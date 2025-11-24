"""Add soft deletes and audit trail

Revision ID: 001
Revises: 
Create Date: 2025-01-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add soft delete and audit fields to leads table
    try:
        op.add_column('leads', sa.Column('deleted_at', sa.DateTime(), nullable=True))
        op.create_index(op.f('ix_leads_deleted_at'), 'leads', ['deleted_at'], unique=False)
    except Exception:
        # Column might already exist, skip
        pass
    
    try:
        op.add_column('leads', sa.Column('created_by', sa.String(), nullable=True))
    except Exception:
        pass
    
    try:
        op.add_column('leads', sa.Column('modified_by', sa.String(), nullable=True))
    except Exception:
        pass
    
    try:
        op.add_column('leads', sa.Column('modified_at', sa.DateTime(), nullable=True))
    except Exception:
        pass
    
    # Add soft delete and audit fields to tasks table
    try:
        op.add_column('tasks', sa.Column('deleted_at', sa.DateTime(), nullable=True))
        op.create_index(op.f('ix_tasks_deleted_at'), 'tasks', ['deleted_at'], unique=False)
    except Exception:
        pass
    
    try:
        op.add_column('tasks', sa.Column('created_by', sa.String(), nullable=True))
    except Exception:
        pass
    
    try:
        op.add_column('tasks', sa.Column('modified_by', sa.String(), nullable=True))
    except Exception:
        pass
    
    try:
        op.add_column('tasks', sa.Column('modified_at', sa.DateTime(), nullable=True))
    except Exception:
        pass


def downgrade() -> None:
    # Remove soft delete and audit fields from tasks table
    try:
        op.drop_index(op.f('ix_tasks_deleted_at'), table_name='tasks')
        op.drop_column('tasks', 'deleted_at')
    except Exception:
        pass
    
    try:
        op.drop_column('tasks', 'modified_at')
    except Exception:
        pass
    
    try:
        op.drop_column('tasks', 'modified_by')
    except Exception:
        pass
    
    try:
        op.drop_column('tasks', 'created_by')
    except Exception:
        pass
    
    # Remove soft delete and audit fields from leads table
    try:
        op.drop_index(op.f('ix_leads_deleted_at'), table_name='leads')
        op.drop_column('leads', 'deleted_at')
    except Exception:
        pass
    
    try:
        op.drop_column('leads', 'modified_at')
    except Exception:
        pass
    
    try:
        op.drop_column('leads', 'modified_by')
    except Exception:
        pass
    
    try:
        op.drop_column('leads', 'created_by')
    except Exception:
        pass

