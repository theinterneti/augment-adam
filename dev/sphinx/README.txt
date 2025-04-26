# Augment Adam Sphinx Documentation

This directory contains the configuration files for the Sphinx documentation system used by Augment Adam.

## Usage Instructions

1. Build the documentation container:
   ```
   docker build -t augment-adam-docs -f /workspace/dev/sphinx/Dockerfile .
   ```

2. Run the documentation server:
   ```
   docker run -p 8033:8033 -v /workspace:/workspace augment-adam-docs
   ```

3. Access the documentation in your browser at http://localhost:8033

## Documentation Structure

- `/workspace/docs/` - Main documentation source files
- `/workspace/docs/_build/html/` - Generated HTML documentation
- `/workspace/dev/sphinx/conf.py` - Sphinx configuration file
- `/workspace/dev/sphinx/index.rst` - Main index file

## Adding New Documentation

1. Create new .md or .rst files in the appropriate directory
2. Add them to the toctree in index.rst or another index file
3. Rebuild the documentation

## Using Autodoc

To automatically generate API documentation from docstrings:

```rst
.. automodule:: augment_adam.memory
   :members:
   :undoc-members:
   :show-inheritance:
```
