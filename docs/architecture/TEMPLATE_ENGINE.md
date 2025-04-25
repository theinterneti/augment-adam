# Template Engine

## Overview

The template engine is a core component of the Augment Adam framework that provides a sophisticated system for generating code, tests, and documentation. It extends the Jinja2 template engine with additional features like tag management, template inheritance, and custom filters optimized for AI-friendly code generation.

## Architecture

The template engine uses a layered approach:

1. **Jinja2 Engine**: Base template rendering engine
2. **Template Metadata**: Rich metadata for templates (tags, variables, description, examples)
3. **Tag Integration**: Deep integration with the tagging system
4. **Template Inheritance**: Enhanced support for template inheritance
5. **Custom Filters**: Extensive custom filters for code and text transformation
6. **Loaders**: Multiple loaders for different template sources
7. **Renderers**: Specialized renderers for different output formats

## Components

### TemplateEngine

The `TemplateEngine` class is the main entry point for the template engine. It provides methods for rendering templates, managing template metadata, and integrating with the tagging system.

```python
from augment_adam.utils.templates import TemplateEngine, get_template_engine

# Get the singleton template engine instance
engine = get_template_engine()

# Or create a new template engine
custom_engine = TemplateEngine()

# Render a template
result = engine.render_template("code/python/class_template.j2", context)
```

### Template and TemplateMetadata

The `Template` class represents a template in the system, including its content, metadata, and rendering capabilities. The `TemplateMetadata` class holds rich metadata about the template.

Templates can include metadata in the form of special comments:

```jinja
{# Template for generating code #}
{# @tags: code, class, python #}
{# @description: This template is used to generate Python classes #}
{# @variables: class_name:str, base_classes:list, attributes:list, methods:list #}
{# @examples: [{"class_name": "MyClass", "base_classes": ["BaseClass"]}] #}
{# @author: John Doe #}
{# @version: 1.0.0 #}
{# @created: 2025-04-25 #}
{# @updated: 2025-04-26 #}
```

The metadata includes:

- **Tags**: Tags for categorizing the template
- **Description**: Detailed description of the template
- **Variables**: Variables used in the template with type hints
- **Examples**: Example usages of the template
- **Author**: Author of the template
- **Version**: Version of the template
- **Created/Updated**: Creation and update timestamps

### TemplateContext

The `TemplateContext` class provides a rich context for rendering templates, including variables, filters, and other context information.

```python
from augment_adam.utils.templates import TemplateContext

# Create a context
context = TemplateContext()
context.add_variable("name", "World")
context.add_filter("custom_filter", lambda x: x.upper())

# Render a template with the context
result = render_template("hello.j2", context)
```

### Tag Integration

The template engine deeply integrates with the tagging system, allowing you to:

1. **Tag Templates**: Add tags to templates using the `@tags` metadata
2. **Filter Templates**: Filter templates by tag, category, or relationship
3. **Generate Tagged Code**: Generate code with semantic tags
4. **Discover Templates**: Find templates based on semantic relationships

```python
# Get all templates with the "code" tag
code_templates = engine.get_templates_by_tag("code")

# Get templates related to memory
memory_templates = engine.get_templates_by_tag_category(TagCategory.MEMORY)

# Find templates that implement a specific interface
implementation_templates = engine.get_templates_by_relationship(
    "interface_template", TagRelationship.IMPLEMENTS
)
```

### Template Inheritance

Templates can inherit from other templates using the Jinja2 inheritance mechanism with enhanced capabilities:

```jinja
{% extends "base_template.j2" %}

{% block content %}
  <!-- Template content -->
{% endblock %}

{% block imports %}
  {{ super() }}
  from typing import List, Dict, Optional
{% endblock %}
```

### Loaders

The template engine supports multiple loaders for loading templates from various sources:

- **FileSystemLoader**: Loads templates from the filesystem
- **PackageLoader**: Loads templates from Python packages
- **MemoryLoader**: Loads templates from memory

