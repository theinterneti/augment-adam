"""
Documentation parser.

This module provides a parser for parsing documentation from various sources.
"""

import re
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type

from augment_adam.utils.tagging import tag, TagCategory


@tag("docs.utils")
class DocParser:
    """
    Parser for documentation.
    
    This class parses documentation from various sources, including docstrings,
    Markdown files, and reStructuredText files.
    
    Attributes:
        metadata: Additional metadata for the parser.
    
    TODO(Issue #12): Add support for more documentation formats
    TODO(Issue #12): Implement parser validation
    """
    
    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the documentation parser.
        
        Args:
            metadata: Additional metadata for the parser.
        """
        self.metadata = metadata or {}
    
    def parse_docstring(self, docstring: str) -> Dict[str, Any]:
        """
        Parse a docstring.
        
        Args:
            docstring: The docstring to parse.
            
        Returns:
            Dictionary of parsed documentation data.
        """
        if not docstring:
            return {"description": ""}
        
        # Remove leading/trailing whitespace
        docstring = docstring.strip()
        
        # Split into sections
        sections = re.split(r"\n\s*\n", docstring)
        
        # Parse description
        description = sections[0].strip()
        
        # Parse other sections
        parsed_sections = {}
        current_section = None
        
        for section in sections[1:]:
            # Check if section is a header
            match = re.match(r"([A-Za-z]+):\s*\n", section)
            if match:
                current_section = match.group(1).lower()
                parsed_sections[current_section] = []
                section = section[match.end():]
            
            # Parse section content
            if current_section:
                # Split into items
                items = re.split(r"\n\s*\n", section)
                
                for item in items:
                    if item.strip():
                        parsed_sections[current_section].append(item.strip())
        
        # Create result
        result = {
            "description": description,
        }
        
        # Add parsed sections
        for section, items in parsed_sections.items():
            result[section] = items
        
        return result
    
    def parse_markdown(self, markdown: str) -> Dict[str, Any]:
        """
        Parse Markdown documentation.
        
        Args:
            markdown: The Markdown documentation to parse.
            
        Returns:
            Dictionary of parsed documentation data.
        """
        if not markdown:
            return {"content": ""}
        
        # Remove leading/trailing whitespace
        markdown = markdown.strip()
        
        # Parse title
        title = ""
        match = re.match(r"#\s+(.+)$", markdown, re.MULTILINE)
        if match:
            title = match.group(1).strip()
            markdown = markdown[match.end():].strip()
        
        # Parse sections
        sections = {}
        current_section = None
        
        for line in markdown.split("\n"):
            # Check if line is a header
            match = re.match(r"##\s+(.+)$", line)
            if match:
                current_section = match.group(1).strip().lower()
                sections[current_section] = []
            elif current_section and line.strip():
                sections[current_section].append(line)
        
        # Create result
        result = {
            "title": title,
            "content": markdown,
        }
        
        # Add parsed sections
        for section, lines in sections.items():
            result[section] = "\n".join(lines)
        
        return result
    
    def parse_rst(self, rst: str) -> Dict[str, Any]:
        """
        Parse reStructuredText documentation.
        
        Args:
            rst: The reStructuredText documentation to parse.
            
        Returns:
            Dictionary of parsed documentation data.
        """
        if not rst:
            return {"content": ""}
        
        # Remove leading/trailing whitespace
        rst = rst.strip()
        
        # Parse title
        title = ""
        match = re.match(r"(.+)\n[=]+\n", rst)
        if match:
            title = match.group(1).strip()
            rst = rst[match.end():].strip()
        
        # Parse sections
        sections = {}
        current_section = None
        
        for line in rst.split("\n"):
            # Check if line is a header
            match = re.match(r"(.+)\n[-]+\n", line)
            if match:
                current_section = match.group(1).strip().lower()
                sections[current_section] = []
            elif current_section and line.strip():
                sections[current_section].append(line)
        
        # Create result
        result = {
            "title": title,
            "content": rst,
        }
        
        # Add parsed sections
        for section, lines in sections.items():
            result[section] = "\n".join(lines)
        
        return result
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the parser.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the parser.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
