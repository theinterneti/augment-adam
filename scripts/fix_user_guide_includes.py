#!/usr/bin/env python3
"""
Script to fix user guide include paths.
"""

import os

def create_user_guide_content():
    """Create user guide content."""
    print("Creating user guide content...")
    
    # Define the files to create
    files = {
        "docs/user_guide/installation.rst": """
Installation
===========

This document provides instructions for installing Augment Adam.

Requirements
-----------

* Python 3.8 or higher
* pip
* virtualenv (recommended)

Installation Steps
----------------

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
=============

This document provides a guide to getting started with Augment Adam.

Basic Usage
---------

To get started with Augment Adam, follow these steps:

1. Import the necessary modules:

   .. code-block:: python

      from augment_adam.memory import VectorMemory
      from augment_adam.context_engine import ContextEngine
      from augment_adam.ai_agent import Agent

2. Initialize the components:

   .. code-block:: python

      memory = VectorMemory()
      context_engine = ContextEngine(memory=memory)
      agent = Agent(context_engine=context_engine)

3. Run the agent:

   .. code-block:: python

      response = agent.run("What is the capital of France?")
      print(response)

Advanced Usage
------------

For more advanced usage, see the following sections:

* :doc:`configuration` - Configuration options
* :doc:`../tutorials/memory_tutorial` - Memory System tutorial
* :doc:`../tutorials/context_engine_tutorial` - Context Engine tutorial
* :doc:`../tutorials/agent_tutorial` - Agent tutorial
* :doc:`../tutorials/plugin_tutorial` - Plugin tutorial
""",
        "docs/user_guide/configuration.rst": """
Configuration
============

This document provides information about configuring Augment Adam.

Configuration Options
------------------

Augment Adam can be configured using the following options:

* **Memory System**: Configure the memory system
* **Context Engine**: Configure the context engine
* **Agent**: Configure the agent
* **Plugin System**: Configure the plugin system
* **Template Engine**: Configure the template engine

Memory System Configuration
------------------------

The Memory System can be configured using the following options:

.. code-block:: python

    from augment_adam.memory import VectorMemory

    # Configure the memory system
    memory = VectorMemory(
        embedding_model="text-embedding-ada-002",
        similarity_threshold=0.7,
        max_results=10
    )

Context Engine Configuration
-------------------------

The Context Engine can be configured using the following options:

.. code-block:: python

    from augment_adam.context_engine import ContextEngine

    # Configure the context engine
    context_engine = ContextEngine(
        memory=memory,
        max_context_length=4096,
        max_results=10,
        similarity_threshold=0.7
    )

Agent Configuration
---------------

The Agent can be configured using the following options:

.. code-block:: python

    from augment_adam.ai_agent import Agent

    # Configure the agent
    agent = Agent(
        context_engine=context_engine,
        model="gpt-4",
        max_tokens=1024,
        temperature=0.7
    )

Plugin System Configuration
------------------------

The Plugin System can be configured using the following options:

.. code-block:: python

    from augment_adam.plugins import PluginRegistry

    # Configure the plugin registry
    registry = PluginRegistry(
        plugin_dir="plugins",
        auto_discover=True
    )

Template Engine Configuration
-------------------------

The Template Engine can be configured using the following options:

.. code-block:: python

    from augment_adam.utils.templates import TemplateEngine

    # Configure the template engine
    template_engine = TemplateEngine(
        template_dir="templates",
        auto_discover=True
    )
""",
        "docs/user_guide/quickstart.rst": """
Quickstart
=========

This document provides a quickstart guide for Augment Adam.

Installation
----------

.. code-block:: bash

    pip install augment-adam

Basic Usage
---------

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
    print(response)  # "The capital of France is Paris."

Next Steps
---------

* :doc:`installation` - Installation guide
* :doc:`getting_started` - Getting started guide
* :doc:`configuration` - Configuration guide
* :doc:`../tutorials/memory_tutorial` - Memory System tutorial
* :doc:`../tutorials/context_engine_tutorial` - Context Engine tutorial
* :doc:`../tutorials/agent_tutorial` - Agent tutorial
* :doc:`../tutorials/plugin_tutorial` - Plugin tutorial
"""
    }
    
    # Write the files
    for file_path, content in files.items():
        with open(file_path, "w") as f:
            f.write(content)
        print(f"  Created {file_path}")

def main():
    """Main function."""
    print("Fixing user guide include paths...")
    
    # Create user guide content
    create_user_guide_content()
    
    print("Done!")

if __name__ == "__main__":
    main()
