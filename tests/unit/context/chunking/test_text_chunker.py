"""
Unit tests for the TextChunker class.

This module contains unit tests for the TextChunker class.
"""

import unittest
import pytest
from unittest.mock import patch, MagicMock

from augment_adam.context.chunking.base import Chunker
from augment_adam.context.chunking.text_chunker import TextChunker

class TestTextChunker(unittest.TestCase):
    """Tests for the TextChunker class."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize objects for testing
        self.instance = TextChunker(chunk_size=1000, overlap=200)
        self.chunker = TextChunker(chunk_size=100, overlap=20)

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test_instantiation(self):
        """Test that the class can be instantiated."""
        self.assertIsInstance(self.instance, TextChunker)

    def test_custom_method(self):
        """Test a custom method that should be preserved during merging."""
        # This is a custom test method that should be preserved
        self.assertEqual(self.chunker.chunk_size, 100)
        self.assertEqual(self.chunker.overlap, 20)

    def test___init___basic(self):
        """Test basic functionality of __init__."""
        # Arrange

        # Act
        instance = TextChunker(chunk_size=1000, overlap=200)

        # Assert
        self.assertIsInstance(instance, TextChunker)

    def test_chunk_basic(self):
        """Test basic functionality of chunk."""
        # Arrange
        text = "This is a test text that should be chunked into smaller pieces."
        expected_result = []  # Adjust based on expected behavior

        # Act
        result = self.instance.chunk(text)

        # Assert
        self.assertIsInstance(result, list)

    @patch("augment_adam.context.chunking.text_chunker.dependency")
    def test_chunk_with_mocks(self, mock_dependency):
        """Test chunk with mocked dependencies."""
        # Arrange
        mock_dependency.return_value = MagicMock()
        text = "This is a test text."
        expected_result = []  # Adjust based on expected behavior

        # Act
        result = self.instance.chunk(text)

        # Assert
        self.assertIsInstance(result, list)

    def test_merge_chunks_basic(self):
        """Test basic functionality of merge_chunks."""
        # Arrange
        chunks = ["This is", "a test", "text."]
        expected_result = "This is a test text."  # Adjust based on expected behavior

        # Act
        result = self.instance.merge_chunks(chunks)

        # Assert
        self.assertIsInstance(result, str)

    @patch("augment_adam.context.chunking.text_chunker.dependency")
    def test_merge_chunks_with_mocks(self, mock_dependency):
        """Test merge_chunks with mocked dependencies."""
        # Arrange
        mock_dependency.return_value = MagicMock()
        chunks = ["This is", "a test", "text."]
        expected_result = "This is a test text."  # Adjust based on expected behavior

        # Act
        result = self.instance.merge_chunks(chunks)

        # Assert
        self.assertIsInstance(result, str)


if __name__ == '__main__':
    unittest.main()
