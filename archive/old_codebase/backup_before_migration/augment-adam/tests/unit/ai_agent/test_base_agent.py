"""Unit tests for the BaseAgent class."""

import unittest
from unittest.mock import MagicMock, patch

from augment_adam.ai_agent.base_agent import BaseAgent
from augment_adam.ai_agent.smc.potential import RegexPotential


class TestBaseAgent(unittest.TestCase):
    """Tests for the BaseAgent class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a potential for testing
        self.potential = RegexPotential(
            pattern=r".*",
            name="test_potential"
        )
        
        # Create a base agent
        self.agent = BaseAgent(
            name="Test Agent",
            description="A test agent",
            potentials=[self.potential],
            num_particles=10
        )
    
    def test_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.name, "Test Agent")
        self.assertEqual(self.agent.description, "A test agent")
        self.assertEqual(len(self.agent.potentials), 1)
        self.assertEqual(self.agent.potentials[0].name, "test_potential")
    
    @patch('augment_adam.context_engine.context_manager.ContextManager.retrieve')
    def test_process(self, mock_retrieve):
        """Test the process method."""
        # Mock the context manager's retrieve method
        mock_retrieve.return_value = []
        
        # Mock the generate method
        self.agent.generate = MagicMock(return_value="Test response")
        
        # Mock the remember method
        self.agent.remember = MagicMock(return_value="test_memory_id")
        
        # Call the process method
        result = self.agent.process("Test input")
        
        # Check the result
        self.assertEqual(result["response"], "Test response")
        self.assertEqual(result["memory_id"], "test_memory_id")
        
        # Verify that the generate method was called
        self.agent.generate.assert_called_once()
        
        # Verify that the remember method was called
        self.agent.remember.assert_called_once()
    
    def test_generate(self):
        """Test the generate method."""
        # Mock the SMC sampler
        self.agent.smc_sampler.sample = MagicMock(return_value="Generated text")
        
        # Call the generate method
        result = self.agent.generate("Test prompt")
        
        # Check the result
        self.assertEqual(result, "Generated text")
        
        # Verify that the SMC sampler was called
        self.agent.smc_sampler.sample.assert_called_once_with(
            prompt="Test prompt",
            max_tokens=1000
        )
    
    @patch('augment_adam.ai_agent.memory_integration.memory_manager.MemoryManager.add')
    def test_remember(self, mock_add):
        """Test the remember method."""
        # Mock the memory manager's add method
        mock_add.return_value = "test_memory_id"
        
        # Call the remember method
        result = self.agent.remember("Test text", {"key": "value"})
        
        # Check the result
        self.assertEqual(result, "test_memory_id")
        
        # Verify that the memory manager's add method was called
        mock_add.assert_called_once_with(
            text="Test text",
            metadata={"key": "value"}
        )
    
    @patch('augment_adam.ai_agent.memory_integration.memory_manager.MemoryManager.retrieve')
    def test_retrieve(self, mock_retrieve):
        """Test the retrieve method."""
        # Mock the memory manager's retrieve method
        mock_retrieve.return_value = [
            ({"text": "Memory 1"}, 0.9),
            ({"text": "Memory 2"}, 0.8)
        ]
        
        # Call the retrieve method
        result = self.agent.retrieve("Test query", 2, {"key": "value"})
        
        # Check the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["text"], "Memory 1")
        self.assertEqual(result[0]["similarity"], 0.9)
        self.assertEqual(result[1]["text"], "Memory 2")
        self.assertEqual(result[1]["similarity"], 0.8)
        
        # Verify that the memory manager's retrieve method was called
        mock_retrieve.assert_called_once_with(
            query="Test query",
            n_results=2,
            filter_metadata={"key": "value"}
        )
    
    @patch('augment_adam.ai_agent.reasoning.chain_of_thought.ChainOfThought.reason')
    def test_reason(self, mock_reason):
        """Test the reason method."""
        # Mock the reasoning engine's reason method
        mock_reason.return_value = {
            "steps": [],
            "conclusion": "Test conclusion"
        }
        
        # Call the reason method
        result = self.agent.reason("Test query")
        
        # Check the result
        self.assertEqual(result["conclusion"], "Test conclusion")
        
        # Verify that the reasoning engine's reason method was called
        mock_reason.assert_called_once()
    
    def test_add_potential(self):
        """Test adding a potential."""
        # Create a new potential
        new_potential = RegexPotential(
            pattern=r".*",
            name="new_potential"
        )
        
        # Add the potential
        self.agent.add_potential(new_potential)
        
        # Check that the potential was added
        self.assertEqual(len(self.agent.potentials), 2)
        self.assertEqual(self.agent.potentials[1].name, "new_potential")


if __name__ == '__main__':
    unittest.main()
