# Documentation Guide

## Introduction

This guide explains how to use the Documentation System to generate, build, and manage documentation for the project. The Documentation System provides tools for extracting documentation from code, building documentation in various formats, and validating documentation quality.

## Getting Started

### Installation

The Documentation System is included in the main package and doesn't require separate installation.

### Basic Usage

To generate documentation for a module:

```python
from augment_adam.docs import ModuleDocGenerator

# Create a generator
generator = ModuleDocGenerator(output_dir="docs/api")

# Generate documentation for a module
data = generator.generate("augment_adam.utils")

# Save documentation to a file
generator.save(data, "docs/api/utils.md")
```

## Documentation Generators

The Documentation System provides several generators for extracting documentation from code:

### Module Documentation Generator

The `ModuleDocGenerator` extracts documentation from a Python module, including module docstrings, classes, functions, and variables.

```python
from augment_adam.docs import ModuleDocGenerator

# Create a generator
generator = ModuleDocGenerator(
    output_dir="docs/api",
    include_private=False,  # Whether to include private members
    include_dunder=False,   # Whether to include dunder methods
)

# Generate documentation for a module
data = generator.generate("augment_adam.utils")

# Save documentation to a file
generator.save(data, "docs/api/utils.md")
```

### Class Documentation Generator

The `ClassDocGenerator` extracts documentation from a Python class, including class docstrings, methods, and attributes.

```python
from augment_adam.docs import ClassDocGenerator
from augment_adam.utils.templates import Template

# Create a generator
generator = ClassDocGenerator(
    output_dir="docs/api",
    include_private=False,  # Whether to include private members
    include_dunder=False,   # Whether to include dunder methods
)

# Generate documentation for a class
data = generator.generate(Template)

# Save documentation to a file
generator.save(data, "docs/api/template.md")
```

### Function Documentation Generator

The `FunctionDocGenerator` extracts documentation from a Python function, including function docstrings, parameters, and return types.

```python
from augment_adam.docs import FunctionDocGenerator
from augment_adam.utils.templates import render_template

# Create a generator
generator = FunctionDocGenerator(output_dir="docs/api")

# Generate documentation for a function
data = generator.generate(render_template)

# Save documentation to a file
generator.save(data, "docs/api/render_template.md")
```

## Documentation Builders

The Documentation System provides several builders for creating documentation files in various formats:

### Markdown Builder

The `MarkdownBuilder` creates documentation files in Markdown format.

```python
from augment_adam.docs import MarkdownBuilder

# Create a builder
builder = MarkdownBuilder(output_dir="docs/api")

# Build documentation from data
builder.build(data, "docs/api/utils.md")

# Build documentation for multiple data items
builder.build_all(data_list, "docs/api")
```

### HTML Builder

The `HtmlBuilder` creates documentation files in HTML format.

```python
from augment_adam.docs import HtmlBuilder

# Create a builder
builder = HtmlBuilder(
    output_dir="docs/api",
    css_file="docs/assets/css/style.css",  # Optional CSS file
    js_file="docs/assets/js/script.js",    # Optional JavaScript file
)

# Build documentation from data
builder.build(data, "docs/api/utils.html")

# Build documentation for multiple data items
builder.build_all(data_list, "docs/api")
```

### Website Builder

The `WebsiteBuilder` creates a documentation website with multiple HTML pages, navigation, search, and other features.

```python
from augment_adam.docs import WebsiteBuilder

# Create a builder
builder = WebsiteBuilder(
    output_dir="docs/website",
    title="Project Documentation",
    description="Documentation for the project",
    theme="default",
)

# Build a documentation page
builder.build(
    {
        "title": "Utils Module",
        "content": "docs/api/utils.md",
        "navigation": [
            {"title": "Home", "url": "index.html"},
            {"title": "Utils", "url": "utils.html"},
        ],
        "breadcrumbs": [
            {"title": "Home", "url": "index.html"},
            {"title": "API", "url": "api.html"},
            {"title": "Utils", "url": "utils.html"},
        ],
    },
    "docs/website/utils.html",
)

# Build a documentation website from multiple data items
builder.build_all(data_list, "docs/website")
```

