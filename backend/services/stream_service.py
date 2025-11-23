"""Chrome live feed streaming service."""
import os
import time
import threading
import psutil
from typing import Optional, Dict
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from backend.config import STREAM_FPS, SCREENSHOT_DIR, TASK_TIMEOUT_SECONDS
from backend.services.port_manager import port_pool
from backend.services.anti_detection import get_anti_detection_service


class ChromeStreamService:
    """Manages Chrome browser instances and provides screenshot streaming."""
    
    def __init__(self):
        self.drivers: Dict[str, webdriver.Chrome] = {}
        self.screenshots: Dict[str, str] = {}  # task_id -> latest screenshot path
        self.running: Dict[str, bool] = {}
        self.ports: Dict[str, int] = {}  # task_id -> allocated port
        self.start_times: Dict[str, float] = {}  # task_id -> start timestamp
        self.lock = threading.Lock()
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        
        # Start cleanup thread
        cleanup_thread = threading.Thread(target=self._cleanup_orphaned_processes, daemon=True)
        cleanup_thread.start()
    
    def start_stream(self, task_id: str, headless: bool = False) -> bool:
        """Start Chrome browser with remote debugging for a task."""
        with self.lock:
            # Check if task already has a driver
            if task_id in self.drivers:
                return True
            
            # Allocate a port
            port = port_pool.allocate_port()
            if port is None:
                return False
            
            try:
                chrome_options = Options()
                
                # Enable remote debugging on allocated port
                chrome_options.add_argument(f"--remote-debugging-port={port}")
                
                # Apply anti-detection enhancements
                anti_detection = get_anti_detection_service()
                chrome_options = anti_detection.enhance_chrome_options(chrome_options)
                
                # Disable headless if streaming (need visible browser)
                if headless:
                    chrome_options.add_argument("--headless")
                
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # Apply fingerprint randomization
                anti_detection.randomize_fingerprint(driver)
                
                self.drivers[task_id] = driver
                self.running[task_id] = True
                self.ports[task_id] = port
                self.start_times[task_id] = time.time()
                
                # Start screenshot capture thread
                thread = threading.Thread(
                    target=self._capture_screenshots,
                    args=(task_id,),
                    daemon=True
                )
                thread.start()
                
                # Start timeout monitoring thread
                timeout_thread = threading.Thread(
                    target=self._monitor_timeout,
                    args=(task_id,),
                    daemon=True
                )
                timeout_thread.start()
                
                return True
            except Exception as e:
                # Release port on failure
                port_pool.release_port(port)
                if task_id in self.ports:
                    del self.ports[task_id]
                return False
    
    def get_driver(self, task_id: str) -> Optional[webdriver.Chrome]:
        """Get Chrome driver for a task."""
        return self.drivers.get(task_id)
    
    def stop_stream(self, task_id: str):
        """Stop Chrome browser and cleanup for a task."""
        with self.lock:
            if task_id in self.drivers:
                try:
                    self.running[task_id] = False
                    driver = self.drivers[task_id]
                    driver.quit()
                except Exception as e:
                    import logging
                    logging.warning(f"Error quitting Chrome driver for task {task_id}: {e}")
                finally:
                    # Release port
                    if task_id in self.ports:
                        port = self.ports[task_id]
                        port_pool.release_port(port)
                        del self.ports[task_id]
                    
                    # Clean up driver references
                    if task_id in self.drivers:
                        del self.drivers[task_id]
                    if task_id in self.screenshots:
                        del self.screenshots[task_id]
                    if task_id in self.running:
                        del self.running[task_id]
                    if task_id in self.start_times:
                        del self.start_times[task_id]
                    
                    # Kill orphaned Chrome processes for this task
                    self._kill_chrome_processes(task_id)
    
    def get_latest_screenshot(self, task_id: str) -> Optional[str]:
        """Get path to latest screenshot for a task."""
        return self.screenshots.get(task_id)
    
    def _capture_screenshots(self, task_id: str):
        """Continuously capture screenshots for streaming."""
        interval = 1.0 / STREAM_FPS  # Time between frames
        
        while self.running.get(task_id, False):
            try:
                driver = self.drivers.get(task_id)
                if driver:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    screenshot_path = os.path.join(
                        SCREENSHOT_DIR,
                        f"{task_id}_{timestamp}.png"
                    )
                    
                    driver.save_screenshot(screenshot_path)
                    self.screenshots[task_id] = screenshot_path
                    
                    # Clean up old screenshots (keep only latest)
                    self._cleanup_old_screenshots(task_id)
                
                time.sleep(interval)
            except Exception:
                # Driver closed or error
                break
    
    def _cleanup_old_screenshots(self, task_id: str):
        """Remove old screenshots, keep only the latest."""
        try:
            latest = self.screenshots.get(task_id)
            if latest and os.path.exists(latest):
                # Find all screenshots for this task
                task_files = [
                    f for f in os.listdir(SCREENSHOT_DIR)
                    if f.startswith(f"{task_id}_") and f.endswith(".png")
                ]
                
                # Remove all except latest
                for filename in task_files:
                    filepath = os.path.join(SCREENSHOT_DIR, filename)
                    if filepath != latest and os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                        except Exception as e:
                            import logging
                            logging.debug(f"Failed to remove old screenshot {filepath}: {e}")
        except Exception as e:
            import logging
            logging.debug(f"Error cleaning up old screenshots for task {task_id}: {e}")
    
    def _monitor_timeout(self, task_id: str):
        """Monitor task timeout and kill if exceeded."""
        while self.running.get(task_id, False):
            time.sleep(60)  # Check every minute
            
            if task_id in self.start_times:
                elapsed = time.time() - self.start_times[task_id]
                if elapsed > TASK_TIMEOUT_SECONDS:
                    # Task exceeded timeout, stop it
                    self.stop_stream(task_id)
                    break
    
    def _cleanup_orphaned_processes(self):
        """Periodically cleanup orphaned Chrome processes."""
        while True:
            time.sleep(300)  # Check every 5 minutes
            
            try:
                # Find Chrome processes that might be orphaned
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if 'chrome' in proc.info['name'].lower() or 'chromedriver' in proc.info['name'].lower():
                            # Check if this process is associated with any active task
                            cmdline = proc.info.get('cmdline', [])
                            if cmdline:
                                cmdline_str = ' '.join(cmdline)
                                # Check if this process matches any active task port
                                is_orphaned = True
                                for task_id, port in self.ports.items():
                                    if f"--remote-debugging-port={port}" in cmdline_str:
                                        is_orphaned = False
                                        break
                                
                                # Kill orphaned processes
                                if is_orphaned and '--remote-debugging-port' in cmdline_str:
                                    try:
                                        proc.kill()
                                    except Exception as e:
                                        import logging
                                        logging.debug(f"Failed to kill orphaned Chrome process {proc.info.get('pid')}: {e}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except Exception:
                pass
    
    def _kill_chrome_processes(self, task_id: str):
        """Kill Chrome processes associated with a task."""
        if task_id not in self.ports:
            return
        
        port = self.ports.get(task_id)
        if port is None:
            return
        
        try:
            for proc in psutil.process_iter(['pid', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline:
                        cmdline_str = ' '.join(cmdline)
                        if f"--remote-debugging-port={port}" in cmdline_str:
                            proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass
    
    def get_port(self, task_id: str) -> Optional[int]:
        """Get the allocated port for a task."""
        return self.ports.get(task_id)


# Global stream service instance
stream_service = ChromeStreamService()

