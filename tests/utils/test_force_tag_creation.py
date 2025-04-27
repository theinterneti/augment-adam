"""
Tests for the force parameter in the create_tag method.
"""

import pytest

from augment_adam.utils.tagging.core import (
    TagCategory,
    create_tag,
    get_tag,
    get_tags,
)
from augment_adam.testing.utils.tag_utils import (
    isolated_tag_registry,
    safe_tag,
)


def test_force_tag_creation():
    """Test that the force parameter allows creating a tag that already exists."""
    with isolated_tag_registry():
        # Create a tag
        tag1 = create_tag("test_tag", TagCategory.UTILITY)
        assert tag1.name == "test_tag"
        assert tag1.category == TagCategory.UTILITY

        # Try to create the same tag without force (should raise ValueError)
        with pytest.raises(ValueError):
            create_tag("test_tag", TagCategory.UTILITY)

        # Try to create the same tag with force (should return the existing tag)
        tag2 = create_tag("test_tag", TagCategory.UTILITY, force=True)
        assert tag2.name == "test_tag"
        assert tag2.category == TagCategory.UTILITY
        assert tag1 is tag2  # Should be the same object


def test_force_tag_creation_with_different_category():
    """Test that the force parameter returns the existing tag even with different category."""
    with isolated_tag_registry():
        # Create a tag
        tag1 = create_tag("test_tag", TagCategory.UTILITY)
        assert tag1.name == "test_tag"
        assert tag1.category == TagCategory.UTILITY

        # Try to create the same tag with a different category and force=True
        tag2 = create_tag("test_tag", TagCategory.MODEL, force=True)
        assert tag2.name == "test_tag"
        # The category should still be the original one
        assert tag2.category == TagCategory.UTILITY
        assert tag1 is tag2  # Should be the same object


def test_force_tag_creation_with_parent():
    """Test that the force parameter works with parent tags."""
    with isolated_tag_registry():
        # Create parent tag
        parent = create_tag("parent", TagCategory.UTILITY)

        # Create child tag
        child = create_tag("child", TagCategory.UTILITY, parent=parent)

        # Try to create the same child tag without force
        with pytest.raises(ValueError):
            create_tag("child", TagCategory.UTILITY, parent=parent)

        # Try to create the same child tag with force
        child2 = create_tag("child", TagCategory.UTILITY, parent=parent, force=True)
        assert child2.name == "child"
        assert child2.parent is parent
        assert child is child2  # Should be the same object


def test_hierarchical_force_tag_creation():
    """Test that the force parameter works with hierarchical tag paths."""
    with isolated_tag_registry():
        # Create a tag with a dot in the name (not a hierarchical tag)
        tag1 = create_tag("parent.child.grandchild", TagCategory.UTILITY)

        # Try to create the same tag without force
        with pytest.raises(ValueError):
            create_tag("parent.child.grandchild", TagCategory.UTILITY)

        # Try to create the same tag with force
        tag2 = create_tag("parent.child.grandchild", TagCategory.UTILITY, force=True)

        # When using create_tag directly, it creates a single tag with the full name
        assert tag2.name == "parent.child.grandchild"
        assert tag1 is tag2  # Should be the same object

        # The tag should not have a parent since it's not a true hierarchical tag
        assert tag1.parent is None

        # Verify that we can retrieve the tag by its full name
        retrieved_tag = get_tag("parent.child.grandchild")
        assert retrieved_tag is not None
        assert retrieved_tag is tag1


def test_safe_tag_decorator():
    """Test that the safe_tag decorator works with hierarchical tags."""
    with isolated_tag_registry():
        # Define a class with the safe_tag decorator
        @safe_tag("parent.child.grandchild")
        class TestClass:
            pass

        # Verify that the hierarchical tags were created
        parent_tag = get_tag("parent")
        assert parent_tag is not None
        assert parent_tag.name == "parent"
        assert parent_tag.parent is None

        # Get the child tag by its name, not its full path
        child_tag = None
        for child in parent_tag.children:
            if child.name == "child":
                child_tag = child
                break

        assert child_tag is not None
        assert child_tag.name == "child"
        assert child_tag.parent is parent_tag

        # Get the grandchild tag by its name, not its full path
        grandchild_tag = None
        for child in child_tag.children:
            if child.name == "grandchild":
                grandchild_tag = child
                break

        assert grandchild_tag is not None
        assert grandchild_tag.name == "grandchild"
        assert grandchild_tag.parent is child_tag

        # Verify that the class has the tags attribute
        assert hasattr(TestClass, "__tags__")
        assert len(TestClass.__tags__) == 1
        assert TestClass.__tags__[0] is grandchild_tag

        # Define another class with the same tag
        @safe_tag("parent.child.grandchild")
        class AnotherTestClass:
            pass

        # Verify that the second class has the same tag
        assert hasattr(AnotherTestClass, "__tags__")
        assert len(AnotherTestClass.__tags__) == 1
        assert AnotherTestClass.__tags__[0] is grandchild_tag

        # Verify the full paths
        assert parent_tag.get_full_path() == "parent"
        assert child_tag.get_full_path() == "parent.child"
        assert grandchild_tag.get_full_path() == "parent.child.grandchild"
