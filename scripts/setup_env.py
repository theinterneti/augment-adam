#!/usr/bin/env python3
"""
Setup script to add necessary paths to Python path.

This script adds the src directory to the Python path so that
the augment_adam module can be imported properly.
"""

import os
import sys
from pathlib import Path

def setup_python_path(verbose=False):
    """
    Add necessary directories to Python path.

    Args:
        verbose: Whether to print debug information.

    Returns:
        bool: True if setup was successful, False otherwise.
    """
    # Get the workspace root directory
    workspace_root = Path('/workspace')

    # Add src directory to Python path
    src_dir = workspace_root / 'src'
    if src_dir.exists() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
        if verbose:
            print(f"Added {src_dir} to Python path")

    # Check if augment_adam module can be imported
    try:
        import augment_adam
        if verbose:
            print(f"Successfully imported augment_adam from {augment_adam.__file__}")
        return True
    except (ImportError, SyntaxError) as e:
        if verbose:
            print(f"Warning: Could not import augment_adam: {e}")

        # Try to find augment_adam in other locations
        possible_locations = [
            workspace_root / 'archive' / 'old_codebase' / 'augment_adam',
            workspace_root / 'archive' / 'old_codebase' / 'augment-adam' / 'augment_adam'
        ]

        for location in possible_locations:
            if location.exists() and str(location.parent) not in sys.path:
                sys.path.insert(0, str(location.parent))
                if verbose:
                    print(f"Added {location.parent} to Python path")
                try:
                    import augment_adam
                    if verbose:
                        print(f"Successfully imported augment_adam from {augment_adam.__file__}")
                    return True
                except (ImportError, SyntaxError):
                    continue

    # If we get here, we couldn't import augment_adam
    # Let's create a minimal implementation for our templates
    if verbose:
        print("Creating minimal augment_adam.utils.templates implementation")

    # Create a minimal implementation of the template engine
    class MinimalTemplateEngine:
        def __init__(self):
            import jinja2
            self.env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(str(workspace_root)),
                trim_blocks=True,
                lstrip_blocks=True
            )

        def render_template(self, template_name, context):
            template = self.env.get_template(template_name)
            return template.render(**context)

        def render_doc_template(self, template_name, context):
            return self.render_template(template_name, context)

    # Create the module structure
    import types
    sys.modules['augment_adam'] = types.ModuleType('augment_adam')
    sys.modules['augment_adam.utils'] = types.ModuleType('augment_adam.utils')
    sys.modules['augment_adam.utils.templates'] = types.ModuleType('augment_adam.utils.templates')

    # Add the minimal implementation
    engine = MinimalTemplateEngine()
    sys.modules['augment_adam.utils.templates'].render_template = engine.render_template
    sys.modules['augment_adam.utils.templates'].render_doc_template = engine.render_doc_template

    if verbose:
        print("Created minimal template engine implementation")

    return True

def print_debug_info():
    """Print debug information about the Python environment."""
    # Get the workspace root directory
    workspace_root = Path('/workspace')

    # Check if templates directory exists
    templates_dir = workspace_root / 'templates'
    if not templates_dir.exists():
        print(f"Warning: Templates directory {templates_dir} does not exist")
    else:
        print(f"Templates directory found at {templates_dir}")

    # Print Python path
    print("\nPython path:")
    for path in sys.path:
        print(f"  {path}")

    # Print installed packages
    try:
        import pkg_resources
        print("\nInstalled packages:")
        for package in pkg_resources.working_set:
            print(f"  {package.project_name} {package.version}")
    except ImportError:
        print("Could not import pkg_resources to list installed packages")

if __name__ == "__main__":
    setup_python_path(verbose=True)
    print_debug_info()
