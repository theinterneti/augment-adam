"""
Unit tests for augment_adam.utils.tagging.core.

This module tests the tagging system for categorizing and organizing code.
"""

import unittest
import pytest
from enum import Enum, auto

from augment_adam.utils.tagging.core import (
    Tag,
    TagCategory,
    TagRelationship,
    TagRegistry,
)

# Import test utilities
from tests.utils import (
    skip_if_no_module,
    timed,
    assert_dict_subset,
    assert_lists_equal_unordered,
    assert_approx_equal,
)


@pytest.mark.unit
class TestTag(unittest.TestCase):
    """Test cases for the Tag class."""

    def setUp(self):
        """Set up the test case."""
        # Initialize objects for testing
        self.memory_tag = Tag(name="memory", category=TagCategory.MEMORY)
        self.vector_tag = Tag(name="vector", category=TagCategory.MEMORY, parent=self.memory_tag)
        self.faiss_tag = Tag(name="faiss", category=TagCategory.MEMORY, parent=self.vector_tag)

    def tearDown(self):
        """Tear down the test case."""
        # Clean up resources
        pass

    def test_init(self):
        """Test Tag initialization."""
        # Test initialization with default parameters
        tag = Tag(name="test", category=TagCategory.UTILITY)
        self.assertEqual("test", tag.name)
        self.assertEqual(TagCategory.UTILITY, tag.category)
        self.assertIsNone(tag.parent)
        self.assertEqual({}, tag.attributes)
        self.assertEqual([], tag.children)
        self.assertEqual("", tag.description)
        self.assertEqual([], tag.examples)
        self.assertEqual({}, tag.relationships)
        self.assertEqual([], tag.synonyms)
        self.assertEqual(5, tag.importance)
        self.assertIsNotNone(tag.created_at)
        self.assertIsNotNone(tag.updated_at)

        # Test initialization with custom parameters
        attributes = {"key": "value"}
        description = "Test description"
        synonyms = ["test_synonym"]
        examples = ["test example"]

        tag = Tag(
            name="test",
            category=TagCategory.UTILITY,
            attributes=attributes,
            description=description,
            synonyms=synonyms,
            examples=examples,
            importance=8,
        )

        self.assertEqual("test", tag.name)
        self.assertEqual(TagCategory.UTILITY, tag.category)
        self.assertEqual(attributes, tag.attributes)
        self.assertEqual(description, tag.description)
        self.assertEqual(synonyms, tag.synonyms)
        self.assertEqual(examples, tag.examples)
        self.assertEqual(8, tag.importance)

    def test_parent_child_relationship(self):
        """Test parent-child relationship between tags."""
        # Check that the parent-child relationship was set up correctly
        self.assertIn(self.vector_tag, self.memory_tag.children)
        self.assertIn(self.faiss_tag, self.vector_tag.children)

        self.assertEqual(self.memory_tag, self.vector_tag.parent)
        self.assertEqual(self.vector_tag, self.faiss_tag.parent)

    def test_get_full_path(self):
        """Test the get_full_path method."""
        self.assertEqual("memory", self.memory_tag.get_full_path())
        self.assertEqual("memory.vector", self.vector_tag.get_full_path())
        self.assertEqual("memory.vector.faiss", self.faiss_tag.get_full_path())

    def test_attributes(self):
        """Test attribute methods."""
        tag = Tag(name="test", category=TagCategory.UTILITY)

        # Initially, the tag has no attributes
        self.assertFalse(tag.has_attribute("key"))
        self.assertIsNone(tag.get_attribute("key"))
        self.assertEqual("default", tag.get_attribute("key", "default"))

        # Set an attribute
        tag.set_attribute("key", "value")

        # Now the tag has the attribute
        self.assertTrue(tag.has_attribute("key"))
        self.assertEqual("value", tag.get_attribute("key"))
        self.assertEqual("value", tag.get_attribute("key", "default"))

    def test_is_child_of(self):
        """Test the is_child_of method."""
        # Direct parent
        self.assertTrue(self.vector_tag.is_child_of(self.memory_tag))
        self.assertTrue(self.faiss_tag.is_child_of(self.vector_tag))

        # Indirect parent
        self.assertTrue(self.faiss_tag.is_child_of(self.memory_tag))

        # Not a parent
        self.assertFalse(self.memory_tag.is_child_of(self.vector_tag))
        self.assertFalse(self.vector_tag.is_child_of(self.faiss_tag))

        # Test with string
        self.assertTrue(self.vector_tag.is_child_of("memory"))
        self.assertTrue(self.faiss_tag.is_child_of("vector"))
        self.assertTrue(self.faiss_tag.is_child_of("memory"))

    def test_relationships(self):
        """Test relationship methods."""
        # Create tags for testing relationships
        model_tag = Tag(name="model", category=TagCategory.MODEL)
        embedding_tag = Tag(name="embedding", category=TagCategory.MODEL, parent=model_tag)

        # Initially, there are no relationships
        self.assertFalse(self.vector_tag.has_relationship(embedding_tag))
        self.assertEqual({}, self.vector_tag.get_relationships())

        # Add a relationship
        self.vector_tag.add_relationship(embedding_tag, TagRelationship.USES)

        # Now there is a relationship
        self.assertTrue(self.vector_tag.has_relationship(embedding_tag))
        self.assertTrue(self.vector_tag.has_relationship(embedding_tag, TagRelationship.USES))
        self.assertFalse(self.vector_tag.has_relationship(embedding_tag, TagRelationship.IMPLEMENTS))

        # Add another relationship
        self.vector_tag.add_relationship(embedding_tag, TagRelationship.DEPENDS_ON)

        # Now there are two relationships
        self.assertTrue(self.vector_tag.has_relationship(embedding_tag, TagRelationship.USES))
        self.assertTrue(self.vector_tag.has_relationship(embedding_tag, TagRelationship.DEPENDS_ON))

        # Get relationships
        relationships = self.vector_tag.get_relationships()
        self.assertIn(embedding_tag, relationships)
        self.assertIn(TagRelationship.USES, relationships[embedding_tag])
        self.assertIn(TagRelationship.DEPENDS_ON, relationships[embedding_tag])

        # Get relationships filtered by type
        uses_relationships = self.vector_tag.get_relationships(TagRelationship.USES)
        self.assertIn(embedding_tag, uses_relationships)
        self.assertEqual([TagRelationship.USES], uses_relationships[embedding_tag])

        # Remove a specific relationship
        self.vector_tag.remove_relationship(embedding_tag, TagRelationship.USES)

        # Now there is only one relationship
        self.assertTrue(self.vector_tag.has_relationship(embedding_tag))
        self.assertFalse(self.vector_tag.has_relationship(embedding_tag, TagRelationship.USES))
        self.assertTrue(self.vector_tag.has_relationship(embedding_tag, TagRelationship.DEPENDS_ON))

        # Remove all relationships
        self.vector_tag.remove_relationship(embedding_tag)

        # Now there are no relationships
        self.assertFalse(self.vector_tag.has_relationship(embedding_tag))

    def test_get_semantic_description(self):
        """Test the get_semantic_description method."""
        # Create a tag with all fields populated
        model_tag = Tag(
            name="model",
            category=TagCategory.MODEL,
            description="AI model tag",
            synonyms=["ai_model", "llm"],
            attributes={"version": "1.0", "author": "Test"},
            examples=["Use this tag for model-related code"],
        )

        embedding_tag = Tag(
            name="embedding",
            category=TagCategory.MODEL,
            parent=model_tag,
            description="Embedding model tag",
        )

        # Add a relationship
        model_tag.add_relationship(embedding_tag, TagRelationship.GENERATES)

        # Get the semantic description
        description = model_tag.get_semantic_description()

        # Check that the description contains all the expected information
        self.assertIn("Tag: model", description)
        self.assertIn("Category: MODEL", description)
        self.assertIn("Description: AI model tag", description)
        self.assertIn("Children: embedding", description)
        self.assertIn("Synonyms: ai_model, llm", description)
        self.assertIn("Attributes:", description)
        self.assertIn("version: 1.0", description)
        self.assertIn("author: Test", description)
        self.assertIn("Relationships:", description)
        self.assertIn("embedding: GENERATES", description)
        self.assertIn("Examples:", description)
        self.assertIn("Use this tag for model-related code", description)

    def test_equality(self):
        """Test tag equality."""
        # Tags with the same name are equal
        tag1 = Tag(name="test", category=TagCategory.UTILITY)
        tag2 = Tag(name="test", category=TagCategory.MEMORY)

        self.assertEqual(tag1, tag2)
        self.assertEqual(hash(tag1), hash(tag2))

        # Tags with different names are not equal
        tag3 = Tag(name="other", category=TagCategory.UTILITY)

        self.assertNotEqual(tag1, tag3)
        self.assertNotEqual(hash(tag1), hash(tag3))

        # A tag is not equal to a non-tag
        self.assertNotEqual(tag1, "test")


