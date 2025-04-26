#!/usr/bin/env python3
"""
Script to improve the Sphinx documentation structure.

This script reorganizes the documentation into a more coherent structure.
"""

import os
import shutil
from pathlib import Path

def create_directory_structure():
    """Create a coherent directory structure for documentation."""
    print("Creating directory structure...")

    # Define the directory structure
    directories = [
        "docs/architecture",
        "docs/user_guide",
        "docs/developer_guide",
        "docs/api_reference",
        "docs/tutorials",
        "docs/examples",
        "docs/_static/images",
        "docs/_templates"
    ]

    # Create the directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  Created directory: {directory}")

def create_index_files():
    """Create index files for each section."""
    print("Creating index files...")

    # Define the index files
    index_files = {
        "docs/index.rst": """
Augment Adam Documentation
=======================

Welcome to the Augment Adam documentation. This documentation provides comprehensive information about the architecture, usage, and development of the Augment Adam system.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   architecture/index
   user_guide/index
   developer_guide/index
   api_reference/index
   tutorials/index
   examples/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
""",
        "docs/architecture/index.rst": """
Architecture
===========

This section provides an overview of the Augment Adam architecture.

.. toctree::
   :maxdepth: 2

   overview
   memory_system
   context_engine
   agent_coordination
   plugin_system
   template_engine
""",
        "docs/user_guide/index.rst": """
User Guide
=========

This section provides information for users of Augment Adam.

.. toctree::
   :maxdepth: 2

   installation
   getting_started
   configuration
   usage
   advanced_usage
""",
        "docs/developer_guide/index.rst": """
Developer Guide
=============

This section provides information for developers of Augment Adam.

.. toctree::
   :maxdepth: 2

   contributing
   development_setup
   testing_framework
   code_style
   architecture_guide
""",
        "docs/api_reference/index.rst": """
API Reference
===========

This section provides reference documentation for the Augment Adam API.

.. toctree::
   :maxdepth: 2

   memory
   context_engine
   agent
   plugin
   template
""",
        "docs/tutorials/index.rst": """
Tutorials
========

This section provides tutorials for using Augment Adam.

.. toctree::
   :maxdepth: 2

   quickstart
   memory_tutorial
   context_engine_tutorial
   agent_tutorial
   plugin_tutorial
""",
        "docs/examples/index.rst": """
Examples
=======

This section provides examples of using Augment Adam.

.. toctree::
   :maxdepth: 2

   basic_example
   memory_example
   context_engine_example
   agent_example
   plugin_example
"""
    }

    # Create the index files
    for file_path, content in index_files.items():
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"  Created index file: {file_path}")

def create_placeholder_files():
    """Create placeholder files for each section."""
    print("Creating placeholder files...")

    # Define the placeholder files
    placeholder_files = {
        # Architecture
        "docs/architecture/overview.rst": """
Overview
=======

This document provides an overview of the Augment Adam architecture.

System Components
---------------

Augment Adam consists of several key components:

* **Memory System**: Provides storage and retrieval of information
* **Context Engine**: Manages and retrieves relevant context
* **Agent Coordination**: Enables multiple agents to work together
* **Plugin System**: Extends the assistant's capabilities
* **Template Engine**: Manages templates for various outputs

Component Interactions
-------------------

These components interact to provide a powerful and flexible system:

.. mermaid::

   graph TD
       A[User] --> B[Assistant]
       B --> C[Memory System]
       B --> D[Context Engine]
       B --> E[Agent Coordination]
       B --> F[Plugin System]
       B --> G[Template Engine]
       C --> D
       D --> E
       E --> F
       F --> G
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

        # User Guide
        "docs/user_guide/installation.rst": """
Installation
==========

This document provides instructions for installing Augment Adam.

Requirements
----------

* Python 3.8 or higher
* pip
* virtualenv (recommended)

Installation Steps
---------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/yourusername/augment-adam.git
      cd augment-adam

2. Create a virtual environment:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\\Scripts\\activate

3. Install the package:

   .. code-block:: bash

      pip install -e .

4. Verify the installation:

   .. code-block:: bash

      python -c "import augment_adam; print(augment_adam.__version__)"
""",
        "docs/user_guide/getting_started.rst": """
Getting Started
============

.. include:: ../../user_guide/getting_started.md
   :parser: myst_parser.sphinx_
""",

        # Developer Guide
        "docs/developer_guide/testing_framework.rst": """
Testing Framework
===============

.. include:: ../../developer_guide/TESTING_FRAMEWORK.md
   :parser: myst_parser.sphinx_
""",

        # API Reference
        "docs/api_reference/memory.rst": """
Memory API
========

.. automodule:: augment_adam.memory
   :members:
   :undoc-members:
   :show-inheritance:
""",
        "docs/api_reference/context_engine.rst": """
Context Engine API
===============

.. automodule:: augment_adam.context_engine
   :members:
   :undoc-members:
   :show-inheritance:
""",
        "docs/api_reference/agent.rst": """
Agent API
=======

.. automodule:: augment_adam.ai_agent
   :members:
   :undoc-members:
   :show-inheritance:
""",
        "docs/api_reference/plugin.rst": """
Plugin API
========

.. automodule:: augment_adam.plugins
   :members:
   :undoc-members:
   :show-inheritance:
""",
        "docs/api_reference/template.rst": """
Template API
=========

.. automodule:: augment_adam.templates
   :members:
   :undoc-members:
   :show-inheritance:
"""
    }

    # Create the placeholder files
    for file_path, content in placeholder_files.items():
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Create the file
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"  Created placeholder file: {file_path}")

def update_conf_py():
    """Update the conf.py file."""
    print("Updating conf.py...")

    conf_py = """
# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = 'Augment Adam'
copyright = '2023-2024, Augment Code'
author = 'Augment Code Team'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinxcontrib.mermaid',
    'myst_parser',
    'sphinx_copybutton',
    'sphinx_design',
    'sphinx_togglebutton',
    'sphinx_tabs.tabs'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------
# Try to import linkify-it-py
try:
    import linkify_it_py
    has_linkify = True
except ImportError:
    has_linkify = False

# Enable extensions based on availability
myst_enable_extensions = [
    'colon_fence',
    'deflist',
    'dollarmath',
    'fieldlist',
    'html_admonition',
    'html_image',
    'replacements',
    'smartquotes',
    'substitution',
    'tasklist'
]

# Add linkify if available
if has_linkify:
    myst_enable_extensions.append('linkify')

# -- Intersphinx configuration ----------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None)
}

# -- Napoleon configuration -------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
napoleon_custom_sections = None

# -- Todo configuration ----------------------------------------------------
todo_include_todos = True
"""

    # Write the conf.py file
    with open("docs/conf.py", 'w') as f:
        f.write(conf_py)
    print("  Updated conf.py")

def main():
    """Main function."""
    print("Improving Sphinx documentation structure...")

    # Create directory structure
    create_directory_structure()

    # Create index files
    create_index_files()

    # Create placeholder files
    create_placeholder_files()

    # Update conf.py
    update_conf_py()

    print("Done!")

if __name__ == "__main__":
    main()
