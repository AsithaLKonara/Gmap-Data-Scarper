"""Chrome instance pool for efficient resource management."""
import threading
import time
from typing import Optional, Dict, Set
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from backend.services.port_manager import port_pool
from backend.services.anti_detection import get_anti_detection_service
from webdriver_manager.chrome import ChromeDriverManager


class ChromePool:
    """Manages a pool of Chrome instances with tab isolation."""
    
    def __init__(
        self,
        pool_size: int = 10,
        headless: bool = True,
        idle_timeout: int = 300  # 5 minutes
    ):
        """
        Initialize Chrome pool.
        
        Args:
            pool_size: Maximum number of Chrome instances
            headless: Run Chrome in headless mode
            idle_timeout: Seconds before idle instance is closed
        """
        self.pool_size = pool_size
        self.headless = headless
        self.idle_timeout = idle_timeout
        
        self.instances: Dict[str, Dict] = {}  # instance_id -> {driver, tabs, last_used, lock}
        self.available_instances: Set[str] = set()
        self.lock = threading.Lock()
        self.cleanup_thread: Optional[threading.Thread] = None
        self._running = True
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start background thread to clean up idle instances."""
        def cleanup_loop():
            while self._running:
                try:
                    time.sleep(60)  # Check every minute
                    self._cleanup_idle_instances()
                except Exception as e:
                    import logging
                    logging.warning(f"Error in Chrome pool cleanup loop: {e}")
        
        self.cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def acquire(self, task_id: str) -> Optional[webdriver.Chrome]:
        """
        Acquire a Chrome instance (or create new tab in existing instance).
        
        Args:
            task_id: Task identifier for tab isolation
        
        Returns:
            Chrome WebDriver instance or None if pool exhausted
        """
        with self.lock:
            # Try to find available instance
            for instance_id in self.available_instances:
                instance = self.instances[instance_id]
                if len(instance["tabs"]) < 10:  # Max 10 tabs per instance
                    # Create new tab
                    try:
                        driver = instance["driver"]
                        # Switch to new tab
                        driver.execute_script("window.open('about:blank', '_blank');")
                        driver.switch_to.window(driver.window_handles[-1])
                        
                        instance["tabs"].add(task_id)
                        instance["last_used"] = time.time()
                        return driver
                    except Exception:
                        continue
            
            # Create new instance if pool not full
            if len(self.instances) < self.pool_size:
                try:
                    driver = self._create_instance()
                    if driver:
                        instance_id = f"chrome_{int(time.time())}_{len(self.instances)}"
                        port = port_pool.allocate_port()
                        
                        self.instances[instance_id] = {
                            "driver": driver,
                            "tabs": {task_id},
                            "last_used": time.time(),
                            "port": port,
                            "lock": threading.Lock()
                        }
                        self.available_instances.add(instance_id)
                        return driver
                except Exception as e:
                    import logging
                    logging.warning(f"Failed to create new Chrome instance: {e}")
        
        return None
    
    def release(self, task_id: str, driver: webdriver.Chrome):
        """
        Release a Chrome tab (close tab, keep instance if other tabs exist).
        
        Args:
            task_id: Task identifier
            driver: Chrome WebDriver instance
        """
        with self.lock:
            for instance_id, instance in self.instances.items():
                if instance["driver"] == driver:
                    if task_id in instance["tabs"]:
                        instance["tabs"].remove(task_id)
                        instance["last_used"] = time.time()
                        
                        # Close tab if not the last one
                        if len(instance["tabs"]) == 0:
                            # No more tabs, close instance
                            self._close_instance(instance_id)
                        else:
                            # Switch to another tab
                            try:
                                handles = driver.window_handles
                                if handles:
                                    driver.switch_to.window(handles[0])
                            except Exception:
                                pass
                    break
    
    def _create_instance(self) -> Optional[webdriver.Chrome]:
        """Create a new Chrome instance with anti-detection."""
        try:
            options = Options()
            if self.headless:
                options.add_argument("--headless=new")
            
            # Apply anti-detection enhancements
            try:
                anti_detection = get_anti_detection_service()
                options = anti_detection.enhance_chrome_options(options)
            except Exception:
                # Fallback to basic options
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
            
            options.add_argument("--window-size=1920,1080")
            
            # Allocate port for remote debugging
            port = port_pool.allocate_port()
            if not port:
                return None
            
            options.add_argument(f"--remote-debugging-port={port}")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Apply fingerprint randomization
            try:
                anti_detection = get_anti_detection_service()
                anti_detection.randomize_fingerprint(driver)
            except Exception:
                pass
            
            return driver
        except Exception:
            return None
    
    def _close_instance(self, instance_id: str):
        """Close a Chrome instance and release resources."""
        if instance_id not in self.instances:
            return
        
        instance = self.instances[instance_id]
        try:
            driver = instance["driver"]
            driver.quit()
        except Exception:
            pass
        
        # Release port
        port = instance.get("port")
        if port:
            port_pool.release_port(port)
        
        # Remove from pool
        self.instances.pop(instance_id, None)
        self.available_instances.discard(instance_id)
    
    def _cleanup_idle_instances(self):
        """Clean up instances that have been idle too long."""
        current_time = time.time()
        to_remove = []
        
        with self.lock:
            for instance_id, instance in self.instances.items():
                idle_time = current_time - instance["last_used"]
                if idle_time > self.idle_timeout and len(instance["tabs"]) == 0:
                    to_remove.append(instance_id)
            
            for instance_id in to_remove:
                self._close_instance(instance_id)
    
    def shutdown(self):
        """Shutdown the pool and close all instances."""
        self._running = False
        
        with self.lock:
            for instance_id in list(self.instances.keys()):
                self._close_instance(instance_id)
            
            self.instances.clear()
            self.available_instances.clear()


# Global pool instance
_chrome_pool: Optional[ChromePool] = None

def get_chrome_pool() -> ChromePool:
    """Get or create global Chrome pool instance."""
    global _chrome_pool
    if _chrome_pool is None:
        _chrome_pool = ChromePool()
    return _chrome_pool

