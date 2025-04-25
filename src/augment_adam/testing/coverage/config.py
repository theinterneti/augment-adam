"""
Test coverage configuration.

This module provides configuration for test coverage.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type

from augment_adam.utils.tagging import tag, TagCategory


@tag("testing.coverage")
@dataclass
class CoverageConfig:
    """
    Configuration for test coverage.
    
    This class provides configuration for test coverage, including the data file,
    config file, source directories, included and omitted files, and branch coverage.
    
    Attributes:
        data_file: The path to the coverage data file.
        config_file: The path to the coverage config file.
        source: The source directories to measure.
        include: Patterns of files to include.
        omit: Patterns of files to omit.
        branch: Whether to measure branch coverage.
        metadata: Additional metadata for the configuration.
    
    TODO(Issue #13): Add support for coverage configuration dependencies
    TODO(Issue #13): Implement coverage configuration analytics
    """
    
    data_file: Optional[str] = None
    config_file: Optional[str] = None
    source: Optional[List[str]] = field(default_factory=lambda: ["src"])
    include: Optional[List[str]] = field(default_factory=lambda: ["src/**/*.py"])
    omit: Optional[List[str]] = field(default_factory=lambda: ["**/test_*.py", "**/conftest.py"])
    branch: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the configuration.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the configuration.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.
        
        Returns:
            A dictionary representation of the configuration.
        """
        return {
            "data_file": self.data_file,
            "config_file": self.config_file,
            "source": self.source,
            "include": self.include,
            "omit": self.omit,
            "branch": self.branch,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoverageConfig":
        """
        Create a configuration from a dictionary.
        
        Args:
            data: A dictionary representation of the configuration.
            
        Returns:
            A coverage configuration.
        """
        return cls(
            data_file=data.get("data_file"),
            config_file=data.get("config_file"),
            source=data.get("source"),
            include=data.get("include"),
            omit=data.get("omit"),
            branch=data.get("branch", True),
            metadata=data.get("metadata", {}),
        )
    
    def to_json(self) -> str:
        """
        Convert the configuration to a JSON string.
        
        Returns:
            A JSON string representation of the configuration.
        """
        import json
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> "CoverageConfig":
        """
        Create a configuration from a JSON string.
        
        Args:
            json_str: A JSON string representation of the configuration.
            
        Returns:
            A coverage configuration.
        """
        import json
        return cls.from_dict(json.loads(json_str))
    
    def to_file(self, file_path: str) -> None:
        """
        Save the configuration to a file.
        
        Args:
            file_path: The path to the file.
        """
        import json
        
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_file(cls, file_path: str) -> "CoverageConfig":
        """
        Load a configuration from a file.
        
        Args:
            file_path: The path to the file.
            
        Returns:
            A coverage configuration.
        """
        import json
        
        with open(file_path, "r") as f:
            return cls.from_dict(json.load(f))
