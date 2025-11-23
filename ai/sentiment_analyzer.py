"""Sentiment analysis for social posts."""
from __future__ import annotations

import re
import requests
from typing import Dict, Optional, Any

from scrapers.base import ScrapeResult


class SentimentAnalyzer:
    """
    Analyzes sentiment of social posts.
    
    Simple keyword-based approach (can be enhanced with NLP libraries).
    """
    
    def __init__(self, use_huggingface: bool = True):
        """
        Initialize sentiment analyzer.
        
        Args:
            use_huggingface: Use Hugging Face Inference API (free tier)
        """
        self.use_huggingface = use_huggingface
        self.huggingface_api_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
        
        # Positive keywords (fallback)
        self.positive_keywords = [
            "great", "excellent", "amazing", "wonderful", "fantastic",
            "love", "happy", "excited", "thrilled", "proud",
            "success", "achievement", "win", "best", "top"
        ]
        
        # Negative keywords (fallback)
        self.negative_keywords = [
            "bad", "terrible", "awful", "disappointed", "frustrated",
            "problem", "issue", "error", "fail", "worst",
            "sad", "angry", "upset", "concerned", "worried"
        ]
    
    def analyze(self, result: ScrapeResult) -> ScrapeResult:
        """
        Analyze sentiment of result.
        
        Args:
            result: ScrapeResult dictionary
            
        Returns:
            ScrapeResult with added sentiment_score and sentiment_trend fields
        """
        bio = result.get("Bio/About", "").lower()
        text = bio
        
        if not text or text == "n/a":
            result["sentiment_score"] = "N/A"
            result["sentiment_trend"] = "N/A"
            return result
        
        # Try Hugging Face API first (free tier)
        if self.use_huggingface:
            sentiment_data = self._analyze_with_huggingface(text)
            if sentiment_data:
                result["sentiment_score"] = sentiment_data["score"]
                result["sentiment_trend"] = sentiment_data["trend"]
                return result
        
        # Fallback to keyword-based analysis
        positive_count = sum(1 for word in self.positive_keywords if word in text)
        negative_count = sum(1 for word in self.negative_keywords if word in text)
        
        # Calculate sentiment score (-1 to 1, scaled to 0-100)
        total_keywords = positive_count + negative_count
        if total_keywords == 0:
            sentiment_score = 50.0  # Neutral
        else:
            sentiment_ratio = (positive_count - negative_count) / max(total_keywords, 1)
            sentiment_score = 50.0 + (sentiment_ratio * 50.0)  # Scale to 0-100
        
        # Determine trend
        if sentiment_score >= 70:
            trend = "Positive"
        elif sentiment_score >= 40:
            trend = "Neutral"
        else:
            trend = "Negative"
        
        result["sentiment_score"] = round(sentiment_score, 2)
        result["sentiment_trend"] = trend
        
        return result
    
    def _analyze_with_huggingface(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Analyze sentiment using Hugging Face Inference API.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with score and trend, or None if API fails
        """
        if not text or len(text.strip()) < 10:
            return None
        
        try:
            response = requests.post(
                self.huggingface_api_url,
                json={"inputs": text[:512]},  # Limit text length
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    scores = data[0]
                    if scores:
                        # Find best sentiment label
                        best_label = max(scores, key=lambda x: x.get("score", 0))
                        label = best_label.get("label", "").lower()
                        score_value = best_label.get("score", 0.5)
                        
                        # Map to 0-100 scale
                        if "positive" in label:
                            sentiment_score = 50.0 + (score_value * 50.0)  # 50-100
                            trend = "Positive"
                        elif "negative" in label:
                            sentiment_score = 50.0 - (score_value * 50.0)  # 0-50
                            trend = "Negative"
                        else:
                            sentiment_score = 50.0  # Neutral
                            trend = "Neutral"
                        
                        return {
                            "score": round(sentiment_score, 2),
                            "trend": trend
                        }
        except Exception:
            # API failed, fallback to keyword-based
            pass
        
        return None

