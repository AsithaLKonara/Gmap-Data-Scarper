"""Category-based query generator for automated search queries."""
from __future__ import annotations

import yaml
from pathlib import Path
from typing import List, Optional


class CategoryQueryGenerator:
    """
    Generates search queries from industry categories and locations.
    
    Creates location-aware queries like "digital marketing agencies in California"
    """
    
    def __init__(self, templates_file: Optional[str] = None):
        """
        Initialize query generator with industry templates.
        
        Args:
            templates_file: Path to industry_templates.yaml. If None, uses default.
        """
        if templates_file is None:
            templates_file = Path(__file__).parent / "industry_templates.yaml"
        
        self.templates_file = Path(templates_file)
        self.industry_map: dict = {}
        self.default_template = "{category} in {location}"
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load industry templates from YAML file."""
        try:
            with open(self.templates_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self.industry_map = data.get("industries", {})
                self.default_template = data.get("default_template", "{category} in {location}")
        except Exception as e:
            print(f"[QUERY_GEN] Warning: Could not load templates: {e}")
            self.industry_map = {}
    
    def generate_queries(
        self, 
        categories: List[str], 
        locations: Optional[List[str]] = None
    ) -> List[str]:
        """
        Generate search queries from categories and locations.
        
        Args:
            categories: List of category/industry names
            locations: Optional list of locations. If None, generates generic queries.
            
        Returns:
            List of generated query strings
        """
        queries = []
        
        if not locations:
            locations = [""]  # Generate queries without location
        
        for category in categories:
            category_lower = category.lower()
            
            # Find matching industry
            industry_config = None
            for industry, config in self.industry_map.items():
                keywords = config.get("keywords", [])
                if category_lower in industry or any(kw in category_lower for kw in keywords):
                    industry_config = config
                    break
            
            # Get templates for this industry
            if industry_config:
                templates = industry_config.get("templates", [self.default_template])
            else:
                templates = [self.default_template]
            
            # Generate queries for each location
            for location in locations:
                for template in templates:
                    query = template.format(category=category, location=location).strip()
                    if query and query not in queries:
                        queries.append(query)
        
        return queries
    
    def generate_from_config(self, config: dict) -> List[str]:
        """
        Generate queries from configuration.
        
        Args:
            config: Configuration dict with 'categories' and optionally 'locations'
            
        Returns:
            List of generated queries
        """
        categories = config.get("categories", [])
        locations = config.get("locations", None)
        
        return self.generate_queries(categories, locations)
    
    def get_available_industries(self) -> List[str]:
        """Get list of all available industries."""
        return list(self.industry_map.keys())

