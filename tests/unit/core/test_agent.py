"""Tests for the Agent class."""

import pytest

from augment_adam.core import Agent
from augment_adam.memory import BaseMemory


class MockMemory(BaseMemory):
    """Mock memory system for testing."""
    
    def __init__(self):
        self.entries = []
    
    def add(self, text, metadata=None):
        self.entries.append({"text": text, "metadata": metadata or {}})
    
    def search(self, query, limit=5):
        return self.entries[:limit]
    
    def clear(self):
        self.entries = []


class TestAgent:
    """Tests for the Agent class."""
    
    def test_init(self):
        """Test that the Agent initializes correctly."""
        agent = Agent(name="Test Agent")
        assert agent.name == "Test Agent"
        assert agent.model_name == "default"
        assert agent.model_params == {}
        assert agent.memory is None
    
    def test_run(self):
        """Test that the Agent.run method works."""
        agent = Agent(name="Test Agent")
        response = agent.run("Hello, world!")
        assert "Hello, world!" in response
    
    def test_memory_integration(self):
        """Test that the Agent integrates with memory systems."""
        memory = MockMemory()
        agent = Agent(name="Test Agent", memory=memory)
        
        # Add to memory
        agent.add_to_memory("Test memory entry", {"source": "test"})
        assert len(memory.entries) == 1
        assert memory.entries[0]["text"] == "Test memory entry"
        assert memory.entries[0]["metadata"]["source"] == "test"
        
        # Search memory
        results = agent.search_memory("test")
        assert len(results) == 1
        assert results[0]["text"] == "Test memory entry"
