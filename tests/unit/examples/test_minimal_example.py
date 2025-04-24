"""Unit tests for the minimal example."""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Import the MinimalAgent class from the example
from examples.minimal_example import MinimalAgent


class TestMinimalExample(unittest.TestCase):
    """Tests for the minimal example."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a minimal agent
        self.agent = MinimalAgent(
            name="Test Agent",
            system_prompt="You are a test agent."
        )

    def test_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.name, "Test Agent")
        self.assertEqual(self.agent.system_prompt, "You are a test agent.")

    def test_process_hello(self):
        """Test processing 'hello' input."""
        result = self.agent.process("hello")
        self.assertIn("Hello", result["response"])
        self.assertIn("minimal AI assistant", result["response"])

    def test_process_help(self):
        """Test processing 'help' input."""
        result = self.agent.process("help")
        self.assertIn("I'm here to help", result["response"])

    def test_process_weather(self):
        """Test processing 'weather' input."""
        result = self.agent.process("What's the weather like?")
        self.assertIn("weather", result["response"])
        self.assertIn("don't have access", result["response"])

    def test_process_framework(self):
        """Test processing 'framework' input."""
        result = self.agent.process("Tell me about the agent framework")
        self.assertIn("Augment Adam agent framework", result["response"])
        self.assertIn("Specialized agents", result["response"])
        self.assertIn("Tool integration", result["response"])
        self.assertIn("Agent coordination", result["response"])
        self.assertIn("MCP server", result["response"])
        self.assertIn("Asynchronous processing", result["response"])

    def test_process_other(self):
        """Test processing other input."""
        result = self.agent.process("Something else")
        self.assertIn("You said: Something else", result["response"])
        self.assertIn("minimal AI assistant", result["response"])

    def test_processing_time(self):
        """Test that processing time is included in the result."""
        result = self.agent.process("hello")
        self.assertIn("processing_time", result)
        self.assertIsInstance(result["processing_time"], float)

    @patch('builtins.input', side_effect=['hello', 'exit'])
    @patch('builtins.print')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_function(self, mock_parse_args, mock_print, mock_input):
        """Test the main function."""
        # Mock the parse_args method to return a mock namespace
        mock_parse_args.return_value = MagicMock()

        # Import the main function
        from examples.minimal_example import main

        # Run the main function
        main()

        # Check that print was called with the expected output
        mock_print.assert_any_call("\nMinimal Assistant: Hello! I'm a minimal AI assistant. How can I help you today?\n")


if __name__ == '__main__':
    unittest.main()
