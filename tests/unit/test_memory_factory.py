"""Unit tests for the memory factory."""

import os
import pytest
import tempfile
from unittest.mock import patch

from augment_adam.memory.memory_factory import MemoryFactory, create_memory, get_default_memory
from augment_adam.memory.faiss_memory import FAISSMemory
from augment_adam.memory.neo4j_memory import Neo4jMemory
from augment_adam.core.errors import ValidationError


class TestMemoryFactory:
    """Tests for the memory factory."""
    
    def setup_method(self):
        """Set up test environment."""
        # Create a temporary directory for FAISS memory
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after tests."""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_faiss_memory(self):
        """Test creating a FAISS memory instance."""
        memory = MemoryFactory.create_memory(
            memory_type="faiss",
            persist_dir=self.temp_dir,
            collection_name="test_memory"
        )
        
        assert isinstance(memory, FAISSMemory)
        assert memory.persist_dir == self.temp_dir
        assert memory.default_collection == "test_memory"
    
    @patch('augment_adam.memory.neo4j_memory.Neo4jClient')
    def test_create_neo4j_memory(self, mock_client):
        """Test creating a Neo4j memory instance."""
        # Mock the Neo4j client to avoid actual connection
        memory = MemoryFactory.create_memory(
            memory_type="neo4j",
            collection_name="test_memory"
        )
        
        assert isinstance(memory, Neo4jMemory)
        assert memory.default_collection == "test_memory"
    
    def test_create_invalid_memory(self):
        """Test creating an invalid memory type."""
        with pytest.raises(ValidationError):
            MemoryFactory.create_memory(memory_type="invalid")
    
    def test_convenience_function(self):
        """Test the convenience function for creating memory."""
        memory = create_memory(
            memory_type="faiss",
            persist_dir=self.temp_dir,
            collection_name="test_memory"
        )
        
        assert isinstance(memory, FAISSMemory)
        assert memory.persist_dir == self.temp_dir
        assert memory.default_collection == "test_memory"
    
    @patch('augment_adam.memory.faiss_memory.get_faiss_memory')
    def test_get_default_memory(self, mock_get_faiss_memory):
        """Test getting the default memory instance."""
        # Mock the get_faiss_memory function to avoid actual creation
        mock_get_faiss_memory.return_value = "faiss_memory_instance"
        
        memory = get_default_memory(memory_type="faiss")
        
        assert memory == "faiss_memory_instance"
        mock_get_faiss_memory.assert_called_once()
    
    @patch('augment_adam.memory.neo4j_memory.get_neo4j_memory')
    def test_get_default_neo4j_memory(self, mock_get_neo4j_memory):
        """Test getting the default Neo4j memory instance."""
        # Mock the get_neo4j_memory function to avoid actual creation
        mock_get_neo4j_memory.return_value = "neo4j_memory_instance"
        
        memory = get_default_memory(memory_type="neo4j")
        
        assert memory == "neo4j_memory_instance"
        mock_get_neo4j_memory.assert_called_once()
    
    def test_get_default_invalid_memory(self):
        """Test getting an invalid default memory type."""
        with pytest.raises(ValidationError):
            get_default_memory(memory_type="invalid")
