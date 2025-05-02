"""
Pytest configuration for Augment Adam tests.

This is a simplified conftest.py that avoids the tagging system issues
by resetting the tag registry before tests run.
"""

import os
import sys
import tempfile
import pytest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# Import our tag utilities
try:
    from augment_adam.testing.utils.tag_utils import reset_tag_registry

    @pytest.fixture(scope="session", autouse=True)
    def reset_tags():
        """Reset the tag registry before running tests."""
        reset_tag_registry()
        yield
except ImportError:
    # If the tag utilities aren't available, provide a dummy fixture
    @pytest.fixture(scope="session", autouse=True)
    def reset_tags():
        """Dummy fixture for when tag utilities aren't available."""
        yield

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

# Mock fixtures for memory systems
@pytest.fixture
def mock_faiss_memory():
    """Create a mocked FAISS memory instance for tests."""
    mock_memory = MagicMock()
    mock_memory.add.return_value = None
    mock_memory.search.return_value = []
    mock_memory.delete.return_value = None
    yield mock_memory

@pytest.fixture
def mock_neo4j_memory():
    """Create a mocked Neo4j memory instance for tests."""
    mock_memory = MagicMock()
    mock_memory.add.return_value = None
    mock_memory.search.return_value = []
    mock_memory.delete.return_value = None
    yield mock_memory

# MCP server fixtures
@pytest.fixture
def mcp_api_key():
    """Get the MCP API key for tests."""
    return "test-api-key"
