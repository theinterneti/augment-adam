# Template Engine API

This document provides a reference for the Template Engine API in Augment Adam.

## Core Classes

### TemplateEngine

The `TemplateEngine` class is the main entry point for the template engine.

```python
from augment_adam.utils.templates import TemplateEngine, get_template_engine

# Get the singleton template engine instance
engine = get_template_engine()

# Or create a new template engine
custom_engine = TemplateEngine()
```

#### Methods

| Method | Description |
| ------ | ----------- |
| `render_template(template_name, context)` | Render a template with the given context |
| `render_string_template(template_string, context)` | Render a template string with the given context |
| `render_code_template(template_name, context)` | Render a code template with the given context |
| `render_test_template(template_name, context)` | Render a test template with the given context |
| `render_doc_template(template_name, context)` | Render a documentation template with the given context |
| `get_template(template_name)` | Get a template by name |
| `get_templates_by_tag(tag)` | Get templates by tag |
| `get_templates_by_tag_category(category)` | Get templates by tag category |
| `get_templates_by_relationship(template_name, relationship)` | Get templates by relationship |
| `search_templates(query)` | Search for templates by keyword |
| `search_templates_by_description(query)` | Search for templates by description |
| `search_templates_by_example(example)` | Search for templates by example |
| `get_similar_templates(template_name)` | Get similar templates |
| `get_template_usage_stats(template_name)` | Get template usage statistics |
| `get_most_used_templates(limit)` | Get most used templates |
| `get_template_performance_metrics(template_name)` | Get template performance metrics |
| `get_template_recommendations(query)` | Get template recommendations based on context |
| `reload_templates()` | Reload all templates from the templates directory |
| `add_filter(name, filter_func)` | Add a custom filter to the template engine |

### Template

The `Template` class represents a template in the system.

```python
from augment_adam.utils.templates import Template

# Create a template from a string
template = Template(
    name="hello.j2",
    content="Hello, {{ name }}!",
    metadata=metadata
)

# Create a template from a file
template = Template.from_file("path/to/template.j2")
```

#### Methods

| Method | Description |
| ------ | ----------- |
| `render(context)` | Render the template with the given context |
| `get_metadata()` | Get the template metadata |
| `get_content()` | Get the template content |
| `get_name()` | Get the template name |
| `get_path()` | Get the template path |
| `from_file(path)` | Create a template from a file |
| `from_string(name, content, metadata)` | Create a template from a string |

### TemplateMetadata

The `TemplateMetadata` class represents the metadata for a template.

```python
from augment_adam.utils.templates import TemplateMetadata

# Create template metadata
metadata = TemplateMetadata(
    tags=["code", "python", "class"],
    description="Template for generating Python classes",
    variables={
        "class_name": {"type": "str", "description": "Name of the class"},
        "base_classes": {"type": "list", "description": "List of base classes"}
    },
    examples=[
        {"class_name": "MyClass", "base_classes": ["BaseClass"]}
    ],
    author="John Doe",
    version="1.0.0"
)
```

#### Properties

| Property | Description |
| -------- | ----------- |
| `tags` | Tags for the template |
| `description` | Description of the template |
| `variables` | Variables used in the template |
| `examples` | Example usages of the template |
| `author` | Author of the template |
| `version` | Version of the template |
| `created_at` | Creation timestamp |
| `updated_at` | Update timestamp |

### TemplateContext

The `TemplateContext` class represents the context for rendering a template.

```python
from augment_adam.utils.templates import TemplateContext

# Create a context
context = TemplateContext()
context.add_variable("name", "World")
context.add_filter("custom_filter", lambda x: x.upper())
```

#### Methods

| Method | Description |
| ------ | ----------- |
| `add_variable(name, value)` | Add a variable to the context |
| `get_variable(name)` | Get a variable from the context |
| `add_filter(name, filter_func)` | Add a filter to the context |
| `get_filter(name)` | Get a filter from the context |
| `to_dict()` | Convert the context to a dictionary |

