"""
Base classes for plugin loader.

This module provides the base classes for the plugin loader, which discovers
and loads plugins from various sources.
"""

import os
import sys
import inspect
import importlib
import importlib.util
import pkgutil
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type, Iterator

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.plugins.interface import Plugin
from augment_adam.plugins.registry import PluginRegistry


@tag("plugins.loader")
class PluginDiscovery(ABC):
    """
    Base class for plugin discovery.
    
    This class defines the interface for plugin discovery, which finds plugins
    from various sources.
    
    TODO(Issue #11): Add support for plugin versioning
    TODO(Issue #11): Implement plugin validation
    """
    
    @abstractmethod
    def discover(self) -> Iterator[Type[Plugin]]:
        """
        Discover plugins.
        
        Returns:
            Iterator of discovered plugin classes.
        """
        pass


@tag("plugins.loader")
class EntryPointDiscovery(PluginDiscovery):
    """
    Discover plugins from entry points.
    
    This class discovers plugins from entry points, which are defined in
    package metadata.
    
    Attributes:
        group: The entry point group to discover plugins from.
    
    TODO(Issue #11): Add support for plugin versioning
    TODO(Issue #11): Implement plugin validation
    """
    
    def __init__(self, group: str = "augment_adam.plugins") -> None:
        """
        Initialize the entry point discovery.
        
        Args:
            group: The entry point group to discover plugins from.
        """
        self.group = group
    
    def discover(self) -> Iterator[Type[Plugin]]:
        """
        Discover plugins from entry points.
        
        Returns:
            Iterator of discovered plugin classes.
        """
        try:
            # Use importlib.metadata for Python 3.8+
            from importlib.metadata import entry_points
            
            # Get entry points for the group
            for entry_point in entry_points().get(self.group, []):
                try:
                    # Load the entry point
                    plugin_class = entry_point.load()
                    
                    # Check if it's a valid plugin class
                    if inspect.isclass(plugin_class) and issubclass(plugin_class, Plugin) and plugin_class is not Plugin:
                        yield plugin_class
                except Exception as e:
                    print(f"Error loading plugin from entry point {entry_point.name}: {e}")
        except ImportError:
            # Fall back to pkg_resources for Python < 3.8
            try:
                import pkg_resources
                
                # Get entry points for the group
                for entry_point in pkg_resources.iter_entry_points(self.group):
                    try:
                        # Load the entry point
                        plugin_class = entry_point.load()
                        
                        # Check if it's a valid plugin class
                        if inspect.isclass(plugin_class) and issubclass(plugin_class, Plugin) and plugin_class is not Plugin:
                            yield plugin_class
                    except Exception as e:
                        print(f"Error loading plugin from entry point {entry_point.name}: {e}")
            except ImportError:
                # If pkg_resources is not available, return an empty iterator
                return


@tag("plugins.loader")
class DirectoryDiscovery(PluginDiscovery):
    """
    Discover plugins from a directory.
    
    This class discovers plugins from Python modules in a directory.
    
    Attributes:
        directory: The directory to discover plugins from.
        recursive: Whether to recursively discover plugins from subdirectories.
    
    TODO(Issue #11): Add support for plugin versioning
    TODO(Issue #11): Implement plugin validation
    """
    
    def __init__(self, directory: str, recursive: bool = True) -> None:
        """
        Initialize the directory discovery.
        
        Args:
            directory: The directory to discover plugins from.
            recursive: Whether to recursively discover plugins from subdirectories.
        """
        self.directory = directory
        self.recursive = recursive
    
    def discover(self) -> Iterator[Type[Plugin]]:
        """
        Discover plugins from a directory.
        
        Returns:
            Iterator of discovered plugin classes.
        """
        # Check if directory exists
        if not os.path.isdir(self.directory):
            return
        
        # Add directory to Python path
        sys.path.insert(0, os.path.abspath(os.path.dirname(self.directory)))
        
        try:
            # Get the package name
            package_name = os.path.basename(self.directory)
            
            # Discover modules
            for _, module_name, is_package in pkgutil.iter_modules([self.directory]):
                # Skip packages if not recursive
                if is_package and not self.recursive:
                    continue
                
                try:
                    # Import the module
                    module = importlib.import_module(f"{package_name}.{module_name}")
                    
                    # Find plugin classes in the module
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, Plugin) and obj is not Plugin:
                            yield obj
                    
                    # Recursively discover plugins from packages
                    if is_package and self.recursive:
                        package_dir = os.path.join(self.directory, module_name)
                        discovery = DirectoryDiscovery(package_dir, recursive=True)
                        
                        for plugin_class in discovery.discover():
                            yield plugin_class
                except Exception as e:
                    print(f"Error loading plugin from module {module_name}: {e}")
        finally:
            # Remove directory from Python path
            if self.directory in sys.path:
                sys.path.remove(self.directory)


