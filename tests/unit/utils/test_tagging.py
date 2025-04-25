"""Unit tests for the tagging system.

This module contains unit tests for the tagging system in augment_adam.utils.tagging.
"""

import pytest
from unittest.mock import Mock, patch
from augment_adam.utils.tagging import (
    TagCategory, Tag, TagRegistry, TagRelationship, get_tag_registry, get_tag,
    create_tag, get_or_create_tag, get_tags_by_category, tag, get_tags,
    relate_tags, get_related_tags, find_tags, describe_tag
)


class TestTag:
    """Tests for the Tag class."""

    def test_init(self):
        """Test Tag initialization."""
        # Arrange
        parent = Tag("parent", TagCategory.MEMORY)

        # Act
        tag = Tag("test", TagCategory.MEMORY, parent)

        # Assert
        assert tag.name == "test"
        assert tag.category == TagCategory.MEMORY
        assert tag.parent == parent
        assert tag in parent.children

    def test_str(self):
        """Test Tag string representation."""
        # Arrange
        tag = Tag("test", TagCategory.MEMORY)

        # Act
        result = str(tag)

        # Assert
        assert result == "test"

    def test_repr(self):
        """Test Tag repr representation."""
        # Arrange
        tag = Tag("test", TagCategory.MEMORY)

        # Act
        result = repr(tag)

        # Assert
        assert "Tag" in result
        assert "test" in result
        assert "MEMORY" in result

    def test_get_full_path_no_parent(self):
        """Test get_full_path with no parent."""
        # Arrange
        tag = Tag("test", TagCategory.MEMORY)

        # Act
        result = tag.get_full_path()

        # Assert
        assert result == "test"

    def test_get_full_path_with_parent(self):
        """Test get_full_path with parent."""
        # Arrange
        parent = Tag("parent", TagCategory.MEMORY)
        tag = Tag("test", TagCategory.MEMORY, parent)

        # Act
        result = tag.get_full_path()

        # Assert
        assert result == "parent.test"

    def test_get_full_path_with_grandparent(self):
        """Test get_full_path with grandparent."""
        # Arrange
        grandparent = Tag("grandparent", TagCategory.MEMORY)
        parent = Tag("parent", TagCategory.MEMORY, grandparent)
        tag = Tag("test", TagCategory.MEMORY, parent)

        # Act
        result = tag.get_full_path()

        # Assert
        assert result == "grandparent.parent.test"

    def test_has_attribute(self):
        """Test has_attribute."""
        # Arrange
        tag = Tag("test", TagCategory.MEMORY, attributes={"key": "value"})

        # Act & Assert
        assert tag.has_attribute("key") is True
        assert tag.has_attribute("nonexistent") is False

    def test_get_attribute(self):
        """Test get_attribute."""
        # Arrange
        tag = Tag("test", TagCategory.MEMORY, attributes={"key": "value"})

        # Act & Assert
        assert tag.get_attribute("key") == "value"
        assert tag.get_attribute("nonexistent") is None
        assert tag.get_attribute("nonexistent", "default") == "default"

    def test_set_attribute(self):
        """Test set_attribute."""
        # Arrange
        tag = Tag("test", TagCategory.MEMORY)

        # Act
        tag.set_attribute("key", "value")

        # Assert
        assert tag.attributes["key"] == "value"

    def test_is_child_of_string(self):
        """Test is_child_of with string parent."""
        # Arrange
        parent = Tag("parent", TagCategory.MEMORY)
        tag = Tag("test", TagCategory.MEMORY, parent)

        # Act & Assert
        assert tag.is_child_of("parent") is True
        assert tag.is_child_of("nonexistent") is False

    def test_is_child_of_tag(self):
        """Test is_child_of with Tag parent."""
        # Arrange
        parent = Tag("parent", TagCategory.MEMORY)
        tag = Tag("test", TagCategory.MEMORY, parent)

        # Act & Assert
        assert tag.is_child_of(parent) is True
        assert tag.is_child_of(Tag("nonexistent", TagCategory.MEMORY)) is False

    def test_is_child_of_grandparent(self):
        """Test is_child_of with grandparent."""
        # Arrange
        grandparent = Tag("grandparent", TagCategory.MEMORY)
        parent = Tag("parent", TagCategory.MEMORY, grandparent)
        tag = Tag("test", TagCategory.MEMORY, parent)

        # Act & Assert
        assert tag.is_child_of("grandparent") is True

    def test_add_relationship(self):
        """Test add_relationship."""
        # Arrange
        tag1 = Tag("tag1", TagCategory.MEMORY)
        tag2 = Tag("tag2", TagCategory.MEMORY)

        # Act
        tag1.add_relationship(tag2, TagRelationship.USES)

        # Assert
        assert tag2 in tag1.relationships
        assert TagRelationship.USES in tag1.relationships[tag2]

    def test_add_relationship_duplicate(self):
        """Test add_relationship with duplicate relationship."""
        # Arrange
        tag1 = Tag("tag1", TagCategory.MEMORY)
        tag2 = Tag("tag2", TagCategory.MEMORY)
        tag1.add_relationship(tag2, TagRelationship.USES)

        # Act
        tag1.add_relationship(tag2, TagRelationship.USES)

        # Assert
        assert tag2 in tag1.relationships
        assert len(tag1.relationships[tag2]) == 1
        assert TagRelationship.USES in tag1.relationships[tag2]

    def test_add_multiple_relationships(self):
        """Test adding multiple relationships."""
        # Arrange
        tag1 = Tag("tag1", TagCategory.MEMORY)
        tag2 = Tag("tag2", TagCategory.MEMORY)

        # Act
        tag1.add_relationship(tag2, TagRelationship.USES)
        tag1.add_relationship(tag2, TagRelationship.DEPENDS_ON)

        # Assert
        assert tag2 in tag1.relationships
        assert len(tag1.relationships[tag2]) == 2
        assert TagRelationship.USES in tag1.relationships[tag2]
        assert TagRelationship.DEPENDS_ON in tag1.relationships[tag2]

    def test_remove_relationship_specific(self):
        """Test remove_relationship with specific relationship."""
        # Arrange
        tag1 = Tag("tag1", TagCategory.MEMORY)
        tag2 = Tag("tag2", TagCategory.MEMORY)
        tag1.add_relationship(tag2, TagRelationship.USES)
        tag1.add_relationship(tag2, TagRelationship.DEPENDS_ON)

        # Act
        tag1.remove_relationship(tag2, TagRelationship.USES)

        # Assert
        assert tag2 in tag1.relationships
        assert len(tag1.relationships[tag2]) == 1
        assert TagRelationship.DEPENDS_ON in tag1.relationships[tag2]

    def test_remove_relationship_all(self):
        """Test remove_relationship with all relationships."""
        # Arrange
        tag1 = Tag("tag1", TagCategory.MEMORY)
        tag2 = Tag("tag2", TagCategory.MEMORY)
        tag1.add_relationship(tag2, TagRelationship.USES)
        tag1.add_relationship(tag2, TagRelationship.DEPENDS_ON)

        # Act
        tag1.remove_relationship(tag2)

        # Assert
        assert tag2 not in tag1.relationships

    def test_has_relationship_specific(self):
        """Test has_relationship with specific relationship."""
        # Arrange
        tag1 = Tag("tag1", TagCategory.MEMORY)
        tag2 = Tag("tag2", TagCategory.MEMORY)
        tag1.add_relationship(tag2, TagRelationship.USES)

        # Act & Assert
        assert tag1.has_relationship(tag2, TagRelationship.USES) is True
        assert tag1.has_relationship(tag2, TagRelationship.DEPENDS_ON) is False

    def test_has_relationship_any(self):
        """Test has_relationship with any relationship."""
        # Arrange
        tag1 = Tag("tag1", TagCategory.MEMORY)
        tag2 = Tag("tag2", TagCategory.MEMORY)
        tag3 = Tag("tag3", TagCategory.MEMORY)
        tag1.add_relationship(tag2, TagRelationship.USES)

        # Act & Assert
        assert tag1.has_relationship(tag2) is True
        assert tag1.has_relationship(tag3) is False

    def test_get_relationships_all(self):
        """Test get_relationships with all relationships."""
        # Arrange
        tag1 = Tag("tag1", TagCategory.MEMORY)
        tag2 = Tag("tag2", TagCategory.MEMORY)
        tag3 = Tag("tag3", TagCategory.MEMORY)
        tag1.add_relationship(tag2, TagRelationship.USES)
        tag1.add_relationship(tag3, TagRelationship.DEPENDS_ON)

        # Act
        relationships = tag1.get_relationships()

        # Assert
        assert len(relationships) == 2
        assert tag2 in relationships
        assert tag3 in relationships
        assert TagRelationship.USES in relationships[tag2]
        assert TagRelationship.DEPENDS_ON in relationships[tag3]

    def test_get_relationships_filtered(self):
        """Test get_relationships with filtered relationships."""
        # Arrange
        tag1 = Tag("tag1", TagCategory.MEMORY)
        tag2 = Tag("tag2", TagCategory.MEMORY)
        tag3 = Tag("tag3", TagCategory.MEMORY)
        tag1.add_relationship(tag2, TagRelationship.USES)
        tag1.add_relationship(tag3, TagRelationship.DEPENDS_ON)

        # Act
        relationships = tag1.get_relationships(TagRelationship.USES)

        # Assert
        assert len(relationships) == 1
        assert tag2 in relationships
        assert tag3 not in relationships
        assert TagRelationship.USES in relationships[tag2]

    def test_get_semantic_description(self):
        """Test get_semantic_description."""
        # Arrange
        parent = Tag("parent", TagCategory.MEMORY, description="Parent tag")
        tag = Tag(
            name="test",
            category=TagCategory.MEMORY,
            parent=parent,
            description="Test tag",
            attributes={"key": "value"},
            synonyms=["test_synonym"],
            examples=["Example usage"]
        )
        related = Tag("related", TagCategory.MEMORY)
        tag.add_relationship(related, TagRelationship.USES)

        # Act
        description = tag.get_semantic_description()

        # Assert
        assert "Tag: test" in description
        assert "Category: MEMORY" in description
        assert "Description: Test tag" in description
        assert "Parent: parent" in description
        assert "Synonyms: test_synonym" in description
        assert "Attributes:" in description
        assert "key: value" in description
        assert "Relationships:" in description
        assert "related: USES" in description
        assert "Examples:" in description
        assert "Example usage" in description


