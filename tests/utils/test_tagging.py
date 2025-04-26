"""
Tests for the tagging system.

This module contains tests for the tagging system, including tests for
hierarchical tags and tag attributes.
"""

from augment_adam.utils.tagging import (
    TagCategory,
    TagRelationship,
    create_tag,
    tag,
    get_tags,
)
from augment_adam.testing.utils.tag_utils import (
    isolated_tag_registry,
    safe_tag,
)


def test_hierarchical_tag_creation():
    """Test creating hierarchical tags."""
    with isolated_tag_registry():
        # Create a hierarchical tag
        memory_tag = create_tag("memory", TagCategory.MEMORY)
        vector_tag = create_tag("vector", TagCategory.MEMORY, memory_tag)
        faiss_tag = create_tag("faiss", TagCategory.MEMORY, vector_tag)

        # Check that the hierarchy is correct
        assert faiss_tag.parent == vector_tag
        assert vector_tag.parent == memory_tag
        assert memory_tag.parent is None

        # Check that the children are correct
        assert faiss_tag in vector_tag.children
        assert vector_tag in memory_tag.children

        # Check that the full paths are correct
        assert memory_tag.get_full_path() == "memory"
        assert vector_tag.get_full_path() == "memory.vector"
        assert faiss_tag.get_full_path() == "memory.vector.faiss"


def test_tag_decorator():
    """Test the tag decorator."""
    with isolated_tag_registry():
        # Define a class with a tag
        @tag("memory.vector.faiss")
        class FAISSMemory:
            pass

        # Check that the tag was applied
        tags = get_tags(FAISSMemory)
        assert len(tags) == 1
        assert tags[0].get_full_path() == "memory.vector.faiss"

        # Define another class with the same tag
        @tag("memory.vector.faiss")
        class AnotherFAISSMemory:
            pass

        # Check that the tag was applied
        tags = get_tags(AnotherFAISSMemory)
        assert len(tags) == 1
        assert tags[0].get_full_path() == "memory.vector.faiss"


def test_safe_tag_decorator():
    """Test the safe_tag decorator."""
    with isolated_tag_registry():
        # Define a class with a tag
        @safe_tag("memory.vector.faiss")
        class FAISSMemory:
            pass

        # Check that the tag was applied
        tags = get_tags(FAISSMemory)
        assert len(tags) == 1
        assert tags[0].get_full_path() == "memory.vector.faiss"

        # Define another class with the same tag
        @safe_tag("memory.vector.faiss")
        class AnotherFAISSMemory:
            pass

        # Check that the tag was applied
        tags = get_tags(AnotherFAISSMemory)
        assert len(tags) == 1
        assert tags[0].get_full_path() == "memory.vector.faiss"


def test_tag_attributes():
    """Test tag attributes."""
    with isolated_tag_registry():
        # Define a class with a tag and attributes
        @tag("memory.vector.faiss", dimension=128, metric="cosine")
        class FAISSMemory:
            pass

        # Check that the tag was applied with attributes
        tags = get_tags(FAISSMemory)
        assert len(tags) == 1
        assert tags[0].get_full_path() == "memory.vector.faiss"
        assert tags[0].get_attribute("dimension") == 128
        assert tags[0].get_attribute("metric") == "cosine"

        # Define another class with the same tag but different attributes
        @tag("memory.vector.faiss", dimension=256, metric="euclidean")
        class AnotherFAISSMemory:
            pass

        # Check that the tag was applied with the new attributes
        tags = get_tags(AnotherFAISSMemory)
        assert len(tags) == 1
        assert tags[0].get_full_path() == "memory.vector.faiss"
        assert tags[0].get_attribute("dimension") == 256
        assert tags[0].get_attribute("metric") == "euclidean"


def test_safe_tag_attributes():
    """Test safe_tag attributes."""
    with isolated_tag_registry():
        # Define a class with a tag and attributes
        @safe_tag("memory.vector.faiss", dimension=128, metric="cosine")
        class FAISSMemory:
            pass

        # Check that the tag was applied with attributes
        tags = get_tags(FAISSMemory)
        assert len(tags) == 1
        assert tags[0].get_full_path() == "memory.vector.faiss"
        assert tags[0].get_attribute("dimension") == 128
        assert tags[0].get_attribute("metric") == "cosine"

        # Define another class with the same tag but different attributes
        @safe_tag("memory.vector.faiss", dimension=256, metric="euclidean")
        class AnotherFAISSMemory:
            pass

        # Check that the tag was applied with the new attributes
        tags = get_tags(AnotherFAISSMemory)
        assert len(tags) == 1
        assert tags[0].get_full_path() == "memory.vector.faiss"
        assert tags[0].get_attribute("dimension") == 256
        assert tags[0].get_attribute("metric") == "euclidean"


def test_multiple_tags():
    """Test applying multiple tags to an object."""
    with isolated_tag_registry():
        # Define a class with multiple tags
        @tag("memory.vector.faiss")
        @tag("model.embedding")
        class FAISSMemory:
            pass

        # Check that both tags were applied
        tags = get_tags(FAISSMemory)
        assert len(tags) == 2
        assert any(
            tag.get_full_path() == "memory.vector.faiss" for tag in tags)
        assert any(tag.get_full_path() == "model.embedding" for tag in tags)


def test_tag_relationships():
    """Test tag relationships."""
    with isolated_tag_registry():
        # Create tags with relationships
        memory_tag = create_tag("memory", TagCategory.MEMORY)
        model_tag = create_tag("model", TagCategory.MODEL)
        memory_tag.add_relationship(model_tag, TagRelationship.USES)

        # Check that the relationship was created
        assert memory_tag.has_relationship(model_tag, TagRelationship.USES)
        assert not model_tag.has_relationship(memory_tag, TagRelationship.USES)

        # Add a bidirectional relationship
        model_tag.add_relationship(memory_tag, TagRelationship.DEPENDS_ON)
        assert model_tag.has_relationship(
            memory_tag, TagRelationship.DEPENDS_ON)
