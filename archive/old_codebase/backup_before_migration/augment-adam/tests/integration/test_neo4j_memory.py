"""Integration tests for the Neo4j memory system."""

import os
import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, List, Any, Optional, Tuple

from augment_adam.memory.neo4j_memory import Neo4jMemory, get_neo4j_memory


@pytest.mark.integration
class TestNeo4jMemory:
    """Integration tests for the Neo4j memory system.
    
    Note: These tests require a running Neo4j instance.
    If Neo4j is not available, the tests will be skipped.
    """
    
    @pytest.fixture(autouse=True)
    def check_neo4j(self):
        """Check if Neo4j is available."""
        # Skip all tests in this class if Neo4j is not available
        neo4j_uri = os.getenv("NEO4J_URI")
        if not neo4j_uri:
            pytest.skip("Neo4j URI not set, skipping Neo4j tests")
    
    def setup_method(self):
        """Set up test environment."""
        # Create a Neo4j memory instance with a unique collection name for testing
        self.collection_name = f"test_memory_{os.getpid()}"
        
        # Create a Neo4j memory instance
        self.memory = Neo4jMemory(
            collection_name=self.collection_name
        )
    
    def teardown_method(self):
        """Clean up after tests."""
        # Clear the test collection
        self.memory.clear(collection_name=self.collection_name)
        
        # Close the Neo4j client
        self.memory.close()
    
    def test_add_and_retrieve(self):
        """Test adding and retrieving memories."""
        # Add some memories
        memory_id1 = self.memory.add(
            text="Python is a programming language with simple syntax and powerful libraries.",
            metadata={"type": "note", "topic": "programming", "language": "python"},
            collection_name=self.collection_name
        )
        
        memory_id2 = self.memory.add(
            text="JavaScript is a programming language used for web development.",
            metadata={"type": "note", "topic": "programming", "language": "javascript"},
            collection_name=self.collection_name
        )
        
        memory_id3 = self.memory.add(
            text="Machine learning is a subset of artificial intelligence.",
            metadata={"type": "note", "topic": "ai", "subtopic": "machine learning"},
            collection_name=self.collection_name
        )
        
        # Retrieve memories about programming
        programming_results = self.memory.retrieve(
            query="programming language",
            n_results=2,
            collection_name=self.collection_name
        )
        
        # Retrieve memories about AI
        ai_results = self.memory.retrieve(
            query="artificial intelligence and machine learning",
            n_results=1,
            collection_name=self.collection_name
        )
        
        # Check programming results
        assert len(programming_results) == 2
        
        # The results should contain the programming languages
        programming_texts = [result[0]["text"] for result in programming_results]
        assert any("Python" in text for text in programming_texts)
        assert any("JavaScript" in text for text in programming_texts)
        
        # Check AI results
        assert len(ai_results) == 1
        assert "Machine learning" in ai_results[0][0]["text"]
    
    def test_retrieve_with_filter(self):
        """Test retrieving memories with filter."""
        # Add some memories
        memory_id1 = self.memory.add(
            text="Python is a programming language with simple syntax and powerful libraries.",
            metadata={"type": "note", "topic": "programming", "language": "python"},
            collection_name=self.collection_name
        )
        
        memory_id2 = self.memory.add(
            text="JavaScript is a programming language used for web development.",
            metadata={"type": "note", "topic": "programming", "language": "javascript"},
            collection_name=self.collection_name
        )
        
        # Retrieve only Python memories
        python_results = self.memory.retrieve(
            query="programming language",
            n_results=2,
            filter_metadata={"language": "python"},
            collection_name=self.collection_name
        )
        
        # Check results
        assert len(python_results) == 1
        assert python_results[0][0]["language"] == "python"
    
    def test_get_by_id(self):
        """Test getting a memory by ID."""
        # Add a memory
        memory_id = self.memory.add(
            text="This is a test memory",
            metadata={"type": "note"},
            collection_name=self.collection_name
        )
        
        # Get the memory by ID
        memory = self.memory.get_by_id(
            memory_id=memory_id,
            collection_name=self.collection_name
        )
        
        # Check the memory
        assert memory is not None
        assert memory["text"] == "This is a test memory"
        assert memory["type"] == "note"
    
    def test_delete(self):
        """Test deleting a memory."""
        # Add a memory
        memory_id = self.memory.add(
            text="This is a test memory",
            metadata={"type": "note"},
            collection_name=self.collection_name
        )
        
        # Delete the memory
        result = self.memory.delete(
            memory_id=memory_id,
            collection_name=self.collection_name
        )
        
        # Check the result
        assert result is True
        
        # Try to get the deleted memory
        memory = self.memory.get_by_id(
            memory_id=memory_id,
            collection_name=self.collection_name
        )
        
        # Check that the memory is gone
        assert memory is None
    
    def test_clear(self):
        """Test clearing a collection."""
        # Add some memories
        self.memory.add(
            text="Memory 1",
            collection_name=self.collection_name
        )
        
        self.memory.add(
            text="Memory 2",
            collection_name=self.collection_name
        )
        
        # Retrieve memories to verify they exist
        results_before = self.memory.retrieve(
            query="memory",
            n_results=10,
            collection_name=self.collection_name
        )
        
        assert len(results_before) > 0
        
        # Clear the collection
        result = self.memory.clear(
            collection_name=self.collection_name
        )
        
        assert result is True
        
        # Retrieve memories again to verify they're gone
        results_after = self.memory.retrieve(
            query="memory",
            n_results=10,
            collection_name=self.collection_name
        )
        
        assert len(results_after) == 0
    
    def test_create_relationship(self):
        """Test creating a relationship between memories."""
        # Add some memories
        memory_id1 = self.memory.add(
            text="Python is a programming language.",
            metadata={"type": "concept", "name": "Python"},
            collection_name=self.collection_name
        )
        
        memory_id2 = self.memory.add(
            text="Programming languages are used to write software.",
            metadata={"type": "concept", "name": "Programming Language"},
            collection_name=self.collection_name
        )
        
        # Create a relationship
        result = self.memory.create_relationship(
            from_id=memory_id1,
            to_id=memory_id2,
            relationship_type="IS_A",
            properties={"confidence": 0.9},
            collection_name=self.collection_name
        )
        
        # Check the result
        assert result is True


@pytest.mark.unit
class TestNeo4jMemoryMocked:
    """Unit tests for the Neo4j memory system using mocks."""
    
    def setup_method(self):
        """Set up test environment."""
        # Create a patch for the Neo4j client
        self.client_patcher = patch('augment_adam.memory.neo4j_memory.Neo4jClient')
        self.mock_client_class = self.client_patcher.start()
        
        # Create a mock client instance
        self.mock_client = MagicMock()
        self.mock_client_class.return_value = self.mock_client
        
        # Create a Neo4j memory instance
        self.memory = Neo4jMemory(
            collection_name="test_memory"
        )
    
    def teardown_method(self):
        """Clean up after tests."""
        # Stop the patch
        self.client_patcher.stop()
    
    def test_singleton_pattern(self):
        """Test the singleton pattern for the default memory instance."""
        # Mock the get_neo4j_client function
        with patch('augment_adam.memory.neo4j_memory.get_neo4j_client') as mock_get_client:
            mock_get_client.return_value = self.mock_client
            
            # Get the default memory instance
            memory1 = get_neo4j_memory(
                collection_name="default_memory"
            )
            
            # Get it again
            memory2 = get_neo4j_memory()
            
            # They should be the same instance
            assert memory1 is memory2
