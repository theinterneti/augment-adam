#!/usr/bin/env python3
"""
Script to add cross-references to Sphinx documentation.
"""

import os
import re
from pathlib import Path

def add_cross_references():
    """Add cross-references to documentation files."""
    print("Adding cross-references...")
    
    # Define the files to update
    files = {
        "docs/architecture/overview.rst": """
Overview
========

This document provides an overview of the Augment Adam architecture.

.. include:: ../../docs/architecture/ARCHITECTURE.md
   :parser: myst_parser.sphinx_

See Also
--------

* :doc:`memory_system` - Memory System documentation
* :doc:`context_engine` - Context Engine documentation
* :doc:`agent_coordination` - Agent Coordination documentation
* :doc:`plugin_system` - Plugin System documentation
* :doc:`template_engine` - Template Engine documentation
* :doc:`../developer_guide/contributing` - Contributing guidelines
* :doc:`../developer_guide/testing_framework` - Testing Framework documentation
""",
        "docs/architecture/memory_system.rst": """
Memory System
============

This document provides information about the memory system.

.. include:: ../../docs/architecture/MEMORY_SYSTEM.md
   :parser: myst_parser.sphinx_

See Also
--------

* :doc:`overview` - Architecture overview
* :doc:`context_engine` - Context Engine documentation
* :doc:`../api/memory` - Memory API reference
""",
        "docs/architecture/context_engine.rst": """
Context Engine
=============

This document provides information about the context engine.

.. include:: ../../docs/architecture/CONTEXT_ENGINE.md
   :parser: myst_parser.sphinx_

See Also
--------

* :doc:`overview` - Architecture overview
* :doc:`memory_system` - Memory System documentation
* :doc:`../api/context_engine` - Context Engine API reference
""",
        "docs/architecture/agent_coordination.rst": """
Agent Coordination
=================

This document provides information about agent coordination.

.. include:: ../../docs/architecture/AGENT_COORDINATION.md
   :parser: myst_parser.sphinx_

See Also
--------

* :doc:`overview` - Architecture overview
* :doc:`../api/agent` - Agent API reference
""",
        "docs/architecture/plugin_system.rst": """
Plugin System
============

This document provides information about the plugin system.

.. include:: ../../docs/architecture/PLUGIN_SYSTEM.md
   :parser: myst_parser.sphinx_

See Also
--------

* :doc:`overview` - Architecture overview
* :doc:`../api/plugin` - Plugin API reference
""",
        "docs/architecture/template_engine.rst": """
Template Engine
==============

This document provides information about the template engine.

.. include:: ../../docs/architecture/TEMPLATE_ENGINE.md
   :parser: myst_parser.sphinx_

See Also
--------

* :doc:`overview` - Architecture overview
* :doc:`../api/template` - Template API reference
""",
        "docs/developer_guide/contributing.rst": """
Contributing
===========

This document provides guidelines for contributing to Augment Adam.

.. include:: ../../docs/development/CONTRIBUTING.md
   :parser: myst_parser.sphinx_

See Also
--------

* :doc:`testing_framework` - Testing Framework documentation
* :doc:`../architecture/overview` - Architecture overview
""",
        "docs/developer_guide/testing_framework.rst": """
Testing Framework
===============

This document provides information about the testing framework.

.. include:: ../../docs/architecture/TESTING_FRAMEWORK.md
   :parser: myst_parser.sphinx_

See Also
--------

* :doc:`contributing` - Contributing guidelines
* :doc:`../architecture/overview` - Architecture overview
""",
        "docs/user_guide/installation.rst": """
Installation
===========

This document provides instructions for installing Augment Adam.

.. include:: ../../docs/user_guide/installation.md
   :parser: myst_parser.sphinx_

See Also
--------

* :doc:`getting_started` - Getting started guide
* :doc:`configuration` - Configuration guide
""",
        "docs/user_guide/getting_started.rst": """
Getting Started
=============

This document provides a guide to getting started with Augment Adam.

.. include:: ../../docs/user_guide/getting_started.md
   :parser: myst_parser.sphinx_

See Also
--------

* :doc:`installation` - Installation guide
* :doc:`configuration` - Configuration guide
* :doc:`quickstart` - Quickstart guide
""",
        "docs/user_guide/configuration.rst": """
Configuration
============

This document provides information about configuring Augment Adam.

.. include:: ../../docs/user_guide/configuration.md
   :parser: myst_parser.sphinx_

See Also
--------

* :doc:`installation` - Installation guide
* :doc:`getting_started` - Getting started guide
""",
        "docs/user_guide/quickstart.rst": """
Quickstart
=========

This document provides a quickstart guide for Augment Adam.

.. include:: ../../docs/user_guide/quickstart.md
   :parser: myst_parser.sphinx_

See Also
--------

* :doc:`installation` - Installation guide
* :doc:`getting_started` - Getting started guide
* :doc:`configuration` - Configuration guide
""",
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

See Also
--------

* :doc:`../architecture/memory_system` - Memory System documentation
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

See Also
--------

* :doc:`../architecture/context_engine` - Context Engine documentation
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

See Also
--------

* :doc:`../architecture/agent_coordination` - Agent Coordination documentation
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

See Also
--------

* :doc:`../architecture/plugin_system` - Plugin System documentation
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

See Also
--------

* :doc:`../architecture/template_engine` - Template Engine documentation
"""
    }
    
    # Write the updated files
    for file_path, content in files.items():
        with open(file_path, "w") as f:
            f.write(content)
        print(f"  Added cross-references to {file_path}")

def main():
    """Main function."""
    print("Adding cross-references to Sphinx documentation...")
    
    # Add cross-references
    add_cross_references()
    
    print("Done!")

if __name__ == "__main__":
    main()
