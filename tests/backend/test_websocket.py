"""Tests for WebSocket functionality."""
import pytest
import os
import websockets
import asyncio
import json

# Set TESTING mode for WebSocket authentication bypass
os.environ["TESTING"] = "true"


@pytest.fixture(scope="session")
def backend_url():
    """Get backend server URL - tries fixture first, then environment, then default."""
    # Try to get from environment variable (set by test runner)
    base_url = os.getenv("API_URL", "http://localhost:8000")
    # Convert http to ws
    ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
    return ws_url


class TestWebSocket:
    """Test WebSocket endpoints."""
    
    @pytest.mark.asyncio
    async def test_logs_websocket_connection(self, backend_url):
        """Test logs WebSocket connection."""
        
        try:
            # Connect to WebSocket endpoint
            ws_url = f"{backend_url}/api/scraper/ws/logs/test-task"
            async with websockets.connect(ws_url) as websocket:
                # Wait for initial connection message
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                
                # Parse JSON message
                data = json.loads(message)
                
                # Verify message structure
                assert "level" in data or "message" in data or "type" in data
        except (websockets.exceptions.InvalidURI, ConnectionRefusedError, OSError) as e:
            pytest.skip(f"Backend server not running or WebSocket connection failed: {e}")
        except asyncio.TimeoutError:
            pytest.skip("WebSocket connection timeout - server may not be running")
    
    @pytest.mark.asyncio
    async def test_progress_websocket_connection(self, backend_url):
        """Test progress WebSocket connection."""
            
        try:
            ws_url = f"{backend_url}/api/scraper/ws/progress/test-task"
            async with websockets.connect(ws_url) as websocket:
                # Wait for initial message
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                
                data = json.loads(message)
                
                # Verify message structure
                assert "type" in data or "progress" in data or "status" in data
        except (websockets.exceptions.InvalidURI, ConnectionRefusedError, OSError) as e:
            pytest.skip(f"Backend server not running or WebSocket connection failed: {e}")
        except asyncio.TimeoutError:
            pytest.skip("WebSocket connection timeout - server may not be running")
    
    @pytest.mark.asyncio
    async def test_results_websocket_connection(self, backend_url):
        """Test results WebSocket connection."""
            
        try:
            ws_url = f"{backend_url}/api/scraper/ws/results/test-task"
            async with websockets.connect(ws_url) as websocket:
                # Wait for initial message
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                
                data = json.loads(message)
                
                # Verify message structure
                assert "type" in data or "result" in data or "status" in data
        except (websockets.exceptions.InvalidURI, ConnectionRefusedError, OSError) as e:
            pytest.skip(f"Backend server not running or WebSocket connection failed: {e}")
        except asyncio.TimeoutError:
            pytest.skip("WebSocket connection timeout - server may not be running")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
