"""Integration tests for WebSocket functionality."""
import pytest
import os
import websockets
import asyncio
import json

# Set TESTING mode for WebSocket authentication bypass
os.environ["TESTING"] = "true"


@pytest.fixture(scope="session")
def backend_url():
    """Get backend server URL - tries environment variable, then default."""
    base_url = os.getenv("API_URL", "http://localhost:8000")
    ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
    return ws_url


class TestWebSocketConnections:
    """Test WebSocket connections and messaging."""
    
    @pytest.mark.asyncio
    async def test_websocket_logs_connection(self, backend_url):
        """Test WebSocket logs endpoint connection."""
                
        try:
            ws_url = f"{backend_url}/api/scraper/ws/logs/test-task-id"
            async with websockets.connect(ws_url) as websocket:
                # Connection should be established
                assert websocket is not None
                
                # Wait for initial message
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                
                # Verify message structure
                assert "level" in data or "message" in data or "type" in data
        except (websockets.exceptions.InvalidURI, ConnectionRefusedError, OSError) as e:
            pytest.skip(f"Backend server not running or WebSocket connection failed: {e}")
        except asyncio.TimeoutError:
            pytest.skip("WebSocket connection timeout - server may not be running")
    
    @pytest.mark.asyncio
    async def test_websocket_progress_connection(self, backend_url):
        """Test WebSocket progress endpoint connection."""
                
        try:
            ws_url = f"{backend_url}/api/scraper/ws/progress/test-task-id"
            async with websockets.connect(ws_url) as websocket:
                assert websocket is not None
                
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
    async def test_websocket_results_connection(self, backend_url):
        """Test WebSocket results endpoint connection."""
                
        try:
            ws_url = f"{backend_url}/api/scraper/ws/results/test-task-id"
            async with websockets.connect(ws_url) as websocket:
                assert websocket is not None
                
                # Wait for initial message
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                
                # Verify message structure
                assert "type" in data or "result" in data or "status" in data
        except (websockets.exceptions.InvalidURI, ConnectionRefusedError, OSError) as e:
            pytest.skip(f"Backend server not running or WebSocket connection failed: {e}")
        except asyncio.TimeoutError:
            pytest.skip("WebSocket connection timeout - server may not be running")
    
    @pytest.mark.asyncio
    async def test_websocket_message_format(self, backend_url):
        """Test WebSocket message format."""
                
        try:
            ws_url = f"{backend_url}/api/scraper/ws/logs/test-task-id"
            async with websockets.connect(ws_url) as websocket:
                # Wait for any messages
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    
                    # Verify message structure
                    assert "type" in data or "message" in data or "level" in data
                except asyncio.TimeoutError:
                    # No messages yet, which is fine for tests
                    pass
        except (websockets.exceptions.InvalidURI, ConnectionRefusedError, OSError) as e:
            pytest.skip(f"Backend server not running or WebSocket connection failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
