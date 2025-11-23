"""Port pool manager for Chrome debug ports."""
import socket
import threading
from typing import Set, Optional


class PortPool:
    """Manages a pool of available Chrome debug ports."""
    
    def __init__(self, start_port: int = 9222, max_ports: int = 100):
        """
        Initialize port pool.
        
        Args:
            start_port: Starting port number
            max_ports: Maximum number of ports in pool
        """
        self.start_port = start_port
        self.max_ports = max_ports
        self.allocated_ports: Set[int] = set()
        self.lock = threading.Lock()
    
    def allocate_port(self) -> Optional[int]:
        """
        Allocate an available port.
        
        Returns:
            Port number if available, None if all ports are in use
        """
        with self.lock:
            for port in range(self.start_port, self.start_port + self.max_ports):
                if port not in self.allocated_ports and self._is_port_available(port):
                    self.allocated_ports.add(port)
                    return port
            return None
    
    def release_port(self, port: int):
        """Release a port back to the pool."""
        with self.lock:
            self.allocated_ports.discard(port)
    
    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available (not in use)."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                # If connection succeeds, port is in use
                return result != 0
        except Exception:
            return False
    
    def get_allocated_count(self) -> int:
        """Get number of currently allocated ports."""
        with self.lock:
            return len(self.allocated_ports)
    
    def get_available_count(self) -> int:
        """Get number of available ports."""
        return self.max_ports - self.get_allocated_count()


# Global port pool instance
port_pool = PortPool(start_port=9222, max_ports=100)