class TestTagRegistry:
    """Tests for the TagRegistry class."""

    def test_init(self):
        """Test TagRegistry initialization."""
        # Act
        registry = TagRegistry()

        # Assert
        assert isinstance(registry.tags, dict)
        assert len(registry.tags) > 0  # Should have predefined tags

    def test_create_tag(self):
        """Test create_tag."""
        # Arrange
        registry = TagRegistry()

        # Act
        tag = registry.create_tag("new_tag", TagCategory.MEMORY)

        # Assert
        assert tag.name == "new_tag"
        assert tag.category == TagCategory.MEMORY
        assert registry.tags["new_tag"] == tag

    def test_create_tag_with_parent_string(self):
        """Test create_tag with parent string."""
        # Arrange
        registry = TagRegistry()

        # Act
        tag = registry.create_tag("new_tag", TagCategory.MEMORY, "memory")

        # Assert
        assert tag.parent == registry.tags["memory"]
        assert tag in registry.tags["memory"].children

    def test_create_tag_with_parent_tag(self):
        """Test create_tag with parent tag."""
        # Arrange
        registry = TagRegistry()
        parent = registry.tags["memory"]

        # Act
        tag = registry.create_tag("new_tag", TagCategory.MEMORY, parent)

        # Assert
        assert tag.parent == parent
        assert tag in parent.children

    def test_create_tag_with_attributes(self):
        """Test create_tag with attributes."""
        # Arrange
        registry = TagRegistry()

        # Act
        tag = registry.create_tag("new_tag", TagCategory.MEMORY, attributes={"key": "value"})

        # Assert
        assert tag.attributes["key"] == "value"

    def test_create_tag_duplicate(self):
        """Test create_tag with duplicate name."""
        # Arrange
        registry = TagRegistry()

        # Act & Assert
        with pytest.raises(ValueError):
            registry.create_tag("memory", TagCategory.MEMORY)

    def test_create_tag_nonexistent_parent(self):
        """Test create_tag with nonexistent parent."""
        # Arrange
        registry = TagRegistry()

        # Act & Assert
        with pytest.raises(ValueError):
            registry.create_tag("new_tag", TagCategory.MEMORY, "nonexistent")

    def test_get_tag(self):
        """Test get_tag."""
        # Arrange
        registry = TagRegistry()

        # Act & Assert
        assert registry.get_tag("memory") is not None
        assert registry.get_tag("nonexistent") is None

    def test_get_or_create_tag_existing(self):
        """Test get_or_create_tag with existing tag."""
        # Arrange
        registry = TagRegistry()

        # Act
        tag = registry.get_or_create_tag("memory", TagCategory.MEMORY)

        # Assert
        assert tag == registry.tags["memory"]

    def test_get_or_create_tag_new(self):
        """Test get_or_create_tag with new tag."""
        # Arrange
        registry = TagRegistry()

        # Act
        tag = registry.get_or_create_tag("new_tag", TagCategory.MEMORY)

        # Assert
        assert tag.name == "new_tag"
        assert tag.category == TagCategory.MEMORY
        assert registry.tags["new_tag"] == tag

    def test_delete_tag(self):
        """Test delete_tag."""
        # Arrange
        registry = TagRegistry()
        registry.create_tag("new_tag", TagCategory.MEMORY)

        # Act
        registry.delete_tag("new_tag")

        # Assert
        assert "new_tag" not in registry.tags

    def test_delete_tag_with_children(self):
        """Test delete_tag with children."""
        # Arrange
        registry = TagRegistry()
        registry.create_tag("parent_tag", TagCategory.MEMORY)
        registry.create_tag("child_tag", TagCategory.MEMORY, "parent_tag")

        # Act
        registry.delete_tag("parent_tag")

        # Assert
        assert "parent_tag" not in registry.tags
        assert "child_tag" not in registry.tags

    def test_delete_tag_nonexistent(self):
        """Test delete_tag with nonexistent tag."""
        # Arrange
        registry = TagRegistry()

        # Act & Assert
        with pytest.raises(ValueError):
            registry.delete_tag("nonexistent")

    def test_get_tags_by_category(self):
        """Test get_tags_by_category."""
        # Arrange
        registry = TagRegistry()

        # Act
        memory_tags = registry.get_tags_by_category(TagCategory.MEMORY)

        # Assert
        assert len(memory_tags) > 0
        assert all(tag.category == TagCategory.MEMORY for tag in memory_tags)

    def test_get_tags_by_attribute(self):
        """Test get_tags_by_attribute."""
        # Arrange
        registry = TagRegistry()
        registry.create_tag("attr_tag", TagCategory.MEMORY, attributes={"key": "value"})

        # Act
        tags = registry.get_tags_by_attribute("key")

        # Assert
        assert len(tags) > 0
        assert all(tag.has_attribute("key") for tag in tags)

    def test_get_tags_by_attribute_with_value(self):
        """Test get_tags_by_attribute with value."""
        # Arrange
        registry = TagRegistry()
        registry.create_tag("attr_tag", TagCategory.MEMORY, attributes={"key": "value"})

        # Act
        tags = registry.get_tags_by_attribute("key", "value")

        # Assert
        assert len(tags) > 0
        assert all(tag.get_attribute("key") == "value" for tag in tags)

    def test_get_children(self):
        """Test get_children."""
        # Arrange
        registry = TagRegistry()

        # Act
        children = registry.get_children("memory")

        # Assert
        assert len(children) > 0
        assert all(tag.parent == registry.tags["memory"] for tag in children)

    def test_get_children_nonexistent(self):
        """Test get_children with nonexistent tag."""
        # Arrange
        registry = TagRegistry()

        # Act & Assert
        with pytest.raises(ValueError):
            registry.get_children("nonexistent")

    def test_get_all_tags(self):
        """Test get_all_tags."""
        # Arrange
        registry = TagRegistry()

        # Act
        tags = registry.get_all_tags()

        # Assert
        assert len(tags) > 0
        assert all(isinstance(tag, Tag) for tag in tags)

    def test_get_root_tags(self):
        """Test get_root_tags."""
        # Arrange
        registry = TagRegistry()

        # Act
        tags = registry.get_root_tags()

        # Assert
        assert len(tags) > 0
        assert all(tag.parent is None for tag in tags)

    def test_relate_tags(self):
        """Test relate_tags."""
        # Arrange
        registry = TagRegistry()

        # Act
        registry.relate_tags("memory", "model", TagRelationship.USES)

        # Assert
        memory_tag = registry.get_tag("memory")
        model_tag = registry.get_tag("model")
        assert model_tag in memory_tag.relationships
        assert TagRelationship.USES in memory_tag.relationships[model_tag]

    def test_relate_tags_nonexistent_source(self):
        """Test relate_tags with nonexistent source."""
        # Arrange
        registry = TagRegistry()

        # Act & Assert
        with pytest.raises(ValueError):
            registry.relate_tags("nonexistent", "memory", TagRelationship.USES)

    def test_relate_tags_nonexistent_target(self):
        """Test relate_tags with nonexistent target."""
        # Arrange
        registry = TagRegistry()

        # Act & Assert
        with pytest.raises(ValueError):
            registry.relate_tags("memory", "nonexistent", TagRelationship.USES)

    def test_get_related_tags(self):
        """Test get_related_tags."""
        # Arrange
        registry = TagRegistry()
        registry.relate_tags("memory", "model", TagRelationship.USES)

        # Act
        related = registry.get_related_tags("memory")

        # Assert
        assert "model" in related
        assert TagRelationship.USES in related["model"]

    def test_get_related_tags_filtered(self):
        """Test get_related_tags with filtered relationship."""
        # Arrange
        registry = TagRegistry()
        registry.relate_tags("memory", "model", TagRelationship.USES)
        registry.relate_tags("memory", "agent", TagRelationship.DEPENDS_ON)

        # Act
        related = registry.get_related_tags("memory", TagRelationship.USES)

        # Assert
        assert "model" in related
        assert "agent" not in related
        assert TagRelationship.USES in related["model"]

    def test_get_related_tags_nonexistent(self):
        """Test get_related_tags with nonexistent tag."""
        # Arrange
        registry = TagRegistry()

        # Act & Assert
        with pytest.raises(ValueError):
            registry.get_related_tags("nonexistent")

    def test_find_tags(self):
        """Test find_tags."""
        # Arrange
        registry = TagRegistry()
        registry.create_tag("findable", TagCategory.MEMORY, description="This tag is findable")

        # Act
        results = registry.find_tags("findable")

        # Assert
        assert len(results) > 0
        assert any(tag.name == "findable" for tag in results)

    def test_find_tags_in_description(self):
        """Test find_tags in description."""
        # Arrange
        registry = TagRegistry()
        registry.create_tag("findable", TagCategory.MEMORY, description="This tag is searchable")

        # Act
        results = registry.find_tags("searchable")

        # Assert
        assert len(results) > 0
        assert any(tag.name == "findable" for tag in results)

    def test_find_tags_in_synonyms(self):
        """Test find_tags in synonyms."""
        # Arrange
        registry = TagRegistry()
        tag = registry.create_tag("findable", TagCategory.MEMORY)
        tag.synonyms = ["searchable"]

        # Act
        results = registry.find_tags("searchable")

        # Assert
        assert len(results) > 0
        assert any(tag.name == "findable" for tag in results)

    def test_find_tags_in_attributes(self):
        """Test find_tags in attributes."""
        # Arrange
        registry = TagRegistry()
        registry.create_tag("findable", TagCategory.MEMORY, attributes={"key": "searchable"})

        # Act
        results = registry.find_tags("searchable")

        # Assert
        assert len(results) > 0
        assert any(tag.name == "findable" for tag in results)

    def test_get_tag_hierarchy(self):
        """Test get_tag_hierarchy."""
        # Arrange
        registry = TagRegistry()

        # Act
        hierarchy = registry.get_tag_hierarchy("vector")

        # Assert
        assert hierarchy["name"] == "memory"
        assert "children" in hierarchy
        assert any(child["name"] == "vector" for child in hierarchy["children"])

    def test_get_tag_hierarchy_nonexistent(self):
        """Test get_tag_hierarchy with nonexistent tag."""
        # Arrange
        registry = TagRegistry()

        # Act & Assert
        with pytest.raises(ValueError):
            registry.get_tag_hierarchy("nonexistent")


