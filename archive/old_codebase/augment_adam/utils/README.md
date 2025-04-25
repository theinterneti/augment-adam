# Utilities

This module provides utility functions and classes for the Augment Adam package.

## Overview

The utilities module includes:

1. Jinja2 template rendering utilities
2. Docstring generation utilities
3. Test generation utilities

## Jinja2 Utilities

The `jinja_utils` module provides utilities for rendering Jinja2 templates:

```python
from augment_adam.utils.jinja_utils import render_template

# Render a template
html = render_template(
    template_name="my_template.j2",
    context={"name": "World"}
)

print(html)  # Hello, World!
```

### Specialized Rendering Functions

The module also provides specialized rendering functions for common use cases:

```python
from augment_adam.utils.jinja_utils import (
    render_cypher_query,
    render_graph_visualization,
    render_test_template,
    render_docstring
)

# Render a Cypher query
query = render_cypher_query(
    query_type="create_node",
    node_label="Vector",
    collection_name="test_collection",
    return_node=False
)

# Render a graph visualization
html = render_graph_visualization(
    nodes=[{"id": "1", "label": "Node 1"}],
    edges=[{"id": "1", "from": "1", "to": "2", "label": "RELATED_TO"}],
    node_types=[{"label": "Vector", "color": "#97C2FC"}]
)

# Render a test template
test_code = render_test_template(
    imports=["import pytest"],
    tests=[{"name": "test_function", "description": "Test a function."}]
)

# Render a docstring
docstring = render_docstring(
    docstring_type="function",
    summary="Render a template with the given context."
)
```

## Customization

The templates are stored in the `templates` directory at the root of the package. You can customize the templates by modifying the files in this directory.
