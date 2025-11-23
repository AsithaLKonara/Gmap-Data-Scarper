"""Load testing with Locust."""
from locust import HttpUser, task, between
import random

class LeadIntelligenceUser(HttpUser):
    """Simulate user behavior for load testing."""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a simulated user starts."""
        # Health check
        self.client.get("/api/health")
    
    @task(3)
    def get_platforms(self):
        """Get available platforms."""
        self.client.get("/api/filters/platforms")
    
    @task(2)
    def get_business_types(self):
        """Get business types."""
        self.client.get("/api/filters/business-types")
    
    @task(1)
    def start_scraper(self):
        """Start a scraping task."""
        payload = {
            "queries": ["test query"],
            "platforms": ["google_maps"],
            "max_results": 5,
            "headless": True
        }
        response = self.client.post("/api/scraper/start", json=payload)
        if response.status_code == 200:
            task_id = response.json().get("task_id")
            if task_id:
                # Check task status
                self.client.get(f"/api/scraper/status/{task_id}")
    
    @task(1)
    def get_analytics_summary(self):
        """Get analytics summary."""
        self.client.get("/api/analytics/summary?days=7")
    
    @task(1)
    def export_data(self):
        """Export data."""
        format_type = random.choice(["csv", "json", "excel"])
        self.client.get(f"/api/export/{format_type}")

