#!/usr/bin/env python3
"""
Script to set up a minimal Sphinx documentation structure.
"""

import os
import shutil
from pathlib import Path

# Create the docs directory if it doesn't exist
os.makedirs("docs", exist_ok=True)

# Create a minimal conf.py file
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
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
"""

# Create a minimal index.rst file
index_rst = """
Welcome to Augment Adam's documentation!
=======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   architecture
   user_guide
   developer_guide
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""

# Create a minimal architecture.rst file
architecture_rst = """
Architecture
===========

This section describes the architecture of Augment Adam.

Memory System
-----------

The Memory System provides various memory implementations for storing and retrieving information.

Context Engine
------------

The Context Engine is responsible for managing and retrieving relevant context for the assistant.

Agent Coordination
---------------

The Agent Coordination system enables multiple agents to work together effectively.

Plugin System
-----------

The Plugin System enables the extension of the assistant's capabilities through plugins.
"""

# Create a minimal user_guide.rst file
user_guide_rst = """
User Guide
=========

This section provides information for users of Augment Adam.

Installation
----------

Instructions for installing Augment Adam.

Getting Started
-------------

A guide to getting started with Augment Adam.

Configuration
-----------

Information about configuring Augment Adam.
"""

# Create a minimal developer_guide.rst file
developer_guide_rst = """
Developer Guide
=============

This section provides information for developers of Augment Adam.

Contributing
----------

Guidelines for contributing to Augment Adam.

Testing Framework
--------------

Information about the testing framework.
"""

# Create a minimal api.rst file
api_rst = """
API Reference
===========

This section provides reference documentation for the Augment Adam API.

Memory API
--------

.. automodule:: augment_adam.memory
   :members:
   :undoc-members:
   :show-inheritance:

Context Engine API
---------------

.. automodule:: augment_adam.context_engine
   :members:
   :undoc-members:
   :show-inheritance:

Agent API
-------

.. automodule:: augment_adam.ai_agent
   :members:
   :undoc-members:
   :show-inheritance:
"""

# Write the files
with open("docs/conf.py", "w") as f:
    f.write(conf_py)

with open("docs/index.rst", "w") as f:
    f.write(index_rst)

with open("docs/architecture.rst", "w") as f:
    f.write(architecture_rst)

with open("docs/user_guide.rst", "w") as f:
    f.write(user_guide_rst)

with open("docs/developer_guide.rst", "w") as f:
    f.write(developer_guide_rst)

with open("docs/api.rst", "w") as f:
    f.write(api_rst)

# Create the _static and _templates directories
os.makedirs("docs/_static", exist_ok=True)
os.makedirs("docs/_templates", exist_ok=True)

print("Minimal Sphinx documentation structure created in docs/")
print("To build the documentation, run:")
print("cd docs && sphinx-build -b html . _build/html")
