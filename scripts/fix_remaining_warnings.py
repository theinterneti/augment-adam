#!/usr/bin/env python3
"""
Script to fix remaining warnings in Sphinx documentation.
"""

import os
import re
import glob
from pathlib import Path

def fix_duplicate_files():
    """Fix duplicate files warnings."""
    print("Fixing duplicate files warnings...")
    
    # Remove duplicate .md files that conflict with .rst files
    duplicate_files = [
        "docs/index.md",
        "docs/architecture/memory_system.md",
        "docs/architecture/plugin_system.md",
        "docs/user_guide/configuration.md",
        "docs/user_guide/getting_started.md",
        "docs/user_guide/installation.md",
        "docs/user_guide/quickstart.md"
    ]
    
    for file_path in duplicate_files:
        if os.path.exists(file_path):
            os.rename(file_path, f"{file_path}.bak")
            print(f"  Renamed {file_path} to {file_path}.bak")

def fix_missing_toctree_entries():
    """Fix missing toctree entries."""
    print("Fixing missing toctree entries...")
    
    # Create missing example files
    example_files = {
        "docs/examples/basic_example.rst": """
Basic Example
============

This document provides a basic example of using Augment Adam.

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine
    from augment_adam.ai_agent import Agent

    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")

    # Initialize context engine
    context_engine = ContextEngine(memory=memory)

    # Initialize agent
    agent = Agent(context_engine=context_engine)

    # Run the agent
    response = agent.run("What is the capital of France?")
    print(response)
""",
        "docs/examples/memory_example.rst": """
Memory Example
============

This document provides an example of using the Memory System.

.. code-block:: python

    from augment_adam.memory import VectorMemory

    # Initialize memory
    memory = VectorMemory()

    # Add data to memory
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")

    # Search memory
    results = memory.search("capital of France")
    print(results)  # ["Paris is the capital of France"]

    # Add data with metadata
    memory.add(
        "Madrid is the capital of Spain",
        metadata={"country": "Spain", "continent": "Europe"}
    )

    # Search with metadata filter
    results = memory.search(
        "capital",
        filter={"continent": "Europe"}
    )
    print(results)  # ["Madrid is the capital of Spain"]
""",
        "docs/examples/context_engine_example.rst": """
Context Engine Example
===================

This document provides an example of using the Context Engine.

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine

    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")

    # Initialize context engine
    context_engine = ContextEngine(memory=memory)

    # Get context
    context = context_engine.get_context("What is the capital of France?")
    print(context)  # ["Paris is the capital of France"]

    # Get context with additional parameters
    context = context_engine.get_context(
        "What are the capitals in Europe?",
        max_results=3,
        threshold=0.7
    )
    print(context)  # ["Paris is the capital of France", "Berlin is the capital of Germany", "Rome is the capital of Italy"]
""",
        "docs/examples/agent_example.rst": """
Agent Example
===========

This document provides an example of using the Agent API.

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine
    from augment_adam.ai_agent import Agent

    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")

    # Initialize context engine
    context_engine = ContextEngine(memory=memory)

    # Initialize agent
    agent = Agent(context_engine=context_engine)

    # Run the agent
    response = agent.run("What is the capital of France?")
    print(response)  # "The capital of France is Paris."

    # Run the agent with additional parameters
    response = agent.run(
        "What are the capitals in Europe?",
        max_tokens=100,
        temperature=0.7
    )
    print(response)  # "The capitals in Europe include Paris (France), Berlin (Germany), and Rome (Italy)."
""",
        "docs/examples/plugin_example.rst": """
Plugin Example
============

This document provides an example of using the Plugin System.

.. code-block:: python

    from augment_adam.plugins import PluginRegistry, Plugin

    # Define a plugin
    class CalculatorPlugin(Plugin):
        name = "calculator"
        description = "A plugin for performing calculations"
        
        def add(self, a, b):
            return a + b
        
        def subtract(self, a, b):
            return a - b
        
        def multiply(self, a, b):
            return a * b
        
        def divide(self, a, b):
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b

    # Initialize plugin registry
    registry = PluginRegistry()

    # Register plugin
    registry.register(CalculatorPlugin())

    # Use plugin
    calculator = registry.get_plugin("calculator")
    result = calculator.add(2, 3)
    print(result)  # 5

    result = calculator.multiply(4, 5)
    print(result)  # 20
"""
    }
    
    # Create missing tutorial files
    tutorial_files = {
        "docs/tutorials/quickstart.rst": """
Quickstart
=========

This document provides a quickstart guide for Augment Adam.

Getting Started
-------------

To get started with Augment Adam, follow these steps:

1. Install Augment Adam:

   .. code-block:: bash

      pip install augment-adam

2. Import the necessary modules:

   .. code-block:: python

      from augment_adam.memory import VectorMemory
      from augment_adam.context_engine import ContextEngine
      from augment_adam.ai_agent import Agent

3. Initialize the components:

   .. code-block:: python

      memory = VectorMemory()
      context_engine = ContextEngine(memory=memory)
      agent = Agent(context_engine=context_engine)

4. Run the agent:

   .. code-block:: python

      response = agent.run("What is the capital of France?")
      print(response)

Next Steps
---------

- Learn more about the :doc:`memory_tutorial`
- Learn more about the :doc:`context_engine_tutorial`
- Learn more about the :doc:`agent_tutorial`
- Learn more about the :doc:`plugin_tutorial`
""",
        "docs/tutorials/memory_tutorial.rst": """
Memory Tutorial
=============

This document provides a tutorial for using the Memory System.

Introduction
-----------

The Memory System provides various memory implementations for storing and retrieving information.

Vector Memory
-----------

The most common memory implementation is the Vector Memory, which stores and retrieves information using vector embeddings.

.. code-block:: python

    from augment_adam.memory import VectorMemory

    # Initialize memory
    memory = VectorMemory()

    # Add data to memory
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")

    # Search memory
    results = memory.search("capital of France")
    print(results)  # ["Paris is the capital of France"]

Advanced Usage
------------

You can also add metadata to your memory entries:

.. code-block:: python

    # Add data with metadata
    memory.add(
        "Madrid is the capital of Spain",
        metadata={"country": "Spain", "continent": "Europe"}
    )

    # Search with metadata filter
    results = memory.search(
        "capital",
        filter={"continent": "Europe"}
    )
    print(results)  # ["Madrid is the capital of Spain"]

Next Steps
---------

- Learn more about the :doc:`context_engine_tutorial`
- Learn more about the :doc:`agent_tutorial`
- Learn more about the :doc:`plugin_tutorial`
""",
        "docs/tutorials/context_engine_tutorial.rst": """
Context Engine Tutorial
====================

This document provides a tutorial for using the Context Engine.

Introduction
-----------

The Context Engine is responsible for managing and retrieving relevant context for the assistant.

Basic Usage
---------

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine

    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")

    # Initialize context engine
    context_engine = ContextEngine(memory=memory)

    # Get context
    context = context_engine.get_context("What is the capital of France?")
    print(context)  # ["Paris is the capital of France"]

Advanced Usage
------------

You can customize the context retrieval with additional parameters:

.. code-block:: python

    # Get context with additional parameters
    context = context_engine.get_context(
        "What are the capitals in Europe?",
        max_results=3,
        threshold=0.7
    )
    print(context)  # ["Paris is the capital of France", "Berlin is the capital of Germany", "Rome is the capital of Italy"]

Next Steps
---------

- Learn more about the :doc:`memory_tutorial`
- Learn more about the :doc:`agent_tutorial`
- Learn more about the :doc:`plugin_tutorial`
""",
        "docs/tutorials/agent_tutorial.rst": """
Agent Tutorial
============

This document provides a tutorial for using the Agent API.

Introduction
-----------

The Agent API provides a high-level interface for creating and running AI agents.

Basic Usage
---------

.. code-block:: python

    from augment_adam.memory import VectorMemory
    from augment_adam.context_engine import ContextEngine
    from augment_adam.ai_agent import Agent

    # Initialize memory
    memory = VectorMemory()
    memory.add("Paris is the capital of France")
    memory.add("Berlin is the capital of Germany")
    memory.add("Rome is the capital of Italy")

    # Initialize context engine
    context_engine = ContextEngine(memory=memory)

    # Initialize agent
    agent = Agent(context_engine=context_engine)

    # Run the agent
    response = agent.run("What is the capital of France?")
    print(response)  # "The capital of France is Paris."

Advanced Usage
------------

You can customize the agent's behavior with additional parameters:

.. code-block:: python

    # Run the agent with additional parameters
    response = agent.run(
        "What are the capitals in Europe?",
        max_tokens=100,
        temperature=0.7
    )
    print(response)  # "The capitals in Europe include Paris (France), Berlin (Germany), and Rome (Italy)."

Next Steps
---------

- Learn more about the :doc:`memory_tutorial`
- Learn more about the :doc:`context_engine_tutorial`
- Learn more about the :doc:`plugin_tutorial`
""",
        "docs/tutorials/plugin_tutorial.rst": """
Plugin Tutorial
=============

This document provides a tutorial for using the Plugin System.

Introduction
-----------

The Plugin System enables the extension of the assistant's capabilities through plugins.

Creating a Plugin
--------------

.. code-block:: python

    from augment_adam.plugins import Plugin

    class CalculatorPlugin(Plugin):
        name = "calculator"
        description = "A plugin for performing calculations"
        
        def add(self, a, b):
            return a + b
        
        def subtract(self, a, b):
            return a - b
        
        def multiply(self, a, b):
            return a * b
        
        def divide(self, a, b):
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b

Registering and Using a Plugin
---------------------------

.. code-block:: python

    from augment_adam.plugins import PluginRegistry

    # Initialize plugin registry
    registry = PluginRegistry()

    # Register plugin
    registry.register(CalculatorPlugin())

    # Use plugin
    calculator = registry.get_plugin("calculator")
    result = calculator.add(2, 3)
    print(result)  # 5

    result = calculator.multiply(4, 5)
    print(result)  # 20

Next Steps
---------

- Learn more about the :doc:`memory_tutorial`
- Learn more about the :doc:`context_engine_tutorial`
- Learn more about the :doc:`agent_tutorial`
"""
    }
    
    # Create the files
    for file_path, content in example_files.items():
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write the file
        with open(file_path, "w") as f:
            f.write(content)
        print(f"  Created {file_path}")
    
    for file_path, content in tutorial_files.items():
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write the file
        with open(file_path, "w") as f:
            f.write(content)
        print(f"  Created {file_path}")

