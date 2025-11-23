"""Test data fixtures for E2E tests."""
from typing import Dict, List
import json
from pathlib import Path


class TestDataFixtures:
    """Provides test data for E2E tests."""
    
    @staticmethod
    def get_sample_queries() -> List[str]:
        """Get sample search queries for testing."""
        return [
            "restaurants in New York",
            "dentists in Los Angeles",
            "ICT students in Toronto",
        ]
    
    @staticmethod
    def get_sample_scrape_request() -> Dict:
        """Get sample scrape request payload."""
        return {
            "queries": ["restaurants in New York"],
            "platforms": ["google_maps"],
            "max_results": 10,
            "headless": True,
        }
    
    @staticmethod
    def get_sample_result() -> Dict:
        """Get sample scrape result."""
        return {
            "search_query": "restaurants in New York",
            "platform": "google_maps",
            "profile_url": "https://maps.google.com/?cid=123456789",
            "display_name": "Test Restaurant",
            "phone": "+1234567890",
            "location": "New York, NY",
            "phones": [
                {
                    "raw_phone": "+1234567890",
                    "normalized_e164": "+1234567890",
                    "validation_status": "valid",
                    "confidence_score": 95,
                    "phone_source": "tel_link",
                }
            ],
        }
    
    @staticmethod
    def get_mock_websocket_message() -> Dict:
        """Get mock WebSocket message."""
        return {
            "type": "result",
            "data": TestDataFixtures.get_sample_result(),
        }
    
    @staticmethod
    def create_test_csv_data(num_records: int = 100) -> List[Dict]:
        """Create test CSV data for volume testing."""
        records = []
        for i in range(num_records):
            records.append({
                "Search Query": f"test query {i}",
                "Platform": "google_maps",
                "Profile URL": f"https://example.com/profile/{i}",
                "Display Name": f"Test Business {i}",
                "Phone": f"+123456789{i:02d}",
                "Location": f"Test City {i}",
            })
        return records

