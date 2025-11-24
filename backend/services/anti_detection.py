"""Anti-detection service for browser fingerprinting evasion."""
import random
import secrets
from typing import Dict, List, Optional
from selenium.webdriver.chrome.options import Options
import logging


class AntiDetectionService:
    """Service for evading browser fingerprinting and detection."""
    
    # User agent pool
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    ]
    
    # Viewport sizes (common resolutions)
    VIEWPORT_SIZES = [
        (1920, 1080),
        (1366, 768),
        (1536, 864),
        (1440, 900),
        (1280, 720),
        (1600, 900),
    ]
    
    def __init__(self, enable_stealth: bool = True):
        """
        Initialize anti-detection service.
        
        Args:
            enable_stealth: Enable stealth mode features
        """
        self.enable_stealth = enable_stealth
        self.proxy_pool: List[str] = []
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent."""
        return random.choice(self.USER_AGENTS)
    
    def get_random_viewport(self) -> tuple[int, int]:
        """Get a random viewport size."""
        return random.choice(self.VIEWPORT_SIZES)
    
    def enhance_chrome_options(self, options: Options) -> Options:
        """
        Enhance Chrome options with anti-detection features.
        
        Args:
            options: Chrome options object
            
        Returns:
            Enhanced options
        """
        # Random user agent
        options.add_argument(f"user-agent={self.get_random_user_agent()}")
        
        # Anti-detection arguments
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Random viewport
        width, height = self.get_random_viewport()
        options.add_argument(f"--window-size={width},{height}")
        
        # Additional stealth options
        if self.enable_stealth:
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins-discovery")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=IsolateOrigins,site-per-process")
            
            # Language and locale randomization
            languages = ["en-US", "en-GB", "en-CA", "en-AU"]
            options.add_argument(f"--lang={random.choice(languages)}")
        
        # Prefs to evade detection
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.images": 2,
        }
        options.add_experimental_option("prefs", prefs)
        
        return options
    
    def get_stealth_script(self) -> str:
        """
        Get JavaScript to inject for stealth mode.
        
        Returns:
            JavaScript code string
        """
        return """
        // Override webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false
        });
        
        // Override plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Override languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Randomize canvas fingerprint
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function() {
            const context = this.getContext('2d');
            const imageData = context.getImageData(0, 0, this.width, this.height);
            for (let i = 0; i < imageData.data.length; i += 4) {
                imageData.data[i] += Math.floor(Math.random() * 10) - 5;
            }
            context.putImageData(imageData, 0, 0);
            return originalToDataURL.apply(this, arguments);
        };
        
        // Randomize WebGL fingerprint
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return 'Intel Inc.';
            }
            if (parameter === 37446) {
                return 'Intel Iris OpenGL Engine';
            }
            return getParameter.apply(this, arguments);
        };
        
        // Override chrome property
        window.chrome = {
            runtime: {}
        };
        """
    
    def randomize_fingerprint(self, driver) -> None:
        """
        Randomize browser fingerprint using JavaScript injection.
        
        Args:
            driver: Selenium WebDriver instance
        """
        try:
            stealth_script = self.get_stealth_script()
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": stealth_script
            })
        except Exception as e:
            logging.info(f"[ANTI-DETECTION] Error injecting stealth script: {e}")
    
    def add_proxy(self, proxy_url: str) -> None:
        """
        Add proxy to proxy pool.
        
        Args:
            proxy_url: Proxy URL (format: http://user:pass@host:port)
        """
        if proxy_url not in self.proxy_pool:
            self.proxy_pool.append(proxy_url)
    
    def get_random_proxy(self) -> Optional[str]:
        """Get a random proxy from the pool."""
        if not self.proxy_pool:
            return None
        return random.choice(self.proxy_pool)
    
    def apply_proxy(self, options: Options, proxy_url: Optional[str] = None) -> Options:
        """
        Apply proxy to Chrome options.
        
        Args:
            options: Chrome options
            proxy_url: Proxy URL (or random if None)
            
        Returns:
            Enhanced options
        """
        if proxy_url is None:
            proxy_url = self.get_random_proxy()
        
        if proxy_url:
            options.add_argument(f"--proxy-server={proxy_url}")
        
        return options


# Global instance
_anti_detection_service: Optional[AntiDetectionService] = None


def get_anti_detection_service() -> AntiDetectionService:
    """Get or create global anti-detection service instance."""
    global _anti_detection_service
    if _anti_detection_service is None:
        _anti_detection_service = AntiDetectionService(enable_stealth=True)
    return _anti_detection_service