def fix_index_rst():
    """Fix the index.rst file."""
    print("Fixing index.rst file...")
    
    # Create a new index.rst file
    index_content = """
Augment Adam Documentation
=======================

Welcome to the Augment Adam documentation!

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/installation
   user_guide/getting_started
   user_guide/configuration
   user_guide/quickstart

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide

   developer_guide/contributing
   developer_guide/testing_framework

.. toctree::
   :maxdepth: 2
   :caption: Architecture

   architecture/overview
   architecture/memory_system
   architecture/context_engine
   architecture/agent_coordination
   architecture/plugin_system
   architecture/template_engine

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/memory
   api/context_engine
   api/agent
   api/plugin
   api/template

.. toctree::
   :maxdepth: 2
   :caption: Tutorials

   tutorials/quickstart
   tutorials/memory_tutorial
   tutorials/context_engine_tutorial
   tutorials/agent_tutorial
   tutorials/plugin_tutorial

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/basic_example
   examples/memory_example
   examples/context_engine_example
   examples/agent_example
   examples/plugin_example

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""
    
    with open("docs/index.rst", "w") as f:
        f.write(index_content)
    
    print("  Fixed docs/index.rst")

def create_documentation_guide():
    """Create a documentation guide."""
    print("Creating documentation guide...")
    
    # Create the documentation guide
    guide_content = """
