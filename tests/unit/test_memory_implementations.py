"""Unit tests for memory implementations."""

import pytest
import tempfile
from unittest.mock import patch, MagicMock

from augment_adam.memory.memory_interface import MemoryInterface
from augment_adam.memory.faiss_memory import FAISSMemory
from augment_adam.memory.neo4j_memory import Neo4jMemory


class TestMemoryImplementations:
    """Tests for memory implementations."""

    def test_faiss_memory_implements_interface(self):
        """Test that FAISSMemory implements MemoryInterface."""
        # Create a temporary directory for FAISS memory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a FAISS memory instance
            memory = FAISSMemory(
                persist_dir=temp_dir,
                collection_name="test_memory"
            )

            # Check that it implements the interface
            assert isinstance(memory, MemoryInterface)

            # Check that it has all the required methods
            assert hasattr(memory, "add")
            assert hasattr(memory, "retrieve")
            assert hasattr(memory, "get_by_id")
            assert hasattr(memory, "delete")
            assert hasattr(memory, "clear")

    def test_neo4j_memory_implements_interface(self):
        """Test that Neo4jMemory implements MemoryInterface."""
        # Mock the Neo4j client and asyncio.run
        with patch('augment_adam.memory.neo4j_memory.Neo4jClient') as mock_client_class, \
             patch('augment_adam.memory.neo4j_memory.asyncio.run') as mock_run:
            # Create a mock client instance
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_run.return_value = None  # Mock asyncio.run to do nothing

            # Mock the create_index method to return True
            mock_client.create_index.return_value = True

            # Create a Neo4j memory instance
            memory = Neo4jMemory(
                collection_name="test_memory"
            )

            # Check that it implements the interface
            assert isinstance(memory, MemoryInterface)

            # Check that it has all the required methods
            assert hasattr(memory, "add")
            assert hasattr(memory, "retrieve")
            assert hasattr(memory, "get_by_id")
            assert hasattr(memory, "delete")
            assert hasattr(memory, "clear")

    def test_memory_interface_methods(self):
        """Test that memory implementations have the correct method signatures."""
        # Get method signatures from the interface
        interface_methods = {
            name: method for name, method in vars(MemoryInterface).items()
            if not name.startswith("_") and callable(method)
        }

        # Create a temporary directory for FAISS memory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a FAISS memory instance
            faiss_memory = FAISSMemory(
                persist_dir=temp_dir,
                collection_name="test_memory"
            )

            # Check FAISS memory methods
            for name, method in interface_methods.items():
                assert hasattr(faiss_memory, name)
                assert callable(getattr(faiss_memory, name))

        # Mock the Neo4j client and asyncio.run
        with patch('augment_adam.memory.neo4j_memory.Neo4jClient') as mock_client_class, \
             patch('augment_adam.memory.neo4j_memory.asyncio.run') as mock_run:
            # Create a mock client instance
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_run.return_value = None  # Mock asyncio.run to do nothing

            # Mock the create_index method to return True
            mock_client.create_index.return_value = True

            # Create a Neo4j memory instance
            neo4j_memory = Neo4jMemory(
                collection_name="test_memory"
            )

            # Check Neo4j memory methods
            for name, method in interface_methods.items():
                assert hasattr(neo4j_memory, name)
                assert callable(getattr(neo4j_memory, name))
