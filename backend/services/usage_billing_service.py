"""Usage-based billing service."""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from backend.models.database import get_session
from backend.models.database import Lead, Task
from backend.services.stripe_service import get_stripe_service
from sqlalchemy import func


class UsageBillingService:
    """Service for tracking and billing usage."""
    
    def track_usage(
        self,
        user_id: str,
        usage_type: str,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Track usage for a user.
        
        Args:
            user_id: User ID
            usage_type: Type of usage (leads_scraped, api_calls, etc.)
            quantity: Quantity used
            
        Returns:
            Usage tracking result
        """
        # Store usage in database or cache
        # This is a simplified implementation
        return {
            "user_id": user_id,
            "usage_type": usage_type,
            "quantity": quantity,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_usage_for_period(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get usage statistics for a period.
        
        Args:
            user_id: User ID
            start_date: Period start
            end_date: Period end
            
        Returns:
            Usage statistics
        """
        db = get_session()
        try:
            # Get user's tasks
            user_tasks = db.query(Task.task_id).filter(
                Task.user_id == user_id,
                Task.started_at >= start_date,
                Task.started_at <= end_date
            ).all()
            task_ids = [t[0] for t in user_tasks]
            
            if not task_ids:
                return {
                    "leads_scraped": 0,
                    "api_calls": 0,
                    "storage_mb": 0,
                }
            
            # Count leads
            leads_count = db.query(func.count(Lead.id)).filter(
                Lead.task_id.in_(task_ids)
            ).scalar() or 0
            
            return {
                "leads_scraped": leads_count,
                "api_calls": 0,  # Would track API calls separately
                "storage_mb": 0,  # Would calculate storage
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
            }
        finally:
            db.close()
    
    def calculate_usage_charge(
        self,
        user_id: str,
        usage_data: Dict[str, Any],
        pricing_tiers: Dict[str, Dict[str, float]]
    ) -> float:
        """
        Calculate charge based on usage.
        
        Args:
            user_id: User ID
            usage_data: Usage statistics
            pricing_tiers: Pricing configuration
            
        Returns:
            Total charge amount
        """
        total = 0.0
        
        # Calculate charge for leads
        leads = usage_data.get("leads_scraped", 0)
        lead_pricing = pricing_tiers.get("leads", {})
        
        # Tiered pricing example
        if leads > 0:
            if leads <= 1000:
                total += leads * lead_pricing.get("tier1", 0.01)
            elif leads <= 5000:
                total += 1000 * lead_pricing.get("tier1", 0.01)
                total += (leads - 1000) * lead_pricing.get("tier2", 0.008)
            else:
                total += 1000 * lead_pricing.get("tier1", 0.01)
                total += 4000 * lead_pricing.get("tier2", 0.008)
                total += (leads - 5000) * lead_pricing.get("tier3", 0.005)
        
        return round(total, 2)
    
    def bill_usage(
        self,
        user_id: str,
        subscription_item_id: str,
        usage_quantity: int
    ) -> Dict[str, Any]:
        """
        Bill usage to Stripe subscription.
        
        Args:
            user_id: User ID
            subscription_item_id: Stripe subscription item ID
            usage_quantity: Quantity to bill
            
        Returns:
            Billing result
        """
        stripe_service = get_stripe_service()
        
        try:
            usage_record = stripe_service.create_usage_record(
                subscription_item_id=subscription_item_id,
                quantity=usage_quantity
            )
            return {
                "success": True,
                "usage_record": usage_record,
                "billed_quantity": usage_quantity
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
usage_billing_service = UsageBillingService()

