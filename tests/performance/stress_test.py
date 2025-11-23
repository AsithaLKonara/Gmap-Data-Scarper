"""Performance and stress tests."""
import pytest
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict


BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"


class TestConcurrency:
    """Test system under concurrent load."""
    
    def test_multiple_requests(self):
        """Test handling multiple simultaneous requests."""
        def make_request():
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=5)
                return response.status_code == 200
            except:
                return False
        
        # Make 20 concurrent requests
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [f.result() for f in as_completed(futures)]
        
        # At least 80% should succeed
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.8, f"Success rate {success_rate} below 80%"
    
    def test_concurrent_task_creation(self):
        """Test creating multiple tasks concurrently."""
        def create_task(task_num):
            try:
                response = requests.post(
                    f"{API_BASE}/scraper/start",
                    json={
                        "queries": [f"test query {task_num}"],
                        "platforms": ["google_maps"],
                        "max_results": 1,
                        "headless": True
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    return response.json().get("task_id")
                return None
            except:
                return None
        
        # Create 5 tasks concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_task, i) for i in range(5)]
            task_ids = [f.result() for f in as_completed(futures)]
        
        # At least 3 should succeed
        successful = [tid for tid in task_ids if tid]
        assert len(successful) >= 3, f"Only {len(successful)} tasks created successfully"


class TestMemoryLeaks:
    """Test for memory leaks."""
    
    def test_long_running_requests(self):
        """Test system stability over time."""
        start_time = time.time()
        request_count = 0
        errors = 0
        
        # Run for 1 minute (or shorter in tests)
        test_duration = 30  # 30 seconds for test
        
        while time.time() - start_time < test_duration:
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=5)
                if response.status_code != 200:
                    errors += 1
                request_count += 1
                time.sleep(1)
            except:
                errors += 1
            
            # Check error rate doesn't increase over time
            if request_count > 10:
                error_rate = errors / request_count
                assert error_rate < 0.1, f"Error rate {error_rate} too high"
        
        assert request_count > 0, "No requests made"


class TestResponseTimes:
    """Test API response times."""
    
    def test_health_endpoint_response_time(self):
        """Test health endpoint responds quickly."""
        start = time.time()
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 1.0, f"Health check took {duration}s (should be < 1s)"
    
    def test_task_creation_response_time(self):
        """Test task creation responds in reasonable time."""
        start = time.time()
        response = requests.post(
            f"{API_BASE}/scraper/start",
            json={
                "queries": ["test"],
                "platforms": ["google_maps"],
                "max_results": 1,
                "headless": True
            },
            timeout=10
        )
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 5.0, f"Task creation took {duration}s (should be < 5s)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

