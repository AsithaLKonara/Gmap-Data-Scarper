from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import datetime

class Tenant(Base):
    __tablename__ = 'tenants'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    branding = Column(JSON, nullable=True)
    sso_config = Column(JSON, nullable=True)
    # Add more fields as needed

    users = relationship('User', back_populates='tenant')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    plan = Column(String(50), default='free')
    stripe_customer_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    queries_today = Column(Integer, default=0)
    last_query_date = Column(DateTime(timezone=True), default=func.now())
    is_banned = Column(Boolean, default=False)
    jobs = relationship('Job', back_populates='user')
    leads = relationship('Lead', back_populates='user')
    profile = relationship('UserProfile', back_populates='user', uselist=False)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    subscription_status = Column(String(50), default="active")
    subscription_start = Column(DateTime)
    subscription_end = Column(DateTime)
    stripe_subscription_id = Column(String(255))
    total_queries = Column(Integer, default=0)
    # API key management fields
    api_key_hash = Column(String(255), nullable=True)
    api_key_created_at = Column(DateTime(timezone=True), nullable=True)
    api_key_last_used = Column(DateTime(timezone=True), nullable=True)
    saved_queries = relationship('SavedQuery', back_populates='user', cascade='all, delete-orphan')
    notifications = relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    scheduled_jobs = relationship('ScheduledJob', back_populates='user', cascade='all, delete-orphan')
    custom_dashboards = relationship('CustomDashboard', back_populates='user', cascade='all, delete-orphan')
    owned_teams = relationship('Team', back_populates='owner', cascade='all, delete-orphan')
    team_memberships = relationship('TeamMembership', back_populates='user', cascade='all, delete-orphan')
    audit_logs = relationship('AuditLog', back_populates='user', cascade='all, delete-orphan')
    webhook_url = Column(String(500), nullable=True)
    # CRM/Email integration fields
    crm_provider = Column(String(50), nullable=True)
    crm_access_token = Column(String(255), nullable=True)
    crm_refresh_token = Column(String(255), nullable=True)
    crm_token_expiry = Column(DateTime(timezone=True), nullable=True)
    email_provider = Column(String(50), nullable=True)
    email_access_token = Column(String(255), nullable=True)
    email_refresh_token = Column(String(255), nullable=True)
    email_token_expiry = Column(DateTime(timezone=True), nullable=True)
    # Referral and usage-based billing fields
    referral_code = Column(String(32), unique=True, nullable=True)
    referred_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    referral_credits = Column(Integer, default=0)
    usage_credits = Column(Integer, default=0)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)
    tenant = relationship('Tenant', back_populates='users')

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True, index=True)
    queries = Column(Text, nullable=False)  # JSON-encoded list
    status = Column(String(50), default='pending', index=True)
    result = Column(Text, nullable=True)  # JSON-encoded result
    csv_path = Column(String(500), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship('User', back_populates='jobs')
    share_token = Column(String(64), unique=True, nullable=True)

class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    company = Column(String(255), nullable=True)
    tag = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(50), default='new', index=True)  # new, contacted, qualified, converted
    source = Column(String(100), nullable=True)  # gmap_scrape, manual, import
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship('User', back_populates='leads')
    share_token = Column(String(64), unique=True, nullable=True)

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    avatar = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    company = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    timezone = Column(String(50), default='UTC')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship('User', back_populates='profile')

class Plan(Base):
    __tablename__ = 'plans'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # free, pro, business
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price_monthly = Column(Float, nullable=True)
    price_yearly = Column(Float, nullable=True)
    max_queries_per_day = Column(Integer, nullable=False)
    max_results_per_query = Column(Integer, nullable=False)
    features = Column(Text, nullable=True)  # JSON-encoded features list
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    limits = Column(Text, nullable=True)  # JSON-encoded limits
    stripe_price_id = Column(String(255))

class SystemLog(Base):
    __tablename__ = 'system_logs'
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    module = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)  # JSON-encoded additional details
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=True)
    target_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship('User', back_populates='audit_logs')

class SavedQuery(Base):
    __tablename__ = 'saved_queries'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    queries = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship('User', back_populates='saved_queries')

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    message = Column(String(255), nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship('User', back_populates='notifications')

class ScheduledJob(Base):
    __tablename__ = 'scheduled_jobs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    queries = Column(JSON, nullable=False)
    schedule = Column(String(50), nullable=False)  # cron string
    active = Column(Boolean, default=True)
    last_run = Column(DateTime(timezone=True), nullable=True)
    next_run = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship('User', back_populates='scheduled_jobs')

class CustomDashboard(Base):
    __tablename__ = 'custom_dashboards'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    config = Column(JSON, nullable=False)  # chart/widget config
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship('User', back_populates='custom_dashboards')

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner = relationship('User', back_populates='owned_teams')
    memberships = relationship('TeamMembership', back_populates='team', cascade='all, delete-orphan')

class TeamMembership(Base):
    __tablename__ = 'team_memberships'
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    role = Column(String(20), nullable=False, default='member')  # admin, member, viewer
    invited_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), nullable=False, default='active')  # active, invited, removed
    team = relationship('Team', back_populates='memberships')
    user = relationship('User', back_populates='team_memberships')

