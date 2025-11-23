"""Automated lead summary generation."""
from __future__ import annotations

import os
from typing import Optional

from scrapers.base import ScrapeResult


class LeadSummarizer:
    """
    Generates short summaries for leads.
    
    Template-based approach (can be enhanced with LLM).
    """
    
    def __init__(self, use_openai: bool = False):
        """
        Initialize lead summarizer.
        
        Args:
            use_openai: Use OpenAI API for summaries (requires API key)
        """
        self.use_openai = use_openai
        self.openai_api_key = os.getenv("OPENAI_API_KEY", None)
        if use_openai and not self.openai_api_key:
            self.use_openai = False  # Disable if no API key
    
    def summarize(self, result: ScrapeResult) -> ScrapeResult:
        """
        Generate summary for lead.
        
        Args:
            result: ScrapeResult dictionary
            
        Returns:
            ScrapeResult with added lead_summary field
        """
        # Try OpenAI API if enabled and API key available
        if self.use_openai and self.openai_api_key:
            summary = self._summarize_with_openai(result)
            if summary:
                result["lead_summary"] = summary
                return result
        
        # Fallback to template-based summary
        display_name = result.get("Display Name", "N/A")
        business_type = result.get("business_type", "N/A")
        city = result.get("city", "N/A")
        job_title = result.get("job_title", "N/A")
        seniority = result.get("seniority_level", "N/A")
        education = result.get("education_level", "N/A")
        followers = result.get("Followers", "N/A")
        is_boosted = result.get("is_boosted", "false")
        last_post = result.get("last_post_date", "N/A")
        
        # Build summary parts
        parts = []
        
        # Location
        if city != "N/A":
            parts.append(f"📍 {display_name}, {city}")
        else:
            parts.append(f"📍 {display_name}")
        
        # Business type
        if business_type != "N/A":
            parts.append(f"– {business_type.replace('_', ' ').title()}")
        
        # Job info
        if job_title != "N/A" and seniority != "N/A":
            parts.append(f"({seniority} {job_title})")
        elif job_title != "N/A":
            parts.append(f"({job_title})")
        
        # Education
        if education != "N/A":
            parts.append(f"– {education}")
        
        # Activity
        activity_parts = []
        if is_boosted == "true":
            activity_parts.append("active with boosted posts")
        elif last_post != "N/A":
            activity_parts.append(f"last post: {last_post}")
        
        if followers != "N/A" and followers != "0":
            activity_parts.append(f"{followers} followers")
        
        if activity_parts:
            parts.append("– " + ", ".join(activity_parts))
        
        summary = " ".join(parts)
        
        # Limit length
        if len(summary) > 200:
            summary = summary[:197] + "..."
        
        result["lead_summary"] = summary if summary else "N/A"
        
        return result
    
    def _summarize_with_openai(self, result: ScrapeResult) -> Optional[str]:
        """
        Generate summary using OpenAI API (optional, requires API key).
        
        Args:
            result: ScrapeResult dictionary
            
        Returns:
            Summary string or None if API fails
        """
        try:
            import requests
            
            # Build prompt
            display_name = result.get("Display Name", "N/A")
            bio = result.get("Bio/About", "N/A")
            business_type = result.get("business_type", "N/A")
            city = result.get("city", "N/A")
            job_title = result.get("job_title", "N/A")
            
            prompt = f"""Summarize this lead in 1-2 sentences:
Name: {display_name}
Bio: {bio}
Business Type: {business_type}
Location: {city}
Job Title: {job_title}

Summary:"""
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that summarizes business leads concisely."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 100,
                    "temperature": 0.7
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    summary = data["choices"][0]["message"]["content"].strip()
                    return summary[:200]  # Limit length
        except Exception:
            # API failed, fallback to template-based
            pass
        
        return None

