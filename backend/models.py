from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
from datetime import datetime

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    TEAM_MEMBER = "team_member"

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"

class PlanType(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"

class WebhookEventType(str, enum.Enum):
    JOB_COMPLETED = "job_completed"
    LEAD_ADDED = "lead_added"
    PLAN_CHANGED = "plan_changed"
    PAYMENT_RECEIVED = "payment_received"

class Users(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    plan = Column(String(50), default="free", nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), default=1)
    tenant_id = Column(String(255), index=True)  # For multi-tenancy
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    jobs = relationship("Jobs", back_populates="user")
    leads = relationship("Leads", back_populates="user")
    api_keys = relationship("ApiKeys", back_populates="user")
    webhooks = relationship("Webhooks", back_populates="user")
    saved_queries = relationship("SavedQueries", back_populates="user")
    notifications = relationship("Notifications", back_populates="user")
    custom_dashboards = relationship("CustomDashboards", back_populates="user")
    onboarding_steps = relationship("OnboardingSteps", back_populates="user")
    demo_projects = relationship("DemoProjects", back_populates="user")
    support_tickets = relationship("SupportTicket", back_populates="user")
    testimonials = relationship("Testimonials", back_populates="user")
    bulk_campaigns = relationship("BulkWhatsAppCampaigns", back_populates="user")

class Plans(Base):
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum(PlanType), nullable=False)
    price = Column(Float, default=0.0)
    max_queries_per_day = Column(Integer, default=10)
    max_results_per_query = Column(Integer, default=100)
    max_leads = Column(Integer, default=1000)
    features = Column(JSON)  # Store features as JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Jobs(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    queries = Column(JSON)  # Store queries as JSON array
    results_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("Users", back_populates="jobs")
    results = relationship("JobResults", back_populates="job")

class JobResults(Base):
    __tablename__ = "job_results"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    business_name = Column(String(255))
    address = Column(Text)
    phone = Column(String(50))
    website = Column(String(255))
    email = Column(String(255))
    rating = Column(Float)
    reviews_count = Column(Integer)
    category = Column(String(255))
    hours = Column(Text)
    description = Column(Text)
    photos = Column(JSON)  # Store photo URLs as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job = relationship("Jobs", back_populates="results")

class Leads(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    company = Column(String(255))
    website = Column(String(255))
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    source = Column(String(100), default="gmaps")
    notes = Column(Text)
    score = Column(Float, default=0.0)  # Lead scoring
    enriched_data = Column(JSON)  # Store enriched data as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("Users", back_populates="leads")
    lead_scores = relationship("LeadScores", back_populates="lead")

class ApiKeys(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("Users", back_populates="api_keys")

class Webhooks(Base):
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url = Column(String(500), nullable=False)
    secret = Column(String(255), nullable=False)
    events = Column(JSON)  # Store event types as JSON array
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("Users", back_populates="webhooks")
    deliveries = relationship("WebhookDeliveries", back_populates="webhook")

class WebhookDeliveries(Base):
    __tablename__ = "webhook_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, ForeignKey("webhooks.id"), nullable=False)
    event_type = Column(Enum(WebhookEventType), nullable=False)
    payload = Column(JSON)
    response_status = Column(Integer)
    response_body = Column(Text)
    delivered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    webhook = relationship("Webhooks", back_populates="deliveries")

class SavedQueries(Base):
    __tablename__ = "saved_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    queries = Column(JSON)  # Store queries as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("Users", back_populates="saved_queries")

class Notifications(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    data = Column(JSON)  # Store additional data as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("Users", back_populates="notifications")

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    queries_run = Column(Integer, default=0)
    leads_generated = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Payments(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(50), default="pending")
    payment_method = Column(String(100))
    stripe_payment_intent_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Teams(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TeamMembers(Base):
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="member")
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

class Integrations(Base):
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String(100), nullable=False)  # zapier, hubspot, etc.
    config = Column(JSON)  # Store integration config as JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLogs(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)
    target_type = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Referrals(Base):
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    referred_email = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")
    reward_amount = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AffiliateLinks(Base):
    __tablename__ = "affiliate_links"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    earnings = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Widgets(Base):
    __tablename__ = "widgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)
    config = Column(JSON)  # Store widget config as JSON
    embed_code = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SSOConfigs(Base):
    __tablename__ = "sso_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False)  # saml, oauth, etc.
    config = Column(JSON)  # Store SSO config as JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Branding(Base):
    __tablename__ = "branding"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    logo_url = Column(String(500))
    primary_color = Column(String(7))  # Hex color
    secondary_color = Column(String(7))
    custom_css = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SocialMediaAccounts(Base):
    __tablename__ = "social_media_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String(100), nullable=False)  # facebook, twitter, etc.
    account_id = Column(String(255), nullable=False)
    access_token = Column(Text)
    refresh_token = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WhatsAppWorkflows(Base):
    __tablename__ = "whatsapp_workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    trigger_conditions = Column(JSON)
    message_template = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WhatsAppWorkflowSteps(Base):
    __tablename__ = "whatsapp_workflow_steps"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("whatsapp_workflows.id"), nullable=False)
    name = Column(String(255), nullable=False)
    step_type = Column(String(50), nullable=False)  # message, delay, condition, action
    content = Column(Text)
    delay_minutes = Column(Integer, default=0)
    conditions = Column(JSON)
    actions = Column(JSON)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    workflow = relationship("WhatsAppWorkflows", backref="steps")

class WhatsAppWorkflowTriggers(Base):
    __tablename__ = "whatsapp_workflow_triggers"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("whatsapp_workflows.id"), nullable=False)
    trigger_type = Column(String(50), nullable=False)  # lead_created, lead_qualified, manual, scheduled
    conditions = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    workflow = relationship("WhatsAppWorkflows", backref="triggers")

