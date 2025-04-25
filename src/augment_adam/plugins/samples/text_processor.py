"""
Text Processor plugin.

This module provides a Text Processor plugin to demonstrate the plugin system.
"""

from typing import Dict, Any

from augment_adam.plugins.interface import Plugin, PluginMetadata, PluginType, PluginCategory, PluginHook


class TextProcessorPlugin(Plugin):
    """
    Text Processor plugin.
    
    This plugin processes text in the context, applying various transformations.
    """
    
    metadata = PluginMetadata(
        name="text_processor",
        description="A plugin for processing text",
        version="0.1.0",
        author="Augment Adam",
        plugin_type=PluginType.UTILITY,
        category=PluginCategory.CORE,
        hooks={PluginHook.PRE_PROCESS, PluginHook.PROCESS, PluginHook.POST_PROCESS},
        tags=["sample", "text", "processor"],
    )
    
    def _initialize(self) -> None:
        """Initialize the plugin."""
        # Get configuration options, or use defaults
        self.to_upper = self.config.get("to_upper", False)
        self.to_lower = self.config.get("to_lower", False)
        self.reverse = self.config.get("reverse", False)
        self.prefix = self.config.get("prefix", "")
        self.suffix = self.config.get("suffix", "")
    
    def _cleanup(self) -> None:
        """Clean up the plugin."""
        pass
    
    def _execute(self, hook: PluginHook, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the plugin.
        
        Args:
            hook: The hook to execute.
            context: The context for execution.
            
        Returns:
            The updated context.
        """
        # Check if text is in context
        if "text" not in context:
            return context
        
        # Get text from context
        text = context["text"]
        
        # Apply transformations based on hook
        if hook == PluginHook.PRE_PROCESS:
            # Apply prefix
            text = self.prefix + text
        
        elif hook == PluginHook.PROCESS:
            # Apply case transformations
            if self.to_upper:
                text = text.upper()
            elif self.to_lower:
                text = text.lower()
            
            # Apply reverse
            if self.reverse:
                text = text[::-1]
        
        elif hook == PluginHook.POST_PROCESS:
            # Apply suffix
            text = text + self.suffix
        
        # Update context
        context["text"] = text
        
        return context