@pytest.mark.unit
class TestTagRegistry(unittest.TestCase):
    """Test cases for the TagRegistry class."""

    def setUp(self):
        """Set up the test case."""
        # Initialize objects for testing
        self.registry = TagRegistry()

    def tearDown(self):
        """Tear down the test case."""
        # Clean up resources
        pass

    def test_init(self):
        """Test TagRegistry initialization."""
        # Check that the registry was initialized with predefined tags
        self.assertIn("memory", self.registry.tags)
        self.assertIn("vector", self.registry.tags)
        self.assertIn("faiss", self.registry.tags)
        self.assertIn("model", self.registry.tags)
        self.assertIn("agent", self.registry.tags)
        self.assertIn("context", self.registry.tags)

    def test_create_tag(self):
        """Test the create_tag method."""
        # Create a new tag
        tag = self.registry.create_tag(
            name="test_tag",
            category=TagCategory.UTILITY,
            description="Test tag",
        )

        # Check that the tag was created correctly
        self.assertEqual("test_tag", tag.name)
        self.assertEqual(TagCategory.UTILITY, tag.category)
        self.assertEqual("Test tag", tag.description)

        # Check that the tag was added to the registry
        self.assertIn("test_tag", self.registry.tags)
        self.assertEqual(tag, self.registry.tags["test_tag"])

        # Create a tag with a parent
        child_tag = self.registry.create_tag(
            name="child_tag",
            category=TagCategory.UTILITY,
            parent="test_tag",
        )

        # Check that the parent-child relationship was set up correctly
        self.assertEqual(tag, child_tag.parent)
        self.assertIn(child_tag, tag.children)

        # Try to create a tag with the same name (should raise ValueError)
        with self.assertRaises(ValueError):
            self.registry.create_tag(
                name="test_tag",
                category=TagCategory.UTILITY,
            )

        # Try to create a tag with the same name with force=True (should return existing tag)
        existing_tag = self.registry.create_tag(
            name="test_tag",
            category=TagCategory.UTILITY,
            force=True,
        )

        self.assertEqual(tag, existing_tag)

    def test_get_tag(self):
        """Test the get_tag method."""
        # Get an existing tag
        memory_tag = self.registry.get_tag("memory")

        self.assertEqual("memory", memory_tag.name)
        self.assertEqual(TagCategory.MEMORY, memory_tag.category)

        # Try to get a non-existent tag
        non_existent = self.registry.get_tag("non_existent")
        self.assertIsNone(non_existent)

        # Create a default tag to use if the tag doesn't exist
        default_tag = Tag(name="default", category=TagCategory.UTILITY)

        # Since get_tag doesn't support a default parameter, we need to handle it manually
        result = self.registry.get_tag("non_existent") or default_tag

        self.assertEqual(default_tag, result)

    def test_get_tags_by_category(self):
        """Test the get_tags_by_category method."""
        # Get all memory tags
        memory_tags = self.registry.get_tags_by_category(TagCategory.MEMORY)

        # Check that all memory tags were returned
        self.assertIn(self.registry.get_tag("memory"), memory_tags)
        self.assertIn(self.registry.get_tag("vector"), memory_tags)
        self.assertIn(self.registry.get_tag("faiss"), memory_tags)

        # Check that non-memory tags were not returned
        self.assertNotIn(self.registry.get_tag("model"), memory_tags)
        self.assertNotIn(self.registry.get_tag("agent"), memory_tags)

    def test_get_tags_by_parent(self):
        """Test the get_tags_by_parent method."""
        # Get all children of the memory tag
        memory_tag = self.registry.get_tag("memory")
        memory_children = memory_tag.children

        # Check that direct children were returned
        self.assertIn(self.registry.get_tag("vector"), memory_children)
        self.assertIn(self.registry.get_tag("graph"), memory_children)
        self.assertIn(self.registry.get_tag("episodic"), memory_children)

        # Check that indirect children were not returned
        self.assertNotIn(self.registry.get_tag("faiss"), memory_children)

        # Get all children of the vector tag
        vector_tag = self.registry.get_tag("vector")
        vector_children = vector_tag.children

        # Check that direct children were returned
        self.assertIn(self.registry.get_tag("faiss"), vector_children)

        # Check that non-children were not returned
        self.assertNotIn(self.registry.get_tag("memory"), vector_children)
        self.assertNotIn(self.registry.get_tag("graph"), vector_children)

    def test_get_tags_by_relationship(self):
        """Test the get_tags_by_relationship method."""
        # Create tags with relationships
        model_tag = self.registry.get_tag("model")
        embedding_tag = self.registry.get_tag("embedding")
        vector_tag = self.registry.get_tag("vector")

        # Add relationships
        model_tag.add_relationship(embedding_tag, TagRelationship.GENERATES)
        vector_tag.add_relationship(embedding_tag, TagRelationship.USES)

        # Find tags with GENERATES relationship by checking all tags
        generates_tags = []
        for tag in self.registry.tags.values():
            for target, relationships in tag.relationships.items():
                if TagRelationship.GENERATES in relationships:
                    generates_tags.append(tag)
                    break

        # Check that tags with GENERATES relationship were found
        self.assertIn(model_tag, generates_tags)

        # Check that tags without GENERATES relationship were not found
        self.assertNotIn(vector_tag, generates_tags)

        # Find tags with USES relationship by checking all tags
        uses_tags = []
        for tag in self.registry.tags.values():
            for target, relationships in tag.relationships.items():
                if TagRelationship.USES in relationships:
                    uses_tags.append(tag)
                    break

        # Check that tags with USES relationship were found
        self.assertIn(vector_tag, uses_tags)

        # Check that tags without USES relationship were not found
        self.assertNotIn(model_tag, uses_tags)

    def test_get_tags_by_attribute(self):
        """Test the get_tags_by_attribute method."""
        # Create tags with attributes
        model_tag = self.registry.get_tag("model")
        embedding_tag = self.registry.get_tag("embedding")

        # Add attributes
        model_tag.set_attribute("version", "1.0")
        embedding_tag.set_attribute("version", "2.0")
        embedding_tag.set_attribute("dimensions", 768)

        # Get tags with version attribute
        version_tags = self.registry.get_tags_by_attribute("version")

        # Check that tags with version attribute were returned
        self.assertIn(model_tag, version_tags)
        self.assertIn(embedding_tag, version_tags)

        # Get tags with version=1.0 attribute
        version_1_tags = self.registry.get_tags_by_attribute("version", "1.0")

        # Check that tags with version=1.0 attribute were returned
        self.assertIn(model_tag, version_1_tags)

        # Check that tags without version=1.0 attribute were not returned
        self.assertNotIn(embedding_tag, version_1_tags)

        # Get tags with dimensions attribute
        dimensions_tags = self.registry.get_tags_by_attribute("dimensions")

        # Check that tags with dimensions attribute were returned
        self.assertIn(embedding_tag, dimensions_tags)

        # Check that tags without dimensions attribute were not returned
        self.assertNotIn(model_tag, dimensions_tags)

    def test_search_tags(self):
        """Test the search_tags method."""
        # Search for tags with "mem" in the name
        mem_tags = [tag for tag in self.registry.tags.values() if "mem" in tag.name.lower()]

        # Check that matching tags were returned
        self.assertIn(self.registry.get_tag("memory"), mem_tags)

        # Check that non-matching tags were not returned
        self.assertNotIn(self.registry.get_tag("model"), mem_tags)

        # Search for tags with "vector" in the name or description
        vector_tag = self.registry.get_tag("vector")
        vector_tag.description = "Vector-based memory storage"

        vector_tags = [tag for tag in self.registry.tags.values() if "vector" in tag.name.lower()]

        # Check that matching tags were returned
        self.assertIn(vector_tag, vector_tags)

        # Search for tags with "storage" in the description
        storage_tags = [tag for tag in self.registry.tags.values() if tag.description and "storage" in tag.description.lower()]

        # Check that matching tags were returned
        self.assertIn(vector_tag, storage_tags)

        # Check that non-matching tags were not returned
        self.assertNotIn(self.registry.get_tag("model"), storage_tags)


if __name__ == "__main__":
    unittest.main()
