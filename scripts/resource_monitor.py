#!/usr/bin/env python3
"""
Resource Monitor.

This module provides a resource monitor that monitors system resources
and throttles test execution when resources are constrained.
"""

import logging
import os
import psutil
import threading
import time
from typing import Dict, Optional, Tuple

logger = logging.getLogger("resource_monitor")


class ResourceMonitor:
    """Resource monitor that monitors system resources."""

    def __init__(
        self,
        threshold: float = 0.8,
        check_interval: float = 5.0,
        memory_weight: float = 0.5,
        cpu_weight: float = 0.3,
        disk_weight: float = 0.2,
    ):
        """Initialize the resource monitor.

        Args:
            threshold: Resource threshold (0.0-1.0) to throttle testing
            check_interval: Interval in seconds to check resource usage
            memory_weight: Weight for memory usage in the resource score
            cpu_weight: Weight for CPU usage in the resource score
            disk_weight: Weight for disk usage in the resource score
        """
        self.threshold = threshold
        self.check_interval = check_interval
        self.memory_weight = memory_weight
        self.cpu_weight = cpu_weight
        self.disk_weight = disk_weight
        self.resource_usage: Dict[str, float] = {
            "memory": 0.0,
            "cpu": 0.0,
            "disk": 0.0,
            "score": 0.0,
        }
        self.lock = threading.Lock()
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def start(self):
        """Start the resource monitor."""
        if self.running:
            return

        logger.info("Starting resource monitor")
        self.running = True
        self.thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the resource monitor."""
        if not self.running:
            return

        logger.info("Stopping resource monitor")
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
            self.thread = None

    def should_throttle(self) -> bool:
        """Check if test execution should be throttled.

        Returns:
            Whether test execution should be throttled
        """
        with self.lock:
            return self.resource_usage["score"] > self.threshold

    def get_resource_usage(self) -> Dict[str, float]:
        """Get the current resource usage.

        Returns:
            Dictionary with resource usage information
        """
        with self.lock:
            return self.resource_usage.copy()

    def _monitor_resources(self):
        """Monitor system resources."""
        while self.running:
            try:
                # Get resource usage
                memory_usage = psutil.virtual_memory().percent / 100.0
                cpu_usage = psutil.cpu_percent() / 100.0
                disk_usage = psutil.disk_usage("/").percent / 100.0

                # Calculate the resource score
                score = (
                    memory_usage * self.memory_weight
                    + cpu_usage * self.cpu_weight
                    + disk_usage * self.disk_weight
                )

                # Update the resource usage
                with self.lock:
                    self.resource_usage = {
                        "memory": memory_usage,
                        "cpu": cpu_usage,
                        "disk": disk_usage,
                        "score": score,
                    }

                # Log the resource usage
                logger.debug(
                    f"Resource usage: memory={memory_usage:.2f}, "
                    f"cpu={cpu_usage:.2f}, disk={disk_usage:.2f}, "
                    f"score={score:.2f}"
                )

                # Sleep for the check interval
                time.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Error monitoring resources: {e}", exc_info=True)
                time.sleep(10.0)  # Wait longer on error


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    monitor = ResourceMonitor()
    monitor.start()
    try:
        while True:
            usage = monitor.get_resource_usage()
            print(
                f"Resource usage: memory={usage['memory']:.2f}, "
                f"cpu={usage['cpu']:.2f}, disk={usage['disk']:.2f}, "
                f"score={usage['score']:.2f}"
            )
            print(f"Should throttle: {monitor.should_throttle()}")
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
