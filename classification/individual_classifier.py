"""Individual lead classifier (students, professionals)."""
from __future__ import annotations

import re
import yaml
from pathlib import Path
from typing import Dict, Optional, Tuple

from scrapers.base import ScrapeResult


class IndividualClassifier:
    """
    Classifies leads as individuals (students, professionals) vs businesses.
    
    Extracts:
    - Field of study (e.g., "ICT", "Computer Science")
    - Degree program
    - Institution name
    - Graduation year
    """
    
    def __init__(
        self,
        student_patterns_file: Optional[str] = None,
        career_patterns_file: Optional[str] = None
    ):
        """
        Initialize individual classifier.
        
        Args:
            student_patterns_file: Path to student_patterns.yaml
            career_patterns_file: Path to career_patterns.yaml
        """
        if student_patterns_file is None:
            student_patterns_file = Path(__file__).parent / "student_patterns.yaml"
        if career_patterns_file is None:
            career_patterns_file = Path(__file__).parent / "career_patterns.yaml"
        
        self.student_patterns_file = Path(student_patterns_file)
        self.career_patterns_file = Path(career_patterns_file)
        
        self.student_patterns: Dict = {}
        self.career_patterns: Dict = {}
        self.field_of_study_keywords: Dict[str, list] = {}
        
        self._load_patterns()
    
    def _load_patterns(self) -> None:
        """Load student and career patterns from YAML files."""
        try:
            # Load student patterns
            if self.student_patterns_file.exists():
                with open(self.student_patterns_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    self.student_patterns = data.get("student_patterns", [])
                    self.field_of_study_keywords = data.get("field_of_study_keywords", {})
        except Exception as e:
            print(f"[INDIVIDUAL] Warning: Could not load student patterns: {e}")
            self.student_patterns = []
            self.field_of_study_keywords = {}
        
        try:
            # Load career patterns
            if self.career_patterns_file.exists():
                with open(self.career_patterns_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    self.career_patterns = data.get("career_patterns", [])
        except Exception as e:
            print(f"[INDIVIDUAL] Warning: Could not load career patterns: {e}")
            self.career_patterns = []
    
    def classify(self, result: ScrapeResult) -> ScrapeResult:
        """
        Classify lead as individual or business and extract education/career info.
        
        Args:
            result: ScrapeResult dictionary
            
        Returns:
            ScrapeResult with added:
            - lead_type: "individual" or "business"
            - field_of_study: Extracted field of study
            - degree_program: Degree program name
            - graduation_year: Year of graduation (if available)
        """
        # Extract text to analyze
        bio = result.get("Bio/About", "")
        display_name = result.get("Display Name", "")
        job_title = result.get("job_title", "")
        
        # Combine text
        text_to_analyze = f"{display_name} {bio} {job_title}".lower()
        
        # Determine if individual or business
        lead_type = self._determine_lead_type(text_to_analyze, bio)
        
        # Extract field of study
        field_of_study = self._extract_field_of_study(text_to_analyze, bio)
        
        # Extract degree program
        degree_program = self._extract_degree_program(text_to_analyze, bio)
        
        # Extract graduation year
        graduation_year = self._extract_graduation_year(bio)
        
        # Update result
        result["lead_type"] = lead_type
        result["field_of_study"] = field_of_study
        result["degree_program"] = degree_program
        result["graduation_year"] = graduation_year
        
        return result
    
    def _determine_lead_type(self, text: str, bio: str) -> str:
        """
        Determine if lead is individual or business.
        
        Args:
            text: Combined lowercase text
            bio: Original bio text
            
        Returns:
            "individual" or "business"
        """
        # Check for student patterns
        for pattern in self.student_patterns:
            if re.search(r'\b' + re.escape(pattern.lower()) + r'\b', text, re.IGNORECASE):
                return "individual"
        
        # Check for career patterns (professionals)
        for pattern in self.career_patterns:
            if re.search(r'\b' + re.escape(pattern.lower()) + r'\b', text, re.IGNORECASE):
                return "individual"
        
        # Check for business indicators
        business_indicators = [
            "company", "corporation", "inc", "llc", "ltd", "business",
            "services", "solutions", "enterprise", "group", "agency"
        ]
        for indicator in business_indicators:
            if re.search(r'\b' + re.escape(indicator) + r'\b', text, re.IGNORECASE):
                return "business"
        
        # Default: assume individual if has personal indicators
        personal_indicators = ["student", "graduate", "alumni", "studying", "major"]
        for indicator in personal_indicators:
            if re.search(r'\b' + re.escape(indicator) + r'\b', text, re.IGNORECASE):
                return "individual"
        
        # Default to business if no clear indicators
        return "business"
    
    def _extract_field_of_study(self, text: str, bio: str) -> str:
        """
        Extract field of study from text.
        
        Args:
            text: Combined lowercase text
            bio: Original bio text
            
        Returns:
            Field of study or "N/A"
        """
        # Check field of study keywords
        for field, keywords in self.field_of_study_keywords.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text, re.IGNORECASE):
                    return field
        
        # Try to extract from common patterns
        patterns = [
            r"studying\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"major(?:ing)?\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"degree\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, bio, re.IGNORECASE)
            if match:
                field = match.group(1).strip()
                if len(field) > 2:
                    return field
        
        return "N/A"
    
    def _extract_degree_program(self, text: str, bio: str) -> str:
        """
        Extract degree program name.
        
        Args:
            text: Combined lowercase text
            bio: Original bio text
            
        Returns:
            Degree program or "N/A"
        """
        # Look for degree patterns
        degree_patterns = [
            r"bachelor['\s]s?\s+(?:degree\s+)?(?:in\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"master['\s]s?\s+(?:degree\s+)?(?:in\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"ph\.?d\.?\s+(?:degree\s+)?(?:in\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"b\.?s\.?\s+(?:degree\s+)?(?:in\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"m\.?s\.?\s+(?:degree\s+)?(?:in\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        ]
        
        for pattern in degree_patterns:
            match = re.search(pattern, bio, re.IGNORECASE)
            if match:
                program = match.group(1).strip()
                if len(program) > 2:
                    return program
        
        return "N/A"
    
    def _extract_graduation_year(self, bio: str) -> Optional[int]:
        """
        Extract graduation year from bio.
        
        Args:
            bio: Bio/About text
            
        Returns:
            Graduation year (int) or None
        """
        # Look for year patterns (4 digits, likely 2000-2030)
        year_patterns = [
            r"graduated\s+(?:in\s+)?(20\d{2})",
            r"class\s+of\s+(20\d{2})",
            r"(?:graduation|grad)\s+year[:\s]+(20\d{2})",
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, bio, re.IGNORECASE)
            if match:
                try:
                    year = int(match.group(1))
                    if 2000 <= year <= 2030:
                        return year
                except:
                    pass
        
        return None