```python
from augment_adam.utils.templates.loaders import FileSystemLoader

# Create a loader
loader = FileSystemLoader("/path/to/templates")

# Load a template
template = loader.load_template("hello.j2")

# Load all templates
templates = loader.load_templates()
```

### Renderers

The template engine provides specialized renderers for different output formats:

- **CodeRenderer**: Renders templates to code (Python, JavaScript, HTML, CSS, SQL, YAML, JSON)
- **DocRenderer**: Renders templates to documentation (Markdown, reStructuredText, HTML)
- **TestRenderer**: Renders templates to tests (unit tests, integration tests, end-to-end tests)

```python
from augment_adam.utils.templates.renderers import CodeRenderer

# Create a renderer
renderer = CodeRenderer()

# Render a Python template
python_code = renderer.render_python("class_template.j2", context)

# Render a JavaScript template
js_code = renderer.render_javascript("function_template.j2", context)
```

### Custom Filters

The template engine provides extensive custom filters for code and text transformation:

#### Code Filters

- **to_camel_case**: Convert a string to camelCase
- **to_snake_case**: Convert a string to snake_case
- **to_pascal_case**: Convert a string to PascalCase
- **to_kebab_case**: Convert a string to kebab-case
- **to_constant_case**: Convert a string to CONSTANT_CASE
- **indent**: Indent a string by a specified number of spaces
- **dedent**: Remove common leading whitespace from a string
- **wrap**: Wrap a string to a specified width
- **format_docstring**: Format a docstring according to a specified style
- **format_type_hint**: Format a type hint
- **format_imports**: Format import statements

#### Text Filters

- **pluralize**: Convert a singular word to its plural form
- **singularize**: Convert a plural word to its singular form
- **capitalize**: Capitalize the first letter of a string
- **titleize**: Capitalize the first letter of each word in a string
- **humanize**: Convert a string to a human-readable format
- **truncate**: Truncate a string to a specified length
- **word_wrap**: Wrap a string to a specified width by words
- **strip_html**: Remove HTML tags from a string
- **markdown_to_html**: Convert Markdown to HTML
- **html_to_markdown**: Convert HTML to Markdown

```jinja
{{ variable|to_camel_case }}
{{ variable|indent(4) }}
{{ variable|format_docstring("google") }}
{{ variable|pluralize }}
{{ variable|markdown_to_html }}
```

## Template Types

The template engine supports a comprehensive set of template types organized by purpose:

### Code Templates

Code templates are used to generate code in various languages:

#### Python Templates

- **class_template.j2**: Generate a Python class
- **module_template.j2**: Generate a Python module
- **function_template.j2**: Generate a Python function
- **dataclass_template.j2**: Generate a Python dataclass
- **enum_template.j2**: Generate a Python enum
- **protocol_template.j2**: Generate a Python protocol
- **type_template.j2**: Generate a Python type definition

#### JavaScript Templates

- **class_template.js.j2**: Generate a JavaScript class
- **module_template.js.j2**: Generate a JavaScript module
- **function_template.js.j2**: Generate a JavaScript function
- **react_component.js.j2**: Generate a React component

#### SQL Templates

- **table_template.sql.j2**: Generate a SQL table definition
- **query_template.sql.j2**: Generate a SQL query
- **index_template.sql.j2**: Generate a SQL index
- **view_template.sql.j2**: Generate a SQL view

#### YAML/JSON Templates

- **config_template.yaml.j2**: Generate a YAML configuration
- **schema_template.json.j2**: Generate a JSON schema
- **api_spec_template.yaml.j2**: Generate an OpenAPI specification

### Test Templates

Test templates are used to generate test code for different testing frameworks:

#### Python Test Templates

