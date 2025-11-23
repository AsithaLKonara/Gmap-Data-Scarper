"""NLP-based intent detection for categorizing lead intent."""
from __future__ import annotations

import re
import yaml
import requests
from pathlib import Path
from typing import Dict, Optional

from scrapers.base import ScrapeResult


class IntentDetector:
    """
    Detects intent from bios and posts.
    
    Categories: Hiring, Promoting, Expanding, Inactive
    """
    
    def __init__(self, patterns_file: Optional[str] = None, use_huggingface: bool = True):
        """
        Initialize intent detector.
        
        Args:
            patterns_file: Path to intent_patterns.yaml. If None, uses default.
            use_huggingface: Use Hugging Face Inference API (free tier)
        """
        if patterns_file is None:
            patterns_file = Path(__file__).parent / "intent_patterns.yaml"
        
        self.patterns_file = Path(patterns_file)
        self.intent_config: Dict = {}
        self.use_huggingface = use_huggingface
        self.huggingface_api_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
        self._load_patterns()
    
    def _load_patterns(self) -> None:
        """Load intent patterns from YAML file."""
        try:
            with open(self.patterns_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self.intent_config = data.get("intents", {})
        except Exception as e:
            print(f"[INTENT] Warning: Could not load patterns: {e}")
            self.intent_config = {}
    
    def detect(self, result: ScrapeResult) -> ScrapeResult:
        """
        Detect intent from result.
        
        Args:
            result: ScrapeResult dictionary
            
        Returns:
            ScrapeResult with added intent_category field
        """
        bio = result.get("Bio/About", "").lower()
        display_name = result.get("Display Name", "").lower()
        
        text = f"{display_name} {bio}"
        
        # Try Hugging Face API first (free tier)
        if self.use_huggingface:
            intent = self._detect_with_huggingface(text)
            if intent != "N/A":
                result["intent_category"] = intent
                return result
        
        # Fallback to keyword-based detection
        best_intent = self._find_intent(text)
        result["intent_category"] = best_intent
        
        return result
    
    def _detect_with_huggingface(self, text: str) -> str:
        """
        Detect intent using Hugging Face Inference API.
        
        Args:
            text: Text to analyze
            
        Returns:
            Intent category or "N/A" if API fails
        """
        if not text or len(text.strip()) < 10:
            return "N/A"
        
        try:
            # Use a text classification model (free tier, no API key needed)
            # For intent detection, we'll use a sentiment/emotion model as proxy
            response = requests.post(
                self.huggingface_api_url,
                json={"inputs": text[:512]},  # Limit text length
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                # The model returns sentiment scores, we map to intent categories
                if isinstance(data, list) and len(data) > 0:
                    scores = data[0]
                    # Map sentiment to intent (simplified)
                    # Positive sentiment -> Promoting, Negative -> Hiring, Neutral -> Inactive
                    if scores:
                        best_label = max(scores, key=lambda x: x.get("score", 0))
                        label = best_label.get("label", "").lower()
                        
                        if "positive" in label or "joy" in label:
                            return "Promoting"
                        elif "negative" in label or "sadness" in label:
                            return "Hiring"
                        else:
                            return "Inactive"
        except Exception:
            # API failed, fallback to keyword-based
            pass
        
        return "N/A"
    
    def _find_intent(self, text: str) -> str:
        """
        Find best matching intent.
        
        Args:
            text: Text to analyze
            
        Returns:
            Intent category or "N/A"
        """
        best_score = 0
        best_intent = "N/A"
        
        for intent_key, config in self.intent_config.items():
            score = 0
            
            # Check keywords
            keywords = config.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in text:
                    score += 2
            
            # Check patterns
            patterns = config.get("patterns", [])
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 5  # Pattern matches are stronger
            
            if score > best_score:
                best_score = score
                best_intent = config.get("category", "N/A")
        
        return best_intent if best_score >= 2 else "N/A"