Documentation Guide
=================

This document provides guidelines for contributing to the Augment Adam documentation.

Documentation Structure
---------------------

The Augment Adam documentation is organized into the following sections:

* **User Guide**: Documentation for users of Augment Adam
* **Developer Guide**: Documentation for developers of Augment Adam
* **Architecture**: Documentation of the Augment Adam architecture
* **API Reference**: Reference documentation for the Augment Adam API
* **Tutorials**: Step-by-step tutorials for using Augment Adam
* **Examples**: Example code for using Augment Adam

Writing Documentation
------------------

When writing documentation, please follow these guidelines:

* Use clear, concise language
* Use proper grammar and spelling
* Use consistent terminology
* Use code examples where appropriate
* Use cross-references to other documentation
* Use diagrams to illustrate complex concepts

reStructuredText Syntax
---------------------

The Augment Adam documentation uses reStructuredText (RST) syntax. Here are some common RST constructs:

Headings
~~~~~~~

::

    Heading 1
    =========

    Heading 2
    ---------

    Heading 3
    ~~~~~~~~~

Lists
~~~~

::

    * Item 1
    * Item 2
    * Item 3

    1. Item 1
    2. Item 2
    3. Item 3

Code Blocks
~~~~~~~~~~

::

    .. code-block:: python

        def hello_world():
            print("Hello, world!")

Links
~~~~

::

    `Link text <https://example.com>`_

    :doc:`Link to another document <document_name>`

Images
~~~~~

::

    .. image:: path/to/image.png
       :alt: Alt text
       :width: 400px

Tables
~~~~~

::

    +------------+------------+------------+
    | Header 1   | Header 2   | Header 3   |
    +============+============+============+
    | Cell 1     | Cell 2     | Cell 3     |
    +------------+------------+------------+
    | Cell 4     | Cell 5     | Cell 6     |
    +------------+------------+------------+

Building the Documentation
-----------------------

To build the documentation, run:

.. code-block:: bash

    python scripts/build_simple_docs.py

To view the documentation, run:

.. code-block:: bash

    cd docs/_build/html && python -m http.server 8033

Then open a browser and navigate to http://localhost:8033.

Contributing Documentation
-----------------------

To contribute documentation:

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

Please ensure that your documentation builds successfully before submitting a pull request.
"""
    
    with open("docs/developer_guide/documentation_guide.rst", "w") as f:
        f.write(guide_content)
    
    print("  Created docs/developer_guide/documentation_guide.rst")
    
    # Update the developer guide index
    with open("docs/developer_guide/index.rst", "r") as f:
        content = f.read()
    
    if "documentation_guide" not in content:
        content = content.replace("   testing_framework", "   testing_framework\n   documentation_guide")
        
        with open("docs/developer_guide/index.rst", "w") as f:
            f.write(content)
        
        print("  Updated docs/developer_guide/index.rst")

def main():
    """Main function."""
    print("Fixing remaining warnings in Sphinx documentation...")
    
    # Fix duplicate files
    fix_duplicate_files()
    
    # Fix missing toctree entries
    fix_missing_toctree_entries()
    
    # Fix index.rst
    fix_index_rst()
    
    # Create documentation guide
    create_documentation_guide()
    
    print("Done!")

if __name__ == "__main__":
    main()
