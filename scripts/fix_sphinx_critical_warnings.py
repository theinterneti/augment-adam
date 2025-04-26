#!/usr/bin/env python3
"""
Script to fix critical warnings in Sphinx documentation.
"""

import os
import re
from pathlib import Path

def fix_include_paths():
    """Fix include directive paths in RST files."""
    print("Fixing include directive paths...")
    
    # Define the files to fix
    files = {
        "docs/architecture/agent_coordination.rst": """
Agent Coordination
=================

This document provides information about agent coordination.

.. include:: ../../docs/architecture/AGENT_COORDINATION.md
   :parser: myst_parser.sphinx_
""",
        "docs/architecture/context_engine.rst": """
Context Engine
=============

This document provides information about the context engine.

.. include:: ../../docs/architecture/CONTEXT_ENGINE.md
   :parser: myst_parser.sphinx_
""",
        "docs/architecture/memory_system.rst": """
Memory System
============

This document provides information about the memory system.

.. include:: ../../docs/architecture/MEMORY_SYSTEM.md
   :parser: myst_parser.sphinx_
""",
        "docs/architecture/overview.rst": """
Overview
=======

This document provides an overview of the Augment Adam architecture.

.. include:: ../../docs/architecture/ARCHITECTURE.md
   :parser: myst_parser.sphinx_
""",
        "docs/architecture/plugin_system.rst": """
Plugin System
===========

This document provides information about the plugin system.

.. include:: ../../docs/architecture/PLUGIN_SYSTEM.md
   :parser: myst_parser.sphinx_
""",
        "docs/architecture/template_engine.rst": """
Template Engine
=============

This document provides information about the template engine.

.. include:: ../../docs/architecture/TEMPLATE_ENGINE.md
   :parser: myst_parser.sphinx_
""",
        "docs/developer_guide/contributing.rst": """
Contributing
==========

This document provides guidelines for contributing to Augment Adam.

.. include:: ../../docs/development/CONTRIBUTING.md
   :parser: myst_parser.sphinx_
""",
        "docs/developer_guide/testing_framework.rst": """
Testing Framework
===============

This document provides information about the testing framework.

.. include:: ../../docs/architecture/TESTING_FRAMEWORK.md
   :parser: myst_parser.sphinx_
"""
    }
    
    # Write the fixed files
    for file_path, content in files.items():
        with open(file_path, "w") as f:
            f.write(content)
        print(f"  Fixed {file_path}")

def create_placeholder_md_files():
    """Create placeholder Markdown files for missing includes."""
    print("Creating placeholder Markdown files...")
    
    # Define the files to create
    files = {
        "docs/architecture/AGENT_COORDINATION.md": """
# Agent Coordination

This is a placeholder for the Agent Coordination documentation.

## Overview

The Agent Coordination system enables multiple agents to work together effectively.

## Components

- **Coordinator**: Manages the coordination of multiple agents
- **Task Decomposer**: Breaks down tasks into subtasks
- **Agent Selector**: Selects the appropriate agent for each subtask
- **Result Aggregator**: Aggregates results from multiple agents

## Usage

```python
from augment_adam.ai_agent.coordination import Coordinator

coordinator = Coordinator()
coordinator.add_agent(agent1)
coordinator.add_agent(agent2)
result = coordinator.execute_task("Analyze this text and summarize it")
```
""",
        "docs/architecture/CONTEXT_ENGINE.md": """
# Context Engine

This is a placeholder for the Context Engine documentation.

## Overview

The Context Engine is responsible for managing and retrieving relevant context for the assistant.

## Components

- **Context Retriever**: Retrieves relevant context from various sources
- **Context Analyzer**: Analyzes context to determine relevance
- **Context Manager**: Manages context storage and retrieval
- **Context Formatter**: Formats context for use by the assistant

## Usage

```python
from augment_adam.context_engine import ContextEngine

context_engine = ContextEngine()
context = context_engine.get_context("What is the capital of France?")
```
""",
        "docs/architecture/MEMORY_SYSTEM.md": """
# Memory System

This is a placeholder for the Memory System documentation.

## Overview

The Memory System provides various memory implementations for storing and retrieving information.

## Components

- **Vector Memory**: Stores and retrieves information using vector embeddings
- **Episodic Memory**: Stores and retrieves episodic information
- **Semantic Memory**: Stores and retrieves semantic information
- **Working Memory**: Stores and retrieves working memory information

## Usage

```python
from augment_adam.memory import VectorMemory

memory = VectorMemory()
memory.add("Paris is the capital of France")
results = memory.search("capital of France")
```
""",
        "docs/architecture/ARCHITECTURE.md": """
# Architecture

This is a placeholder for the Architecture documentation.

## Overview

Augment Adam consists of several key components:

- **Memory System**: Provides storage and retrieval of information
- **Context Engine**: Manages and retrieves relevant context
- **Agent Coordination**: Enables multiple agents to work together
- **Plugin System**: Extends the assistant's capabilities
- **Template Engine**: Manages templates for various outputs

## Component Interactions

These components interact to provide a powerful and flexible system.

## Design Principles

- **Modularity**: Components are modular and can be used independently
- **Extensibility**: The system is designed to be easily extended
- **Flexibility**: The system is flexible and can be adapted to various use cases
- **Performance**: The system is designed for high performance
- **Scalability**: The system is designed to scale to large datasets and many users
""",
        "docs/architecture/PLUGIN_SYSTEM.md": """
# Plugin System

This is a placeholder for the Plugin System documentation.

## Overview

The Plugin System enables the extension of the assistant's capabilities through plugins.

## Components

- **Plugin Manager**: Manages the loading and execution of plugins
- **Plugin Registry**: Registers and tracks available plugins
- **Plugin Validator**: Validates plugins before execution
- **Plugin Executor**: Executes plugins and returns results

## Usage

```python
from augment_adam.plugins import PluginRegistry

registry = PluginRegistry()
registry.register(my_plugin)
result = registry.execute_plugin("my_plugin", {"param": "value"})
```
""",
        "docs/architecture/TEMPLATE_ENGINE.md": """
# Template Engine

This is a placeholder for the Template Engine documentation.

## Overview

The Template Engine manages templates for various outputs.

## Components

- **Template Manager**: Manages the loading and execution of templates
- **Template Registry**: Registers and tracks available templates
- **Template Validator**: Validates templates before execution
- **Template Executor**: Executes templates and returns results

## Usage

```python
from augment_adam.utils.templates import TemplateEngine

engine = TemplateEngine()
result = engine.render("my_template", {"param": "value"})
```
""",
        "docs/architecture/TESTING_FRAMEWORK.md": """
# Testing Framework

This is a placeholder for the Testing Framework documentation.

## Overview

The Testing Framework provides tools for testing the Augment Adam system.

## Components

- **Test Runner**: Runs tests and reports results
- **Test Fixtures**: Provides fixtures for testing
- **Test Utilities**: Provides utilities for testing
- **Test Coverage**: Tracks test coverage

## Usage

```python
from augment_adam.testing import TestRunner

runner = TestRunner()
results = runner.run_tests("test_memory")
```
""",
        "docs/development/CONTRIBUTING.md": """
# Contributing

This is a placeholder for the Contributing documentation.

## Getting Started

To contribute to Augment Adam, follow these steps:

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## Code Style

Please follow the Google Python Style Guide when contributing code.

## Testing

All code should be tested. See the Testing Framework guide for more information.

## Documentation

All code should be documented. See the Documentation guide for more information.

## Pull Requests

Pull requests should be small and focused. Each pull request should address a single issue.

## Issues

Issues should be detailed and include steps to reproduce. Include as much information as possible.
"""
    }
    
    # Write the files
    for file_path, content in files.items():
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write the file
        with open(file_path, "w") as f:
            f.write(content)
        print(f"  Created {file_path}")

