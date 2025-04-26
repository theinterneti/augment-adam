#!/usr/bin/env python3
"""
Script to set up the Sphinx documentation structure.

This script creates the necessary directories and files for Sphinx documentation.
"""

import os
import shutil
from pathlib import Path

# Define the documentation directories
doc_dirs = [
    "docs/architecture",
    "docs/developer_guide",
    "docs/user_guide",
    "docs/api",
    "docs/_static",
    "docs/_templates"
]

# Define the Sphinx configuration files
sphinx_files = {
    "docs/conf.py": "/workspace/dev/sphinx/conf.py",
    "docs/index.rst": "/workspace/dev/sphinx/index.rst"
}

# Create the documentation directories
for doc_dir in doc_dirs:
    os.makedirs(doc_dir, exist_ok=True)
    print(f"Created directory: {doc_dir}")

# Copy the Sphinx configuration files
for dest, src in sphinx_files.items():
    shutil.copy2(src, dest)
    print(f"Copied {src} to {dest}")

# Create placeholder files for each section
placeholders = {
    # Architecture
    "docs/architecture/overview.rst": """
Architecture Overview
====================

This document provides an overview of the Augment Adam architecture.

.. toctree::
   :maxdepth: 2

   memory_system
   context_engine
   agent_coordination
   plugin_system
   template_engine
""",
    "docs/architecture/memory_system.rst": """
Memory System
============

.. include:: ../../architecture/MEMORY_SYSTEM.md
   :parser: myst_parser.sphinx_
""",
    "docs/architecture/context_engine.rst": """
Context Engine
=============

.. include:: ../../architecture/CONTEXT_ENGINE.md
   :parser: myst_parser.sphinx_
""",
    "docs/architecture/agent_coordination.rst": """
Agent Coordination
================

.. include:: ../../architecture/AGENT_COORDINATION.md
   :parser: myst_parser.sphinx_
""",
    "docs/architecture/plugin_system.rst": """
Plugin System
===========

.. include:: ../../architecture/PLUGIN_SYSTEM.md
   :parser: myst_parser.sphinx_
""",
    "docs/architecture/template_engine.rst": """
Template Engine
=============

.. include:: ../../architecture/TEMPLATE_ENGINE.md
   :parser: myst_parser.sphinx_
""",

    # Developer Guide
    "docs/developer_guide/architecture.rst": """
Architecture Guide
================

This guide provides information about the architecture of Augment Adam for developers.

.. toctree::
   :maxdepth: 2

   ../architecture/overview
""",
    "docs/developer_guide/testing_framework.rst": """
Testing Framework
===============

.. include:: ../../developer_guide/TESTING_FRAMEWORK.md
   :parser: myst_parser.sphinx_
""",
    "docs/developer_guide/contributing.rst": """
Contributing
==========

This guide provides information about contributing to Augment Adam.

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
""",

    # User Guide
    "docs/user_guide/installation.rst": """
Installation
==========

.. include:: ../../user_guide/installation.md
   :parser: myst_parser.sphinx_
""",
    "docs/user_guide/getting_started.rst": """
Getting Started
============

.. include:: ../../user_guide/getting_started.md
   :parser: myst_parser.sphinx_
""",
    "docs/user_guide/configuration.rst": """
Configuration
===========

.. include:: ../../user_guide/configuration.md
   :parser: myst_parser.sphinx_
""",
    "docs/user_guide/quickstart.rst": """
Quickstart
========

.. include:: ../../user_guide/quickstart.md
   :parser: myst_parser.sphinx_
""",

    # API Reference
    "docs/api/memory.rst": """
Memory API
========

.. automodule:: augment_adam.memory
   :members:
   :undoc-members:
   :show-inheritance:
""",
    "docs/api/context_engine.rst": """
Context Engine API
===============

.. automodule:: augment_adam.context_engine
   :members:
   :undoc-members:
   :show-inheritance:
""",
    "docs/api/agent.rst": """
Agent API
=======

.. automodule:: augment_adam.ai_agent
   :members:
   :undoc-members:
   :show-inheritance:
""",
    "docs/api/plugin.rst": """
Plugin API
========

.. automodule:: augment_adam.plugins
   :members:
   :undoc-members:
   :show-inheritance:
""",
    "docs/api/template.rst": """
Template API
=========

.. automodule:: augment_adam.templates
   :members:
   :undoc-members:
   :show-inheritance:
"""
}

# Create the placeholder files
for file_path, content in placeholders.items():
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"Created file: {file_path}")

print("\nSphinx documentation structure set up successfully!")
print("\nTo build the documentation, run:")
print("docker build -t augment-adam-docs -f /workspace/dev/sphinx/Dockerfile .")
print("docker run -p 8033:8033 -v /workspace:/workspace augment-adam-docs")
print("\nThen access the documentation at http://localhost:8033")
