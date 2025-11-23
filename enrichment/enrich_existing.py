"""Data enrichment API for re-scraping and updating existing datasets."""
from __future__ import annotations

import csv
import os
from typing import Dict, List, Optional

from scrapers.base import ScrapeResult
from classification import BusinessClassifier, JobClassifier, EducationParser
from utils.geolocation import GeolocationExtractor
from enrichment import ActivityScraper
from intelligence import LeadScorer


class EnrichmentAPI:
    """
    Enriches existing CSV datasets with new metadata.
    
    Reads existing CSV, re-scrapes profiles, and updates with:
    - Classification data (business type, job title, education)
    - Location data
    - Activity data
    - Lead scores
    """
    
    def __init__(self):
        """Initialize enrichment API with all classifiers."""
        self.business_classifier = BusinessClassifier()
        self.job_classifier = JobClassifier()
        self.education_parser = EducationParser()
        self.geolocation_extractor = GeolocationExtractor()
        self.activity_scraper = ActivityScraper()
        self.lead_scorer = LeadScorer()
    
    def enrich_csv(
        self,
        input_csv: str,
        output_csv: str,
        platforms: Optional[List[str]] = None
    ) -> None:
        """
        Enrich existing CSV file with new metadata.
        
        Args:
            input_csv: Path to input CSV file
            output_csv: Path to output enriched CSV file
            platforms: Optional list of platforms to enrich (None = all)
        """
        if not os.path.exists(input_csv):
            raise FileNotFoundError(f"Input CSV not found: {input_csv}")
        
        # Read existing data
        rows = []
        with open(input_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"[ENRICH] Processing {len(rows)} rows...")
        
        # Enrich each row
        enriched_rows = []
        for idx, row in enumerate(rows, 1):
            if platforms and row.get("Platform", "") not in platforms:
                enriched_rows.append(row)
                continue
            
            print(f"[ENRICH] [{idx}/{len(rows)}] Enriching: {row.get('Display Name', 'N/A')}")
            
            # Convert row to ScrapeResult format
            result: ScrapeResult = dict(row)
            
            # Apply all enrichment
            try:
                result = self.business_classifier.classify(result)
                result = self.job_classifier.classify(result)
                result = self.education_parser.parse(result)
                
                # Extract location
                address = result.get("Address", "")
                if address and address != "N/A":
                    location_data = self.geolocation_extractor.extract_location(address)
                    result.update(location_data)
                
                # Scrape activity
                profile_url = result.get("Profile URL", "")
                platform = result.get("Platform", "")
                if profile_url and profile_url != "N/A" and platform in ["facebook", "instagram", "x", "tiktok"]:
                    activity_data = self.activity_scraper.scrape_activity(profile_url, platform)
                    result.update(activity_data)
                
                # Calculate lead score
                result = self.lead_scorer.score(result)
                
            except Exception as e:
                print(f"[ENRICH] Error enriching row {idx}: {e}")
            
            enriched_rows.append(result)
        
        # Write enriched data
        if enriched_rows:
            fieldnames = list(enriched_rows[0].keys())
            with open(output_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(enriched_rows)
            
            print(f"[ENRICH] Enriched data saved to: {output_csv}")
        else:
            print("[ENRICH] No rows to write")


def enrich_existing_csv(input_csv: str, output_csv: Optional[str] = None) -> None:
    """
    Convenience function to enrich an existing CSV.
    
    Args:
        input_csv: Path to input CSV
        output_csv: Optional output path (default: input_csv with _enriched suffix)
    """
    if output_csv is None:
        base, ext = os.path.splitext(input_csv)
        output_csv = f"{base}_enriched{ext}"
    
    api = EnrichmentAPI()
    api.enrich_csv(input_csv, output_csv)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m enrichment.enrich_existing <input_csv> [output_csv]")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else None
    
    enrich_existing_csv(input_csv, output_csv)

