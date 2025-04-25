#!/usr/bin/env python3
"""
Documentation generator script.

This script generates documentation for the Augment Adam project using templates.
It can generate API documentation, user guides, developer guides, and architecture documentation.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from augment_adam.utils.templates import render_template, TemplateContext
    from augment_adam.utils.templates.renderers import DocRenderer
except ImportError:
    print("Error: Could not import the template engine. Make sure the project is installed.")
    print("Try running: pip install -e .")
    sys.exit(1)


def generate_api_doc(module_name, output_path, data_file=None):
    """
    Generate API documentation for a module.
    
    Args:
        module_name: Name of the module to document.
        output_path: Path to save the documentation.
        data_file: Optional JSON file with documentation data.
    """
    # Create the context
    context = TemplateContext()
    
    # Load data from file if provided
    if data_file and os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        for key, value in data.items():
            context.add_variable(key, value)
    else:
        # Set default values
        context.add_variable("module_name", module_name)
        context.add_variable("module_description", f"API documentation for the {module_name} module.")
        context.add_variable("classes", [])
        context.add_variable("functions", [])
        context.add_variable("examples", [])
    
    # Render the template
    doc_renderer = DocRenderer()
    output = doc_renderer.render_markdown("api_doc_template.md.j2", context)
    
    # Save the output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(output)
    
    print(f"Generated API documentation for {module_name} at {output_path}")


def generate_user_guide(title, output_path, data_file=None):
    """
    Generate a user guide.
    
    Args:
        title: Title of the user guide.
        output_path: Path to save the documentation.
        data_file: Optional JSON file with documentation data.
    """
    # Create the context
    context = TemplateContext()
    
    # Load data from file if provided
    if data_file and os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        for key, value in data.items():
            context.add_variable(key, value)
    else:
        # Set default values
        context.add_variable("title", title)
        context.add_variable("description", f"This guide explains how to use {title}.")
        context.add_variable("sections", [])
        context.add_variable("examples", [])
    
    # Render the template
    doc_renderer = DocRenderer()
    output = doc_renderer.render_markdown("user_guide_template.md.j2", context)
    
    # Save the output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(output)
    
    print(f"Generated user guide for {title} at {output_path}")


def generate_developer_guide(title, output_path, data_file=None):
    """
    Generate a developer guide.
    
    Args:
        title: Title of the developer guide.
        output_path: Path to save the documentation.
        data_file: Optional JSON file with documentation data.
    """
    # Create the context
    context = TemplateContext()
    
    # Load data from file if provided
    if data_file and os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        for key, value in data.items():
            context.add_variable(key, value)
    else:
        # Set default values
        context.add_variable("title", title)
        context.add_variable("description", f"This guide explains how to develop with {title}.")
        context.add_variable("sections", [])
        context.add_variable("examples", [])
        context.add_variable("best_practices", [])
        context.add_variable("next_steps", [])
    
    # Render the template
    doc_renderer = DocRenderer()
    output = doc_renderer.render_markdown("developer_guide_template.md.j2", context)
    
    # Save the output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(output)
    
    print(f"Generated developer guide for {title} at {output_path}")


def generate_architecture_doc(title, output_path, data_file=None):
    """
    Generate architecture documentation.
    
    Args:
        title: Title of the architecture documentation.
        output_path: Path to save the documentation.
        data_file: Optional JSON file with documentation data.
    """
    # Create the context
    context = TemplateContext()
    
    # Load data from file if provided
    if data_file and os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        for key, value in data.items():
            context.add_variable(key, value)
    else:
        # Set default values
        context.add_variable("title", title)
        context.add_variable("description", f"This document describes the architecture of the {title}.")
        context.add_variable("components", [])
        context.add_variable("interfaces", [])
        context.add_variable("examples", [])
        context.add_variable("future_enhancements", [])
    
    # Render the template
    doc_renderer = DocRenderer()
    output = doc_renderer.render_markdown("architecture_doc_template.md.j2", context)
    
    # Save the output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(output)
    
    print(f"Generated architecture documentation for {title} at {output_path}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate documentation for Augment Adam")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # API documentation parser
    api_parser = subparsers.add_parser("api", help="Generate API documentation")
    api_parser.add_argument("module", help="Module name")
    api_parser.add_argument("output", help="Output file path")
    api_parser.add_argument("--data", help="JSON file with documentation data")
    
    # User guide parser
    user_parser = subparsers.add_parser("user", help="Generate a user guide")
    user_parser.add_argument("title", help="Guide title")
    user_parser.add_argument("output", help="Output file path")
    user_parser.add_argument("--data", help="JSON file with documentation data")
    
    # Developer guide parser
    dev_parser = subparsers.add_parser("dev", help="Generate a developer guide")
    dev_parser.add_argument("title", help="Guide title")
    dev_parser.add_argument("output", help="Output file path")
    dev_parser.add_argument("--data", help="JSON file with documentation data")
    
    # Architecture documentation parser
    arch_parser = subparsers.add_parser("arch", help="Generate architecture documentation")
    arch_parser.add_argument("title", help="Documentation title")
    arch_parser.add_argument("output", help="Output file path")
    arch_parser.add_argument("--data", help="JSON file with documentation data")
    
    # Batch generation parser
    batch_parser = subparsers.add_parser("batch", help="Generate multiple documentation files from a JSON file")
    batch_parser.add_argument("config", help="JSON configuration file")
    
    args = parser.parse_args()
    
    if args.command == "api":
        generate_api_doc(args.module, args.output, args.data)
    elif args.command == "user":
        generate_user_guide(args.title, args.output, args.data)
    elif args.command == "dev":
        generate_developer_guide(args.title, args.output, args.data)
    elif args.command == "arch":
        generate_architecture_doc(args.title, args.output, args.data)
    elif args.command == "batch":
        if not os.path.exists(args.config):
            print(f"Error: Configuration file {args.config} not found.")
            sys.exit(1)
        
        with open(args.config, 'r') as f:
            config = json.load(f)
        
        for doc in config.get("api", []):
            generate_api_doc(doc["module"], doc["output"], doc.get("data"))
        
        for doc in config.get("user", []):
            generate_user_guide(doc["title"], doc["output"], doc.get("data"))
        
        for doc in config.get("dev", []):
            generate_developer_guide(doc["title"], doc["output"], doc.get("data"))
        
        for doc in config.get("arch", []):
            generate_architecture_doc(doc["title"], doc["output"], doc.get("data"))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
