"""
Core components of the template engine.

This module provides the core components of the template engine, including
the TemplateEngine class, Template class, and related utilities.
"""

from augment_adam.utils.templates.core.engine import (
    TemplateEngine,
    Template,
    TemplateMetadata,
    TemplateContext,
    get_template_engine,
    render_template,
    render_string_template,
    render_code_template,
    render_test_template,
    render_doc_template,
    get_docstring,
)

__all__ = [
    "TemplateEngine",
    "Template",
    "TemplateMetadata",
    "TemplateContext",
    "get_template_engine",
    "render_template",
    "render_string_template",
    "render_code_template",
    "render_test_template",
    "render_doc_template",
    "get_docstring",
]
