"""Code Retriever for the Context Engine.

This module provides a retriever for fetching relevant code from a codebase.

Version: 0.1.0
Created: 2025-04-26
"""

import logging
import os
import re
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path

from augment_adam.core.errors import (
    ResourceError, wrap_error, log_error, ErrorCategory
)
from augment_adam.context_engine.context_manager import ContextItem

logger = logging.getLogger(__name__)


class CodeRetriever:
    """Code Retriever for the Context Engine.
    
    This class retrieves relevant code from a codebase.
    
    Attributes:
        code_dir: Directory containing code
        default_relevance: The default relevance score for retrieved items
        supported_extensions: List of supported file extensions
    """
    
    def __init__(
        self,
        code_dir: Optional[str] = None,
        default_relevance: float = 0.5
    ):
        """Initialize the Code Retriever.
        
        Args:
            code_dir: Directory containing code
            default_relevance: The default relevance score for retrieved items
        """
        self.code_dir = code_dir
        self.default_relevance = default_relevance
        self.supported_extensions = [
            ".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".hpp",
            ".cs", ".go", ".rb", ".php", ".swift", ".kt", ".rs"
        ]
        
        logger.info("Code Retriever initialized")
    
    def retrieve(
        self,
        query: str,
        max_items: int = 10,
        file_pattern: Optional[str] = None,
        extensions: Optional[List[str]] = None
    ) -> List[ContextItem]:
        """Retrieve context items from code.
        
        Args:
            query: The query to retrieve context for
            max_items: The maximum number of items to retrieve
            file_pattern: Pattern to filter files by name
            extensions: List of file extensions to include
            
        Returns:
            The retrieved context items
        """
        try:
            if not self.code_dir:
                logger.warning("Code directory not provided")
                return []
            
            # Use provided extensions or defaults
            extensions = extensions or self.supported_extensions
            
            # Get list of code files
            code_files = self._get_code_files(file_pattern, extensions)
            
            # Search for relevant code
            items = []
            for file_path in code_files:
                # Read file
                content = self._read_file(file_path)
                if not content:
                    continue
                
                # Find relevant sections
                sections = self._find_relevant_sections(content, query)
                
                # Create context items from sections
                for i, (section, line_start, line_end) in enumerate(sections):
                    # Estimate token count (very rough approximation)
                    token_count = len(section.split()) * 1.3  # Rough approximation
                    
                    item = ContextItem(
                        content=section,
                        source=f"code:{file_path.name}",
                        relevance=self.default_relevance,
                        metadata={
                            "file": str(file_path),
                            "line_start": line_start,
                            "line_end": line_end,
                            "section_index": i,
                            "total_sections": len(sections),
                        },
                        token_count=int(token_count)
                    )
                    items.append(item)
                    
                    # Stop if we've reached max_items
                    if len(items) >= max_items:
                        break
                
                # Stop if we've reached max_items
                if len(items) >= max_items:
                    break
            
            logger.info(f"Retrieved {len(items)} items from code for query: {query}")
            return items
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to retrieve from code",
                category=ErrorCategory.RESOURCE,
                details={
                    "query": query,
                    "code_dir": self.code_dir,
                },
            )
            log_error(error, logger=logger)
            return []
    
    def _get_code_files(
        self,
        file_pattern: Optional[str] = None,
        extensions: Optional[List[str]] = None
    ) -> List[Path]:
        """Get list of code files.
        
        Args:
            file_pattern: Pattern to filter files by name
            extensions: List of file extensions to include
            
        Returns:
            List of code file paths
        """
        if not self.code_dir:
            return []
        
        code_dir = Path(self.code_dir)
        if not code_dir.exists() or not code_dir.is_dir():
            logger.warning(f"Code directory not found: {self.code_dir}")
            return []
        
        # Use provided extensions or defaults
        extensions = extensions or self.supported_extensions
        
        # Get all files with supported extensions
        code_files = []
        for ext in extensions:
            code_files.extend(code_dir.glob(f"**/*{ext}"))
        
        # Filter by pattern if provided
        if file_pattern:
            code_files = [file for file in code_files if file_pattern in file.name]
        
        return code_files
    
    def _read_file(self, file_path: Path) -> Optional[str]:
        """Read a code file.
        
        Args:
            file_path: Path to the code file
            
        Returns:
            The file content, or None if the read failed
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except Exception as e:
            logger.warning(f"Failed to read file {file_path}: {e}")
            return None
    
    def _find_relevant_sections(
        self,
        content: str,
        query: str
    ) -> List[Tuple[str, int, int]]:
        """Find relevant sections in code.
        
        Args:
            content: The code content
            query: The query to find relevant sections for
            
        Returns:
            List of tuples containing (section, line_start, line_end)
        """
        # Split content into lines
        lines = content.split("\n")
        
        # Extract keywords from query
        keywords = re.findall(r'\b\w+\b', query.lower())
        
        # Find matches
        matches = []
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords):
                matches.append(i)
        
        # Group matches into sections
        sections = []
        if matches:
            section_start = matches[0]
            section_end = matches[0]
            
            for i in range(1, len(matches)):
                # If this match is close to the previous one, extend the section
                if matches[i] - section_end <= 5:  # Within 5 lines
                    section_end = matches[i]
                else:
                    # Add the current section
                    section_lines = lines[max(0, section_start - 2):min(len(lines), section_end + 3)]
                    section = "\n".join(section_lines)
                    sections.append((section, section_start + 1, section_end + 1))
                    
                    # Start a new section
                    section_start = matches[i]
                    section_end = matches[i]
            
            # Add the last section
            section_lines = lines[max(0, section_start - 2):min(len(lines), section_end + 3)]
            section = "\n".join(section_lines)
            sections.append((section, section_start + 1, section_end + 1))
        
        return sections
