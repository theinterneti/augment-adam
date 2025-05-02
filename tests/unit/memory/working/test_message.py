"""
Unit tests for augment_adam.memory.working.message.

This module contains unit tests for the message module.
"""

import unittest
import pytest
from unittest.mock import patch, MagicMock

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.memory.working.message import Message


class TestMessage(unittest.TestCase):
    """Tests for the Message class."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize objects for testing
        self.message = Message(
            content="Test message content",
            role="user",
            metadata={"timestamp": "2023-01-01T12:00:00Z"}
        )

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test_init(self):
        """Test initialization of Message."""
        # Verify the instance was created correctly
        self.assertEqual(self.message.content, "Test message content")
        self.assertEqual(self.message.role, "user")
        self.assertEqual(self.message.metadata["timestamp"], "2023-01-01T12:00:00Z")
        self.assertIsNotNone(self.message.id)
        self.assertIsNotNone(self.message.created_at)
        self.assertIsNotNone(self.message.updated_at)

    def test_init_with_defaults(self):
        """Test initialization of Message with default values."""
        # Create a message with minimal parameters
        message = Message(content="Minimal message")

        # Verify defaults were applied
        self.assertEqual(message.content, "Minimal message")
        self.assertEqual(message.role, "user")  # Default role
        self.assertEqual(message.metadata, {})  # Default empty metadata
        self.assertIsNotNone(message.id)
        self.assertIsNotNone(message.created_at)
        self.assertIsNotNone(message.updated_at)

    def test_to_dict(self):
        """Test to_dict method."""
        # Get dict representation
        message_dict = self.message.to_dict()

        # Verify dict contains expected keys and values
        self.assertEqual(message_dict["content"], "Test message content")
        self.assertEqual(message_dict["role"], "user")
        self.assertEqual(message_dict["metadata"]["timestamp"], "2023-01-01T12:00:00Z")
        self.assertEqual(message_dict["id"], self.message.id)
        self.assertIn("created_at", message_dict)
        self.assertIn("updated_at", message_dict)

    def test_from_dict(self):
        """Test from_dict method."""
        # Create a dict representation
        data = {
            "id": "msg-123",
            "content": "Dict message content",
            "role": "assistant",
            "metadata": {"source": "test"},
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T01:00:00Z"
        }

        # Create message from dict
        message = Message.from_dict(data)

        # Verify message was created correctly
        self.assertEqual(message.id, "msg-123")
        self.assertEqual(message.content, "Dict message content")
        self.assertEqual(message.role, "assistant")
        self.assertEqual(message.metadata["source"], "test")
        self.assertIsNotNone(message.created_at)
        self.assertIsNotNone(message.updated_at)

    def test_format_for_conversation(self):
        """Test format_for_conversation method."""
        # Format message for conversation
        formatted = self.message.format_for_conversation()

        # Verify formatting
        self.assertEqual(formatted, "user: Test message content")

        # Test with different role
        assistant_message = Message(
            content="I can help with that",
            role="assistant"
        )
        formatted = assistant_message.format_for_conversation()
        self.assertEqual(formatted, "assistant: I can help with that")


if __name__ == '__main__':
    unittest.main()