## Loaders

### FileSystemLoader

The `FileSystemLoader` loads templates from the filesystem.

```python
from augment_adam.utils.templates.loaders import FileSystemLoader

# Create a loader
loader = FileSystemLoader("/path/to/templates")

# Load a template
template = loader.load_template("hello.j2")

# Load all templates
templates = loader.load_templates()
```

#### Methods

| Method | Description |
| ------ | ----------- |
| `load_template(template_path)` | Load a template from the filesystem |
| `load_templates(pattern)` | Load all templates matching a pattern from the templates directory |

### PackageLoader

The `PackageLoader` loads templates from Python packages.

```python
from augment_adam.utils.templates.loaders import PackageLoader

# Create a loader
loader = PackageLoader("augment_adam.templates")

# Load a template
template = loader.load_template("hello.j2")

# Load all templates
templates = loader.load_templates()
```

#### Methods

| Method | Description |
| ------ | ----------- |
| `load_template(template_name)` | Load a template from the package |
| `load_templates(pattern)` | Load all templates matching a pattern from the package |

### MemoryLoader

The `MemoryLoader` loads templates from memory.

```python
from augment_adam.utils.templates.loaders import MemoryLoader

# Create a loader
loader = MemoryLoader()

# Add a template
loader.add_template("hello.j2", "Hello, {{ name }}!")

# Load a template
template = loader.load_template("hello.j2")

# Load all templates
templates = loader.load_templates()
```

#### Methods

| Method | Description |
| ------ | ----------- |
| `add_template(name, content, metadata)` | Add a template to memory |
| `load_template(name)` | Load a template from memory |
| `load_templates()` | Load all templates from memory |

## Renderers

### CodeRenderer

The `CodeRenderer` renders templates to code.

```python
from augment_adam.utils.templates.renderers import CodeRenderer

# Create a renderer
renderer = CodeRenderer()

# Render a Python template
python_code = renderer.render_python("class_template.j2", context)

# Render a JavaScript template
js_code = renderer.render_javascript("function_template.j2", context)
```

#### Methods

| Method | Description |
| ------ | ----------- |
| `render_python(template_name, context)` | Render a template to Python code |
| `render_javascript(template_name, context)` | Render a template to JavaScript code |
| `render_html(template_name, context)` | Render a template to HTML code |
| `render_css(template_name, context)` | Render a template to CSS code |
| `render_sql(template_name, context)` | Render a template to SQL code |
| `render_yaml(template_name, context)` | Render a template to YAML code |
| `render_json(template_name, context)` | Render a template to JSON code |

### DocRenderer

The `DocRenderer` renders templates to documentation.

```python
from augment_adam.utils.templates.renderers import DocRenderer

# Create a renderer
renderer = DocRenderer()

# Render a Markdown template
markdown_doc = renderer.render_markdown("api_doc_template.j2", context)

# Render a reStructuredText template
rst_doc = renderer.render_rst("sphinx_doc_template.j2", context)
```

#### Methods

| Method | Description |
| ------ | ----------- |
| `render_markdown(template_name, context)` | Render a template to Markdown documentation |
| `render_rst(template_name, context)` | Render a template to reStructuredText documentation |
| `render_html(template_name, context)` | Render a template to HTML documentation |

### TestRenderer

The `TestRenderer` renders templates to tests.

```python
from augment_adam.utils.templates.renderers import TestRenderer

# Create a renderer
renderer = TestRenderer()

# Render a unit test template
unit_test = renderer.render_unit_test("test_template.j2", context)

# Render an integration test template
integration_test = renderer.render_integration_test("test_template.j2", context)
```

#### Methods

| Method | Description |
| ------ | ----------- |
| `render_unit_test(template_name, context)` | Render a template to a unit test |
| `render_integration_test(template_name, context)` | Render a template to an integration test |
| `render_e2e_test(template_name, context)` | Render a template to an end-to-end test |

## Filters

### Code Filters

