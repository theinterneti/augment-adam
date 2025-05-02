"""
Integration tests for augment_adam.memory.working.base.
"""

import unittest
import pytest
import tempfile
import os
from unittest.mock import MagicMock, patch

from augment_adam.memory.core.base import MemoryType
from augment_adam.memory.working.base import WorkingMemory, WorkingMemoryItem
from augment_adam.memory.working.message import Message


@pytest.mark.integration
class TestWorkingMemoryIntegration(unittest.TestCase):
    """Integration tests for WorkingMemory."""

    def setUp(self):
        """Set up the test case."""
        self.temp_dir = tempfile.mkdtemp()
        self.working_memory = WorkingMemory(name="test_working_memory")

    def tearDown(self):
        """Tear down the test case."""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_working_memory_with_messages(self):
        """Test integration of WorkingMemory with Message objects."""
        # Create messages
        message1 = Message(
            content="Hello, how can I help you?",
            role="assistant",
            metadata={"timestamp": "2023-01-01T12:00:00Z"}
        )

        message2 = Message(
            content="I need help with Python.",
            role="user",
            metadata={"timestamp": "2023-01-01T12:01:00Z"}
        )

        # Create WorkingMemoryItems from messages
        item1 = WorkingMemoryItem(
            content=message1.content,
            metadata={
                "role": message1.role,
                "timestamp": message1.metadata["timestamp"],
                "message_type": "message"
            }
        )

        item2 = WorkingMemoryItem(
            content=message2.content,
            metadata={
                "role": message2.role,
                "timestamp": message2.metadata["timestamp"],
                "message_type": "message"
            }
        )

        # Add items to working memory
        self.working_memory.add(item1)
        self.working_memory.add(item2)

        # Verify items were added
        items = self.working_memory.get_all()
        self.assertEqual(len(items), 2)

        # Verify message content
        message_contents = [item.content for item in items]
        self.assertIn("Hello, how can I help you?", message_contents)
        self.assertIn("I need help with Python.", message_contents)

        # Test conversation formatting
        conversation = "\n".join([
            f"{item.metadata['role']}: {item.content}"
            for item in items
            if item.metadata.get("message_type") == "message"
        ])
        self.assertIn("assistant: Hello, how can I help you?", conversation)
        self.assertIn("user: I need help with Python.", conversation)

    def test_working_memory_persistence(self):
        """Test persistence of WorkingMemory."""
        # Add items to working memory
        item1 = WorkingMemoryItem(content="Test content 1")
        item2 = WorkingMemoryItem(content="Test content 2")

        self.working_memory.add(item1)
        self.working_memory.add(item2)

        # Save working memory to dict
        memory_dict = self.working_memory.to_dict()

        # Create new working memory from dict
        new_memory = WorkingMemory.from_dict(memory_dict)

        # Verify items were restored
        self.assertEqual(len(new_memory.items), 2)
        self.assertIn(item1.id, new_memory.items)
        self.assertIn(item2.id, new_memory.items)
        self.assertEqual(new_memory.items[item1.id].content, "Test content 1")
        self.assertEqual(new_memory.items[item2.id].content, "Test content 2")


if __name__ == '__main__':
    unittest.main()
