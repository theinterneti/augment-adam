"""
Resource management for parallel processing.

This module provides resource management for parallel processing, including
monitoring and throttling of system resources.
"""

import time
import threading
import psutil
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar, Generic, Tuple

from augment_adam.utils.tagging import tag, TagCategory


@tag("parallel.utils")
class ResourceMonitor:
    """
    Monitor system resources.
    
    This class monitors system resources, including CPU, memory, and disk usage.
    
    Attributes:
        interval: The interval between resource checks, in seconds.
        history_size: The number of resource checks to keep in history.
        history: Dictionary of resource history.
        running: Whether the monitor is running.
        thread: The monitoring thread.
    
    TODO(Issue #10): Add support for GPU monitoring
    TODO(Issue #10): Implement resource analytics
    """
    
    def __init__(self, interval: float = 1.0, history_size: int = 60) -> None:
        """
        Initialize the resource monitor.
        
        Args:
            interval: The interval between resource checks, in seconds.
            history_size: The number of resource checks to keep in history.
        """
        self.interval = interval
        self.history_size = history_size
        self.history: Dict[str, List[Tuple[float, float]]] = {
            "cpu": [],
            "memory": [],
            "disk": [],
        }
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.RLock()
    
    def start(self) -> None:
        """Start the resource monitor."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self) -> None:
        """Stop the resource monitor."""
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=self.interval * 2)
            self.thread = None
    
    def get_current_usage(self) -> Dict[str, float]:
        """
        Get the current resource usage.
        
        Returns:
            Dictionary of resource usage, with keys "cpu", "memory", and "disk".
        """
        return {
            "cpu": psutil.cpu_percent() / 100.0,
            "memory": psutil.virtual_memory().percent / 100.0,
            "disk": psutil.disk_usage("/").percent / 100.0,
        }
    
    def get_average_usage(self, resource: str, window: int = 5) -> float:
        """
        Get the average usage of a resource over a window.
        
        Args:
            resource: The resource to get the average usage of.
            window: The number of resource checks to average over.
            
        Returns:
            The average usage of the resource.
        """
        with self.lock:
            history = self.history.get(resource, [])
            if not history:
                return 0.0
            
            # Get the most recent window entries
            recent = history[-window:]
            if not recent:
                return 0.0
            
            # Compute average
            return sum(usage for _, usage in recent) / len(recent)
    
    def _monitor_loop(self) -> None:
        """Monitor loop for checking resource usage."""
        while self.running:
            try:
                # Get current resource usage
                usage = self.get_current_usage()
                timestamp = time.time()
                
                # Update history
                with self.lock:
                    for resource, value in usage.items():
                        if resource not in self.history:
                            self.history[resource] = []
                        
                        self.history[resource].append((timestamp, value))
                        
                        # Trim history
                        if len(self.history[resource]) > self.history_size:
                            self.history[resource] = self.history[resource][-self.history_size:]
                
                # Sleep until next check
                time.sleep(self.interval)
            except Exception as e:
                print(f"Error in resource monitor: {e}")
                time.sleep(self.interval)


@tag("parallel.utils")
class ResourceThrottler:
    """
    Throttle resource usage.
    
    This class throttles resource usage by limiting the number of concurrent tasks
    based on system resource usage.
    
    Attributes:
        monitor: The resource monitor to use.
        cpu_threshold: The CPU usage threshold, above which to throttle.
        memory_threshold: The memory usage threshold, above which to throttle.
        disk_threshold: The disk usage threshold, above which to throttle.
        min_concurrency: The minimum number of concurrent tasks.
        max_concurrency: The maximum number of concurrent tasks.
        current_concurrency: The current number of concurrent tasks.
    
    TODO(Issue #10): Add support for GPU throttling
    TODO(Issue #10): Implement adaptive throttling
    """
    
    def __init__(
        self,
        monitor: Optional[ResourceMonitor] = None,
        cpu_threshold: float = 0.8,
        memory_threshold: float = 0.8,
        disk_threshold: float = 0.8,
        min_concurrency: int = 1,
        max_concurrency: int = 100
    ) -> None:
        """
        Initialize the resource throttler.
        
        Args:
            monitor: The resource monitor to use. If None, create a new one.
            cpu_threshold: The CPU usage threshold, above which to throttle.
            memory_threshold: The memory usage threshold, above which to throttle.
            disk_threshold: The disk usage threshold, above which to throttle.
            min_concurrency: The minimum number of concurrent tasks.
            max_concurrency: The maximum number of concurrent tasks.
        """
        self.monitor = monitor or ResourceMonitor()
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        self.min_concurrency = min_concurrency
        self.max_concurrency = max_concurrency
        self.current_concurrency = max_concurrency
        self.lock = threading.RLock()
    
    def start(self) -> None:
        """Start the resource throttler."""
        self.monitor.start()
    
    def stop(self) -> None:
        """Stop the resource throttler."""
        self.monitor.stop()
    
    def get_concurrency(self) -> int:
        """
        Get the current concurrency limit.
        
        Returns:
            The current concurrency limit.
        """
        with self.lock:
            return self.current_concurrency
    
    def update_concurrency(self) -> int:
        """
        Update the concurrency limit based on resource usage.
        
        Returns:
            The updated concurrency limit.
        """
        # Get current resource usage
        cpu_usage = self.monitor.get_average_usage("cpu")
        memory_usage = self.monitor.get_average_usage("memory")
        disk_usage = self.monitor.get_average_usage("disk")
        
        # Compute throttling factor
        cpu_factor = max(0.0, 1.0 - (cpu_usage - self.cpu_threshold) / (1.0 - self.cpu_threshold)) if cpu_usage > self.cpu_threshold else 1.0
        memory_factor = max(0.0, 1.0 - (memory_usage - self.memory_threshold) / (1.0 - self.memory_threshold)) if memory_usage > self.memory_threshold else 1.0
        disk_factor = max(0.0, 1.0 - (disk_usage - self.disk_threshold) / (1.0 - self.disk_threshold)) if disk_usage > self.disk_threshold else 1.0
        
        # Compute overall throttling factor
        factor = min(cpu_factor, memory_factor, disk_factor)
        
        # Compute new concurrency
        new_concurrency = int(self.max_concurrency * factor)
        new_concurrency = max(self.min_concurrency, new_concurrency)
        
        # Update concurrency
        with self.lock:
            self.current_concurrency = new_concurrency
        
        return new_concurrency
    
    def wait_for_resources(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for resources to be available.
        
        Args:
            timeout: The maximum time to wait, in seconds. If None, wait indefinitely.
            
        Returns:
            True if resources are available, False if the timeout expired.
        """
        # Calculate deadline
        deadline = None if timeout is None else time.time() + timeout
        
        while True:
            # Update concurrency
            concurrency = self.update_concurrency()
            
            # If concurrency is above minimum, resources are available
            if concurrency > self.min_concurrency:
                return True
            
            # Check if deadline has passed
            if deadline is not None and time.time() >= deadline:
                return False
            
            # Wait a bit before checking again
            time.sleep(1.0)
