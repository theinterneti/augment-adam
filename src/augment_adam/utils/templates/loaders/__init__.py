"""
Template loaders for the template engine.

This module provides loaders for loading templates from various sources,
including the filesystem, packages, and databases.
"""

from augment_adam.utils.templates.loaders.filesystem import FileSystemLoader
from augment_adam.utils.templates.loaders.package import PackageLoader
from augment_adam.utils.templates.loaders.memory import MemoryLoader

__all__ = [
    "FileSystemLoader",
    "PackageLoader",
    "MemoryLoader",
]
