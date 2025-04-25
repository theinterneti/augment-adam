"""
Documentation System.

This module provides a comprehensive documentation system for the project,
including architecture documentation, API documentation, user guides, developer
guides, and examples.

TODO(Issue #12): Add interactive examples
TODO(Issue #12): Implement documentation versioning
TODO(Issue #12): Add documentation search
"""

from augment_adam.docs.generator import (
    DocGenerator,
    ModuleDocGenerator,
    ClassDocGenerator,
    FunctionDocGenerator,
)

from augment_adam.docs.builder import (
    DocBuilder,
    MarkdownBuilder,
    HtmlBuilder,
    WebsiteBuilder,
)

from augment_adam.docs.utils import (
    DocParser,
    DocFormatter,
    DocExtractor,
    DocValidator,
)

__all__ = [
    # Generator
    "DocGenerator",
    "ModuleDocGenerator",
    "ClassDocGenerator",
    "FunctionDocGenerator",

    # Builder
    "DocBuilder",
    "MarkdownBuilder",
    "HtmlBuilder",
    "WebsiteBuilder",

    # Utils
    "DocParser",
    "DocFormatter",
    "DocExtractor",
    "DocValidator",
]
