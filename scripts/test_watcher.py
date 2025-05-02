#!/usr/bin/env python3
"""
Test Watcher.

This module provides a file watcher that monitors code changes and
triggers test generation and execution.
"""

import logging
import os
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Set

logger = logging.getLogger("test_watcher")


class TestWatcher:
    """File watcher that monitors code changes."""

    def __init__(self, source_dir: str, watch_interval: float = 2.0):
        """Initialize the test watcher.

        Args:
            source_dir: Directory containing source code to monitor
            watch_interval: Interval in seconds to check for file changes
        """
        self.source_dir = source_dir
        self.watch_interval = watch_interval
        self.file_mtimes: Dict[str, float] = {}
        self.changed_files: List[str] = []
        self.lock = threading.Lock()
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def start(self):
        """Start the file watcher."""
        if self.running:
            return

        logger.info(f"Starting file watcher for {self.source_dir}")
        self.running = True
        self.thread = threading.Thread(target=self._watch_files, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the file watcher."""
        if not self.running:
            return

        logger.info("Stopping file watcher")
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
            self.thread = None

    def get_changed_files(self) -> List[str]:
        """Get the list of changed files and clear the internal list.

        Returns:
            List of changed file paths
        """
        with self.lock:
            changed_files = self.changed_files.copy()
            self.changed_files = []
        return changed_files

    def _watch_files(self):
        """Watch files for changes."""
        # Initial scan to get file mtimes
        self._scan_files()

        # Watch for changes
        while self.running:
            try:
                self._scan_files()
                time.sleep(self.watch_interval)
            except Exception as e:
                logger.error(f"Error watching files: {e}", exc_info=True)
                time.sleep(5.0)  # Wait longer on error

    def _scan_files(self):
        """Scan files for changes."""
        for root, _, files in os.walk(self.source_dir):
            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(file_path)
                    if file_path in self.file_mtimes:
                        if mtime > self.file_mtimes[file_path]:
                            logger.debug(f"File changed: {file_path}")
                            with self.lock:
                                if file_path not in self.changed_files:
                                    self.changed_files.append(file_path)
                    self.file_mtimes[file_path] = mtime
                except Exception as e:
                    logger.error(f"Error checking file {file_path}: {e}")


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.DEBUG)
    watcher = TestWatcher("src")
    watcher.start()
    try:
        while True:
            changed = watcher.get_changed_files()
            if changed:
                print(f"Changed files: {changed}")
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