class LeadSource(Base):
    __tablename__ = 'lead_sources'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    type = Column(String(50), nullable=False)  # social, web, api, manual
    config = Column(Text, nullable=True)  # JSON config for API keys, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class LeadCollection(Base):
    __tablename__ = 'lead_collections'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_id = Column(Integer, ForeignKey('lead_sources.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    config = Column(Text, nullable=True)  # JSON config for collection settings
    status = Column(String(50), default='active')  # active, paused, completed
    last_run = Column(DateTime(timezone=True), nullable=True)
    next_run = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    source = relationship('LeadSource')
    user = relationship('User')

class SocialMediaLead(Base):
    __tablename__ = 'social_media_leads'
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)  # facebook, instagram, whatsapp, linkedin, twitter
    platform_id = Column(String(255), nullable=False)  # ID from the platform
    username = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    bio = Column(Text, nullable=True)
    followers_count = Column(Integer, nullable=True)
    following_count = Column(Integer, nullable=True)
    posts_count = Column(Integer, nullable=True)
    location = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    profile_url = Column(String(500), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    verified = Column(Boolean, default=False)
    business_category = Column(String(100), nullable=True)
    contact_info = Column(Text, nullable=True)  # JSON with additional contact info
    engagement_score = Column(Float, nullable=True)  # Calculated engagement metric
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    collection_id = Column(Integer, ForeignKey('lead_collections.id'), nullable=True)
    status = Column(String(50), default='new')  # new, contacted, qualified, converted, ignored
    tags = Column(Text, nullable=True)  # JSON array of tags
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship('User')
    collection = relationship('LeadCollection')

class WhatsAppCampaign(Base):
    __tablename__ = 'whatsapp_campaigns'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    template_id = Column(Integer, ForeignKey('whatsapp_templates.id'), nullable=True)
    status = Column(String(50), default='draft')  # draft, active, paused, completed
    schedule_type = Column(String(50), default='immediate')  # immediate, scheduled, recurring
    schedule_time = Column(DateTime(timezone=True), nullable=True)
    max_messages_per_hour = Column(Integer, default=50)
    max_messages_per_day = Column(Integer, default=500)
    messages_sent = Column(Integer, default=0)
    messages_failed = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship('User')
    template = relationship('WhatsAppTemplate')

class WhatsAppTemplate(Base):
    __tablename__ = 'whatsapp_templates'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    variables = Column(Text, nullable=True)  # JSON array of variable names
    media_url = Column(String(500), nullable=True)
    media_type = Column(String(50), nullable=True)  # image, video, document
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship('User')

class WhatsAppMessage(Base):
    __tablename__ = 'whatsapp_messages'
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey('whatsapp_campaigns.id'), nullable=True)
    template_id = Column(Integer, ForeignKey('whatsapp_templates.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    recipient_phone = Column(String(50), nullable=False)
    recipient_name = Column(String(255), nullable=True)
    message_content = Column(Text, nullable=False)
    message_type = Column(String(50), default='text')  # text, image, video, document, template
    media_url = Column(String(500), nullable=True)
    status = Column(String(50), default='pending')  # pending, sent, delivered, read, failed
    whatsapp_message_id = Column(String(255), nullable=True)  # WhatsApp's message ID
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    campaign = relationship('WhatsAppCampaign')
    template = relationship('WhatsAppTemplate')
    user = relationship('User')

class WhatsAppContact(Base):
    __tablename__ = 'whatsapp_contacts'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    phone_number = Column(String(50), nullable=False, unique=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    tags = Column(Text, nullable=True)  # JSON array of tags
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    opt_out = Column(Boolean, default=False)
    last_message_sent = Column(DateTime(timezone=True), nullable=True)
    total_messages_sent = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship('User')

class WhatsAppAutomation(Base):
    __tablename__ = 'whatsapp_automations'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    trigger_type = Column(String(50), nullable=False)  # lead_added, lead_status_changed, time_based, manual
    trigger_conditions = Column(Text, nullable=True)  # JSON conditions
    template_id = Column(Integer, ForeignKey('whatsapp_templates.id'), nullable=False)
    delay_minutes = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship('User')
    template = relationship('WhatsAppTemplate') 