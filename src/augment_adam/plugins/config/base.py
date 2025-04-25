"""
Base classes for plugin configuration.

This module provides the base classes for plugin configuration, allowing users
to customize plugin behavior.
"""

import os
import json
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type

from augment_adam.utils.tagging import tag, TagCategory


@dataclass
class PluginConfigSchema:
    """
    Schema for plugin configuration.
    
    This class defines the schema for plugin configuration, including the
    properties, required properties, and default values.
    
    Attributes:
        properties: Dictionary of property schemas.
        required: List of required property names.
        default_values: Dictionary of default values.
    
    TODO(Issue #11): Add support for schema validation
    TODO(Issue #11): Implement schema analytics
    """
    
    properties: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)
    default_values: Dict[str, Any] = field(default_factory=dict)
    
    def add_property(
        self,
        name: str,
        type_: str,
        description: str,
        required: bool = False,
        default: Any = None
    ) -> None:
        """
        Add a property to the schema.
        
        Args:
            name: The name of the property.
            type_: The type of the property.
            description: The description of the property.
            required: Whether the property is required.
            default: The default value for the property.
        """
        self.properties[name] = {
            "type": type_,
            "description": description,
        }
        
        if required:
            self.required.append(name)
        
        if default is not None:
            self.default_values[name] = default
    
    def validate(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate a configuration against the schema.
        
        Args:
            config: The configuration to validate.
            
        Returns:
            List of validation error messages.
        """
        errors = []
        
        # Check required properties
        for name in self.required:
            if name not in config:
                errors.append(f"Missing required property: {name}")
        
        # Check property types
        for name, value in config.items():
            if name in self.properties:
                property_schema = self.properties[name]
                
                # Check type
                if property_schema["type"] == "string" and not isinstance(value, str):
                    errors.append(f"Property {name} must be a string")
                elif property_schema["type"] == "number" and not isinstance(value, (int, float)):
                    errors.append(f"Property {name} must be a number")
                elif property_schema["type"] == "integer" and not isinstance(value, int):
                    errors.append(f"Property {name} must be an integer")
                elif property_schema["type"] == "boolean" and not isinstance(value, bool):
                    errors.append(f"Property {name} must be a boolean")
                elif property_schema["type"] == "array" and not isinstance(value, list):
                    errors.append(f"Property {name} must be an array")
                elif property_schema["type"] == "object" and not isinstance(value, dict):
                    errors.append(f"Property {name} must be an object")
        
        return errors
    
    def apply_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply default values to a configuration.
        
        Args:
            config: The configuration to apply defaults to.
            
        Returns:
            The configuration with defaults applied.
        """
        # Create a copy of the configuration
        result = config.copy()
        
        # Apply defaults
        for name, value in self.default_values.items():
            if name not in result:
                result[name] = value
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the schema to a dictionary.
        
        Returns:
            Dictionary representation of the schema.
        """
        return {
            "properties": self.properties,
            "required": self.required,
            "default_values": self.default_values,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginConfigSchema":
        """
        Create a schema from a dictionary.
        
        Args:
            data: Dictionary representation of the schema.
            
        Returns:
            The created schema.
        """
        return cls(
            properties=data.get("properties", {}),
            required=data.get("required", []),
            default_values=data.get("default_values", {}),
        )


@tag("plugins.config")
class PluginConfig:
    """
    Configuration for plugins.
    
    This class manages configuration for plugins, including loading, saving,
    and validating configuration.
    
    Attributes:
        schema: The schema for the configuration.
        config: The configuration data.
    
    TODO(Issue #11): Add support for config validation
    TODO(Issue #11): Implement config analytics
    """
    
    def __init__(
        self,
        schema: Optional[PluginConfigSchema] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the plugin configuration.
        
        Args:
            schema: The schema for the configuration.
            config: The configuration data.
        """
        self.schema = schema or PluginConfigSchema()
        self.config = config or {}
        
        # Apply defaults
        if schema is not None:
            self.config = schema.apply_defaults(self.config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The key for the configuration value.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The configuration value, or the default value if the key doesn't exist.
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: The key for the configuration value.
            value: The value to set.
        """
        self.config[key] = value
    
    def validate(self) -> List[str]:
        """
        Validate the configuration against the schema.
        
        Returns:
            List of validation error messages.
        """
        return self.schema.validate(self.config)
    
    def load(self, file_path: str) -> bool:
        """
        Load configuration from a file.
        
        Args:
            file_path: The path to the configuration file.
            
        Returns:
            True if the configuration was loaded, False otherwise.
        """
        try:
            # Check if file exists
            if not os.path.isfile(file_path):
                return False
            
            # Load configuration
            with open(file_path, "r") as f:
                if file_path.endswith(".json"):
                    self.config = json.load(f)
                elif file_path.endswith(".yaml") or file_path.endswith(".yml"):
                    self.config = yaml.safe_load(f)
                else:
                    return False
            
            # Apply defaults
            self.config = self.schema.apply_defaults(self.config)
            
            return True
        except Exception as e:
            print(f"Error loading configuration from {file_path}: {e}")
            return False
    
    def save(self, file_path: str) -> bool:
        """
        Save configuration to a file.
        
        Args:
            file_path: The path to the configuration file.
            
        Returns:
            True if the configuration was saved, False otherwise.
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save configuration
            with open(file_path, "w") as f:
                if file_path.endswith(".json"):
                    json.dump(self.config, f, indent=2)
                elif file_path.endswith(".yaml") or file_path.endswith(".yml"):
                    yaml.dump(self.config, f)
                else:
                    return False
            
            return True
        except Exception as e:
            print(f"Error saving configuration to {file_path}: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.
        
        Returns:
            Dictionary representation of the configuration.
        """
        return self.config.copy()
    
    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        schema: Optional[PluginConfigSchema] = None
    ) -> "PluginConfig":
        """
        Create a configuration from a dictionary.
        
        Args:
            data: Dictionary representation of the configuration.
            schema: The schema for the configuration.
            
        Returns:
            The created configuration.
        """
        return cls(schema=schema, config=data)
