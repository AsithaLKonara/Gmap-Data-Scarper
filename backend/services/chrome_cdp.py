"""Chrome DevTools Protocol service for element coordinate extraction."""
import json
import requests
from typing import Optional, Dict, List, Tuple
from selenium.webdriver.remote.webdriver import WebDriver


class ChromeCDPService:
    """Service for interacting with Chrome DevTools Protocol."""
    
    def __init__(self, driver: WebDriver, debug_port: int):
        """
        Initialize CDP service.
        
        Args:
            driver: Selenium WebDriver instance
            debug_port: Chrome remote debugging port
        """
        self.driver = driver
        self.debug_port = debug_port
        self.cdp_url = f"http://localhost:{debug_port}"
        self.session_id = None
        self._init_cdp_session()
    
    def _init_cdp_session(self):
        """Initialize CDP session."""
        try:
            # Get list of targets
            response = requests.get(f"{self.cdp_url}/json")
            targets = response.json()
            
            # Find the page target
            page_target = None
            for target in targets:
                if target.get("type") == "page":
                    page_target = target
                    break
            
            if not page_target:
                raise Exception("No page target found")
            
            # Create CDP session
            ws_url = page_target.get("webSocketDebuggerUrl")
            if not ws_url:
                # Fallback: use target ID to create session
                target_id = page_target.get("id")
                response = requests.post(
                    f"{self.cdp_url}/json/new",
                    json={"targetId": target_id}
                )
                session = response.json()
                self.session_id = session.get("id")
            else:
                # Extract session ID from WebSocket URL
                # Format: ws://localhost:9222/devtools/page/{session_id}
                parts = ws_url.split("/")
                self.session_id = parts[-1] if parts else None
        except Exception as e:
            # Fallback: try to get session from driver capabilities
            try:
                caps = self.driver.capabilities
                if "goog:chromeOptions" in caps:
                    debugger_address = caps.get("goog:chromeOptions", {}).get("debuggerAddress", "")
                    if debugger_address:
                        # Extract port from debugger address
                        pass
            except:
                pass
    
    def get_element_bounding_box(self, selector: str) -> Optional[Dict[str, float]]:
        """
        Get element bounding box using CSS selector.
        
        Args:
            selector: CSS selector for the element
            
        Returns:
            Dict with x, y, width, height, or None if not found
        """
        try:
            # Use Selenium to find element first
            element = self.driver.find_element("css selector", selector)
            
            # Get element location and size
            location = element.location
            size = element.size
            
            # Get viewport dimensions
            viewport_size = self.driver.get_window_size()
            
            # Get scroll position
            scroll_x = self.driver.execute_script("return window.pageXOffset;")
            scroll_y = self.driver.execute_script("return window.pageYOffset;")
            
            # Calculate relative to viewport
            x = location["x"] - scroll_x
            y = location["y"] - scroll_y
            width = size["width"]
            height = size["height"]
            
            # Normalize coordinates (0-1 range)
            viewport_width = viewport_size["width"]
            viewport_height = viewport_size["height"]
            
            normalized = {
                "x": x / viewport_width if viewport_width > 0 else 0,
                "y": y / viewport_height if viewport_height > 0 else 0,
                "width": width / viewport_width if viewport_width > 0 else 0,
                "height": height / viewport_height if viewport_height > 0 else 0,
                "absolute_x": location["x"],
                "absolute_y": location["y"],
                "viewport_width": viewport_width,
                "viewport_height": viewport_height,
                "scroll_x": scroll_x,
                "scroll_y": scroll_y
            }
            
            return normalized
        except Exception as e:
            return None
    
    def get_element_coordinates(self, selector: str) -> Optional[Tuple[float, float, float, float]]:
        """
        Get element coordinates (x, y, width, height) relative to viewport.
        
        Args:
            selector: CSS selector for the element
            
        Returns:
            Tuple of (x, y, width, height) normalized to 0-1 range, or None
        """
        bbox = self.get_element_bounding_box(selector)
        if bbox:
            return (
                bbox["x"],
                bbox["y"],
                bbox["width"],
                bbox["height"]
            )
        return None
    
    def highlight_element(self, selector: str, color: str = "yellow", duration: float = 2.0):
        """
        Highlight an element in the browser.
        
        Args:
            selector: CSS selector for the element
            color: Highlight color (CSS color)
            duration: Duration in seconds
        """
        try:
            script = f"""
            (function() {{
                var element = document.querySelector('{selector}');
                if (element) {{
                    var originalStyle = {{
                        outline: element.style.outline,
                        outlineOffset: element.style.outlineOffset,
                        backgroundColor: element.style.backgroundColor
                    }};
                    element.style.outline = '3px solid {color}';
                    element.style.outlineOffset = '2px';
                    element.style.backgroundColor = '{color}33';
                    setTimeout(function() {{
                        element.style.outline = originalStyle.outline;
                        element.style.outlineOffset = originalStyle.outlineOffset;
                        element.style.backgroundColor = originalStyle.backgroundColor;
                    }}, {duration * 1000});
                }}
            }})();
            """
            self.driver.execute_script(script)
        except Exception:
            pass
    
    def scroll_to_element(self, selector: str):
        """
        Scroll to element in viewport.
        
        Args:
            selector: CSS selector for the element
        """
        try:
            element = self.driver.find_element("css selector", selector)
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        except Exception:
            pass
    
    def get_viewport_info(self) -> Dict[str, int]:
        """Get current viewport information."""
        try:
            viewport_size = self.driver.get_window_size()
            scroll_x = self.driver.execute_script("return window.pageXOffset;")
            scroll_y = self.driver.execute_script("return window.pageYOffset;")
            
            return {
                "width": viewport_size["width"],
                "height": viewport_size["height"],
                "scroll_x": int(scroll_x),
                "scroll_y": int(scroll_y)
            }
        except Exception:
            return {"width": 0, "height": 0, "scroll_x": 0, "scroll_y": 0}

