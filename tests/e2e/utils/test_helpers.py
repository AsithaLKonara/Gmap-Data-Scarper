"""Test helper utilities for E2E tests."""
import time
import json
from typing import Dict, List, Optional
from fastapi.testclient import TestClient
from websockets import connect
import asyncio


class TestHelpers:
    """Helper utilities for E2E testing."""
    
    @staticmethod
    def wait_for_condition(condition_func, timeout: int = 30, interval: float = 0.5):
        """Wait for a condition to be true."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        return False
    
    @staticmethod
    def create_task_via_api(client: TestClient, request_data: Dict) -> Optional[str]:
        """Create a scraping task via API and return task_id."""
        response = client.post("/api/scraper/start", json=request_data)
        if response.status_code == 200:
            return response.json().get("task_id")
        return None
    
    @staticmethod
    def get_task_status(client: TestClient, task_id: str) -> Optional[Dict]:
        """Get task status via API."""
        response = client.get(f"/api/scraper/status/{task_id}")
        if response.status_code == 200:
            return response.json()
        return None
    
    @staticmethod
    def stop_task_via_api(client: TestClient, task_id: str) -> bool:
        """Stop a task via API."""
        response = client.post(f"/api/scraper/stop/{task_id}")
        return response.status_code == 200
    
    @staticmethod
    async def connect_websocket(base_url: str, task_id: str, ws_type: str = "logs"):
        """Connect to WebSocket and return connection."""
        ws_url = f"{base_url.replace('http://', 'ws://').replace('https://', 'wss://')}/api/scraper/ws/{ws_type}/{task_id}"
        return await connect(ws_url)
    
    @staticmethod
    async def receive_websocket_messages(ws, max_messages: int = 10, timeout: float = 5.0):
        """Receive messages from WebSocket."""
        messages = []
        start_time = time.time()
        
        try:
            while len(messages) < max_messages and (time.time() - start_time) < timeout:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    messages.append(json.loads(message))
                except asyncio.TimeoutError:
                    continue
        except Exception:
            pass
        
        return messages
    
    @staticmethod
    def check_health_endpoint(client: TestClient) -> bool:
        """Check if health endpoint is responding."""
        response = client.get("/health")
        return response.status_code == 200 and response.json().get("status") == "healthy"
    
    @staticmethod
    def check_metrics_endpoint(client: TestClient) -> bool:
        """Check if metrics endpoint is responding."""
        response = client.get("/metrics")
        return response.status_code == 200 and "active_tasks" in response.json()
    
    @staticmethod
    def export_csv_via_api(client: TestClient, task_id: Optional[str] = None) -> Optional[bytes]:
        """Export CSV via API."""
        url = "/api/export/csv"
        if task_id:
            url += f"?task_id={task_id}"
        
        response = client.get(url)
        if response.status_code == 200:
            return response.content
        return None
    
    @staticmethod
    def count_csv_records(csv_content: bytes) -> int:
        """Count records in CSV content."""
        if not csv_content:
            return 0
        
        lines = csv_content.decode('utf-8').strip().split('\n')
        # Subtract 1 for header
        return max(0, len(lines) - 1)

