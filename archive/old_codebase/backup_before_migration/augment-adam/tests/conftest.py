"""Pytest configuration for Augment Adam tests."""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from augment_adam.memory.faiss_memory import FAISSMemory
from augment_adam.memory.neo4j_memory import Neo4jMemory


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def faiss_memory(temp_dir):
    """Create a FAISS memory instance for tests."""
    memory = FAISSMemory(
        persist_dir=temp_dir,
        collection_name="test_memory"
    )
    yield memory


@pytest.fixture
def neo4j_memory_mock():
    """Create a mocked Neo4j memory instance for tests."""
    with patch('augment_adam.memory.neo4j_memory.Neo4jClient') as mock_client_class:
        # Create a mock client instance
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Create a Neo4j memory instance
        memory = Neo4jMemory(
            collection_name="test_memory"
        )
        
        yield memory
