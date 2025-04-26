
Plugin Example
==============

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
