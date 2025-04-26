#!/usr/bin/env python3
"""
Script to set up a simple, working Sphinx documentation structure.
"""

import os
import shutil
from pathlib import Path

def create_directory_structure():
    """Create the basic directory structure."""
    print("Creating directory structure...")
    
    # Define the directory structure
    directories = [
        "docs/user_guide",
        "docs/developer_guide",
        "docs/architecture",
        "docs/api",
        "docs/_static",
        "docs/_templates",
        "docs/_build/html"
    ]
    
    # Create the directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  Created directory: {directory}")

def copy_configuration_files():
    """Copy the configuration files from dev/sphinx."""
    print("Copying configuration files...")
    
    # Copy conf.py
    shutil.copy2("/workspace/dev/sphinx/conf.py", "docs/conf.py")
    print("  Copied conf.py")

def create_index_file():
    """Create a simple index.rst file."""
    print("Creating index.rst...")
    
    index_content = """
Augment Adam Documentation
=======================

Welcome to the Augment Adam documentation!

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   user_guide/index
   developer_guide/index
   architecture/index
   api/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""
    
    with open("docs/index.rst", "w") as f:
        f.write(index_content)
    
    print("  Created index.rst")

def create_section_index_files():
    """Create index.rst files for each section."""
    print("Creating section index files...")
    
    # User Guide
    user_guide_index = """
User Guide
=========

This section provides information for users of Augment Adam.

.. toctree::
   :maxdepth: 2

   installation
   getting_started
   configuration
   quickstart
"""
    
    with open("docs/user_guide/index.rst", "w") as f:
        f.write(user_guide_index)
    
    print("  Created user_guide/index.rst")
    
    # Developer Guide
    developer_guide_index = """
Developer Guide
=============

This section provides information for developers of Augment Adam.

.. toctree::
   :maxdepth: 2

   contributing
   testing_framework
"""
    
    with open("docs/developer_guide/index.rst", "w") as f:
        f.write(developer_guide_index)
    
    print("  Created developer_guide/index.rst")
    
    # Architecture
    architecture_index = """
Architecture
==========

This section provides an overview of the Augment Adam architecture.

.. toctree::
   :maxdepth: 2

   overview
   memory_system
   context_engine
   agent_coordination
   plugin_system
   template_engine
"""
    
    with open("docs/architecture/index.rst", "w") as f:
        f.write(architecture_index)
    
    print("  Created architecture/index.rst")
    
    # API
    api_index = """
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
"""
    
    with open("docs/api/index.rst", "w") as f:
        f.write(api_index)
    
    print("  Created api/index.rst")

def create_simple_rst_files():
    """Create simple RST files for each section."""
    print("Creating simple RST files...")
    
    # User Guide
    files = {
        "docs/user_guide/installation.rst": """
Installation
==========

This document provides instructions for installing Augment Adam.

.. include:: ../../user_guide/installation.md
   :parser: myst_parser.sphinx_
""",
        "docs/user_guide/getting_started.rst": """
Getting Started
============

This document provides a guide to getting started with Augment Adam.

.. include:: ../../user_guide/getting_started.md
   :parser: myst_parser.sphinx_
""",
        "docs/user_guide/configuration.rst": """
Configuration
===========

This document provides information about configuring Augment Adam.

.. include:: ../../user_guide/configuration.md
   :parser: myst_parser.sphinx_
""",
        "docs/user_guide/quickstart.rst": """
Quickstart
========

This document provides a quickstart guide for Augment Adam.

.. include:: ../../user_guide/quickstart.md
   :parser: myst_parser.sphinx_
""",
        
        # Developer Guide
        "docs/developer_guide/contributing.rst": """
Contributing
==========

This document provides guidelines for contributing to Augment Adam.

.. include:: ../../development/CONTRIBUTING.md
   :parser: myst_parser.sphinx_
""",
        "docs/developer_guide/testing_framework.rst": """
Testing Framework
==============

This document provides information about the testing framework.

.. include:: ../../architecture/TESTING_FRAMEWORK.md
   :parser: myst_parser.sphinx_
""",
        
        # Architecture
        "docs/architecture/overview.rst": """
Overview
=======

This document provides an overview of the Augment Adam architecture.

.. include:: ../../architecture/ARCHITECTURE.md
   :parser: myst_parser.sphinx_
""",
        "docs/architecture/memory_system.rst": """
Memory System
===========

This document provides information about the memory system.

.. include:: ../../architecture/MEMORY_SYSTEM.md
   :parser: myst_parser.sphinx_
""",
        "docs/architecture/context_engine.rst": """
Context Engine
============

This document provides information about the context engine.

.. include:: ../../architecture/CONTEXT_ENGINE.md
   :parser: myst_parser.sphinx_
""",
        "docs/architecture/agent_coordination.rst": """
Agent Coordination
===============

This document provides information about agent coordination.

.. include:: ../../architecture/AGENT_COORDINATION.md
   :parser: myst_parser.sphinx_
""",
        "docs/architecture/plugin_system.rst": """
Plugin System
===========

This document provides information about the plugin system.

.. include:: ../../architecture/PLUGIN_SYSTEM.md
   :parser: myst_parser.sphinx_
""",
        "docs/architecture/template_engine.rst": """
Template Engine
============

This document provides information about the template engine.

.. include:: ../../architecture/TEMPLATE_ENGINE.md
   :parser: myst_parser.sphinx_
""",
        
        # API
        "docs/api/memory.rst": """
Memory API
========

This document provides reference documentation for the Memory API.

.. automodule:: augment_adam.memory
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: augment_adam.memory.core
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: augment_adam.memory.vector
   :members:
   :undoc-members:
   :show-inheritance:
""",
        "docs/api/context_engine.rst": """
Context Engine API
===============

This document provides reference documentation for the Context Engine API.

.. automodule:: augment_adam.context_engine
   :members:
   :undoc-members:
   :show-inheritance:
""",
        "docs/api/agent.rst": """
Agent API
=======

This document provides reference documentation for the Agent API.

.. automodule:: augment_adam.ai_agent
   :members:
   :undoc-members:
   :show-inheritance:
""",
        "docs/api/plugin.rst": """
Plugin API
========

This document provides reference documentation for the Plugin API.

.. automodule:: augment_adam.plugins
   :members:
   :undoc-members:
   :show-inheritance:
""",
        "docs/api/template.rst": """
Template API
=========

This document provides reference documentation for the Template API.

.. automodule:: augment_adam.utils.templates
   :members:
   :undoc-members:
   :show-inheritance:
"""
    }
    
    for file_path, content in files.items():
        with open(file_path, "w") as f:
            f.write(content)
        print(f"  Created {file_path}")

def main():
    """Main function."""
    print("Setting up a simple, working Sphinx documentation structure...")
    
    # Create the directory structure
    create_directory_structure()
    
    # Copy the configuration files
    copy_configuration_files()
    
    # Create the index file
    create_index_file()
    
    # Create the section index files
    create_section_index_files()
    
    # Create simple RST files
    create_simple_rst_files()
    
    print("\nDone!")
    print("\nTo build the documentation, run:")
    print("cd docs && sphinx-build -b html . _build/html")
    print("\nTo view the documentation, run:")
    print("cd docs/_build/html && python -m http.server 8033")

if __name__ == "__main__":
    main()