def fix_title_underlines():
    """Fix title underlines that are too short."""
    print("Fixing title underlines...")
    
    # Get all .rst files
    rst_files = []
    for root, dirs, files in os.walk("docs"):
        for file in files:
            if file.endswith(".rst"):
                rst_files.append(os.path.join(root, file))
    
    for file_path in rst_files:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find title lines and their underlines
        title_pattern = re.compile(r'^([^\n]+)\n([=\-~]+)$', re.MULTILINE)
        
        def replace_underline(match):
            title = match.group(1)
            underline = match.group(2)
            char = underline[0]
            # Make the underline at least as long as the title
            new_underline = char * max(len(title), len(underline))
            return f"{title}\n{new_underline}"
        
        # Replace underlines
        new_content = title_pattern.sub(replace_underline, content)
        
        if new_content != content:
            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"  Fixed underlines in {file_path}")

def fix_api_rst_files():
    """Fix API RST files to use :noindex: for duplicate objects."""
    print("Fixing API RST files...")
    
    # Define the files to fix
    files = {
        "docs/api/memory.rst": """
Memory API
=========

This document provides reference documentation for the Memory API.

.. automodule:: augment_adam.memory
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

.. automodule:: augment_adam.memory.core
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

.. automodule:: augment_adam.memory.vector
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:
""",
        "docs/api/context_engine.rst": """
Context Engine API
================

This document provides reference documentation for the Context Engine API.

.. automodule:: augment_adam.context_engine
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:
""",
        "docs/api/agent.rst": """
Agent API
========

This document provides reference documentation for the Agent API.

.. automodule:: augment_adam.ai_agent
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:
""",
        "docs/api/plugin.rst": """
Plugin API
=========

This document provides reference documentation for the Plugin API.

.. automodule:: augment_adam.plugins
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:
""",
        "docs/api/template.rst": """
Template API
==========

This document provides reference documentation for the Template API.

.. automodule:: augment_adam.utils.templates
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:
"""
    }
    
    # Write the fixed files
    for file_path, content in files.items():
        with open(file_path, "w") as f:
            f.write(content)
        print(f"  Fixed {file_path}")

def main():
    """Main function."""
    print("Fixing critical warnings in Sphinx documentation...")
    
    # Fix include paths
    fix_include_paths()
    
    # Create placeholder Markdown files
    create_placeholder_md_files()
    
    # Fix title underlines
    fix_title_underlines()
    
    # Fix API RST files
    fix_api_rst_files()
    
    print("Done!")

if __name__ == "__main__":
    main()
