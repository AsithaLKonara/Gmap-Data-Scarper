"""Chrome remote debugging controller."""
from typing import Optional
import requests
from backend.config import CHROME_DEBUG_PORT


class ChromeController:
    """Controls Chrome via Chrome DevTools Protocol."""
    
    def __init__(self, port: int = CHROME_DEBUG_PORT):
        self.port = port
        self.base_url = f"http://localhost:{port}"
    
    def get_tabs(self) -> list:
        """Get list of open tabs."""
        try:
            response = requests.get(f"{self.base_url}/json")
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []
    
    def take_screenshot(self, tab_id: Optional[str] = None) -> Optional[bytes]:
        """Take screenshot of a tab."""
        try:
            tabs = self.get_tabs()
            if not tabs:
                return None
            
            # Use first tab if no tab_id specified
            if not tab_id:
                tab_id = tabs[0]["id"]
            
            # Use Chrome DevTools Protocol to take screenshot
            # This requires WebSocket connection, simplified here
            # For now, use Selenium screenshot instead
            return None
        except:
            return None

