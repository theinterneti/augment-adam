# Template Engine

## Overview

The template engine is a core component of the Augment Adam framework that provides a way to generate code, tests, and documentation. It extends the Jinja2 template engine with additional features like tag management and template inheritance.

## Architecture

The template engine uses a layered approach:

1. **Jinja2 Engine**: Base template rendering engine
2. **Template Metadata**: Metadata for templates (tags, variables, description)
3. **Tag Integration**: Integration with the tagging system
4. **Template Inheritance**: Support for template inheritance
5. **Custom Filters**: Custom filters for template rendering

## Components

### TemplateEngine

The `TemplateEngine` class is the main entry point for the template engine. It provides methods for rendering templates, managing template metadata, and integrating with the tagging system.

```python
from augment_adam.utils.template_engine import TemplateEngine

# Create a template engine
engine = TemplateEngine()

# Render a template
result = engine.render_template("code/class_template.j2", context)
```

### Template Metadata

Templates can include metadata in the form of special comments:

```jinja
{# Template for generating code #}
{# @tags: code, class, python #}
{# @description: This template is used to generate Python classes #}
{# @variables: class_name:str, base_classes:list, attributes:list, methods:list #}
```

The metadata includes:

- **Tags**: Tags for categorizing the template
- **Description**: Description of the template
- **Variables**: Variables used in the template

### Tag Integration

The template engine integrates with the tagging system, allowing you to:

1. **Tag Templates**: Add tags to templates using the `@tags` metadata
2. **Filter Templates**: Filter templates by tag
3. **Generate Tagged Code**: Generate code with tags

```python
# Get all templates with the "code" tag
code_templates = engine.get_templates_by_tag("code")
```

### Template Inheritance

Templates can inherit from other templates using the Jinja2 inheritance mechanism:

```jinja
{% extends "base_template.j2" %}

{% block content %}
  <!-- Template content -->
{% endblock %}
```

### Custom Filters

The template engine provides several custom filters:

- **tojson**: Convert an object to JSON
- **to_camel_case**: Convert a string to camelCase
- **to_snake_case**: Convert a string to snake_case
- **to_pascal_case**: Convert a string to PascalCase
- **to_kebab_case**: Convert a string to kebab-case

```jinja
{{ variable|to_camel_case }}
```

## Template Types

The template engine supports several types of templates:

### Code Templates

Code templates are used to generate Python code:

- **class_template.j2**: Generate a Python class
- **module_template.j2**: Generate a Python module
- **function_template.j2**: Generate a Python function

### Test Templates

Test templates are used to generate test code:

- **unit_test_template.j2**: Generate a unit test
- **integration_test_template.j2**: Generate an integration test
- **e2e_test_template.j2**: Generate an end-to-end test

### Documentation Templates

Documentation templates are used to generate documentation:

- **module_doc_template.j2**: Generate module documentation
- **api_doc_template.j2**: Generate API documentation
- **guide_template.j2**: Generate a guide

### Memory Templates

Memory templates are used to generate memory-related code:

- **cypher_query.j2**: Generate a Cypher query
- **graph_visualization.j2**: Generate a graph visualization

## Usage

### Rendering a Template

```python
from augment_adam.utils.template_engine import render_template

# Render a template
result = render_template("code/class_template.j2", {
    "class_name": "MyClass",
    "base_classes": ["BaseClass"],
    "attributes": [
        {
            "name": "attribute1",
            "type": "str",
            "description": "Description of attribute1",
            "default": "default_value",
            "init": True
        }
    ],
    "methods": [
        {
            "name": "method1",
            "parameters": [
                {
                    "name": "param1",
                    "type": "str",
                    "description": "Description of param1",
                    "default": "default_value"
                }
            ],
            "docstring": {
                "summary": "Summary of method1",
                "description": "Description of method1",
                "returns": {
                    "type": "str",
                    "description": "Description of return value"
                }
            },
            "body": "return param1"
        }
    ],
    "imports": [
        "from typing import List, Dict, Optional"
    ],
    "module_docstring": {
        "summary": "Summary of module",
        "description": "Description of module"
    },
    "class_docstring": {
        "summary": "Summary of class",
        "description": "Description of class"
    }
})
```

### Generating a Docstring

```python
from augment_adam.utils.template_engine import get_docstring

# Generate a function docstring
docstring = get_docstring(
    docstring_type="function",
    summary="Summary of function",
    description="Description of function",
    parameters=[
        {
            "name": "param1",
            "type": "str",
            "description": "Description of param1"
        }
    ],
    returns={
        "type": "str",
        "description": "Description of return value"
    }
)
```

### Filtering Templates by Tag

```python
from augment_adam.utils.template_engine import get_template_engine

# Get the template engine
engine = get_template_engine()

# Get all templates with the "code" tag
code_templates = engine.get_templates_by_tag("code")
```

## Integration with Tagging System

The template engine is integrated with the tagging system, allowing you to:

1. **Tag Templates**: Add tags to templates using the `@tags` metadata
2. **Filter Templates**: Filter templates by tag
3. **Generate Tagged Code**: Generate code with tags

```python
from augment_adam.utils.template_engine import get_template_engine
from augment_adam.utils.tagging import get_tag

# Get the template engine
engine = get_template_engine()

# Get all templates with the "code" tag
code_templates = engine.get_templates_by_tag("code")

# Get a specific tag
memory_tag = get_tag("memory")

# Get all templates with the "memory" tag
memory_templates = engine.get_templates_by_tag("memory")
```

## Future Enhancements

Potential future enhancements:

- **Template Validation**: Validate templates against a schema
- **Template Versioning**: Version templates for backward compatibility
- **Template Repository**: Central repository for templates
- **Template Editor**: Visual editor for templates
- **Template Analytics**: Analyze template usage and coverage