def test_get_tag_registry():
    """Test get_tag_registry."""
    # Act
    registry1 = get_tag_registry()
    registry2 = get_tag_registry()

    # Assert
    assert registry1 is registry2  # Singleton


def test_get_tag():
    """Test get_tag."""
    # Act
    tag = get_tag("memory")

    # Assert
    assert tag is not None
    assert tag.name == "memory"


def test_create_tag():
    """Test create_tag."""
    # Act
    tag = create_tag("test_tag", TagCategory.MEMORY)

    # Assert
    assert tag is not None
    assert tag.name == "test_tag"
    assert tag.category == TagCategory.MEMORY


def test_get_or_create_tag():
    """Test get_or_create_tag."""
    # Act
    tag1 = get_or_create_tag("memory", TagCategory.MEMORY)
    tag2 = get_or_create_tag("test_tag2", TagCategory.MEMORY)

    # Assert
    assert tag1.name == "memory"
    assert tag2.name == "test_tag2"


def test_get_tags_by_category():
    """Test get_tags_by_category."""
    # Act
    tags = get_tags_by_category(TagCategory.MEMORY)

    # Assert
    assert len(tags) > 0
    assert all(tag.category == TagCategory.MEMORY for tag in tags)


def test_tag_decorator():
    """Test tag decorator."""
    # Arrange & Act
    @tag("test_tag")
    class TestClass:
        pass

    # Assert
    tags = get_tags(TestClass)
    assert len(tags) == 1
    assert tags[0].name == "test_tag"


