"""Job title classification and seniority level detection."""
from __future__ import annotations

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from scrapers.base import ScrapeResult


class JobClassifier:
    """
    Extracts and classifies job titles from lead data.
    
    Analyzes:
    - LinkedIn profile headings
    - Facebook/Instagram bios
    - Display names
    - Bio/About text
    """
    
    def __init__(self, titles_file: Optional[str] = None):
        """
        Initialize job classifier with title patterns.
        
        Args:
            titles_file: Path to job_titles.yaml. If None, uses default.
        """
        if titles_file is None:
            titles_file = Path(__file__).parent / "job_titles.yaml"
        
        self.titles_file = Path(titles_file)
        self.job_patterns: Dict = {}
        self.seniority_levels: List[str] = []
        self._load_patterns()
    
    def _load_patterns(self) -> None:
        """Load job title patterns from YAML file."""
        try:
            with open(self.titles_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self.job_patterns = data.get("job_titles", {})
                self.seniority_levels = data.get("seniority_levels", [])
        except Exception as e:
            print(f"[JOB_CLASSIFIER] Warning: Could not load patterns: {e}")
            self.job_patterns = {}
            self.seniority_levels = []
    
    def classify(self, result: ScrapeResult) -> ScrapeResult:
        """
        Extract and classify job title from result.
        
        Args:
            result: ScrapeResult dictionary
            
        Returns:
            ScrapeResult with added job_title and seniority_level fields
        """
        # Extract text to analyze
        display_name = result.get("Display Name", "")
        bio = result.get("Bio/About", "")
        handle = result.get("Handle", "")
        
        # Combine all text
        text_to_analyze = f"{display_name} {bio} {handle}".lower()
        
        # Find job title
        job_title, seniority = self._extract_job_title(text_to_analyze, display_name, bio)
        
        result["job_title"] = job_title
        result["seniority_level"] = seniority
        
        return result
    
    def _extract_job_title(
        self, 
        text: str, 
        display_name: str, 
        bio: str
    ) -> Tuple[str, str]:
        """
        Extract job title and determine seniority level.
        
        Args:
            text: Combined lowercase text
            display_name: Original display name
            bio: Bio/About text
            
        Returns:
            Tuple of (job_title, seniority_level)
        """
        best_match = None
        best_score = 0
        best_seniority = "N/A"
        
        # Check each job category
        for category, config in self.job_patterns.items():
            patterns = config.get("patterns", [])
            seniority = config.get("seniority", "N/A")
            level = config.get("level", 0)
            
            for pattern in patterns:
                # Create regex pattern (word boundaries for better matching)
                regex_pattern = r'\b' + re.escape(pattern) + r'\b'
                
                matches = re.finditer(regex_pattern, text, re.IGNORECASE)
                for match in matches:
                    # Calculate score based on position and context
                    score = level
                    
                    # Higher score if in display name (more likely to be current role)
                    if pattern.lower() in display_name.lower():
                        score += 2
                    
                    # Higher score if in bio (also important)
                    if pattern.lower() in bio.lower():
                        score += 1
                    
                    if score > best_score:
                        best_score = score
                        # Extract the actual title (try to get full phrase)
                        title = self._extract_full_title(match, text, pattern)
                        best_match = title
                        best_seniority = seniority
        
        if best_match:
            return (best_match.title(), best_seniority)
        
        return ("N/A", "N/A")
    
    def _extract_full_title(self, match: re.Match, text: str, pattern: str) -> str:
        """
        Extract full job title phrase from match.
        
        Args:
            match: Regex match object
            pattern: Matched pattern
            text: Full text
            
        Returns:
            Full job title string
        """
        start = match.start()
        end = match.end()
        
        # Try to extract a reasonable phrase around the match
        # Look for common delimiters
        phrase_start = max(0, start - 30)
        phrase_end = min(len(text), end + 30)
        
        phrase = text[phrase_start:phrase_end]
        
        # Try to find sentence boundaries or common separators
        separators = [',', '|', '•', 'at', ' - ', ' — ']
        for sep in separators:
            if sep in phrase:
                parts = phrase.split(sep)
                for part in parts:
                    if pattern.lower() in part.lower():
                        return part.strip()
        
        # If no separator, return the pattern itself
        return pattern
    
    def filter_by_seniority(
        self, 
        results: List[ScrapeResult], 
        seniority_levels: List[str]
    ) -> List[ScrapeResult]:
        """
        Filter results by seniority level.
        
        Args:
            results: List of ScrapeResult dictionaries
            seniority_levels: List of seniority levels to include
            
        Returns:
            Filtered list of results
        """
        if not seniority_levels:
            return results
        
        seniority_lower = [s.lower() for s in seniority_levels]
        filtered = []
        
        for result in results:
            result_seniority = result.get("seniority_level", "N/A").lower()
            if result_seniority in seniority_lower:
                filtered.append(result)
        
        return filtered
    
    def filter_by_job_title(
        self, 
        results: List[ScrapeResult], 
        job_titles: List[str]
    ) -> List[ScrapeResult]:
        """
        Filter results by job title keywords.
        
        Args:
            results: List of ScrapeResult dictionaries
            job_titles: List of job title keywords to match
            
        Returns:
            Filtered list of results
        """
        if not job_titles:
            return results
        
        job_titles_lower = [jt.lower() for jt in job_titles]
        filtered = []
        
        for result in results:
            result_title = result.get("job_title", "N/A").lower()
            if any(jt in result_title for jt in job_titles_lower):
                filtered.append(result)
        
        return filtered

