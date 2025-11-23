"""Business classification engine for categorizing leads by business type."""
from __future__ import annotations

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from scrapers.base import ScrapeResult


class BusinessClassifier:
    """
    Classifies business leads by type, industry, and sub-category.
    
    Uses keyword matching and category detection from:
    - Google Maps category field
    - Website content (domain analysis)
    - Business name
    - Bio/About text
    """
    
    def __init__(self, keywords_file: Optional[str] = None):
        """
        Initialize classifier with keyword mappings.
        
        Args:
            keywords_file: Path to business_keywords.yaml. If None, uses default.
        """
        if keywords_file is None:
            keywords_file = Path(__file__).parent / "business_keywords.yaml"
        
        self.keywords_file = Path(keywords_file)
        self.keyword_map: Dict = {}
        self.industries: List[str] = []
        self._load_keywords()
    
    def _load_keywords(self) -> None:
        """Load keyword mappings from YAML file."""
        try:
            with open(self.keywords_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self.keyword_map = data.get("business_types", {})
                self.industries = data.get("industries", [])
        except Exception as e:
            print(f"[CLASSIFIER] Warning: Could not load keywords: {e}")
            self.keyword_map = {}
            self.industries = []
    
    def classify(self, result: ScrapeResult) -> ScrapeResult:
        """
        Classify a lead result and add business_type, industry, sub_category fields.
        
        Args:
            result: ScrapeResult dictionary
            
        Returns:
            ScrapeResult with added classification fields
        """
        # Extract text to analyze
        category = result.get("Category", "").lower()
        name = result.get("Display Name", "").lower()
        bio = result.get("Bio/About", "").lower()
        website = result.get("Website", "").lower()
        
        # Combine all text for analysis
        text_to_analyze = f"{category} {name} {bio} {website}"
        
        # Find best match
        best_match = self._find_best_match(text_to_analyze, category)
        
        if best_match:
            business_type, industry, sub_category = best_match
            result["business_type"] = business_type
            result["industry"] = industry
            result["sub_category"] = sub_category
        else:
            # Default values
            result["business_type"] = "N/A"
            result["industry"] = "N/A"
            result["sub_category"] = "N/A"
        
        return result
    
    def _find_best_match(self, text: str, category: str) -> Optional[Tuple[str, str, str]]:
        """
        Find the best matching business type for given text.
        
        Args:
            text: Combined text to search
            category: Google Maps category (if available)
            
        Returns:
            Tuple of (business_type, industry, sub_category) or None
        """
        best_score = 0
        best_match = None
        
        for business_type, config in self.keyword_map.items():
            score = 0
            
            # Check keywords
            keywords = config.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in text:
                    score += 2  # Keyword match
            
            # Check categories (higher weight for exact category match)
            categories = config.get("categories", [])
            for cat in categories:
                if cat.lower() in category:
                    score += 5  # Category match (stronger signal)
                elif cat.lower() in text:
                    score += 1  # Category mentioned in text
            
            # If we have a strong match, return it
            if score > best_score:
                best_score = score
                industry = config.get("industry", "N/A")
                sub_categories = config.get("sub_categories", [])
                sub_category = sub_categories[0] if sub_categories else "N/A"
                best_match = (business_type, industry, sub_category)
        
        # Only return if we have a reasonable match
        if best_score >= 2:
            return best_match
        
        return None
    
    def get_business_types(self) -> List[str]:
        """Get list of all supported business types."""
        return list(self.keyword_map.keys())
    
    def get_industries(self) -> List[str]:
        """Get list of all supported industries."""
        return self.industries
    
    def filter_by_type(self, results: List[ScrapeResult], business_types: List[str]) -> List[ScrapeResult]:
        """
        Filter results by business type.
        
        Args:
            results: List of ScrapeResult dictionaries
            business_types: List of business types to include
            
        Returns:
            Filtered list of results
        """
        if not business_types:
            return results
        
        business_types_lower = [bt.lower() for bt in business_types]
        filtered = []
        
        for result in results:
            result_type = result.get("business_type", "N/A").lower()
            if result_type in business_types_lower:
                filtered.append(result)
        
        return filtered

