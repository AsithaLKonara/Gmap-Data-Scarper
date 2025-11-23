"""Tests for job classifier."""
import unittest
from classification.job_classifier import JobClassifier
from scrapers.base import ScrapeResult


class TestJobClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = JobClassifier()
    
    def test_classify_ceo(self):
        result: ScrapeResult = {
            "Display Name": "John Smith",
            "Bio/About": "CEO and Founder of ABC Corp",
        }
        result = self.classifier.classify(result)
        self.assertIn("job_title", result)
        self.assertIn("seniority_level", result)
    
    def test_classify_manager(self):
        result: ScrapeResult = {
            "Display Name": "Jane Doe",
            "Bio/About": "Marketing Manager at XYZ",
        }
        result = self.classifier.classify(result)
        self.assertIn("job_title", result)


if __name__ == "__main__":
    unittest.main()

