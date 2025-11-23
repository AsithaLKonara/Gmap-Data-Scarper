"""Plan service for managing user plans and lead limits."""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any
from backend.models.database import get_session
from backend.models.user_plan import UserPlan
from backend.models.lead_usage import LeadUsage
from backend.models.user import User


class PlanService:
    """Service for managing user plans and lead usage limits."""
    
    def __init__(self, db: Optional[Session] = None):
        """Initialize plan service."""
        self.db = db or get_session()
    
    def get_user_plan(self, user_id: str) -> Optional[UserPlan]:
        """
        Get user's current active plan.
        
        Args:
            user_id: User ID
            
        Returns:
            UserPlan object or None
        """
        plan = self.db.query(UserPlan).filter(
            and_(
                UserPlan.user_id == user_id,
                UserPlan.status == 'active'
            )
        ).first()
        
        # If no plan found, create default free plan
        if not plan:
            plan = self._create_default_plan(user_id)
        
        return plan
    
    def _create_default_plan(self, user_id: str) -> UserPlan:
        """Create default free plan for user."""
        plan = UserPlan(
            user_id=user_id,
            plan_type='free',
            daily_lead_limit=10,
            status='active'
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan
    
    def check_lead_limit(self, user_id: str) -> Dict[str, Any]:
        """
        Check if user can create more leads today.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with 'allowed', 'remaining', 'limit', 'used' keys
        """
        plan = self.get_user_plan(user_id)
        
        # Paid plans have unlimited leads
        if plan.plan_type in ['paid_monthly', 'paid_usage']:
            return {
                'allowed': True,
                'remaining': None,  # Unlimited
                'limit': None,
                'used': 0,
                'plan_type': plan.plan_type
            }
        
        # Free plan: check daily limit
        today = date.today()
        usage = self.db.query(LeadUsage).filter(
            and_(
                LeadUsage.user_id == user_id,
                LeadUsage.usage_date == today
            )
        ).first()
        
        if not usage:
            # No usage today, create record
            usage = LeadUsage(
                user_id=user_id,
                usage_date=today,
                leads_count=0,
                reset_at=datetime.combine(today + timedelta(days=1), datetime.min.time())
            )
            self.db.add(usage)
            self.db.commit()
        
        limit = plan.daily_lead_limit or 10
        used = usage.leads_count
        remaining = max(0, limit - used)
        
        return {
            'allowed': used < limit,
            'remaining': remaining,
            'limit': limit,
            'used': used,
            'plan_type': plan.plan_type
        }
    
    def increment_lead_count(self, user_id: str) -> bool:
        """
        Increment daily lead count for user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False if limit exceeded
        """
        check_result = self.check_lead_limit(user_id)
        
        if not check_result['allowed']:
            return False
        
        today = date.today()
        usage = self.db.query(LeadUsage).filter(
            and_(
                LeadUsage.user_id == user_id,
                LeadUsage.usage_date == today
            )
        ).first()
        
        if usage:
            usage.leads_count += 1
            usage.updated_at = datetime.utcnow()
        else:
            usage = LeadUsage(
                user_id=user_id,
                usage_date=today,
                leads_count=1,
                reset_at=datetime.combine(today + timedelta(days=1), datetime.min.time())
            )
            self.db.add(usage)
        
        self.db.commit()
        return True
    
    def get_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get current usage statistics for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with usage statistics
        """
        plan = self.get_user_plan(user_id)
        today = date.today()
        
        usage = self.db.query(LeadUsage).filter(
            and_(
                LeadUsage.user_id == user_id,
                LeadUsage.usage_date == today
            )
        ).first()
        
        used = usage.leads_count if usage else 0
        limit = plan.daily_lead_limit if plan.plan_type == 'free' else None
        
        return {
            'plan_type': plan.plan_type,
            'daily_limit': limit,
            'used_today': used,
            'remaining_today': limit - used if limit else None,
            'is_unlimited': plan.plan_type in ['paid_monthly', 'paid_usage']
        }
    
    def reset_daily_limits(self) -> int:
        """
        Reset daily lead counts for all users.
        Should be called daily via Celery task.
        
        Returns:
            Number of records reset
        """
        yesterday = date.today() - timedelta(days=1)
        
        # Delete old usage records (older than 7 days to keep some history)
        cutoff_date = date.today() - timedelta(days=7)
        deleted = self.db.query(LeadUsage).filter(
            LeadUsage.usage_date < cutoff_date
        ).delete()
        
        self.db.commit()
        return deleted
    
    def update_user_plan(
        self,
        user_id: str,
        plan_type: str,
        stripe_subscription_id: Optional[str] = None,
        stripe_customer_id: Optional[str] = None
    ) -> UserPlan:
        """
        Update or create user plan.
        
        Args:
            user_id: User ID
            plan_type: 'free', 'paid_monthly', or 'paid_usage'
            stripe_subscription_id: Stripe subscription ID (for paid plans)
            stripe_customer_id: Stripe customer ID (for paid plans)
            
        Returns:
            Updated UserPlan object
        """
        # Cancel existing active plan
        existing = self.db.query(UserPlan).filter(
            and_(
                UserPlan.user_id == user_id,
                UserPlan.status == 'active'
            )
        ).first()
        
        if existing:
            existing.status = 'cancelled'
            existing.cancelled_at = datetime.utcnow()
        
        # Create new plan
        plan_config = self._get_plan_config(plan_type)
        new_plan = UserPlan(
            user_id=user_id,
            plan_type=plan_type,
            daily_lead_limit=plan_config.get('daily_lead_limit'),
            monthly_price=plan_config.get('monthly_price'),
            price_per_lead=plan_config.get('price_per_lead'),
            stripe_subscription_id=stripe_subscription_id,
            stripe_customer_id=stripe_customer_id,
            status='active'
        )
        
        self.db.add(new_plan)
        self.db.commit()
        self.db.refresh(new_plan)
        
        return new_plan
    
    def _get_plan_config(self, plan_type: str) -> Dict[str, Any]:
        """Get configuration for plan type."""
        configs = {
            'free': {
                'daily_lead_limit': 10,
                'monthly_price': None,
                'price_per_lead': None,
            },
            'paid_monthly': {
                'daily_lead_limit': None,  # Unlimited
                'monthly_price': 29.0,
                'price_per_lead': None,
            },
            'paid_usage': {
                'daily_lead_limit': None,  # Unlimited
                'monthly_price': None,
                'price_per_lead': 0.50,
            },
        }
        return configs.get(plan_type, configs['free'])


# Global instance - use session from get_session() for each call
def get_plan_service(db: Optional[Session] = None) -> PlanService:
    """Get plan service instance with database session."""
    if db is None:
        db = get_session()
    return PlanService(db=db)

