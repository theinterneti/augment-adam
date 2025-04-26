Advanced Plugin Example
=======================

This document provides advanced examples of using the Plugin System.

Plugin with Configuration
-------------------------

This example shows how to create a plugin with configuration:

.. code-block:: python

    from augment_adam.plugins import Plugin, PluginRegistry
    
    # Define a plugin with configuration
    class WeatherPlugin(Plugin):
        name = "weather"
        description = "A plugin for getting weather information"
        
        def __init__(self, api_key=None, units="metric"):
            self.api_key = api_key
            self.units = units
        
        def configure(self, api_key, units="metric"):
            self.api_key = api_key
            self.units = units
        
        def get_weather(self, location):
            # This is a simplified example - in practice, you would call a weather API
            if not self.api_key:
                raise ValueError("API key not configured")
            
            if location.lower() == "paris":
                temp = 25 if self.units == "metric" else 77
                return f"Sunny, {temp}°{'C' if self.units == 'metric' else 'F'}"
            elif location.lower() == "berlin":
                temp = 18 if self.units == "metric" else 64
                return f"Cloudy, {temp}°{'C' if self.units == 'metric' else 'F'}"
            elif location.lower() == "rome":
                temp = 30 if self.units == "metric" else 86
                return f"Sunny, {temp}°{'C' if self.units == 'metric' else 'F'}"
            else:
                return "Unknown location"
    
    # Initialize plugin registry
    registry = PluginRegistry()
    
    # Register plugin
    weather_plugin = WeatherPlugin()
    registry.register(weather_plugin)
    
    # Configure plugin
    weather_plugin.configure(api_key="your_api_key", units="imperial")
    
    # Use plugin
    weather = registry.get_plugin("weather")
    result = weather.get_weather("Paris")
    print(result)  # "Sunny, 77°F"

Plugin with Dependencies
------------------------

This example shows how to create a plugin with dependencies:

.. code-block:: python

    from augment_adam.plugins import Plugin, PluginRegistry
    
    # Define a database plugin
    class DatabasePlugin(Plugin):
        name = "database"
        description = "A plugin for database operations"
        
        def __init__(self):
            self.data = {}
        
        def set(self, key, value):
            self.data[key] = value
        
        def get(self, key):
            return self.data.get(key)
    
    # Define a cache plugin that depends on the database plugin
    class CachePlugin(Plugin):
        name = "cache"
        description = "A plugin for caching operations"
        dependencies = ["database"]
        
        def __init__(self):
            self.cache = {}
            self.database = None
        
        def set_dependencies(self, **dependencies):
            self.database = dependencies["database"]
        
        def get(self, key):
            # Check cache first
            if key in self.cache:
                return self.cache[key]
            
            # If not in cache, check database
            value = self.database.get(key)
            if value is not None:
                # Store in cache for next time
                self.cache[key] = value
            
            return value
        
        def set(self, key, value):
            # Store in cache
            self.cache[key] = value
            
            # Store in database
            self.database.set(key, value)
    
    # Initialize plugin registry
    registry = PluginRegistry()
    
    # Register plugins
    registry.register(DatabasePlugin())
    registry.register(CachePlugin())
    
    # Get plugins
    database = registry.get_plugin("database")
    cache = registry.get_plugin("cache")
    
    # Use plugins
    database.set("greeting", "Hello, world!")
    result = cache.get("greeting")
    print(result)  # "Hello, world!"
    
    cache.set("farewell", "Goodbye, world!")
    result = database.get("farewell")
    print(result)  # "Goodbye, world!"

Plugin with Lifecycle Hooks
---------------------------

This example shows how to create a plugin with lifecycle hooks:

.. code-block:: python

    from augment_adam.plugins import Plugin, PluginRegistry
    
    # Define a plugin with lifecycle hooks
    class LoggerPlugin(Plugin):
        name = "logger"
        description = "A plugin for logging"
        
        def __init__(self):
            self.logs = []
        
        def on_load(self):
            print("Logger plugin loaded")
            self.log("Plugin loaded")
        
        def on_unload(self):
            print("Logger plugin unloaded")
            self.log("Plugin unloaded")
        
        def log(self, message):
            self.logs.append(message)
            print(f"Log: {message}")
        
        def get_logs(self):
            return self.logs
    
    # Initialize plugin registry
    registry = PluginRegistry()
    
    # Register plugin (triggers on_load)
    registry.register(LoggerPlugin())
    
    # Get plugin
    logger = registry.get_plugin("logger")
    
    # Use plugin
    logger.log("Hello, world!")
    
    # Unregister plugin (triggers on_unload)
    registry.unregister("logger")

Plugin Discovery and Auto-Loading
---------------------------------

This example shows how to use plugin discovery and auto-loading:

.. code-block:: python

    from augment_adam.plugins import Plugin, PluginRegistry
    
    # Define plugins in separate files
    # plugins/weather.py
    class WeatherPlugin(Plugin):
        name = "weather"
        description = "A plugin for getting weather information"
        
        def get_weather(self, location):
            # Implementation...
            pass
    
    # plugins/calculator.py
    class CalculatorPlugin(Plugin):
        name = "calculator"
        description = "A plugin for performing calculations"
        
        def add(self, a, b):
            return a + b
        
        def subtract(self, a, b):
            return a - b
    
    # Main code
    # Initialize plugin registry with auto-discovery
    registry = PluginRegistry(plugin_dir="plugins", auto_discover=True)
    
    # All plugins in the plugins directory are automatically loaded
    
    # Get plugins
    weather = registry.get_plugin("weather")
    calculator = registry.get_plugin("calculator")
    
    # Use plugins
    result = calculator.add(2, 3)
    print(result)  # 5
    
    result = weather.get_weather("Paris")
    print(result)

See Also
--------

* :doc:`plugin_example` - Basic plugin example
* :doc:`../api/plugin` - Plugin API reference
* :doc:`../tutorials/plugin_tutorial` - Plugin tutorial
