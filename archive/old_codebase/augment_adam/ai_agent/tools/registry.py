"""Tool Registry.

This module provides a registry for tools that can be used by AI agents.

Version: 0.1.0
Created: 2025-04-30
"""

import logging
from typing import Dict, List, Any, Optional, Union, Type

from augment_adam.ai_agent.tools.base_tool import Tool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Tool Registry.
    
    This class provides a registry for tools that can be used by AI agents.
    
    Attributes:
        tools: Dictionary mapping tool names to tool instances
    """
    
    def __init__(self):
        """Initialize the Tool Registry."""
        self.tools = {}
        logger.info("Initialized Tool Registry")
    
    def register_tool(self, tool: Tool) -> None:
        """Register a tool.
        
        Args:
            tool: Tool to register
        """
        if tool.name in self.tools:
            logger.warning(f"Tool '{tool.name}' already registered, overwriting")
        
        self.tools[tool.name] = tool
        logger.info(f"Registered tool '{tool.name}'")
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool.
        
        Args:
            tool_name: Name of the tool to unregister
            
        Returns:
            True if tool was unregistered, False otherwise
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Unregistered tool '{tool_name}'")
            return True
        else:
            logger.warning(f"Tool '{tool_name}' not found in registry")
            return False
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name.
        
        Args:
            tool_name: Name of the tool to get
            
        Returns:
            Tool instance or None if not found
        """
        return self.tools.get(tool_name)
    
    def get_all_tools(self) -> Dict[str, Tool]:
        """Get all registered tools.
        
        Returns:
            Dictionary mapping tool names to tool instances
        """
        return self.tools.copy()
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all registered tools.
        
        Returns:
            List of tool schemas
        """
        return [tool.get_schema() for tool in self.tools.values()]
    
    def clear(self) -> None:
        """Clear all registered tools."""
        self.tools.clear()
        logger.info("Cleared all registered tools")


# Global tool registry
_global_registry = ToolRegistry()


def get_global_tool_registry() -> ToolRegistry:
    """Get the global tool registry.
    
    Returns:
        Global tool registry
    """
    global _global_registry
    return _global_registry


def register_tool(tool: Tool) -> None:
    """Register a tool in the global registry.
    
    Args:
        tool: Tool to register
    """
    global _global_registry
    _global_registry.register_tool(tool)


def unregister_tool(tool_name: str) -> bool:
    """Unregister a tool from the global registry.
    
    Args:
        tool_name: Name of the tool to unregister
        
    Returns:
        True if tool was unregistered, False otherwise
    """
    global _global_registry
    return _global_registry.unregister_tool(tool_name)


def get_tool(tool_name: str) -> Optional[Tool]:
    """Get a tool by name from the global registry.
    
    Args:
        tool_name: Name of the tool to get
        
    Returns:
        Tool instance or None if not found
    """
    global _global_registry
    return _global_registry.get_tool(tool_name)


def get_all_tools() -> Dict[str, Tool]:
    """Get all registered tools from the global registry.
    
    Returns:
        Dictionary mapping tool names to tool instances
    """
    global _global_registry
    return _global_registry.get_all_tools()


def get_tool_schemas() -> List[Dict[str, Any]]:
    """Get schemas for all registered tools from the global registry.
    
    Returns:
        List of tool schemas
    """
    global _global_registry
    return _global_registry.get_tool_schemas()


def clear_tools() -> None:
    """Clear all registered tools from the global registry."""
    global _global_registry
    _global_registry.clear()
