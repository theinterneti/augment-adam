#!/usr/bin/env python3
"""
Tests for the ModelManager class
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/models')))

from model_manager import ModelManager

class TestModelManager(unittest.TestCase):
    """Test cases for the ModelManager class."""
    
    @patch('model_manager.requests.post')
    def test_generate_local(self, mock_post):
        """Test generating a response using a local model."""
        # Mock the response from Ollama
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "This is a test response"}
        mock_post.return_value = mock_response
        
        # Create a ModelManager instance
        manager = ModelManager(model_name="test-model", use_local=True)
        
        # Call the generate_response method
        response = manager.generate_response("Test prompt", "Test system prompt")
        
        # Check that the response is correct
        self.assertEqual(response, "This is a test response")
        
        # Check that the request was made with the correct parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "http://localhost:11434/api/generate")
        self.assertEqual(kwargs["json"]["model"], "test-model")
        self.assertEqual(kwargs["json"]["prompt"], "Test prompt")
        self.assertEqual(kwargs["json"]["system"], "Test system prompt")
    
    @patch('model_manager.requests.get')
    def test_get_available_models(self, mock_get):
        """Test getting available models."""
        # Mock the response from Ollama
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "models": [
                {"name": "model1"},
                {"name": "model2"},
                {"name": "model3"}
            ]
        }
        mock_get.return_value = mock_response
        
        # Create a ModelManager instance
        manager = ModelManager(use_local=True)
        
        # Call the get_available_models method
        models = manager.get_available_models()
        
        # Check that the models list is correct
        self.assertEqual(models, ["model1", "model2", "model3"])
        
        # Check that the request was made to the correct URL
        mock_get.assert_called_once_with("http://localhost:11434/api/tags")

if __name__ == '__main__':
    unittest.main()