- **unit_test_template.j2**: Generate a Python unit test
- **integration_test_template.j2**: Generate a Python integration test
- **e2e_test_template.j2**: Generate a Python end-to-end test
- **pytest_fixture_template.j2**: Generate a pytest fixture
- **pytest_parametrize_template.j2**: Generate a pytest parametrized test
- **mock_template.j2**: Generate a mock object

#### JavaScript Test Templates

- **jest_test_template.js.j2**: Generate a Jest test
- **mocha_test_template.js.j2**: Generate a Mocha test

### Documentation Templates

Documentation templates are used to generate documentation in various formats:

#### Markdown Templates

- **module_doc_template.md.j2**: Generate module documentation
- **api_doc_template.md.j2**: Generate API documentation
- **guide_template.md.j2**: Generate a user guide
- **readme_template.md.j2**: Generate a README file
- **changelog_template.md.j2**: Generate a changelog

#### reStructuredText Templates

- **sphinx_doc_template.rst.j2**: Generate Sphinx documentation
- **api_doc_template.rst.j2**: Generate API documentation for Sphinx

#### HTML Templates

- **api_doc_template.html.j2**: Generate HTML API documentation
- **guide_template.html.j2**: Generate an HTML user guide

### Memory Templates

Memory templates are used to generate memory-related code:

- **vector_query_template.j2**: Generate a vector database query
- **cypher_query_template.j2**: Generate a Cypher query for Neo4j
- **graph_visualization_template.j2**: Generate a graph visualization
- **memory_schema_template.j2**: Generate a memory schema
- **embedding_template.j2**: Generate embedding code

### Agent Templates

Agent templates are used to generate agent-related code:

- **agent_template.j2**: Generate an agent class
- **tool_template.j2**: Generate a tool class
- **prompt_template.j2**: Generate a prompt template
- **workflow_template.j2**: Generate a workflow
- **coordination_template.j2**: Generate coordination code

## Usage

### Rendering a Template

```python
from augment_adam.utils.templates import render_template, TemplateContext

# Create a context
context = TemplateContext()
context.add_variable("class_name", "MyClass")
context.add_variable("base_classes", ["BaseClass"])
context.add_variable("attributes", [
    {
        "name": "attribute1",
        "type": "str",
        "description": "Description of attribute1",
        "default": "default_value",
        "init": True
    }
])
context.add_variable("methods", [
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
])
context.add_variable("imports", [
    "from typing import List, Dict, Optional"
])
context.add_variable("module_docstring", {
    "summary": "Summary of module",
    "description": "Description of module"
})
context.add_variable("class_docstring", {
    "summary": "Summary of class",
    "description": "Description of class"
})

# Render a template
result = render_template("code/python/class_template.j2", context)

# Or use a dictionary context
result = render_template("code/python/class_template.j2", {
    "class_name": "MyClass",
    "base_classes": ["BaseClass"],
    # ... other variables
})
```

### Using Specialized Renderers

```python
from augment_adam.utils.templates.renderers import CodeRenderer, DocRenderer, TestRenderer

# Create renderers
code_renderer = CodeRenderer()
doc_renderer = DocRenderer()
test_renderer = TestRenderer()

# Render code
python_code = code_renderer.render_python("class_template.j2", context)
js_code = code_renderer.render_javascript("function_template.j2", context)
sql_code = code_renderer.render_sql("query_template.j2", context)

# Render documentation
markdown_doc = doc_renderer.render_markdown("api_doc_template.j2", context)
rst_doc = doc_renderer.render_rst("sphinx_doc_template.j2", context)
html_doc = doc_renderer.render_html("guide_template.j2", context)

# Render tests
unit_test = test_renderer.render_unit_test("test_template.j2", context)
integration_test = test_renderer.render_integration_test("test_template.j2", context)
e2e_test = test_renderer.render_e2e_test("test_template.j2", context)
```

### Generating a Docstring

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

### Working with Template Metadata

