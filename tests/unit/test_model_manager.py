"""Tests for the model manager module.

This module contains tests for the model management functionality.

Version: 0.1.0
Created: 2025-04-22
"""

import pytest
from unittest.mock import patch, MagicMock

import dspy

from dukat.core.model_manager import ModelManager, get_model_manager


@pytest.fixture
def mock_dspy_lm():
    """Create a mock DSPy LM instance."""
    mock_lm = MagicMock(spec=dspy.LM)
    mock_lm.return_value = ["This is a test response"]
    return mock_lm


@patch("dukat.core.model_manager.dspy.LM")
def test_model_manager_init(mock_lm_class, mock_dspy_lm):
    """Test that the model manager initializes correctly."""
    # Set up the mock
    mock_lm_class.return_value = mock_dspy_lm

    # Create a model manager
    manager = ModelManager(
        model_name="test-model",
        ollama_host="http://test-host:11434",
    )

    # Check that the model was loaded correctly
    mock_lm_class.assert_called_once_with(
        "ollama_chat/test-model",
        api_base="http://test-host:11434",
        api_key="",
    )

    # Check that the manager has the correct attributes
    assert manager.model_name == "test-model"
    assert manager.ollama_host == "http://test-host:11434"
    assert manager.lm == mock_dspy_lm


@patch("dukat.core.model_manager.dspy.LM")
def test_model_manager_generate_response(mock_lm_class, mock_dspy_lm):
    """Test that the model manager generates responses correctly."""
    # Set up the mock
    mock_lm_class.return_value = mock_dspy_lm

    # Create a model manager
    manager = ModelManager(
        model_name="test-model",
        ollama_host="http://test-host:11434",
    )

    # Generate a response
    response = manager.generate_response("Test prompt")

    # Check that the model was called correctly
    mock_dspy_lm.assert_called_once_with("Test prompt")

    # Check that the response is correct
    assert response == "This is a test response"


@patch("dukat.core.model_manager.dspy.ChainOfThought")
@patch("dukat.core.model_manager.dspy.LM")
def test_model_manager_create_module(mock_lm_class, mock_cot_class, mock_dspy_lm):
    """Test that the model manager creates modules correctly."""
    # Set up the mocks
    mock_lm_class.return_value = mock_dspy_lm
    mock_module = MagicMock()
    mock_cot_class.return_value = mock_module

    # Create a model manager
    manager = ModelManager(
        model_name="test-model",
        ollama_host="http://test-host:11434",
    )

    # Create a module
    module = manager.create_module("test -> response")

    # Check that the module was created correctly
    mock_cot_class.assert_called_once_with("test -> response")

    # Check that the module is correct
    assert module == mock_module


@patch("dukat.core.model_manager.dspy.Example")
@patch("dukat.core.model_manager.dspy.LM")
def test_model_manager_optimize_module(mock_lm_class, mock_example_class, mock_dspy_lm):
    """Test that the model manager optimizes modules correctly."""
    # Set up the mocks
    mock_lm_class.return_value = mock_dspy_lm

    mock_dataset = MagicMock()
    mock_example_class.from_list.return_value = mock_dataset

    # Create a model manager
    manager = ModelManager(
        model_name="test-model",
        ollama_host="http://test-host:11434",
    )

    # Create a module to optimize
    mock_module = MagicMock()
    mock_module.__class__.__name__ = "TestModule"

    # Create example data
    examples = [
        {"test": "example1", "response": "answer1"},
        {"test": "example2", "response": "answer2"},
    ]

    # Optimize the module
    optimized_module = manager.optimize_module(mock_module, examples)

    # Check that the dataset was created correctly
    mock_example_class.from_list.assert_called_once_with(examples)

    # Check that the optimized module is the same as the input module
    # (since our implementation just returns the original module)
    assert optimized_module == mock_module


@patch("dukat.core.model_manager.ModelManager")
def test_get_model_manager(mock_manager_class):
    """Test that the get_model_manager function works correctly."""
    # Set up the mock
    mock_manager = MagicMock()
    mock_manager_class.return_value = mock_manager

    # Get a model manager
    manager = get_model_manager(
        model_name="test-model",
        ollama_host="http://test-host:11434",
    )

    # Check that the manager was created correctly
    mock_manager_class.assert_called_once_with(
        "test-model",
        "http://test-host:11434",
        "",
    )

    # Check that the manager is correct
    assert manager == mock_manager

    # Get the manager again
    manager2 = get_model_manager()

    # Check that the manager was not created again
    assert mock_manager_class.call_count == 1

    # Check that the same manager is returned
    assert manager2 == manager
