"""Base Tool Implementation.

This module provides the base tool implementation for AI agents.

Version: 0.1.0
Created: 2025-04-30
"""

import logging
import inspect
from typing import Dict, List, Any, Optional, Union, Callable
import asyncio

logger = logging.getLogger(__name__)


class Tool:
    """Base Tool class.
    
    This class provides the foundation for all tools in Augment Adam.
    
    Attributes:
        name: Name of the tool
        description: Description of the tool
        parameters: Parameters for the tool
        is_async: Whether the tool supports async execution
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Optional[Dict[str, Dict[str, Any]]] = None,
        is_async: bool = False
    ):
        """Initialize the Tool.
        
        Args:
            name: Name of the tool
            description: Description of the tool
            parameters: Parameters for the tool
            is_async: Whether the tool supports async execution
        """
        self.name = name
        self.description = description
        self.parameters = parameters or {}
        self.is_async = is_async
        
        # Validate execute method
        if not hasattr(self, "execute") or not callable(getattr(self, "execute")):
            raise ValueError(f"Tool {name} must implement execute method")
        
        # Check if async execute method exists
        self.is_async = self.is_async or hasattr(self, "execute_async") and callable(getattr(self, "execute_async"))
        
        logger.info(f"Initialized tool '{name}'")
    
    def execute(self, **kwargs) -> Any:
        """Execute the tool.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        raise NotImplementedError("Tool must implement execute method")
    
    async def execute_async(self, **kwargs) -> Any:
        """Execute the tool asynchronously.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        if not self.is_async:
            # If no async implementation, run execute in a thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: self.execute(**kwargs))
        
        raise NotImplementedError("Tool must implement execute_async method if is_async=True")
    
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate parameters for the tool.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            Validated parameters
            
        Raises:
            ValueError: If parameters are invalid
        """
        validated = {}
        
        # Check required parameters
        for param_name, param_spec in self.parameters.items():
            if param_spec.get("required", False) and param_name not in kwargs:
                raise ValueError(f"Missing required parameter: {param_name}")
        
        # Validate and convert parameters
        for param_name, param_value in kwargs.items():
            if param_name in self.parameters:
                param_spec = self.parameters[param_name]
                
                # Check type
                param_type = param_spec.get("type")
                if param_type and not isinstance(param_value, eval(param_type)):
                    # Try to convert
                    try:
                        param_value = eval(param_type)(param_value)
                    except Exception:
                        raise ValueError(f"Parameter {param_name} must be of type {param_type}")
                
                # Check enum
                param_enum = param_spec.get("enum")
                if param_enum and param_value not in param_enum:
                    raise ValueError(f"Parameter {param_name} must be one of: {param_enum}")
                
                # Add to validated parameters
                validated[param_name] = param_value
            else:
                # Unknown parameter, add as is
                validated[param_name] = param_value
        
        # Add default values for missing parameters
        for param_name, param_spec in self.parameters.items():
            if param_name not in validated and "default" in param_spec:
                validated[param_name] = param_spec["default"]
        
        return validated
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the schema for the tool.
        
        Returns:
            Tool schema
        """
        # Get execute method signature
        sig = inspect.signature(self.execute)
        
        # Build schema
        schema = {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        
        # Add parameters
        for param_name, param_spec in self.parameters.items():
            schema["parameters"]["properties"][param_name] = {
                "type": param_spec.get("type", "string"),
                "description": param_spec.get("description", "")
            }
            
            # Add enum if present
            if "enum" in param_spec:
                schema["parameters"]["properties"][param_name]["enum"] = param_spec["enum"]
            
            # Add required parameters
            if param_spec.get("required", False):
                schema["parameters"]["required"].append(param_name)
        
        return schema
