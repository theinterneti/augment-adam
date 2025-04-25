"""
Enhanced template engine with tagging support.

This module provides a powerful template engine with tagging support, template inheritance,
and custom filters for code generation. It extends the Jinja2 template engine with
additional features for AI-friendly code generation.

TODO(Issue #5): Add template versioning support
TODO(Issue #5): Implement template validation against a schema
TODO(Issue #5): Add template analytics to track usage and coverage
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