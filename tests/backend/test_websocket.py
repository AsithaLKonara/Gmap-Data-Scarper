"""Tests for WebSocket functionality."""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


class TestWebSocket:
    """Test WebSocket endpoints."""
    
    def test_logs_websocket_connection(self):
        """Test logs WebSocket connection."""
        client = TestClient(app)
        
        with client.websocket_connect("/api/scraper/ws/logs/test-task") as websocket:
            data = websocket.receive_json()
            assert "type" in data or "message" in data
    
    def test_progress_websocket_connection(self):
        """Test progress WebSocket connection."""
        client = TestClient(app)
        
        with client.websocket_connect("/api/scraper/ws/progress/test-task") as websocket:
            data = websocket.receive_json()
            assert "type" in data
    
    def test_results_websocket_connection(self):
        """Test results WebSocket connection."""
        client = TestClient(app)
        
        with client.websocket_connect("/api/scraper/ws/results/test-task") as websocket:
            data = websocket.receive_json()
            assert "type" in data


if __name__ == "__main__":
    pytest.main([__file__])