@tag("plugins.loader")
class PluginLoader:
    """
    Loader for plugins.
    
    This class loads plugins from various sources and registers them with the
    plugin registry.
    
    Attributes:
        registry: The plugin registry to register plugins with.
        discoveries: List of plugin discoveries to use.
    
    TODO(Issue #11): Add support for plugin versioning
    TODO(Issue #11): Implement plugin validation
    """
    
    def __init__(
        self,
        registry: Optional[PluginRegistry] = None,
        discoveries: Optional[List[PluginDiscovery]] = None
    ) -> None:
        """
        Initialize the plugin loader.
        
        Args:
            registry: The plugin registry to register plugins with. If None, use the default registry.
            discoveries: List of plugin discoveries to use. If None, use the default discoveries.
        """
        self.registry = registry or PluginRegistry()
        self.discoveries = discoveries or [
            EntryPointDiscovery(),
            DirectoryDiscovery(os.path.join(os.path.dirname(__file__), "..", "samples")),
        ]
    
    def load_plugins(self) -> List[Type[Plugin]]:
        """
        Load plugins from all discoveries.
        
        Returns:
            List of loaded plugin classes.
        """
        loaded_plugins = []
        
        # Discover and register plugins
        for discovery in self.discoveries:
            for plugin_class in discovery.discover():
                try:
                    self.registry.register(plugin_class)
                    loaded_plugins.append(plugin_class)
                except Exception as e:
                    print(f"Error registering plugin {plugin_class.__name__}: {e}")
        
        return loaded_plugins
    
    def load_plugin(self, plugin_path: str) -> Optional[Type[Plugin]]:
        """
        Load a plugin from a Python module.
        
        Args:
            plugin_path: The path to the Python module.
            
        Returns:
            The loaded plugin class, or None if not found.
        """
        try:
            # Split path into module and attribute
            if ":" in plugin_path:
                module_path, attr_name = plugin_path.split(":", 1)
            else:
                module_path, attr_name = plugin_path, None
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Get the plugin class
            if attr_name:
                plugin_class = getattr(module, attr_name)
                
                # Check if it's a valid plugin class
                if not (inspect.isclass(plugin_class) and issubclass(plugin_class, Plugin) and plugin_class is not Plugin):
                    return None
                
                # Register the plugin
                self.registry.register(plugin_class)
                return plugin_class
            else:
                # Find plugin classes in the module
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, Plugin) and obj is not Plugin:
                        # Register the plugin
                        self.registry.register(obj)
                        return obj
            
            return None
        except Exception as e:
            print(f"Error loading plugin from {plugin_path}: {e}")
            return None
    
    def load_plugin_from_file(self, file_path: str) -> Optional[Type[Plugin]]:
        """
        Load a plugin from a Python file.
        
        Args:
            file_path: The path to the Python file.
            
        Returns:
            The loaded plugin class, or None if not found.
        """
        try:
            # Get module name from file path
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Import the module from file
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes in the module
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Plugin) and obj is not Plugin:
                    # Register the plugin
                    self.registry.register(obj)
                    return obj
            
            return None
        except Exception as e:
            print(f"Error loading plugin from file {file_path}: {e}")
            return None
