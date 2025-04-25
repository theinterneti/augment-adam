"""Tagging system for categorizing and organizing code for AI agent comprehension.

This module provides a tagging system optimized for AI agent understanding and reasoning.
It defines tag categories, hierarchies, relationships, and utilities for working with tags
in a way that facilitates AI comprehension of code structure, purpose, and relationships.
"""

from augment_adam.utils.tagging.core import (
    TagCategory,
    Tag,
    TagRegistry,
    TagRelationship,
    get_tag_registry,
    get_tag,
    create_tag,
    get_or_create_tag,
    get_tags_by_category,
    tag,
    get_tags,
    relate_tags,
    get_related_tags,
    find_tags,
    describe_tag,
)

__all__ = [
    "TagCategory",
    "Tag",
    "TagRegistry",
    "TagRelationship",
    "get_tag_registry",
    "get_tag",
    "create_tag",
    "get_or_create_tag",
    "get_tags_by_category",
    "tag",
    "get_tags",
    "relate_tags",
    "get_related_tags",
    "find_tags",
    "describe_tag",
]