"""Tests for business classifier."""
import unittest
from classification.business_classifier import BusinessClassifier
from scrapers.base import ScrapeResult


class TestBusinessClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = BusinessClassifier()
    
    def test_classify_restaurant(self):
        result: ScrapeResult = {
            "Display Name": "Joe's Pizza",
            "Category": "Restaurant",
            "Bio/About": "Italian restaurant serving pizza",
        }
        result = self.classifier.classify(result)
        self.assertIn("business_type", result)
        self.assertIn("industry", result)
    
    def test_classify_software(self):
        result: ScrapeResult = {
            "Display Name": "Tech Solutions Inc",
            "Category": "Software Company",
            "Website": "techsolutions.com",
        }
        result = self.classifier.classify(result)
        self.assertIn("business_type", result)


if __name__ == "__main__":
    unittest.main()