def test_tag_decorator_with_attributes():
    """Test tag decorator with attributes."""
    # Arrange & Act
    @tag("test_tag", key="value")
    class TestClass:
        pass

    # Assert
    tags = get_tags(TestClass)
    assert len(tags) == 1
    assert tags[0].name == "test_tag"
    assert tags[0].get_attribute("key") == "value"


def test_tag_decorator_hierarchical():
    """Test tag decorator with hierarchical tag."""
    # Arrange & Act
    @tag("parent.child")
    class TestClass:
        pass

    # Assert
    tags = get_tags(TestClass)
    assert len(tags) == 1
    assert tags[0].name == "child"
    assert tags[0].parent is not None
    assert tags[0].parent.name == "parent"


def test_tag_decorator_multiple():
    """Test multiple tag decorators."""
    # Arrange & Act
    @tag("tag1")
    @tag("tag2")
    class TestClass:
        pass

    # Assert
    tags = get_tags(TestClass)
    assert len(tags) == 2
    assert any(tag.name == "tag1" for tag in tags)
    assert any(tag.name == "tag2" for tag in tags)


def test_get_tags_no_tags():
    """Test get_tags with no tags."""
    # Arrange
    class TestClass:
        pass

    # Act
    tags = get_tags(TestClass)

    # Assert
    assert len(tags) == 0


