"""Education level classification and institution extraction."""
from __future__ import annotations

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from scrapers.base import ScrapeResult


class EducationParser:
    """
    Extracts and classifies education levels from lead data.
    
    Analyzes:
    - LinkedIn education sections
    - Facebook profile education fields
    - Bio/About text
    """
    
    def __init__(self, patterns_file: Optional[str] = None):
        """
        Initialize education parser with patterns.
        
        Args:
            patterns_file: Path to education_patterns.yaml. If None, uses default.
        """
        if patterns_file is None:
            patterns_file = Path(__file__).parent / "education_patterns.yaml"
        
        self.patterns_file = Path(patterns_file)
        self.education_levels: Dict = {}
        self.institution_patterns: List[str] = []
        self._load_patterns()
    
    def _load_patterns(self) -> None:
        """Load education patterns from YAML file."""
        try:
            with open(self.patterns_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self.education_levels = data.get("education_levels", {})
                self.institution_patterns = data.get("institution_patterns", [])
        except Exception as e:
            print(f"[EDUCATION] Warning: Could not load patterns: {e}")
            self.education_levels = {}
            self.institution_patterns = []
    
    def parse(self, result: ScrapeResult) -> ScrapeResult:
        """
        Extract and classify education from result.
        
        Args:
            result: ScrapeResult dictionary
            
        Returns:
            ScrapeResult with added education_level and institution_name fields
        """
        # Extract text to analyze
        bio = result.get("Bio/About", "")
        display_name = result.get("Display Name", "")
        
        # Combine text
        text_to_analyze = f"{display_name} {bio}".lower()
        
        # Find education level
        education_level, institution = self._extract_education(text_to_analyze, bio)
        
        result["education_level"] = education_level
        result["institution_name"] = institution
        
        return result
    
    def _extract_education(self, text: str, bio: str) -> Tuple[str, str]:
        """
        Extract education level and institution name.
        
        Args:
            text: Combined lowercase text
            bio: Original bio text (for institution extraction)
            
        Returns:
            Tuple of (education_level, institution_name)
        """
        best_level = "N/A"
        best_priority = 0
        institution = "N/A"
        
        # Check each education level
        for level_key, config in self.education_levels.items():
            patterns = config.get("patterns", [])
            level_name = config.get("level", "N/A")
            priority = config.get("priority", 0)
            
            for pattern in patterns:
                # Create regex pattern
                regex_pattern = r'\b' + re.escape(pattern) + r'\b'
                
                if re.search(regex_pattern, text, re.IGNORECASE):
                    if priority > best_priority:
                        best_priority = priority
                        best_level = level_name
        
        # Extract institution name
        if bio:
            institution = self._extract_institution(bio)
        
        return (best_level, institution)
    
    def _extract_institution(self, bio: str) -> str:
        """
        Extract institution name from bio text.
        
        Args:
            bio: Bio/About text
            
        Returns:
            Institution name or "N/A"
        """
        bio_lower = bio.lower()
        
        # Look for institution patterns
        for pattern in self.institution_patterns:
            # Try to find the institution name around the pattern
            match = re.search(rf"([A-Z][^.!?]*?\b{re.escape(pattern)}\b[^.!?]*)", bio, re.IGNORECASE)
            if match:
                institution = match.group(1).strip()
                # Clean up common prefixes/suffixes
                institution = re.sub(r"^(at|from|studied at|graduated from)\s+", "", institution, flags=re.IGNORECASE)
                institution = re.sub(r"\s+(university|college|institute|school).*$", "", institution, flags=re.IGNORECASE)
                if institution and len(institution) > 3:
                    return institution
        
        return "N/A"
    
    def filter_by_education(
        self, 
        results: List[ScrapeResult], 
        education_levels: List[str]
    ) -> List[ScrapeResult]:
        """
        Filter results by education level.
        
        Args:
            results: List of ScrapeResult dictionaries
            education_levels: List of education levels to include
            
        Returns:
            Filtered list of results
        """
        if not education_levels:
            return results
        
        education_lower = [e.lower() for e in education_levels]
        filtered = []
        
        for result in results:
            result_education = result.get("education_level", "N/A").lower()
            if result_education in education_lower:
                filtered.append(result)
        
        return filtered