The template engine provides several code filters:

| Filter | Description |
| ------ | ----------- |
| `to_camel_case(s)` | Convert a string to camelCase |
| `to_snake_case(s)` | Convert a string to snake_case |
| `to_pascal_case(s)` | Convert a string to PascalCase |
| `to_kebab_case(s)` | Convert a string to kebab-case |
| `to_constant_case(s)` | Convert a string to CONSTANT_CASE |
| `indent(s, width)` | Indent a string by a specified number of spaces |
| `dedent(s)` | Remove common leading whitespace from a string |
| `wrap(s, width)` | Wrap a string to a specified width |
| `format_docstring(s, style)` | Format a docstring according to a specified style |
| `format_type_hint(s)` | Format a type hint |
| `format_imports(s)` | Format import statements |

### Text Filters

The template engine provides several text filters:

| Filter | Description |
| ------ | ----------- |
| `pluralize(s)` | Convert a singular word to its plural form |
| `singularize(s)` | Convert a plural word to its singular form |
| `capitalize(s)` | Capitalize the first letter of a string |
| `titleize(s)` | Capitalize the first letter of each word in a string |
| `humanize(s)` | Convert a string to a human-readable format |
| `truncate(s, length)` | Truncate a string to a specified length |
| `word_wrap(s, width)` | Wrap a string to a specified width by words |
| `strip_html(s)` | Remove HTML tags from a string |
| `markdown_to_html(s)` | Convert Markdown to HTML |
| `html_to_markdown(s)` | Convert HTML to Markdown |

## Utility Functions

### Template Rendering

```python
from augment_adam.utils.templates import render_template, render_string_template

# Render a template
result = render_template("hello.j2", {"name": "World"})

# Render a template string
result = render_string_template("Hello, {{ name }}!", {"name": "World"})
```

### Specialized Rendering

```python
from augment_adam.utils.templates import render_code_template, render_test_template, render_doc_template

# Render a code template
code = render_code_template("class_template.j2", context)

# Render a test template
test = render_test_template("unit_test_template.j2", context)

# Render a documentation template
doc = render_doc_template("api_doc_template.j2", context)
```

### Docstring Generation

```python
from augment_adam.utils.templates import get_docstring

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
    },
    style="google"  # or "numpy", "sphinx", etc.
)
```

## Examples

### Basic Template Rendering

```python
from augment_adam.utils.templates import render_template

# Render a simple template
result = render_template("hello.j2", {"name": "World"})
print(result)  # Output: Hello, World!
```

### Rendering with TemplateContext

```python
from augment_adam.utils.templates import render_template, TemplateContext

# Create a context
context = TemplateContext()
context.add_variable("name", "World")
context.add_filter("custom_filter", lambda x: x.upper())

# Render a template with the context
result = render_template("hello.j2", context)
print(result)  # Output: Hello, World!
```

### Generating a Python Class

```python
from augment_adam.utils.templates import render_code_template

# Generate a Python class
code = render_code_template("code/python/class_template.j2", {
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

### Generating Documentation

```python
from augment_adam.utils.templates import render_doc_template

# Generate API documentation
doc = render_doc_template("api_doc_template.j2", {
    "module_name": "augment_adam.utils.templates",
    "classes": [
        {
            "name": "TemplateEngine",
            "description": "Enhanced template engine with tagging support",
            "methods": [
                {
                    "name": "render_template",
                    "description": "Render a template with the given context"
                }
            ]
        }
    ]
})
```

### Generating Tests

```python
from augment_adam.utils.templates import render_test_template

# Generate a unit test
test = render_test_template("unit_test_template.j2", {
    "module_name": "augment_adam.utils.templates",
    "class_name": "TemplateEngine",
    "method_name": "render_template",
    "test_cases": [
        {
            "name": "test_render_template_with_valid_input",
            "input": {
                "template_name": "hello.j2",
                "context": {"name": "World"}
            },
            "expected": "Hello, World!"
        }
    ]
})
```
