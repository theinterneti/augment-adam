"""
Test coverage reporter.

This module provides a reporter for measuring and reporting test coverage.
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type, TextIO

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.testing.coverage.config import CoverageConfig


@tag("testing.coverage")
class CoverageReporter:
    """
    Reporter for test coverage.
    
    This class provides a reporter for measuring and reporting test coverage.
    
    Attributes:
        config: The configuration for the coverage reporter.
        metadata: Additional metadata for the coverage reporter.
        coverage: The coverage object.
    
    TODO(Issue #13): Add support for coverage reporter dependencies
    TODO(Issue #13): Implement coverage reporter analytics
    """
    
    def __init__(
        self,
        config: Optional[CoverageConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the coverage reporter.
        
        Args:
            config: The configuration for the coverage reporter.
            metadata: Additional metadata for the coverage reporter.
        """
        self.config = config or CoverageConfig()
        self.metadata = metadata or {}
        self.coverage = None
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the coverage reporter.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the coverage reporter.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
    
    def start(self) -> None:
        """Start measuring coverage."""
        try:
            import coverage
            
            # Create a coverage object
            self.coverage = coverage.Coverage(
                data_file=self.config.data_file,
                config_file=self.config.config_file,
                source=self.config.source,
                include=self.config.include,
                omit=self.config.omit,
                branch=self.config.branch,
            )
            
            # Start measuring coverage
            self.coverage.start()
        except ImportError:
            print("Warning: coverage package not found. Coverage will not be measured.", file=sys.stderr)
    
    def stop(self) -> None:
        """Stop measuring coverage."""
        if self.coverage is not None:
            self.coverage.stop()
    
    def save(self) -> None:
        """Save coverage data."""
        if self.coverage is not None:
            self.coverage.save()
    
    def report(self, file: Optional[TextIO] = None, show_missing: bool = True) -> float:
        """
        Report coverage.
        
        Args:
            file: The file to write the report to.
            show_missing: Whether to show missing lines.
            
        Returns:
            The total coverage percentage.
        """
        if self.coverage is not None:
            return self.coverage.report(file=file, show_missing=show_missing)
        
        return 0.0
    
    def html_report(self, directory: Optional[str] = None, title: Optional[str] = None) -> float:
        """
        Generate an HTML coverage report.
        
        Args:
            directory: The directory to write the report to.
            title: The title of the report.
            
        Returns:
            The total coverage percentage.
        """
        if self.coverage is not None:
            return self.coverage.html_report(directory=directory, title=title)
        
        return 0.0
    
    def xml_report(self, outfile: Optional[str] = None) -> float:
        """
        Generate an XML coverage report.
        
        Args:
            outfile: The file to write the report to.
            
        Returns:
            The total coverage percentage.
        """
        if self.coverage is not None:
            return self.coverage.xml_report(outfile=outfile)
        
        return 0.0
    
    def json_report(self, outfile: Optional[str] = None) -> float:
        """
        Generate a JSON coverage report.
        
        Args:
            outfile: The file to write the report to.
            
        Returns:
            The total coverage percentage.
        """
        if self.coverage is not None:
            return self.coverage.json_report(outfile=outfile)
        
        return 0.0
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get coverage data.
        
        Returns:
            A dictionary containing coverage data.
        """
        if self.coverage is not None:
            data = self.coverage.get_data()
            
            return {
                "files": list(data.measured_files()),
                "lines": {
                    file: list(data.lines(file))
                    for file in data.measured_files()
                },
                "arcs": {
                    file: list(data.arcs(file))
                    for file in data.measured_files()
                    if data.has_arcs()
                },
            }
        
        return {}
    
    def get_total_coverage(self) -> float:
        """
        Get the total coverage percentage.
        
        Returns:
            The total coverage percentage.
        """
        if self.coverage is not None:
            data = self.coverage.get_data()
            total_lines = 0
            covered_lines = 0
            
            for file in data.measured_files():
                file_lines = data.lines(file)
                file_missing = data.missing_lines(file)
                
                total_lines += len(file_lines)
                covered_lines += len(file_lines) - len(file_missing)
            
            if total_lines > 0:
                return 100.0 * covered_lines / total_lines
        
        return 0.0
    
    def get_file_coverage(self, file: str) -> float:
        """
        Get the coverage percentage for a file.
        
        Args:
            file: The file to get coverage for.
            
        Returns:
            The coverage percentage for the file.
        """
        if self.coverage is not None:
            data = self.coverage.get_data()
            
            if file in data.measured_files():
                file_lines = data.lines(file)
                file_missing = data.missing_lines(file)
                
                if len(file_lines) > 0:
                    return 100.0 * (len(file_lines) - len(file_missing)) / len(file_lines)
        
        return 0.0
    
    def get_missing_lines(self, file: str) -> List[int]:
        """
        Get the missing lines for a file.
        
        Args:
            file: The file to get missing lines for.
            
        Returns:
            A list of missing line numbers.
        """
        if self.coverage is not None:
            data = self.coverage.get_data()
            
            if file in data.measured_files():
                return list(data.missing_lines(file))
        
        return []
