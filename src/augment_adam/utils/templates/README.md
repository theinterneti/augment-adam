# Enhanced Template Engine

## Overview

This module provides a powerful template engine with tagging support, template inheritance, and custom filters for code generation. It extends the Jinja2 template engine with additional features for AI-friendly code generation.

## Components

### Template

The `Template` class represents a template in the template engine, including its content, metadata, and rendering capabilities. Templates can have metadata like tags, description, variables, and examples.

### TemplateMetadata

The `TemplateMetadata` class represents the metadata for a template, including tags, description, variables, and other metadata extracted from template comments.

### TemplateContext

The `TemplateContext` class represents the context for rendering a template, including variables, filters, and other context information.

### TemplateEngine

The `TemplateEngine` class extends the Jinja2 template engine with additional features like tag management and template inheritance. It provides methods for rendering templates with tags and managing template metadata.

## Loaders

The template engine supports multiple loaders for loading templates from various sources:

- **FileSystemLoader**: Loads templates from the filesystem
- **PackageLoader**: Loads templates from Python packages
- **MemoryLoader**: Loads templates from memory

## Renderers

The template engine provides renderers for rendering templates to various formats:

- **CodeRenderer**: Renders templates to code (Python, JavaScript, HTML, CSS, SQL, YAML, JSON)
- **DocRenderer**: Renders templates to documentation (Markdown, reStructuredText, HTML)
- **TestRenderer**: Renders templates to tests (unit tests, integration tests, end-to-end tests)

## Filters

The template engine provides custom filters for code generation and text transformation:

### Code Filters

- **to_camel_case**: Convert a string to camelCase
- **to_snake_case**: Convert a string to snake_case
- **to_pascal_case**: Convert a string to PascalCase
- **to_kebab_case**: Convert a string to kebab-case
- **to_constant_case**: Convert a string to CONSTANT_CASE
- **indent**: Indent a string by a specified amount
- **dedent**: Dedent a string, removing common leading whitespace
- **wrap**: Wrap a string to a specified width
- **format_docstring**: Format a docstring according to a specified style
- **format_type_hint**: Format a type hint for Python code
- **format_imports**: Format a list of imports according to best practices

### Text Filters

- **pluralize**: Convert a singular word to its plural form
- **singularize**: Convert a plural word to its singular form
- **capitalize**: Capitalize the first letter of a string
- **titleize**: Capitalize the first letter of each word in a string
- **humanize**: Convert a string to a human-readable format
- **truncate**: Truncate a string to a specified length
- **word_wrap**: Wrap a string to a specified width, preserving paragraphs
- **strip_html**: Remove HTML tags from a string
- **markdown_to_html**: Convert Markdown to HTML
- **html_to_markdown**: Convert HTML to Markdown

## Usage

### Creating a Template

Templates can be created from strings or files:

```python
from augment_adam.utils.templates import Template

# Create a template from a string
template = Template(
    name="hello",
    path="hello.j2",
    content="Hello, {{ name }}!"
)

# Create a template from a file
template = Template.from_file("path/to/template.j2")
```

### Rendering a Template

Templates can be rendered with a context:

```python
from augment_adam.utils.templates import render_template, TemplateContext

# Create a context
context = TemplateContext()
context.add_variable("name", "World")

# Render a template
result = render_template("hello.j2", context)
```

### Using the Template Engine

The template engine provides methods for rendering templates:

```python
from augment_adam.utils.templates import get_template_engine

# Get the template engine
engine = get_template_engine()

# Render a template
result = engine.render_template("hello.j2", {"name": "World"})
```

### Using Renderers

Renderers provide methods for rendering templates to specific formats:

```python
from augment_adam.utils.templates.renderers import CodeRenderer

# Create a code renderer
renderer = CodeRenderer()

# Render a Python class
result = renderer.render_class({
    "class_name": "MyClass",
    "attributes": [
        {"name": "name", "type": "str", "default": "''"},
        {"name": "age", "type": "int", "default": "0"}
    ],
    "methods": [
        {
            "name": "greet",
            "args": [{"name": "self"}],
            "return_type": "str",
            "body": "return f'Hello, {self.name}!'"
        }
    ]
})
```

## Template Metadata

Templates can have metadata in the form of comments:

```jinja
{# @tags: code, class, python #}
{# @description: This template is used to generate Python classes #}
{# @variables: class_name:str, attributes:list, methods:list #}
{# @author: John Doe #}
{# @version: 1.0.0 #}
{# @examples: class_name="MyClass", attributes=[{"name": "name", "type": "str"}] #}
{# @related_templates: function.py.j2, module.py.j2 #}

class {{ class_name }}:
    """{{ description }}"""
    
    {% for attribute in attributes %}
    {{ attribute.name }}: {{ attribute.type }}{% if attribute.default %} = {{ attribute.default }}{% endif %}
    {% endfor %}
    
    {% for method in methods %}
    def {{ method.name }}({% for arg in method.args %}{{ arg.name }}{% if not loop.last %}, {% endif %}{% endfor %}){% if method.return_type %} -> {{ method.return_type }}{% endif %}:
        {{ method.body | indent(8) }}
    {% endfor %}
```

## TODOs

- Add template versioning support (Issue #5)
- Implement template validation against a schema (Issue #5)
- Add template analytics to track usage and coverage (Issue #5)
- Add support for template inheritance (Issue #5)
- Add support for template includes (Issue #5)
- Add support for template macros (Issue #5)
- Add support for template versioning (Issue #5)
- Add support for template validation (Issue #5)
- Add support for template analytics (Issue #5)
- Add support for code formatting (Issue #5)
- Add support for code validation (Issue #5)
- Add support for documentation validation (Issue #5)
- Add support for documentation formatting (Issue #5)
- Add support for test validation (Issue #5)
- Add support for test formatting (Issue #5)
