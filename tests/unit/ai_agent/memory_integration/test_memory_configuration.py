"""Unit tests for the memory configuration module.

This module contains unit tests for the memory configuration module.

Version: 0.1.0
Created: 2025-05-01
"""

import unittest
from unittest.mock import MagicMock, patch

from augment_adam.ai_agent.memory_integration.memory_configuration import (
    MemoryConfiguration,
    MemoryAllocation,
    get_memory_configuration,
)


class TestMemoryConfiguration(unittest.TestCase):
    """Unit tests for the MemoryConfiguration class."""

    def setUp(self):
        """Set up test fixtures."""
        self.memory_config = MemoryConfiguration()

    def test_get_allocation_for_role(self):
        """Test getting memory allocation for a specific role."""
        # Test default role
        default_allocation = self.memory_config.get_allocation_for_role("default")
        self.assertEqual(default_allocation.working_memory_size, 20)
        self.assertEqual(default_allocation.episodic_memory_size, 100)
        self.assertEqual(default_allocation.semantic_memory_size, 500)
        self.assertEqual(default_allocation.context_window_size, 8192)

        # Test researcher role
        researcher_allocation = self.memory_config.get_allocation_for_role("researcher")
        self.assertEqual(researcher_allocation.working_memory_size, 15)
        self.assertEqual(researcher_allocation.episodic_memory_size, 150)
        self.assertEqual(researcher_allocation.semantic_memory_size, 1000)
        self.assertEqual(researcher_allocation.context_window_size, 8192)

        # Test coder role
        coder_allocation = self.memory_config.get_allocation_for_role("coder")
        self.assertEqual(coder_allocation.working_memory_size, 25)
        self.assertEqual(coder_allocation.episodic_memory_size, 100)
        self.assertEqual(coder_allocation.semantic_memory_size, 300)
        self.assertEqual(coder_allocation.context_window_size, 8192)

        # Test writer role
        writer_allocation = self.memory_config.get_allocation_for_role("writer")
        self.assertEqual(writer_allocation.working_memory_size, 30)
        self.assertEqual(writer_allocation.episodic_memory_size, 200)
        self.assertEqual(writer_allocation.semantic_memory_size, 400)
        self.assertEqual(writer_allocation.context_window_size, 8192)

        # Test coordinator role
        coordinator_allocation = self.memory_config.get_allocation_for_role(
            "coordinator"
        )
        self.assertEqual(coordinator_allocation.working_memory_size, 40)
        self.assertEqual(coordinator_allocation.episodic_memory_size, 80)
        self.assertEqual(coordinator_allocation.semantic_memory_size, 200)
        self.assertEqual(coordinator_allocation.context_window_size, 8192)

        # Test unknown role (should return default)
        unknown_allocation = self.memory_config.get_allocation_for_role("unknown")
        self.assertEqual(unknown_allocation.working_memory_size, 20)
        self.assertEqual(unknown_allocation.episodic_memory_size, 100)
        self.assertEqual(unknown_allocation.semantic_memory_size, 500)
        self.assertEqual(unknown_allocation.context_window_size, 8192)

    def test_get_context_window_size(self):
        """Test getting context window size for a specific model."""
        # Test Anthropic models
        self.assertEqual(
            self.memory_config.get_context_window_size("claude-3-opus-20240229"), 200000
        )
        self.assertEqual(
            self.memory_config.get_context_window_size("claude-3-sonnet-20240229"),
            200000,
        )
        self.assertEqual(
            self.memory_config.get_context_window_size("claude-3-haiku-20240307"),
            200000,
        )

        # Test OpenAI models
        self.assertEqual(
            self.memory_config.get_context_window_size("gpt-4-turbo"), 128000
        )
        self.assertEqual(self.memory_config.get_context_window_size("gpt-4"), 8192)
        self.assertEqual(self.memory_config.get_context_window_size("gpt-4-32k"), 32768)

        # Test Hugging Face models
        self.assertEqual(self.memory_config.get_context_window_size("llama-2-7b"), 4096)
        self.assertEqual(self.memory_config.get_context_window_size("mistral-7b"), 8192)
        self.assertEqual(
            self.memory_config.get_context_window_size("mixtral-8x7b"), 32768
        )

        # Test unknown model (should return default)
        self.assertEqual(
            self.memory_config.get_context_window_size("unknown-model"), 4096
        )

    def test_register_role(self):
        """Test registering a new role configuration."""
        # Create a new allocation
        new_allocation = MemoryAllocation(
            working_memory_size=50,
            episodic_memory_size=200,
            semantic_memory_size=1000,
            context_window_size=16384,
            working_memory_token_ratio=0.4,
            episodic_memory_token_ratio=0.3,
            semantic_memory_token_ratio=0.2,
            procedural_memory_token_ratio=0.1,
        )

        # Register the new role
        self.memory_config.register_role("custom_role", new_allocation)

        # Get the allocation for the new role
        custom_allocation = self.memory_config.get_allocation_for_role("custom_role")
        self.assertEqual(custom_allocation.working_memory_size, 50)
        self.assertEqual(custom_allocation.episodic_memory_size, 200)
        self.assertEqual(custom_allocation.semantic_memory_size, 1000)
        self.assertEqual(custom_allocation.context_window_size, 16384)
        self.assertEqual(custom_allocation.working_memory_token_ratio, 0.4)
        self.assertEqual(custom_allocation.episodic_memory_token_ratio, 0.3)
        self.assertEqual(custom_allocation.semantic_memory_token_ratio, 0.2)
        self.assertEqual(custom_allocation.procedural_memory_token_ratio, 0.1)

    def test_register_model(self):
        """Test registering a new model with its context window size."""
        # Register a new model
        self.memory_config.register_model("custom-model", 12345)

        # Get the context window size for the new model
        context_window_size = self.memory_config.get_context_window_size("custom-model")
        self.assertEqual(context_window_size, 12345)

    @patch(
        "augment_adam.ai_agent.memory_integration.memory_configuration.MemoryManager"
    )
    @patch(
        "augment_adam.ai_agent.memory_integration.memory_configuration.get_context_manager"
    )
    def test_configure_memory_for_agent(
        self, mock_get_context_manager, mock_memory_manager
    ):
        """Test configuring memory for an agent."""
        # Mock context manager
        mock_context_manager = MagicMock()
        mock_get_context_manager.return_value = mock_context_manager
        mock_context_window = MagicMock()
        mock_context_manager.create_context_window.return_value = mock_context_window

        # Configure memory for an agent
        memory_components = self.memory_config.configure_memory_for_agent(
            agent_name="test_agent",
            role="researcher",
            model_name="claude-3-sonnet-20240229",
        )

        # Check that the components were created
        self.assertIn("memory_manager", memory_components)
        self.assertIn("context_window", memory_components)
        self.assertIn("working_memory", memory_components)
        self.assertIn("episodic_memory", memory_components)
        self.assertIn("semantic_memory", memory_components)
        self.assertIn("allocation", memory_components)
        self.assertIn("token_budgets", memory_components)

        # Check token budgets
        token_budgets = memory_components["token_budgets"]
        self.assertIn("working_memory", token_budgets)
        self.assertIn("episodic_memory", token_budgets)
        self.assertIn("semantic_memory", token_budgets)
        self.assertIn("procedural_memory", token_budgets)

        # Check that context window was created with correct size
        mock_context_manager.create_context_window.assert_called_once()
        args, kwargs = mock_context_manager.create_context_window.call_args
        self.assertEqual(kwargs["name"], "test_agent_window")
        self.assertEqual(kwargs["max_tokens"], 8192)  # Limited by allocation, not model

    def test_get_memory_configuration(self):
        """Test getting the global memory configuration instance."""
        # Get the global instance
        memory_config = get_memory_configuration()

        # Check that it's a MemoryConfiguration instance
        self.assertIsInstance(memory_config, MemoryConfiguration)

        # Get it again and check that it's the same instance
        memory_config2 = get_memory_configuration()
        self.assertIs(memory_config, memory_config2)


if __name__ == "__main__":
    unittest.main()
