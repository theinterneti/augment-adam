"""
Custom filters for the template engine.

This module provides custom filters for the template engine, including
filters for code generation, formatting, and transformation.
"""

from augment_adam.utils.templates.filters.code import (
    to_camel_case,
    to_snake_case,
    to_pascal_case,
    to_kebab_case,
    to_constant_case,
    indent,
    dedent,
    wrap,
    format_docstring,
    format_type_hint,
    format_imports,
)

from augment_adam.utils.templates.filters.text import (
    pluralize,
    singularize,
    capitalize,
    titleize,
    humanize,
    truncate,
    word_wrap,
    strip_html,
    markdown_to_html,
    html_to_markdown,
)

__all__ = [
    "to_camel_case",
    "to_snake_case",
    "to_pascal_case",
    "to_kebab_case",
    "to_constant_case",
    "indent",
    "dedent",
    "wrap",
    "format_docstring",
    "format_type_hint",
    "format_imports",
    "pluralize",
    "singularize",
    "capitalize",
    "titleize",
    "humanize",
    "truncate",
    "word_wrap",
    "strip_html",
    "markdown_to_html",
    "html_to_markdown",
]
