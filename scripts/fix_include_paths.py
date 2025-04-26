#!/usr/bin/env python3
"""
Script to fix include paths in RST files.
"""

import os
import re

def fix_include_paths():
    """Fix include directive paths in RST files."""
    print("Fixing include directive paths...")
    
    # Define the files to fix
    files = {
        "docs/architecture/agent_coordination.rst": """
Agent Coordination
===============

This document provides information about agent coordination.

.. include:: ../../architecture/AGENT_COORDINATION.md
   :parser: myst_parser.sphinx_
""",
        "docs/architecture/context_engine.rst": """
Context Engine
============

This document provides information about the context engine.

.. include:: ../../architecture/CONTEXT_ENGINE.md
   :parser: myst_parser.sphinx_
""",
        "docs/architecture/memory_system.rst": """
Memory System
===========

This document provides information about the memory system.

.. include:: ../../architecture/MEMORY_SYSTEM.md
   :parser: myst_parser.sphinx_
""",
        "docs/architecture/overview.rst": """
Overview
=======

This document provides an overview of the Augment Adam architecture.

.. include:: ../../architecture/ARCHITECTURE.md
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
"""
    }
    
    # Write the fixed files
    for file_path, content in files.items():
        with open(file_path, "w") as f:
            f.write(content)
        print(f"  Fixed {file_path}")

def main():
    """Main function."""
    fix_include_paths()
    print("Done!")

if __name__ == "__main__":
    main()
