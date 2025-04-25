"""Integration tests for the FAISS memory system."""

import os
import pytest
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Tuple

from augment_adam.memory.faiss_memory import FAISSMemory, get_faiss_memory


class TestFAISSMemory:
    """Integration tests for the FAISS memory system."""
    
    def setup_method(self):
        """Set up test environment."""
        # Create a temporary directory for FAISS memory
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a FAISS memory instance
        self.memory = FAISSMemory(
            persist_dir=self.temp_dir,
            collection_name="test_memory"
        )
    
    def teardown_method(self):
        """Clean up after tests."""
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_add_and_retrieve(self):
        """Test adding and retrieving memories."""
        # Add some memories
        memory_id1 = self.memory.add(
            text="Python is a programming language with simple syntax and powerful libraries.",
            metadata={"type": "note", "topic": "programming", "language": "python"},
            collection_name="test_collection"
        )
        
        memory_id2 = self.memory.add(
            text="JavaScript is a programming language used for web development.",
            metadata={"type": "note", "topic": "programming", "language": "javascript"},
            collection_name="test_collection"
        )
        
        memory_id3 = self.memory.add(
            text="Machine learning is a subset of artificial intelligence.",
            metadata={"type": "note", "topic": "ai", "subtopic": "machine learning"},
            collection_name="test_collection"
        )
        
        # Retrieve memories about programming
        programming_results = self.memory.retrieve(
            query="programming language",
            n_results=2,
            collection_name="test_collection"
        )
        
        # Retrieve memories about AI
        ai_results = self.memory.retrieve(
            query="artificial intelligence and machine learning",
            n_results=1,
            collection_name="test_collection"
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
            collection_name="test_collection"
        )
        
        memory_id2 = self.memory.add(
            text="JavaScript is a programming language used for web development.",
            metadata={"type": "note", "topic": "programming", "language": "javascript"},
            collection_name="test_collection"
        )
        
        # Retrieve only Python memories
        python_results = self.memory.retrieve(
            query="programming language",
            n_results=2,
            filter_metadata={"language": "python"},
            collection_name="test_collection"
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
            collection_name="test_collection"
        )
        
        # Get the memory by ID
        memory = self.memory.get_by_id(
            memory_id=memory_id,
            collection_name="test_collection"
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
            collection_name="test_collection"
        )
        
        # Delete the memory
        result = self.memory.delete(
            memory_id=memory_id,
            collection_name="test_collection"
        )
        
        # Check the result
        assert result is True
        
        # Try to get the deleted memory
        memory = self.memory.get_by_id(
            memory_id=memory_id,
            collection_name="test_collection"
        )
        
        # Check that the memory is gone
        assert memory is None
    
    def test_clear(self):
        """Test clearing a collection."""
        # Add some memories
        self.memory.add(
            text="Memory 1",
            collection_name="test_collection"
        )
        
        self.memory.add(
            text="Memory 2",
            collection_name="test_collection"
        )
        
        # Retrieve memories to verify they exist
        results_before = self.memory.retrieve(
            query="memory",
            n_results=10,
            collection_name="test_collection"
        )
        
        assert len(results_before) > 0
        
        # Clear the collection
        result = self.memory.clear(
            collection_name="test_collection"
        )
        
        assert result is True
        
        # Retrieve memories again to verify they're gone
        results_after = self.memory.retrieve(
            query="memory",
            n_results=10,
            collection_name="test_collection"
        )
        
        assert len(results_after) == 0
    
    def test_singleton_pattern(self):
        """Test the singleton pattern for the default memory instance."""
        # Get the default memory instance
        memory1 = get_faiss_memory(
            persist_dir=self.temp_dir,
            collection_name="default_memory"
        )
        
        # Get it again
        memory2 = get_faiss_memory()
        
        # They should be the same instance
        assert memory1 is memory2
        
        # Add a memory using the first instance
        memory_id = memory1.add(
            text="This is a test memory",
            collection_name="default_memory"
        )
        
        # Retrieve it using the second instance
        memory = memory2.get_by_id(
            memory_id=memory_id,
            collection_name="default_memory"
        )
        
        # Check that it worked
        assert memory is not None
        assert memory["text"] == "This is a test memory"