def test_relate_tags_function():
    """Test relate_tags function."""
    # Arrange
    tag1 = create_tag("test_tag1", TagCategory.MEMORY)
    tag2 = create_tag("test_tag2", TagCategory.MEMORY)

    # Act
    relate_tags("test_tag1", "test_tag2", TagRelationship.USES)

    # Assert
    related = get_related_tags("test_tag1")
    assert "test_tag2" in related
    assert TagRelationship.USES in related["test_tag2"]


def test_get_related_tags_function():
    """Test get_related_tags function."""
    # Arrange
    tag1 = create_tag("test_tag3", TagCategory.MEMORY)
    tag2 = create_tag("test_tag4", TagCategory.MEMORY)
    relate_tags("test_tag3", "test_tag4", TagRelationship.USES)

    # Act
    related = get_related_tags("test_tag3")

    # Assert
    assert "test_tag4" in related
    assert TagRelationship.USES in related["test_tag4"]


def test_find_tags_function():
    """Test find_tags function."""
    # Arrange
    tag = create_tag("findable_tag", TagCategory.MEMORY, description="This tag is findable")

    # Act
    results = find_tags("findable")

    # Assert
    assert len(results) > 0
    assert any(t.name == "findable_tag" for t in results)


def test_describe_tag_function():
    """Test describe_tag function."""
    # Arrange
    tag = create_tag("describable", TagCategory.MEMORY, description="This tag is describable")

    # Act
    description = describe_tag("describable")

    # Assert
    assert "Tag: describable" in description
    assert "Category: MEMORY" in description
    assert "Description: This tag is describable" in description
