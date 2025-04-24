"""Unit tests for the FAISS-based semantic memory.

This module contains unit tests for the FAISS-based semantic memory,
testing the core functionality of the FAISSSemanticMemory class.

Version: 0.1.0
Created: 2025-04-24
"""

import os
import time
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import pytest

from augment_adam.memory.faiss_semantic import FAISSSemanticMemory, Concept


class TestFAISSSemanticMemory(unittest.TestCase):
    """Test the FAISSSemanticMemory class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.persist_dir = os.path.join(self.temp_dir.name, "faiss_semantic")

        # Create a real FAISS semantic memory instance for testing
        self.memory = FAISSSemanticMemory(
            persist_dir=self.persist_dir,
            collection_name="test_concepts",
        )

    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary directory
        self.temp_dir.cleanup()

    def test_init(self):
        """Test that FAISSSemanticMemory initializes correctly."""
        # Check that the memory was initialized correctly
        self.assertEqual(self.memory.persist_dir, self.persist_dir)
        self.assertEqual(self.memory.collection_name, "test_concepts")
        self.assertIsNotNone(self.memory.memory)

    def test_add_concept(self):
        """Test adding a concept."""
        # Add a concept
        concept = self.memory.add_concept(
            name="Python",
            description="A programming language",
            content="Python is a high-level, interpreted programming language.",
            metadata={"type": "language", "tags": ["programming", "scripting"]},
        )

        # Check that the concept was added
        self.assertIsNotNone(concept)
        self.assertTrue(concept.id.startswith("con_"))
        self.assertEqual(concept.name, "Python")
        self.assertEqual(concept.description, "A programming language")
        self.assertEqual(concept.content, "Python is a high-level, interpreted programming language.")
        self.assertEqual(concept.metadata["type"], "language")
        self.assertEqual(concept.metadata["tags"], ["programming", "scripting"])

    def test_get_concept(self):
        """Test getting a concept by ID."""
        # Add a concept
        concept = self.memory.add_concept(
            name="Python",
            description="A programming language",
            content="Python is a high-level, interpreted programming language.",
            metadata={"type": "language"},
        )

        # Get the concept by ID
        retrieved_concept = self.memory.get_concept(concept.id)

        # Check that the concept was retrieved
        self.assertIsNotNone(retrieved_concept)
        self.assertEqual(retrieved_concept.id, concept.id)
        self.assertEqual(retrieved_concept.name, "Python")
        self.assertEqual(retrieved_concept.description, "A programming language")
        self.assertEqual(retrieved_concept.content, "Python is a high-level, interpreted programming language.")
        self.assertEqual(retrieved_concept.metadata["type"], "language")

    def test_get_concept_by_name(self):
        """Test getting a concept by name."""
        # Add some concepts
        self.memory.add_concept(
            name="Python",
            description="A programming language",
            content="Python is a high-level, interpreted programming language.",
            metadata={"type": "language"},
        )
        self.memory.add_concept(
            name="JavaScript",
            description="A programming language",
            content="JavaScript is a high-level, interpreted programming language.",
            metadata={"type": "language"},
        )

        # Get a concept by name (exact match)
        concept = self.memory.get_concept_by_name("Python", exact_match=True)

        # Check that the concept was retrieved
        self.assertIsNotNone(concept)
        self.assertEqual(concept.name, "Python")

        # Get a concept by name (partial match)
        concept = self.memory.get_concept_by_name("Java", exact_match=False)

        # Check that the concept was retrieved
        self.assertIsNotNone(concept)
        self.assertEqual(concept.name, "JavaScript")

        # Try to get a concept that doesn't exist
        concept = self.memory.get_concept_by_name("Ruby", exact_match=True)

        # Check that no concept was found
        self.assertIsNone(concept)

    def test_search_concepts(self):
        """Test searching for concepts."""
        # Add some concepts
        self.memory.add_concept(
            name="Python",
            description="A programming language",
            content="Python is a high-level, interpreted programming language.",
            metadata={"type": "language", "paradigm": "object-oriented"},
        )
        self.memory.add_concept(
            name="JavaScript",
            description="A programming language",
            content="JavaScript is a high-level, interpreted programming language.",
            metadata={"type": "language", "paradigm": "object-oriented"},
        )
        self.memory.add_concept(
            name="Weather",
            description="Atmospheric conditions",
            content="Weather is the state of the atmosphere at a particular place and time.",
            metadata={"type": "natural phenomenon"},
        )

        # Search for concepts
        results = self.memory.search_concepts(
            query="programming language",
            n_results=10,
        )

        # Check that the concepts were found
        self.assertEqual(len(results), 2)
        names = [concept.name for concept, _ in results]
        self.assertIn("Python", names)
        self.assertIn("JavaScript", names)

        # Search with filter
        results = self.memory.search_concepts(
            query="programming language",
            n_results=10,
            filter_metadata={"paradigm": "object-oriented"},
        )

        # Check that the filtered concepts were found
        self.assertEqual(len(results), 2)
        names = [concept.name for concept, _ in results]
        self.assertIn("Python", names)
        self.assertIn("JavaScript", names)

    def test_delete_concept(self):
        """Test deleting a concept."""
        # Add a concept
        concept = self.memory.add_concept(
            name="Python",
            description="A programming language",
            content="Python is a high-level, interpreted programming language.",
            metadata={"type": "language"},
        )

        # Delete the concept
        result = self.memory.delete_concept(concept.id)

        # Check that the concept was deleted
        self.assertTrue(result)

        # Try to get the deleted concept
        retrieved_concept = self.memory.get_concept(concept.id)

        # Check that the concept is gone
        self.assertIsNone(retrieved_concept)

    def test_clear(self):
        """Test clearing all concepts."""
        # Add some concepts
        self.memory.add_concept(
            name="Python",
            description="A programming language",
            content="Python is a high-level, interpreted programming language.",
            metadata={"type": "language"},
        )
        self.memory.add_concept(
            name="JavaScript",
            description="A programming language",
            content="JavaScript is a high-level, interpreted programming language.",
            metadata={"type": "language"},
        )

        # Clear all concepts
        result = self.memory.clear()

        # Check that the concepts were cleared
        self.assertTrue(result)

        # Try to search for concepts
        results = self.memory.search_concepts(
            query="programming language",
            n_results=10,
        )

        # Check that no concepts were found
        self.assertEqual(len(results), 0)

    def test_add_empty_fields(self):
        """Test adding a concept with empty fields."""
        # Try to add a concept with empty name
        with self.assertRaises(ValueError):
            self.memory.add_concept(
                name="",
                description="A programming language",
                content="Python is a high-level, interpreted programming language.",
            )

        # Try to add a concept with empty description
        with self.assertRaises(ValueError):
            self.memory.add_concept(
                name="Python",
                description="",
                content="Python is a high-level, interpreted programming language.",
            )

        # Try to add a concept with empty content
        with self.assertRaises(ValueError):
            self.memory.add_concept(
                name="Python",
                description="A programming language",
                content="",
            )

    def test_concept_to_dict(self):
        """Test converting a concept to a dictionary."""
        # Create a concept
        concept = Concept(
            name="Python",
            description="A programming language",
            content="Python is a high-level, interpreted programming language.",
            timestamp=1000,
            metadata={"type": "language"},
            concept_id="con_12345678",
        )

        # Convert to dictionary
        data = concept.to_dict()

        # Check the dictionary
        self.assertEqual(data["id"], "con_12345678")
        self.assertEqual(data["name"], "Python")
        self.assertEqual(data["description"], "A programming language")
        self.assertEqual(data["content"], "Python is a high-level, interpreted programming language.")
        self.assertEqual(data["timestamp"], 1000)
        self.assertEqual(data["metadata"]["type"], "language")

    def test_concept_from_dict(self):
        """Test creating a concept from a dictionary."""
        # Create a dictionary
        data = {
            "id": "con_12345678",
            "name": "Python",
            "description": "A programming language",
            "content": "Python is a high-level, interpreted programming language.",
            "timestamp": 1000,
            "metadata": {"type": "language"},
        }

        # Create a concept from the dictionary
        concept = Concept.from_dict(data)

        # Check the concept
        self.assertEqual(concept.id, "con_12345678")
        self.assertEqual(concept.name, "Python")
        self.assertEqual(concept.description, "A programming language")
        self.assertEqual(concept.content, "Python is a high-level, interpreted programming language.")
        self.assertEqual(concept.timestamp, 1000)
        self.assertEqual(concept.metadata["type"], "language")

    def test_concept_str(self):
        """Test the string representation of a concept."""
        # Create a concept
        concept = Concept(
            name="Python",
            description="A programming language",
            content="Python is a high-level, interpreted programming language.",
            concept_id="con_12345678",
        )

        # Get the string representation
        string = str(concept)

        # Check the string
        self.assertEqual(string, "Python (con_12345678): A programming language")


if __name__ == "__main__":
    unittest.main()
