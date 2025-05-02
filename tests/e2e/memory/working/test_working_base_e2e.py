"""
End-to-end tests for augment_adam.memory.working.base.
"""

import unittest
import pytest
import tempfile
import os
from unittest.mock import MagicMock, patch

from augment_adam.memory.working.base import WorkingMemory, WorkingMemoryItem


@pytest.mark.e2e
class TestWorkingMemoryE2E(unittest.TestCase):
    """End-to-end tests for WorkingMemory."""

    def setUp(self):
        """Set up the test case."""
        self.temp_dir = tempfile.mkdtemp()
        self.working_memory = WorkingMemory(name="test_working_memory")

    def tearDown(self):
        """Tear down the test case."""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_working_memory_basic_operations(self):
        """Test basic operations of WorkingMemory in an end-to-end scenario."""
        # Add items to working memory
        item1 = WorkingMemoryItem(content="Test content 1")
        item2 = WorkingMemoryItem(content="Test content 2")

        self.working_memory.add(item1)
        self.working_memory.add(item2)

        # Verify items were added
        self.assertEqual(len(self.working_memory.items), 2)

        # Retrieve items
        retrieved_item1 = self.working_memory.get(item1.id)
        self.assertEqual(retrieved_item1.content, "Test content 1")

        # Search for items
        search_results = self.working_memory.search("Test content 2")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].content, "Test content 2")

        # Update an item
        self.working_memory.update(item1.id, content="Updated content")
        updated_item = self.working_memory.get(item1.id)
        self.assertEqual(updated_item.content, "Updated content")

        # Delete an item
        self.working_memory.remove(item2.id)
        self.assertEqual(len(self.working_memory.items), 1)


if __name__ == '__main__':
    unittest.main()
