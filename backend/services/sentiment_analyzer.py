"""Sentiment analysis and intent detection service."""
from typing import Dict, Any, Optional, List
import os


class SentimentAnalyzer:
    """Service for analyzing sentiment and detecting intent."""
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_ai = bool(self.openai_api_key)
    
    def analyze_sentiment(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with sentiment analysis
        """
        if not text or len(text) < 10:
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": 0.0
            }
        
        if self.use_ai:
            return self._analyze_with_ai(text)
        else:
            return self._analyze_rule_based(text)
    
    def _analyze_with_ai(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using AI."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Analyze sentiment. Respond with JSON: {\"sentiment\": \"positive|negative|neutral\", \"score\": 0.0-1.0, \"confidence\": 0.0-1.0}"},
                    {"role": "user", "content": f"Text: {text[:500]}\n\nAnalyze sentiment:"}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            import json
            result = json.loads(response.choices[0].message.content.strip())
            return result
        except:
            return self._analyze_rule_based(text)
    
    def _analyze_rule_based(self, text: str) -> Dict[str, Any]:
        """Rule-based sentiment analysis."""
        text_lower = text.lower()
        
        positive_words = ["good", "great", "excellent", "amazing", "love", "best", "perfect", "wonderful"]
        negative_words = ["bad", "terrible", "awful", "hate", "worst", "poor", "disappointed"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            score = min(1.0, 0.5 + (positive_count * 0.1))
        elif negative_count > positive_count:
            sentiment = "negative"
            score = max(0.0, 0.5 - (negative_count * 0.1))
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {
            "sentiment": sentiment,
            "score": round(score, 2),
            "confidence": 0.7  # Rule-based has lower confidence
        }
    
    def detect_intent(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        Detect intent from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with intent detection
        """
        if not text or len(text) < 10:
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "keywords": []
            }
        
        text_lower = text.lower()
        
        # Intent patterns
        buying_intents = ["buy", "purchase", "need", "looking for", "interested in", "want"]
        selling_intents = ["sell", "offer", "provide", "service", "available"]
        inquiry_intents = ["question", "ask", "wonder", "curious", "information"]
        complaint_intents = ["problem", "issue", "complaint", "wrong", "error"]
        
        intents = []
        
        if any(word in text_lower for word in buying_intents):
            intents.append({"intent": "buying", "confidence": 0.7})
        
        if any(word in text_lower for word in selling_intents):
            intents.append({"intent": "selling", "confidence": 0.7})
        
        if any(word in text_lower for word in inquiry_intents):
            intents.append({"intent": "inquiry", "confidence": 0.6})
        
        if any(word in text_lower for word in complaint_intents):
            intents.append({"intent": "complaint", "confidence": 0.8})
        
        if not intents:
            intents.append({"intent": "general", "confidence": 0.5})
        
        # Get top intent
        top_intent = max(intents, key=lambda x: x["confidence"])
        
        # Extract keywords
        keywords = self._extract_keywords(text)
        
        return {
            "intent": top_intent["intent"],
            "confidence": top_intent["confidence"],
            "all_intents": intents,
            "keywords": keywords
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        import re
        
        # Simple keyword extraction (remove stop words)
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Get most common
        from collections import Counter
        common = Counter(keywords).most_common(5)
        
        return [word for word, count in common]


# Global instance
sentiment_analyzer = SentimentAnalyzer()

