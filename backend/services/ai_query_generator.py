"""AI-powered query generation service for natural language lead finding."""
from typing import Dict, Any, List, Optional
import os
import json


class AIQueryGenerator:
    """Service for generating search queries and configurations from natural language."""
    
    def __init__(self):
        """Initialize AI query generator."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.use_openai = bool(self.openai_api_key)
        self.use_anthropic = bool(self.anthropic_api_key) and not self.use_openai
    
    def generate_search_config(self, user_input: str) -> Dict[str, Any]:
        """
        Generate search configuration from natural language input.
        
        Args:
            user_input: Natural language query (e.g., "Find me 500 Shopify stores in Canada doing paid ads")
            
        Returns:
            Dict with generated queries, platforms, filters, and expected results
        """
        if self.use_openai:
            return self._generate_with_openai(user_input)
        elif self.use_anthropic:
            return self._generate_with_anthropic(user_input)
        else:
            # Fallback to rule-based generation if no AI API available
            return self._generate_rule_based(user_input)
    
    def _generate_with_openai(self, user_input: str) -> Dict[str, Any]:
        """Generate using OpenAI GPT-4."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            prompt = f"""You are a lead generation expert. Analyze this user request and generate an optimal search configuration.

User Request: "{user_input}"

Generate a JSON response with:
1. "queries": List of optimized search queries (3-5 variations)
2. "platforms": List of recommended platforms (from: google_maps, facebook, instagram, linkedin, x, youtube, tiktok, yelp, crunchbase, tripadvisor, indeed, github)
3. "filters": Object with recommended filters (business_type, location, job_level, etc.)
4. "expected_results": Estimated number of results (high/medium/low)
5. "confidence": Confidence score 0-100
6. "reasoning": Brief explanation of the configuration

Example response:
{{
  "queries": ["Shopify stores Canada", "Shopify ecommerce Canada", "Shopify online stores Canada"],
  "platforms": ["google_maps", "crunchbase", "linkedin"],
  "filters": {{
    "business_type": ["ecommerce", "online_store"],
    "location": "Canada"
  }},
  "expected_results": "high",
  "confidence": 85,
  "reasoning": "Focusing on ecommerce platforms and Canadian businesses"
}}

Respond with JSON only, no markdown formatting."""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a lead generation expert. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            print(f"[AI] OpenAI generation failed: {e}")
            return self._generate_rule_based(user_input)
    
    def _generate_with_anthropic(self, user_input: str) -> Dict[str, Any]:
        """Generate using Anthropic Claude."""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.anthropic_api_key)
            
            prompt = f"""You are a lead generation expert. Analyze this user request and generate an optimal search configuration.

User Request: "{user_input}"

Generate a JSON response with:
1. "queries": List of optimized search queries (3-5 variations)
2. "platforms": List of recommended platforms
3. "filters": Object with recommended filters
4. "expected_results": Estimated number of results (high/medium/low)
5. "confidence": Confidence score 0-100
6. "reasoning": Brief explanation

Respond with JSON only."""

            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            print(f"[AI] Anthropic generation failed: {e}")
            return self._generate_rule_based(user_input)
    
    def _generate_rule_based(self, user_input: str) -> Dict[str, Any]:
        """Fallback rule-based generation."""
        user_lower = user_input.lower()
        
        # Extract quantity
        quantity = 100
        for num in ["500", "1000", "100", "50", "200"]:
            if num in user_input:
                quantity = int(num)
                break
        
        # Extract location
        location = None
        locations = ["canada", "toronto", "usa", "united states", "uk", "london", "australia", "sydney"]
        for loc in locations:
            if loc in user_lower:
                location = loc.title()
                break
        
        # Determine business type
        business_type = []
        if "shopify" in user_lower or "ecommerce" in user_lower:
            business_type = ["ecommerce", "online_store"]
        elif "restaurant" in user_lower:
            business_type = ["restaurant", "cafe"]
        elif "software" in user_lower or "saas" in user_lower:
            business_type = ["software", "saas", "tech"]
        elif "clinic" in user_lower or "medical" in user_lower:
            business_type = ["medical", "clinic", "healthcare"]
        
        # Determine platforms
        platforms = ["google_maps", "linkedin"]
        if "shopify" in user_lower or "ecommerce" in user_lower:
            platforms = ["google_maps", "crunchbase", "linkedin"]
        elif "restaurant" in user_lower:
            platforms = ["google_maps", "yelp", "tripadvisor"]
        
        # Generate queries
        base_query = user_input.split("in")[0].strip() if "in" in user_input else user_input
        queries = [
            base_query,
            f"{base_query} {location}" if location else base_query,
            f"{base_query} businesses" if "business" not in base_query.lower() else base_query
        ]
        
        return {
            "queries": queries[:3],
            "platforms": platforms,
            "filters": {
                "business_type": business_type if business_type else None,
                "location": location
            },
            "expected_results": "high" if quantity >= 500 else "medium",
            "confidence": 70,
            "reasoning": "Rule-based generation based on keywords"
        }


# Global instance
ai_query_generator = AIQueryGenerator()

