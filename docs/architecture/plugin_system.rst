
Plugin System
=============

This document provides information about the plugin system.

.. include:: ../../docs/architecture/PLUGIN_SYSTEM.md
   :parser: myst_parser.sphinx_

Plugin System Architecture
--------------------------

.. mermaid::

    graph TD
        Core[Core System] --> |Loads| PluginManager[Plugin Manager]
        PluginManager --> |Discovers| PluginRegistry[Plugin Registry]
        PluginRegistry --> |Registers| Plugin1[Plugin 1]
        PluginRegistry --> |Registers| Plugin2[Plugin 2]
        PluginRegistry --> |Registers| Plugin3[Plugin 3]
        
        Core --> |Requests| PluginManager
        PluginManager --> |Validates| PluginValidator[Plugin Validator]
        PluginValidator --> |Validates| Plugin1
        PluginValidator --> |Validates| Plugin2
        PluginValidator --> |Validates| Plugin3
        
        PluginManager --> |Executes| PluginExecutor[Plugin Executor]
        PluginExecutor --> |Executes| Plugin1
        PluginExecutor --> |Executes| Plugin2
        PluginExecutor --> |Executes| Plugin3
        
        Plugin1 --> |Returns| Result1[Result 1]
        Plugin2 --> |Returns| Result2[Result 2]
        Plugin3 --> |Returns| Result3[Result 3]
        
        Result1 --> |Collects| ResultCollector[Result Collector]
        Result2 --> |Collects| ResultCollector
        Result3 --> |Collects| ResultCollector
        
        ResultCollector --> |Returns| Core
        
        subgraph Plugin System
            PluginManager
            PluginRegistry
            PluginValidator
            PluginExecutor
            ResultCollector
        end
        
        subgraph Plugins
            Plugin1
            Plugin2
            Plugin3
        end

See Also
--------

* :doc:`overview` - Architecture overview
* :doc:`../api/plugin` - Plugin API reference
