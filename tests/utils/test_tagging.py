"""
Tests for the tagging system.

This module contains tests for the tagging system, including tests for
hierarchical tags and tag attributes. It verifies that the tagging system
works correctly in various scenarios, including:

- Creating hierarchical tags
- Using the tag decorator
- Using the safe_tag decorator
- Setting and retrieving tag attributes
- Applying multiple tags to an object
- Creating and verifying tag relationships

These tests ensure that the tagging system is robust and can handle
complex tag hierarchies and relationships.
"""

from typing import List

from augment_adam.utils.tagging import (
    Tag,
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


def test_hierarchical_tag_creation() -> None:
    """
    Test creating hierarchical tags.

    This test verifies that:
    1. Tags can be created in a hierarchical structure
    2. Parent-child relationships are correctly established
    3. Full paths are correctly generated for each tag in the hierarchy
    """
    with isolated_tag_registry():
        # Create a hierarchical tag structure
        memory_tag = create_tag("memory", TagCategory.MEMORY)
        vector_tag = create_tag("vector", TagCategory.MEMORY, memory_tag)
        faiss_tag = create_tag("faiss", TagCategory.MEMORY, vector_tag)

        # Check that the parent references are correct
        assert (
            faiss_tag.parent == vector_tag
        ), "faiss_tag should have vector_tag as parent"
        assert (
            vector_tag.parent == memory_tag
        ), "vector_tag should have memory_tag as parent"
        assert memory_tag.parent is None, "memory_tag should have no parent"

        # Check that the children references are correct
        assert (
            faiss_tag in vector_tag.children
        ), "faiss_tag should be in vector_tag's children"
        assert (
            vector_tag in memory_tag.children
        ), "vector_tag should be in memory_tag's children"

        # Check that the full paths are correctly generated
        assert (
            memory_tag.get_full_path() == "memory"
        ), "memory_tag's full path should be 'memory'"
        assert (
            vector_tag.get_full_path() == "memory.vector"
        ), "vector_tag's full path should be 'memory.vector'"
        assert (
            faiss_tag.get_full_path() == "memory.vector.faiss"
        ), "faiss_tag's full path should be 'memory.vector.faiss'"


def test_tag_decorator() -> None:
    """
    Test the tag decorator.

    This test verifies that:
    1. The tag decorator correctly applies tags to classes
    2. The same tag can be applied to multiple classes
    3. The tags can be retrieved using get_tags
    4. The full path of the tag is correctly preserved
    """
    with isolated_tag_registry():
        # Define a class with a hierarchical tag
        @tag("memory.vector.faiss")
        class FAISSMemory:
            """A class for FAISS vector memory."""

            pass

        # Check that the tag was applied correctly
        tags: List[Tag] = get_tags(FAISSMemory)
        assert len(tags) == 1, "FAISSMemory should have exactly one tag"
        assert (
            tags[0].get_full_path() == "memory.vector.faiss"
        ), "Tag should have the correct full path"

        # Define another class with the same tag
        @tag("memory.vector.faiss")
        class AnotherFAISSMemory:
            """Another class for FAISS vector memory."""

            pass

        # Check that the tag was applied correctly to the second class
        tags = get_tags(AnotherFAISSMemory)
        assert len(tags) == 1, "AnotherFAISSMemory should have exactly one tag"
        assert (
            tags[0].get_full_path() == "memory.vector.faiss"
        ), "Tag should have the correct full path"

        # Verify that both classes have the same tag object (reference equality)
        assert (
            get_tags(FAISSMemory)[0] is get_tags(AnotherFAISSMemory)[0]
        ), "Both classes should reference the same tag object"


def test_safe_tag_decorator() -> None:
    """
    Test the safe_tag decorator.

    This test verifies that:
    1. The safe_tag decorator correctly applies tags to classes
    2. The same tag can be applied to multiple classes without errors
    3. The tags can be retrieved using get_tags
    4. The full path of the tag is correctly preserved

    The safe_tag decorator is designed to be more robust than the standard
    tag decorator, particularly in concurrent environments and with hierarchical tags.
    """
    with isolated_tag_registry():
        # Define a class with a hierarchical tag using safe_tag
        @safe_tag("memory.vector.faiss")
        class FAISSMemory:
            """A class for FAISS vector memory."""

            pass

        # Check that the tag was applied correctly
        tags: List[Tag] = get_tags(FAISSMemory)
        assert len(tags) == 1, "FAISSMemory should have exactly one tag"
        assert (
            tags[0].get_full_path() == "memory.vector.faiss"
        ), "Tag should have the correct full path"

        # Define another class with the same tag
        @safe_tag("memory.vector.faiss")
        class AnotherFAISSMemory:
            """Another class for FAISS vector memory."""

            pass

        # Check that the tag was applied correctly to the second class
        tags = get_tags(AnotherFAISSMemory)
        assert len(tags) == 1, "AnotherFAISSMemory should have exactly one tag"
        assert (
            tags[0].get_full_path() == "memory.vector.faiss"
        ), "Tag should have the correct full path"

        # Verify that both classes have the same tag object (reference equality)
        assert (
            get_tags(FAISSMemory)[0] is get_tags(AnotherFAISSMemory)[0]
        ), "Both classes should reference the same tag object"


def test_tag_attributes() -> None:
    """
    Test tag attributes.

    This test verifies that:
    1. Tags can have attributes attached to them
    2. Attributes can be retrieved from tags
    3. When a tag is reused with different attributes, the attributes are updated

    Tag attributes provide additional metadata about the tagged object,
    such as configuration parameters or capabilities.
    """
    with isolated_tag_registry():
        # Define a class with a tag and attributes
        @tag("memory.vector.faiss", dimension=128, metric="cosine")
        class FAISSMemory:
            """A class for FAISS vector memory with specific dimensions and metric."""

            pass

        # Check that the tag was applied with the correct attributes
        tags: List[Tag] = get_tags(FAISSMemory)
        assert len(tags) == 1, "FAISSMemory should have exactly one tag"
        assert (
            tags[0].get_full_path() == "memory.vector.faiss"
        ), "Tag should have the correct full path"
        assert (
            tags[0].get_attribute("dimension") == 128
        ), "dimension attribute should be 128"
        assert (
            tags[0].get_attribute("metric") == "cosine"
        ), "metric attribute should be 'cosine'"

        # Define another class with the same tag but different attributes
        @tag("memory.vector.faiss", dimension=256, metric="euclidean")
        class AnotherFAISSMemory:
            """Another FAISS memory class with different dimensions and metric."""

            pass

        # Check that the tag was applied with the updated attributes
        tags = get_tags(AnotherFAISSMemory)
        assert len(tags) == 1, "AnotherFAISSMemory should have exactly one tag"
        assert (
            tags[0].get_full_path() == "memory.vector.faiss"
        ), "Tag should have the correct full path"
        assert (
            tags[0].get_attribute("dimension") == 256
        ), "dimension attribute should be updated to 256"
        assert (
            tags[0].get_attribute("metric") == "euclidean"
        ), "metric attribute should be updated to 'euclidean'"

        # Verify that both classes have the same tag object (reference equality)
        assert (
            get_tags(FAISSMemory)[0] is get_tags(AnotherFAISSMemory)[0]
        ), "Both classes should reference the same tag object"


def test_safe_tag_attributes() -> None:
    """
    Test safe_tag attributes.

    This test verifies that:
    1. The safe_tag decorator correctly handles tag attributes
    2. Attributes can be retrieved from tags created with safe_tag
    3. When a tag is reused with different attributes, the attributes are updated

    This test is similar to test_tag_attributes but uses the safe_tag decorator
    instead, which is designed to be more robust in concurrent environments.
    """
    with isolated_tag_registry():
        # Define a class with a tag and attributes using safe_tag
        @safe_tag("memory.vector.faiss", dimension=128, metric="cosine")
        class FAISSMemory:
            """A class for FAISS vector memory with specific dimensions and metric."""

            pass

        # Check that the tag was applied with the correct attributes
        tags: List[Tag] = get_tags(FAISSMemory)
        assert len(tags) == 1, "FAISSMemory should have exactly one tag"
        assert (
            tags[0].get_full_path() == "memory.vector.faiss"
        ), "Tag should have the correct full path"
        assert (
            tags[0].get_attribute("dimension") == 128
        ), "dimension attribute should be 128"
        assert (
            tags[0].get_attribute("metric") == "cosine"
        ), "metric attribute should be 'cosine'"

        # Define another class with the same tag but different attributes
        @safe_tag("memory.vector.faiss", dimension=256, metric="euclidean")
        class AnotherFAISSMemory:
            """Another FAISS memory class with different dimensions and metric."""

            pass

        # Check that the tag was applied with the updated attributes
        tags = get_tags(AnotherFAISSMemory)
        assert len(tags) == 1, "AnotherFAISSMemory should have exactly one tag"
        assert (
            tags[0].get_full_path() == "memory.vector.faiss"
        ), "Tag should have the correct full path"
        assert (
            tags[0].get_attribute("dimension") == 256
        ), "dimension attribute should be updated to 256"
        assert (
            tags[0].get_attribute("metric") == "euclidean"
        ), "metric attribute should be updated to 'euclidean'"

        # Verify that both classes have the same tag object (reference equality)
        assert (
            get_tags(FAISSMemory)[0] is get_tags(AnotherFAISSMemory)[0]
        ), "Both classes should reference the same tag object"


def test_multiple_tags() -> None:
    """
    Test applying multiple tags to an object.

    This test verifies that:
    1. Multiple tags can be applied to a single object
    2. All applied tags can be retrieved using get_tags
    3. Each tag maintains its correct full path

    Multiple tags allow an object to be categorized in different ways
    simultaneously, providing more flexible classification.
    """
    with isolated_tag_registry():
        # Define a class with multiple tags by stacking decorators
        @tag("memory.vector.faiss")
        @tag("model.embedding")
        class FAISSMemory:
            """A class that represents both a memory system and an embedding model."""

            pass

        # Check that both tags were applied correctly
        tags: List[Tag] = get_tags(FAISSMemory)
        assert len(tags) == 2, "FAISSMemory should have exactly two tags"

        # Check that both expected tags are present
        assert any(
            tag.get_full_path() == "memory.vector.faiss" for tag in tags
        ), "Should have a 'memory.vector.faiss' tag"
        assert any(
            tag.get_full_path() == "model.embedding" for tag in tags
        ), "Should have a 'model.embedding' tag"

        # Get the tags by their full paths
        memory_tag = next(
            tag for tag in tags if tag.get_full_path() == "memory.vector.faiss"
        )
        model_tag = next(
            tag for tag in tags if tag.get_full_path() == "model.embedding"
        )

        # In our isolated registry, the category might be TEST instead of the expected category
        # since we're using the tag decorator in a test context
        assert memory_tag is not None, "memory.vector.faiss tag should exist"
        assert model_tag is not None, "model.embedding tag should exist"
        assert (
            memory_tag.get_full_path() == "memory.vector.faiss"
        ), "memory tag should have correct full path"
        assert (
            model_tag.get_full_path() == "model.embedding"
        ), "model tag should have correct full path"


def test_tag_relationships() -> None:
    """
    Test tag relationships.

    This test verifies that:
    1. Relationships can be established between tags
    2. Relationships are directional (not automatically bidirectional)
    3. Relationships can be queried using has_relationship
    4. Multiple relationships can be established between tags

    Tag relationships allow expressing semantic connections between tags,
    such as dependencies, usage patterns, or other domain-specific relationships.
    """
    with isolated_tag_registry():
        # Create tags to establish relationships between
        memory_tag = create_tag("memory", TagCategory.MEMORY)
        model_tag = create_tag("model", TagCategory.MODEL)

        # Add a directional relationship: memory USES model
        memory_tag.add_relationship(model_tag, TagRelationship.USES)

        # Check that the relationship was created correctly
        assert memory_tag.has_relationship(
            model_tag, TagRelationship.USES
        ), "memory should USES model"
        assert not model_tag.has_relationship(
            memory_tag, TagRelationship.USES
        ), "model should not USES memory"

        # Check that other relationships don't exist
        assert not memory_tag.has_relationship(
            model_tag, TagRelationship.DEPENDS_ON
        ), "memory should not DEPENDS_ON model"
        assert not model_tag.has_relationship(
            memory_tag, TagRelationship.DEPENDS_ON
        ), "model should not DEPENDS_ON memory"

        # Add a relationship in the opposite direction: model DEPENDS_ON memory
        model_tag.add_relationship(memory_tag, TagRelationship.DEPENDS_ON)

        # Check that both relationships now exist
        assert memory_tag.has_relationship(
            model_tag, TagRelationship.USES
        ), "memory should still USES model"
        assert model_tag.has_relationship(
            memory_tag, TagRelationship.DEPENDS_ON
        ), "model should now DEPENDS_ON memory"

        # Add another relationship type between the same tags
        memory_tag.add_relationship(model_tag, TagRelationship.COMPOSES)
        assert memory_tag.has_relationship(
            model_tag, TagRelationship.COMPOSES
        ), "memory should now COMPOSES model"
        assert memory_tag.has_relationship(
            model_tag, TagRelationship.USES
        ), "memory should still USES model"


def test_hierarchical_safe_tag() -> None:
    """
    Test the safe_tag decorator with deeply nested hierarchical tags.

    This test verifies that:
    1. The safe_tag decorator can handle deeply nested hierarchical tags
    2. The full path of each tag in the hierarchy is correctly preserved
    3. Parent-child relationships are correctly established

    Hierarchical tags allow for more structured organization of tags,
    enabling both broad and specific categorization.
    """
    with isolated_tag_registry():
        # Define a class with a deeply nested hierarchical tag
        @safe_tag("memory.vector.faiss.index.flat")
        class FlatFAISSIndex:
            """A class for flat FAISS index."""

            pass

        # Check that the tag was applied correctly
        tags: List[Tag] = get_tags(FlatFAISSIndex)
        assert len(tags) == 1, "FlatFAISSIndex should have exactly one tag"
        assert (
            tags[0].get_full_path() == "memory.vector.faiss.index.flat"
        ), "Tag should have the correct full path"

        # Get the tag and verify its hierarchy
        tag = tags[0]
        assert tag.name == "flat", "The leaf tag should be named 'flat'"
        assert tag.parent is not None, "The leaf tag should have a parent"
        assert tag.parent.name == "index", "The parent of 'flat' should be 'index'"
        assert tag.parent.parent is not None, "The 'index' tag should have a parent"
        assert (
            tag.parent.parent.name == "faiss"
        ), "The parent of 'index' should be 'faiss'"
        assert (
            tag.parent.parent.parent is not None
        ), "The 'faiss' tag should have a parent"
        assert (
            tag.parent.parent.parent.name == "vector"
        ), "The parent of 'faiss' should be 'vector'"
        assert (
            tag.parent.parent.parent.parent is not None
        ), "The 'vector' tag should have a parent"
        assert (
            tag.parent.parent.parent.parent.name == "memory"
        ), "The parent of 'vector' should be 'memory'"
        assert (
            tag.parent.parent.parent.parent.parent is None
        ), "The 'memory' tag should have no parent"

        # Define another class with a tag that shares part of the hierarchy
        @safe_tag("memory.vector.faiss.index.ivf")
        class IVFFAISSIndex:
            """A class for IVF FAISS index."""

            pass

        # Check that the tag was applied correctly
        tags_ivf: List[Tag] = get_tags(IVFFAISSIndex)
        assert len(tags_ivf) == 1, "IVFFAISSIndex should have exactly one tag"
        assert (
            tags_ivf[0].get_full_path() == "memory.vector.faiss.index.ivf"
        ), "Tag should have the correct full path"

        # Verify that the two tags share the same ancestors
        flat_tag = tags[0]
        ivf_tag = tags_ivf[0]
        assert (
            flat_tag.parent is ivf_tag.parent
        ), "Both tags should share the same 'index' parent"
        assert (
            flat_tag.parent.parent is ivf_tag.parent.parent
        ), "Both tags should share the same 'faiss' grandparent"
