"""
Base classes for test fixtures.

This module provides the base classes for test fixtures, which are used to set up
and tear down test environments.
"""

import os
import tempfile
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type, Generator

from augment_adam.utils.tagging import tag, TagCategory


@tag("testing.fixtures")
class Fixture(ABC):
    """
    Base class for test fixtures.
    
    This class defines the interface for test fixtures, which are used to set up
    and tear down test environments.
    
    Attributes:
        name: The name of the fixture.
        scope: The scope of the fixture (function, class, module, session).
        metadata: Additional metadata for the fixture.
    
    TODO(Issue #13): Add support for fixture dependencies
    TODO(Issue #13): Implement fixture validation
    """
    
    def __init__(
        self,
        name: str,
        scope: str = "function",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the fixture.
        
        Args:
            name: The name of the fixture.
            scope: The scope of the fixture (function, class, module, session).
            metadata: Additional metadata for the fixture.
        """
        self.name = name
        self.scope = scope
        self.metadata = metadata or {}
    
    @abstractmethod
    def setup(self) -> Any:
        """
        Set up the fixture.
        
        Returns:
            The fixture value.
        """
        pass
    
    @abstractmethod
    def teardown(self) -> None:
        """Tear down the fixture."""
        pass
    
    def __call__(self) -> Generator[Any, None, None]:
        """
        Call the fixture.
        
        Yields:
            The fixture value.
        """
        value = self.setup()
        try:
            yield value
        finally:
            self.teardown()
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the fixture.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the fixture.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("testing.fixtures")
class TempDirFixture(Fixture):
    """
    Fixture for temporary directories.
    
    This fixture creates a temporary directory for tests and cleans it up afterwards.
    
    Attributes:
        name: The name of the fixture.
        scope: The scope of the fixture (function, class, module, session).
        metadata: Additional metadata for the fixture.
        prefix: The prefix for the temporary directory.
        suffix: The suffix for the temporary directory.
        dir: The parent directory for the temporary directory.
    
    TODO(Issue #13): Add support for directory templates
    TODO(Issue #13): Implement directory validation
    """
    
    def __init__(
        self,
        name: str = "temp_dir",
        scope: str = "function",
        metadata: Optional[Dict[str, Any]] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        dir: Optional[str] = None
    ) -> None:
        """
        Initialize the temporary directory fixture.
        
        Args:
            name: The name of the fixture.
            scope: The scope of the fixture (function, class, module, session).
            metadata: Additional metadata for the fixture.
            prefix: The prefix for the temporary directory.
            suffix: The suffix for the temporary directory.
            dir: The parent directory for the temporary directory.
        """
        super().__init__(name, scope, metadata)
        self.prefix = prefix
        self.suffix = suffix
        self.dir = dir
        self._temp_dir = None
    
    def setup(self) -> str:
        """
        Set up the temporary directory.
        
        Returns:
            The path to the temporary directory.
        """
        self._temp_dir = tempfile.TemporaryDirectory(
            prefix=self.prefix,
            suffix=self.suffix,
            dir=self.dir
        )
        return self._temp_dir.name
    
    def teardown(self) -> None:
        """Clean up the temporary directory."""
        if self._temp_dir is not None:
            self._temp_dir.cleanup()
            self._temp_dir = None


@tag("testing.fixtures")
class MockFixture(Fixture):
    """
    Fixture for mocks.
    
    This fixture creates a mock object for tests.
    
    Attributes:
        name: The name of the fixture.
        scope: The scope of the fixture (function, class, module, session).
        metadata: Additional metadata for the fixture.
        target: The target to mock.
        return_value: The return value for the mock.
        side_effect: The side effect for the mock.
        spec: The spec for the mock.
    
    TODO(Issue #13): Add support for mock validation
    TODO(Issue #13): Implement mock analytics
    """
    
    def __init__(
        self,
        name: str,
        target: str,
        scope: str = "function",
        metadata: Optional[Dict[str, Any]] = None,
        return_value: Any = None,
        side_effect: Any = None,
        spec: Any = None
    ) -> None:
        """
        Initialize the mock fixture.
        
        Args:
            name: The name of the fixture.
            target: The target to mock.
            scope: The scope of the fixture (function, class, module, session).
            metadata: Additional metadata for the fixture.
            return_value: The return value for the mock.
            side_effect: The side effect for the mock.
            spec: The spec for the mock.
        """
        super().__init__(name, scope, metadata)
        self.target = target
        self.return_value = return_value
        self.side_effect = side_effect
        self.spec = spec
        self._patcher = None
        self._mock = None
    
    def setup(self) -> Any:
        """
        Set up the mock.
        
        Returns:
            The mock object.
        """
        import unittest.mock as mock
        
        self._patcher = mock.patch(self.target, spec=self.spec)
        self._mock = self._patcher.start()
        
        if self.return_value is not None:
            self._mock.return_value = self.return_value
        
        if self.side_effect is not None:
            self._mock.side_effect = self.side_effect
        
        return self._mock
    
    def teardown(self) -> None:
        """Clean up the mock."""
        if self._patcher is not None:
            self._patcher.stop()
            self._patcher = None
            self._mock = None
