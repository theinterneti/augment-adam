
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