## Documentation Utilities

The Documentation System provides several utilities for parsing, formatting, extracting, and validating documentation:

### Documentation Parser

The `DocParser` parses documentation from various sources, including docstrings, Markdown files, and reStructuredText files.

```python
from augment_adam.docs.utils import DocParser

# Create a parser
parser = DocParser()

# Parse a docstring
data = parser.parse_docstring(docstring)

# Parse Markdown documentation
data = parser.parse_markdown(markdown)

# Parse reStructuredText documentation
data = parser.parse_rst(rst)
```

### Documentation Formatter

The `DocFormatter` formats documentation in various formats, including Markdown, reStructuredText, and HTML.

```python
from augment_adam.docs.utils import DocFormatter

# Create a formatter
formatter = DocFormatter()

# Format documentation as Markdown
markdown = formatter.format_markdown(data)

# Format documentation as reStructuredText
rst = formatter.format_rst(data)

# Format documentation as HTML
html = formatter.format_html(data)
```

### Documentation Extractor

The `DocExtractor` extracts documentation from code, including docstrings, type hints, and other metadata.

```python
from augment_adam.docs.utils import DocExtractor

# Create an extractor
extractor = DocExtractor()

# Extract documentation from a module
data = extractor.extract_module("augment_adam.utils")

# Extract documentation from a class
data = extractor.extract_class(Template)

# Extract documentation from a function
data = extractor.extract_function(render_template)

# Extract documentation from a Python file
data = extractor.extract_file("src/augment_adam/utils/templates.py")
```

### Documentation Validator

The `DocValidator` validates documentation, ensuring it meets certain requirements and standards.

```python
from augment_adam.docs.utils import DocValidator

# Create a validator
validator = DocValidator()

# Validate a docstring
errors = validator.validate_docstring(docstring)

# Validate module documentation
errors = validator.validate_module_doc(module_doc)

# Validate class documentation
errors = validator.validate_class_doc(class_doc)

# Validate function documentation
errors = validator.validate_function_doc(function_doc)
```

## Integration with Template Engine

The Documentation System integrates with the Template Engine to render documentation using templates. The `DocRenderer` class in the Template Engine provides a flexible way to render documentation in various formats.

```python
from augment_adam.utils.templates.renderers import DocRenderer

# Create a renderer
renderer = DocRenderer()

# Render documentation using a template
content = renderer.render(template, data)
```

## Best Practices

### Writing Good Documentation

1. **Be Clear and Concise**: Write clear and concise documentation that is easy to understand.
2. **Use Examples**: Include examples to illustrate how to use the code.
3. **Document Parameters and Return Values**: Document all parameters and return values, including their types and descriptions.
4. **Keep Documentation Up-to-Date**: Update documentation when the code changes.
5. **Use Consistent Style**: Use a consistent style for documentation throughout the project.

### Organizing Documentation

1. **Use a Hierarchical Structure**: Organize documentation in a hierarchical structure, with high-level concepts at the top and details at the bottom.
2. **Separate API Documentation from Guides**: Separate API documentation from user guides and tutorials.
3. **Use Cross-References**: Use cross-references to link related documentation.
4. **Include a Table of Contents**: Include a table of contents for long documentation.
5. **Use Meaningful File Names**: Use meaningful file names for documentation files.

## Troubleshooting

### Common Issues

1. **Missing Documentation**: If documentation is missing, check if the code has proper docstrings.
2. **Incorrect Documentation**: If documentation is incorrect, check if the docstrings are up-to-date.
3. **Formatting Issues**: If documentation has formatting issues, check if the docstrings use the correct format.
4. **Build Errors**: If documentation build fails, check if the output directory exists and is writable.

### Getting Help

If you encounter issues with the Documentation System, please:

1. Check the documentation for the specific component you're using.
2. Look for examples in the codebase.
3. Ask for help in the project's issue tracker or discussion forum.

## Conclusion

The Documentation System provides a comprehensive solution for generating, building, and managing documentation for the project. By following the guidelines in this guide, you can create high-quality documentation that helps users understand and use the project effectively.
