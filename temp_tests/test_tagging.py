"""
Unit tests for the tagging system.

This module contains tests for the tagging system, which is a core component
of the Augment Adam framework.
"""

import unittest
from unittest.mock import patch, MagicMock

import pytest
from src.augment_adam.utils.tagging.core import (
    Tag, TagCategory, get_tag, create_tag, get_or_create_tag, tag
)
from src.augment_adam.testing.utils.tag_utils import reset_tag_registry, safe_tag

class TestTagging(unittest.TestCase):
    """
    Tests for the tagging system.
    """
    
    def setUp(self):
        """Set up the test case."""
        # Reset the tag registry before each test
        reset_tag_registry()
    
    def test_create_tag(self):
        """Test creating a tag."""
        # Create a tag
        tag_obj = create_tag("test_tag", TagCategory.TEST)
        
        # Verify the tag was created
        self.assertEqual(tag_obj.name, "test_tag")
        self.assertEqual(tag_obj.category, TagCategory.TEST)
        self.assertIsNone(tag_obj.parent)
        
        # Verify we can retrieve the tag
        retrieved_tag = get_tag("test_tag")
        self.assertEqual(retrieved_tag, tag_obj)
    
    def test_get_or_create_tag(self):
        """Test get_or_create_tag function."""
        # Create a tag
        tag1 = get_or_create_tag("test_tag", TagCategory.TEST)
        
        # Get the same tag
        tag2 = get_or_create_tag("test_tag", TagCategory.TEST)
        
        # Verify they are the same object
        self.assertIs(tag1, tag2)
    
    def test_tag_decorator(self):
        """Test the tag decorator."""
        # Define a class with the tag decorator
        @tag("test.decorator")
        class TestClass:
            pass
        
        # Verify the tag was created and applied
        self.assertTrue(hasattr(TestClass, "__tags__"))
        self.assertEqual(len(TestClass.__tags__), 1)
        self.assertEqual(TestClass.__tags__[0].name, "decorator")
        
        # Verify the parent tag was created
        parent_tag = get_tag("test")
        self.assertIsNotNone(parent_tag)
        self.assertEqual(parent_tag.name, "test")
    
    def test_safe_tag_decorator(self):
        """Test the safe_tag decorator."""
        # Define a class with the safe_tag decorator
        @safe_tag("test.safe_decorator")
        class TestClass:
            pass
        
        # Define another class with the same tag
        @safe_tag("test.safe_decorator")
        class AnotherClass:
            pass
        
        # Verify both classes have the tag
        self.assertTrue(hasattr(TestClass, "__tags__"))
        self.assertTrue(hasattr(AnotherClass, "__tags__"))
        
        # Verify the tags are the same object
        self.assertIs(TestClass.__tags__[0], AnotherClass.__tags__[0])
    
    def test_hierarchical_tags(self):
        """Test hierarchical tags."""
        # Create a hierarchy of tags
        parent = create_tag("parent", TagCategory.TEST)
        child = create_tag("child", TagCategory.TEST, parent)
        grandchild = create_tag("grandchild", TagCategory.TEST, child)
        
        # Verify the hierarchy
        self.assertIn(child, parent.children)
        self.assertIn(grandchild, child.children)
        self.assertEqual(child.parent, parent)
        self.assertEqual(grandchild.parent, child)
        
if __name__ == "__main__":
    unittest.main()