class ROIProjects(Base):
    __tablename__ = "roi_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    initial_investment = Column(Float, default=0.0)
    monthly_revenue = Column(Float, default=0.0)
    monthly_costs = Column(Float, default=0.0)
    roi_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class LeadScoringRules(Base):
    __tablename__ = "lead_scoring_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    conditions = Column(JSON)  # Store scoring conditions as JSON
    score = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ShowcaseProjects(Base):
    __tablename__ = "showcase_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    results = Column(JSON)  # Store project results as JSON
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    custom_domain = Column(String(255), unique=True, nullable=True)
    # Add any other fields you need for your SaaS tenants 

# --- Added missing models for lead collection and social media ---
class LeadSources(Base):
    __tablename__ = "lead_sources"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Some sources may be global
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)
    config = Column(JSON)
    status = Column(String(50), default="active")
    last_sync = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class LeadCollections(Base):
    __tablename__ = "lead_collections"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    source_id = Column(Integer, ForeignKey("lead_sources.id"), nullable=False)
    config = Column(JSON)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SocialMediaLeads(Base):
    __tablename__ = "social_media_leads"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String(100), nullable=False)
    platform_id = Column(String(255))
    username = Column(String(255))
    display_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    bio = Column(Text)
    followers_count = Column(Integer)
    following_count = Column(Integer)
    posts_count = Column(Integer)
    location = Column(String(255))
    website = Column(String(255))
    profile_url = Column(String(500))
    avatar_url = Column(String(500))
    verified = Column(Boolean, default=False)
    business_category = Column(String(255))
    engagement_score = Column(Float)
    status = Column(String(50), default="new")
    tags = Column(JSON)
    notes = Column(Text)
    collection_id = Column(Integer, ForeignKey("lead_collections.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 

class Affiliates(Base):
    __tablename__ = "affiliates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    total_earnings = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("Users")
    commissions = relationship("Commissions", back_populates="affiliate")

class Commissions(Base):
    __tablename__ = "commissions"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"), nullable=False)
    referred_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    affiliate = relationship("Affiliates", back_populates="commissions")
    referred_user = relationship("Users") 

class CustomDashboards(Base):
    __tablename__ = "custom_dashboards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("Users") 

class LeadScores(Base):
    __tablename__ = "lead_scores"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, unique=True)
    overall_score = Column(Float, nullable=False)
    factors = Column(JSON, nullable=False)
    recommendations = Column(JSON, nullable=False)
    risk_level = Column(String(50), nullable=False)
    conversion_probability = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    lead = relationship("Leads") 

class OnboardingSteps(Base):
    __tablename__ = "onboarding_steps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    step_id = Column(String(100), nullable=False)
    completed = Column(Boolean, default=False)
    data = Column(JSON)
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("Users")

class DemoProjects(Base):
    __tablename__ = "demo_projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    queries = Column(JSON, nullable=False)
    tags = Column(JSON)
    is_demo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("Users") 

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tenant_id = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    phone = Column(String(50))
    status = Column(String(50), default="open")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("Users") 

class Testimonials(Base):
    __tablename__ = "testimonials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    company = Column(String(255))
    message = Column(Text, nullable=False)
    avatar_url = Column(String(500))
    featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("Users") 

class WhatsAppMessages(Base):
    __tablename__ = "whatsapp_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workflow_id = Column(Integer, ForeignKey("whatsapp_workflows.id"), nullable=True)
    contact_id = Column(Integer, nullable=True)  # Could be FK to WhatsAppContacts if exists
    message = Column(Text, nullable=False)
    status = Column(String(50), default="pending")  # pending, sent, failed, delivered, read
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("Users")
    workflow = relationship("WhatsAppWorkflows") 

class WhatsAppCampaigns(Base):
    __tablename__ = "whatsapp_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    template_id = Column(Integer, nullable=True)  # Could be FK to WhatsAppTemplates if exists
    status = Column(String(50), default="draft")  # draft, scheduled, running, completed, failed
    scheduled_at = Column(DateTime(timezone=True))
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("Users") 

class WhatsAppTemplates(Base):
    __tablename__ = "whatsapp_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(50), default="draft")  # draft, approved, rejected, archived
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("Users")
    bulk_campaigns = relationship("BulkWhatsAppCampaigns", back_populates="template")

class WhatsAppContacts(Base):
    __tablename__ = "whatsapp_contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    status = Column(String(50), default="active")  # active, blocked, unsubscribed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("Users") 

class WhatsAppAutomations(Base):
    __tablename__ = "whatsapp_automations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    trigger_type = Column(String(50), nullable=False)  # e.g., lead_created, scheduled, manual
    actions = Column(JSON, nullable=False)  # List of actions as JSON
    status = Column(String(50), default="active")  # active, paused, disabled
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("Users") 

class BulkWhatsAppCampaigns(Base):
    __tablename__ = "bulk_whatsapp_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    message_content = Column(Text, nullable=False)
    template_id = Column(Integer, ForeignKey("whatsapp_templates.id"), nullable=True)
    schedule_type = Column(String(50), default="immediate")  # immediate, scheduled, recurring
    schedule_time = Column(DateTime, nullable=True)
    delay_between_messages = Column(Integer, default=30)  # seconds
    max_messages_per_hour = Column(Integer, default=50)
    max_messages_per_day = Column(Integer, default=500)
    retry_failed = Column(Boolean, default=True)
    max_retries = Column(Integer, default=3)
    status = Column(String(50), default="pending")  # pending, running, completed, failed, paused
    total_contacts = Column(Integer, default=0)
    sent_messages = Column(Integer, default=0)
    failed_messages = Column(Integer, default=0)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("Users", back_populates="bulk_campaigns")
    messages = relationship("BulkWhatsAppMessages", back_populates="campaign", cascade="all, delete-orphan")
    template = relationship("WhatsAppTemplates", back_populates="bulk_campaigns")

class BulkWhatsAppMessages(Base):
    __tablename__ = "bulk_whatsapp_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("bulk_whatsapp_campaigns.id"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    contact_name = Column(String(255), nullable=True)
    message_content = Column(Text, nullable=False)
    status = Column(String(50), default="pending")  # pending, sent, failed, delivered, read
    message_id = Column(String(255), nullable=True)  # WhatsApp message ID
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("BulkWhatsAppCampaigns", back_populates="messages") 