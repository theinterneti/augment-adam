"""
Documentation formatter.

This module provides a formatter for formatting documentation in various formats.
"""

import re
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type

from augment_adam.utils.tagging import tag, TagCategory


@tag("docs.utils")
class DocFormatter:
    """
    Formatter for documentation.
    
    This class formats documentation in various formats, including Markdown,
    reStructuredText, and HTML.
    
    Attributes:
        metadata: Additional metadata for the formatter.
    
    TODO(Issue #12): Add support for more documentation formats
    TODO(Issue #12): Implement formatter validation
    """
    
    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the documentation formatter.
        
        Args:
            metadata: Additional metadata for the formatter.
        """
        self.metadata = metadata or {}
    
    def format_markdown(self, data: Dict[str, Any]) -> str:
        """
        Format documentation data as Markdown.
        
        Args:
            data: The documentation data to format.
            
        Returns:
            Formatted Markdown documentation.
        """
        lines = []
        
        # Title
        if "title" in data:
            lines.append(f"# {data['title']}")
            lines.append("")
        
        # Description
        if "description" in data:
            lines.append(data["description"])
            lines.append("")
        
        # Sections
        for key, value in data.items():
            if key not in ["title", "description", "content"]:
                lines.append(f"## {key.capitalize()}")
                lines.append("")
                
                if isinstance(value, list):
                    for item in value:
                        lines.append(f"- {item}")
                else:
                    lines.append(str(value))
                
                lines.append("")
        
        # Content
        if "content" in data and data["content"] not in [None, ""]:
            lines.append(data["content"])
        
        return "\n".join(lines)
    
    def format_rst(self, data: Dict[str, Any]) -> str:
        """
        Format documentation data as reStructuredText.
        
        Args:
            data: The documentation data to format.
            
        Returns:
            Formatted reStructuredText documentation.
        """
        lines = []
        
        # Title
        if "title" in data:
            lines.append(data["title"])
            lines.append("=" * len(data["title"]))
            lines.append("")
        
        # Description
        if "description" in data:
            lines.append(data["description"])
            lines.append("")
        
        # Sections
        for key, value in data.items():
            if key not in ["title", "description", "content"]:
                section_title = key.capitalize()
                lines.append(section_title)
                lines.append("-" * len(section_title))
                lines.append("")
                
                if isinstance(value, list):
                    for item in value:
                        lines.append(f"* {item}")
                else:
                    lines.append(str(value))
                
                lines.append("")
        
        # Content
        if "content" in data and data["content"] not in [None, ""]:
            lines.append(data["content"])
        
        return "\n".join(lines)
    
    def format_html(self, data: Dict[str, Any]) -> str:
        """
        Format documentation data as HTML.
        
        Args:
            data: The documentation data to format.
            
        Returns:
            Formatted HTML documentation.
        """
        lines = []
        
        # HTML header
        lines.append("<!DOCTYPE html>")
        lines.append("<html>")
        lines.append("<head>")
        lines.append("    <meta charset=\"UTF-8\">")
        
        if "title" in data:
            lines.append(f"    <title>{data['title']}</title>")
        else:
            lines.append("    <title>Documentation</title>")
        
        lines.append("    <style>")
        lines.append("        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }")
        lines.append("        h1 { color: #333; }")
        lines.append("        h2 { color: #666; }")
        lines.append("        pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }")
        lines.append("        code { background-color: #f5f5f5; padding: 2px 5px; border-radius: 3px; }")
        lines.append("        .container { max-width: 800px; margin: 0 auto; }")
        lines.append("    </style>")
        lines.append("</head>")
        lines.append("<body>")
        lines.append("    <div class=\"container\">")
        
        # Title
        if "title" in data:
            lines.append(f"        <h1>{data['title']}</h1>")
        
        # Description
        if "description" in data:
            lines.append(f"        <p>{data['description']}</p>")
        
        # Sections
        for key, value in data.items():
            if key not in ["title", "description", "content"]:
                lines.append(f"        <h2>{key.capitalize()}</h2>")
                
                if isinstance(value, list):
                    lines.append("        <ul>")
                    for item in value:
                        lines.append(f"            <li>{item}</li>")
                    lines.append("        </ul>")
                else:
                    lines.append(f"        <p>{value}</p>")
        
        # Content
        if "content" in data and data["content"] not in [None, ""]:
            lines.append(f"        <div>{data['content']}</div>")
        
        # HTML footer
        lines.append("    </div>")
        lines.append("</body>")
        lines.append("</html>")
        
        return "\n".join(lines)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the formatter.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the formatter.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
