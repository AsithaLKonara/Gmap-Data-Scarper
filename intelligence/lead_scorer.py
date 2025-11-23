"""Lead scoring system for ranking and prioritizing leads."""
from __future__ import annotations

import re
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from scrapers.base import ScrapeResult


class LeadScorer:
    """
    Scores leads based on multiple weighted factors.
    
    Factors:
    - Recency of activity (30%)
    - Engagement (25%)
    - Data completeness (20%)
    - Business relevance (15%)
    - Education/seniority (10%)
    """
    
    def __init__(self, weights_file: Optional[str] = None):
        """
        Initialize lead scorer with weights configuration.
        
        Args:
            weights_file: Path to scoring_weights.yaml. If None, uses default.
        """
        if weights_file is None:
            weights_file = Path(__file__).parent / "scoring_weights.yaml"
        
        self.weights_file = Path(weights_file)
        self.config: Dict = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load scoring configuration from YAML file."""
        try:
            with open(self.weights_file, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[SCORER] Warning: Could not load config: {e}")
            self.config = {}
    
    def score(self, result: ScrapeResult) -> ScrapeResult:
        """
        Calculate lead score and add to result.
        
        Args:
            result: ScrapeResult dictionary
            
        Returns:
            ScrapeResult with added lead_score field
        """
        weights = self.config.get("weights", {})
        
        # Calculate component scores
        recency_score = self._score_recency(result) * (weights.get("recency_of_activity", 30) / 100.0)
        engagement_score = self._score_engagement(result) * (weights.get("engagement", 25) / 100.0)
        completeness_score = self._score_completeness(result) * (weights.get("data_completeness", 20) / 100.0)
        business_score = self._score_business_relevance(result) * (weights.get("business_relevance", 15) / 100.0)
        education_score = self._score_education_seniority(result) * (weights.get("education_seniority", 10) / 100.0)
        
        # Total score (0-100)
        total_score = recency_score + engagement_score + completeness_score + business_score + education_score
        
        # Round to 2 decimal places
        result["lead_score"] = round(total_score, 2)
        
        return result
    
    def _score_recency(self, result: ScrapeResult) -> float:
        """Score based on recency of activity (0-100)."""
        last_post = result.get("last_post_date", "N/A")
        if not last_post or last_post == "N/A":
            return 20.0  # Default low score for no activity data
        
        recency_config = self.config.get("recency", {})
        very_recent = recency_config.get("very_recent", 7)
        recent = recency_config.get("recent", 30)
        somewhat_recent = recency_config.get("somewhat_recent", 60)
        old = recency_config.get("old", 90)
        
        try:
            # Parse relative dates
            if "ago" in last_post.lower():
                match = re.search(r"(\d+)\s*([hdwmy])", last_post.lower())
                if match:
                    num = int(match.group(1))
                    unit = match.group(2)
                    
                    if unit == "h":
                        days_ago = num / 24.0
                    elif unit == "d":
                        days_ago = num
                    elif unit == "w":
                        days_ago = num * 7
                    elif unit == "m":
                        days_ago = num * 30
                    else:
                        days_ago = 999
                    
                    if days_ago <= very_recent:
                        return 100.0
                    elif days_ago <= recent:
                        return 80.0
                    elif days_ago <= somewhat_recent:
                        return 60.0
                    elif days_ago <= old:
                        return 40.0
                    else:
                        return 20.0
            
            # Parse absolute dates
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", last_post)
            if date_match:
                post_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                days_ago = (datetime.now() - post_date).days
                
                if days_ago <= very_recent:
                    return 100.0
                elif days_ago <= recent:
                    return 80.0
                elif days_ago <= somewhat_recent:
                    return 60.0
                elif days_ago <= old:
                    return 40.0
                else:
                    return 20.0
        except Exception:
            pass
        
        return 20.0
    
    def _score_engagement(self, result: ScrapeResult) -> float:
        """Score based on engagement metrics (0-100)."""
        engagement_config = self.config.get("engagement", {})
        high_followers = engagement_config.get("high_followers", 10000)
        medium_followers = engagement_config.get("medium_followers", 5000)
        low_followers = engagement_config.get("low_followers", 1000)
        very_low_followers = engagement_config.get("very_low_followers", 100)
        boosted_bonus = engagement_config.get("boosted_bonus", 10)
        high_engagement_bonus = engagement_config.get("high_engagement_bonus", 5)
        
        # Get followers count
        followers_str = result.get("Followers", "0")
        followers = self._parse_number(followers_str)
        
        # Base score from followers
        if followers >= high_followers:
            base_score = 100.0
        elif followers >= medium_followers:
            base_score = 80.0
        elif followers >= low_followers:
            base_score = 60.0
        elif followers >= very_low_followers:
            base_score = 40.0
        else:
            base_score = 20.0
        
        # Bonus for boosted posts
        is_boosted = result.get("is_boosted", "false").lower() == "true"
        if is_boosted:
            base_score = min(100.0, base_score + boosted_bonus)
        
        # Bonus for high engagement
        post_engagement = result.get("post_engagement", "N/A")
        if post_engagement != "N/A":
            engagement_num = self._parse_number(post_engagement)
            if engagement_num >= 1000:
                base_score = min(100.0, base_score + high_engagement_bonus)
        
        return base_score
    
    def _score_completeness(self, result: ScrapeResult) -> float:
        """Score based on data completeness (0-100)."""
        completeness_config = self.config.get("completeness", {})
        required_fields = completeness_config.get("required_fields", [])
        valuable_fields = completeness_config.get("valuable_fields", [])
        required_weight = completeness_config.get("required_weight", 0.5)
        valuable_weight = completeness_config.get("valuable_weight", 0.5)
        
        # Check required fields
        required_count = 0
        for field in required_fields:
            value = result.get(field, "")
            if value and value != "N/A" and value.strip():
                required_count += 1
        
        required_score = (required_count / len(required_fields)) * 100.0 if required_fields else 0.0
        
        # Check valuable fields
        valuable_count = 0
        for field in valuable_fields:
            value = result.get(field, "")
            if value and value != "N/A" and value.strip():
                valuable_count += 1
        
        valuable_score = (valuable_count / len(valuable_fields)) * 100.0 if valuable_fields else 0.0
        
        # Weighted total
        total_score = (required_score * required_weight) + (valuable_score * valuable_weight)
        
        return total_score
    
    def _score_business_relevance(self, result: ScrapeResult) -> float:
        """Score based on business type relevance (0-100)."""
        business_type = result.get("business_type", "N/A")
        if business_type == "N/A":
            return 50.0  # Neutral score
        
        business_config = self.config.get("business_relevance", {})
        preferred_types = business_config.get("preferred_types", [])
        preferred_bonus = business_config.get("preferred_bonus", 5)
        
        base_score = 70.0  # Default good score for having a business type
        
        if business_type in preferred_types:
            base_score = min(100.0, base_score + preferred_bonus)
        
        return base_score
    
    def _score_education_seniority(self, result: ScrapeResult) -> float:
        """Score based on education and seniority (0-100)."""
        education_config = self.config.get("education_seniority", {})
        education_levels = education_config.get("education_levels", {})
        seniority_levels = education_config.get("seniority_levels", {})
        
        education_level = result.get("education_level", "N/A")
        seniority_level = result.get("seniority_level", "N/A")
        
        education_score = education_levels.get(education_level, 0)
        seniority_score = seniority_levels.get(seniority_level, 0)
        
        # Average of education and seniority (max 10 each, so max 10 total, scale to 100)
        total_score = ((education_score + seniority_score) / 20.0) * 100.0
        
        return total_score
    
    def _parse_number(self, num_str: str) -> int:
        """Parse number string (handles K, M, B suffixes)."""
        if not num_str or num_str == "N/A":
            return 0
        
        # Remove commas and spaces
        num_str = num_str.replace(",", "").replace(" ", "").strip()
        
        # Try to extract number
        match = re.search(r"([\d.]+)([KMBkmb]?)", num_str)
        if match:
            num = float(match.group(1))
            suffix = match.group(2).upper()
            
            if suffix == "K":
                return int(num * 1000)
            elif suffix == "M":
                return int(num * 1000000)
            elif suffix == "B":
                return int(num * 1000000000)
            else:
                return int(num)
        
        # Try direct conversion
        try:
            return int(float(num_str))
        except:
            return 0
    
    def get_quality_tier(self, score: float) -> str:
        """
        Get quality tier based on score.
        
        Args:
            score: Lead score (0-100)
            
        Returns:
            Quality tier: "high", "medium", or "low"
        """
        thresholds = self.config.get("thresholds", {})
        high_score = thresholds.get("high_score", 70)
        medium_score = thresholds.get("medium_score", 40)
        
        if score >= high_score:
            return "high"
        elif score >= medium_score:
            return "medium"
        else:
            return "low"

