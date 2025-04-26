
Plugin API
=========

This document provides reference documentation for the Plugin API.

Overview
-------

The Plugin API enables the extension of the assistant's capabilities through plugins.

Core Components
-------------

* **Plugin**: Base class for plugins
* **PluginRegistry**: Registry for plugins
* **PluginLoader**: Loads plugins
* **PluginExecutor**: Executes plugins

Usage
----

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

API Reference
-----------

.. automodule:: augment_adam.plugins
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

See Also
--------

* :doc:`../architecture/plugin_system` - Plugin System documentation
