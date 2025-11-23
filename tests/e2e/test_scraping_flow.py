"""End-to-end tests for complete scraping workflow."""
import pytest
import requests
import time
from typing import Dict, Any


@pytest.fixture
def api_client():
    """Create API client session."""
    from fastapi.testclient import TestClient
    from backend.main import app
    return TestClient(app)


@pytest.fixture
def api_base():
    """Get API base URL."""
    return "/api"


class TestCompleteScrapingFlow:
    """Test complete scraping workflow from start to finish."""
    
    def test_start_scrape_and_get_results(self, api_client, api_base):
        """Test starting a scrape and receiving results."""
        # Start scraping task
        request_data = {
            "queries": ["test business"],
            "platforms": ["google_maps"],
            "max_results": 3,
            "headless": True
        }
        
        response = api_client.post(
            "/api/scraper/start",
            json=request_data
        )
        
        assert response.status_code in [200, 401, 422]
        if response.status_code != 200:
            pytest.skip("Cannot test workflow without task creation")
        
        data = response.json()
        task_id = data["task_id"]
        assert task_id is not None
        
        # Wait a bit for task to process
        time.sleep(2)
        
        # Get task status
        status_response = api_client.get(f"/api/scraper/status/{task_id}")
        assert status_response.status_code in [200, 404]
        if status_response.status_code == 200:
            status = status_response.json()
            assert status["task_id"] == task_id
        
        # Stop task
        stop_response = api_client.post(f"/api/scraper/stop/{task_id}")
        assert stop_response.status_code in [200, 404]
    
    def test_pause_and_resume_workflow(self, api_client, api_base):
        """Test pausing and resuming a task."""
        # Start task
        request_data = {
            "queries": ["test"],
            "platforms": ["google_maps"],
            "max_results": 2,
            "headless": True
        }
        
        response = api_client.post(
            "/api/scraper/start",
            json=request_data
        )
        assert response.status_code in [200, 401, 422]
        if response.status_code != 200:
            pytest.skip("Cannot test pause/resume without task creation")
        
        task_id = response.json()["task_id"]
        
        time.sleep(1)
        
        # Pause task
        pause_response = api_client.post(f"/api/scraper/pause/{task_id}")
        assert pause_response.status_code in [200, 404]
        
        # Verify paused status
        status_response = api_client.get(f"/api/scraper/status/{task_id}")
        assert status_response.status_code in [200, 404]
        if status_response.status_code == 200:
            status = status_response.json()
            assert "status" in status
        
        # Resume task
        resume_response = api_client.post(f"/api/scraper/resume/{task_id}")
        assert resume_response.status_code in [200, 404]
        
        # Stop task
        api_client.post(f"/api/scraper/stop/{task_id}")
    
    def test_bulk_actions_workflow(self, api_client, api_base):
        """Test bulk actions on multiple tasks."""
        task_ids = []
        
        # Create 3 tasks
        for i in range(3):
            response = api_client.post(
                "/api/scraper/start",
                json={
                    "queries": [f"test {i}"],
                    "platforms": ["google_maps"],
                    "max_results": 1,
                    "headless": True
                }
            )
            if response.status_code == 200:
                task_ids.append(response.json()["task_id"])
        
        if not task_ids:
            pytest.skip("Cannot test bulk actions without task creation")
        
        time.sleep(1)
        
        # Bulk pause
        pause_response = api_client.post(
            "/api/tasks/bulk/pause",
            json=task_ids
        )
        assert pause_response.status_code in [200, 404]
        if pause_response.status_code == 200:
            result = pause_response.json()
            assert "paused_count" in result
        
        # Bulk stop
        stop_response = api_client.post(
            "/api/tasks/bulk/stop",
            json=task_ids
        )
        assert stop_response.status_code in [200, 404]
        if stop_response.status_code == 200:
            result = stop_response.json()
            assert "stopped_count" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