```python
from augment_adam.utils.templates import Template, TemplateMetadata

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

# Create a template with metadata
template = Template(
    name="class_template.j2",
    content="class {{ class_name }}({% for base in base_classes %}{{ base }}{% if not loop.last %}, {% endif %}{% endfor %}):\n    pass",
    metadata=metadata
)

# Get template metadata
metadata = template.metadata
print(f"Template tags: {metadata.tags}")
print(f"Template description: {metadata.description}")
print(f"Template variables: {metadata.variables}")
```

### Filtering and Discovering Templates

```python
from augment_adam.utils.templates import get_template_engine
from augment_adam.utils.tagging import TagCategory, TagRelationship

# Get the template engine
engine = get_template_engine()

# Get all templates with the "code" tag
code_templates = engine.get_templates_by_tag("code")

# Get templates by tag category
memory_templates = engine.get_templates_by_tag_category(TagCategory.MEMORY)

# Get templates by tag relationship
implementation_templates = engine.get_templates_by_relationship(
    "interface_template", TagRelationship.IMPLEMENTS
)

# Search for templates
search_results = engine.search_templates("python class")
```

## Integration with Tagging System

The template engine is deeply integrated with the tagging system, allowing for sophisticated template discovery, categorization, and relationship management:

1. **Tag Templates**: Add tags to templates using the `@tags` metadata
2. **Filter Templates**: Filter templates by tag, category, or relationship
3. **Generate Tagged Code**: Generate code with semantic tags
4. **Discover Templates**: Find templates based on semantic relationships
5. **Template Recommendations**: Get template recommendations based on context

```python
from augment_adam.utils.templates import get_template_engine
from augment_adam.utils.tagging import get_tag, TagCategory, TagRelationship

# Get the template engine
engine = get_template_engine()

# Get all templates with the "code" tag
code_templates = engine.get_templates_by_tag("code")

# Get a specific tag
memory_tag = get_tag("memory")

# Get all templates with the "memory" tag
memory_templates = engine.get_templates_by_tag("memory")

# Get templates by tag category
model_templates = engine.get_templates_by_tag_category(TagCategory.MODEL)

# Get templates by tag relationship
implements_templates = engine.get_templates_by_relationship(
    "interface_template", TagRelationship.IMPLEMENTS
)

# Get template recommendations based on context
recommendations = engine.get_template_recommendations("I need to create a Python class")
```

## Template Discovery and Search

The template engine provides powerful search capabilities for finding templates:

```python
from augment_adam.utils.templates import get_template_engine

# Get the template engine
engine = get_template_engine()

# Search for templates by keyword
results = engine.search_templates("python class")

# Search for templates by description
results = engine.search_templates_by_description("generate a Python class")

# Search for templates by example
results = engine.search_templates_by_example({
    "class_name": "MyClass",
    "base_classes": ["BaseClass"]
})

# Get similar templates
similar = engine.get_similar_templates("class_template.j2")
```

## Template Analytics

The template engine provides analytics for tracking template usage and performance:

```python
from augment_adam.utils.templates import get_template_engine

# Get the template engine
engine = get_template_engine()

# Get template usage statistics
stats = engine.get_template_usage_stats("class_template.j2")

# Get most used templates
most_used = engine.get_most_used_templates(limit=10)

# Get template performance metrics
performance = engine.get_template_performance_metrics("class_template.j2")
```

## Future Enhancements

Planned future enhancements:

- **Template Validation**: Validate templates against a schema
- **Template Versioning**: Version templates for backward compatibility
- **Template Repository**: Central repository for templates
- **Template Editor**: Visual editor for templates
- **Template Analytics**: Enhanced analytics for template usage and coverage
- **Template Recommendations**: AI-powered template recommendations
- **Template Generation**: AI-assisted template generation
- **Template Optimization**: Performance optimization for template rendering
- **Template Caching**: Intelligent caching for frequently used templates
- **Template Sharing**: Sharing templates between projects and teams
