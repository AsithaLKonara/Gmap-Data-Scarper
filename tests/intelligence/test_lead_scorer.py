"""Tests for lead scorer."""
import unittest
from intelligence.lead_scorer import LeadScorer
from scrapers.base import ScrapeResult


class TestLeadScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = LeadScorer()
    
    def test_score_lead(self):
        result: ScrapeResult = {
            "Display Name": "Test Business",
            "Profile URL": "https://example.com",
            "Platform": "facebook",
            "Followers": "1000",
            "last_post_date": "2 days ago",
            "business_type": "restaurant",
        }
        result = self.scorer.score(result)
        self.assertIn("lead_score", result)
        self.assertIsInstance(result["lead_score"], (int, float, str))
    
    def test_get_quality_tier(self):
        tier = self.scorer.get_quality_tier(75.0)
        self.assertIn(tier, ["high", "medium", "low"])


if __name__ == "__main__":
    unittest.main()

