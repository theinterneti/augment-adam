"""Tests for the prompt manager module.

This module contains tests for the prompt management functionality.

Version: 0.1.0
Created: 2025-04-22
"""

import os
import tempfile
from pathlib import Path
import json
import time

import pytest
from unittest.mock import patch, MagicMock

import dspy

from dukat.core.prompt_manager import PromptTemplate, PromptManager, get_prompt_manager


def test_prompt_template_init():
    """Test that a prompt template initializes correctly."""
    # Create a template with explicit variables
    template = PromptTemplate(
        name="test",
        template="Hello, {name}!",
        variables=["name"],
        description="A test template",
    )
    
    assert template.name == "test"
    assert template.template == "Hello, {name}!"
    assert template.variables == ["name"]
    assert template.description == "A test template"
    assert isinstance(template.created_at, int)
    assert isinstance(template.updated_at, int)
    assert template.created_at == template.updated_at
    
    # Create a template with extracted variables
    template = PromptTemplate(
        name="test2",
        template="Hello, {name}! Your age is {age}.",
        description="Another test template",
    )
    
    assert template.name == "test2"
    assert template.template == "Hello, {name}! Your age is {age}."
    assert sorted(template.variables) == sorted(["name", "age"])
    assert template.description == "Another test template"


def test_prompt_template_format():
    """Test that a prompt template formats correctly."""
    template = PromptTemplate(
        name="test",
        template="Hello, {name}! Your age is {age}.",
    )
    
    # Format with all variables
    result = template.format(name="Alice", age=30)
    assert result == "Hello, Alice! Your age is 30."
    
    # Format with missing variables
    with pytest.raises(ValueError):
        template.format(name="Alice")
    
    # Format with extra variables
    result = template.format(name="Alice", age=30, extra="ignored")
    assert result == "Hello, Alice! Your age is 30."


def test_prompt_template_to_dict():
    """Test that a prompt template converts to a dictionary correctly."""
    template = PromptTemplate(
        name="test",
        template="Hello, {name}!",
        variables=["name"],
        description="A test template",
    )
    
    data = template.to_dict()
    
    assert data["name"] == "test"
    assert data["template"] == "Hello, {name}!"
    assert data["variables"] == ["name"]
    assert data["description"] == "A test template"
    assert "created_at" in data
    assert "updated_at" in data


def test_prompt_template_from_dict():
    """Test that a prompt template is created from a dictionary correctly."""
    data = {
        "name": "test",
        "template": "Hello, {name}!",
        "variables": ["name"],
        "description": "A test template",
        "created_at": 1234567890,
        "updated_at": 1234567890,
    }
    
    template = PromptTemplate.from_dict(data)
    
    assert template.name == "test"
    assert template.template == "Hello, {name}!"
    assert template.variables == ["name"]
    assert template.description == "A test template"
    assert template.created_at == 1234567890
    assert template.updated_at == 1234567890


def test_prompt_manager_init():
    """Test that a prompt manager initializes correctly."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a prompt manager
        manager = PromptManager(persist_dir=temp_dir)
        
        # Check that the directory was created
        assert os.path.exists(temp_dir)
        
        # Check that default templates were created
        assert "conversation" in manager.templates
        assert "chain_of_thought" in manager.templates
        assert "tool_use" in manager.templates
        
        # Check that the templates were saved
        assert os.path.exists(os.path.join(temp_dir, "conversation.json"))
        assert os.path.exists(os.path.join(temp_dir, "chain_of_thought.json"))
        assert os.path.exists(os.path.join(temp_dir, "tool_use.json"))


def test_prompt_manager_add_template():
    """Test that a prompt manager adds templates correctly."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a prompt manager
        manager = PromptManager(persist_dir=temp_dir)
        
        # Add a new template
        result = manager.add_template(
            name="test",
            template="Hello, {name}!",
            variables=["name"],
            description="A test template",
        )
        
        # Check that the template was added
        assert result is True
        assert "test" in manager.templates
        assert manager.templates["test"].name == "test"
        assert manager.templates["test"].template == "Hello, {name}!"
        assert manager.templates["test"].variables == ["name"]
        assert manager.templates["test"].description == "A test template"
        
        # Check that the template was saved
        assert os.path.exists(os.path.join(temp_dir, "test.json"))
        
        # Try to add a duplicate template
        result = manager.add_template(
            name="test",
            template="Goodbye, {name}!",
            variables=["name"],
            description="Another test template",
        )
        
        # Check that the template was not added
        assert result is False
        assert manager.templates["test"].template == "Hello, {name}!"
        
        # Add a duplicate template with overwrite
        result = manager.add_template(
            name="test",
            template="Goodbye, {name}!",
            variables=["name"],
            description="Another test template",
            overwrite=True,
        )
        
        # Check that the template was updated
        assert result is True
        assert manager.templates["test"].template == "Goodbye, {name}!"
        assert manager.templates["test"].description == "Another test template"


def test_prompt_manager_get_template():
    """Test that a prompt manager gets templates correctly."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a prompt manager
        manager = PromptManager(persist_dir=temp_dir)
        
        # Add a template
        manager.add_template(
            name="test",
            template="Hello, {name}!",
            variables=["name"],
            description="A test template",
        )
        
        # Get the template
        template = manager.get_template("test")
        
        # Check that the template was retrieved
        assert template is not None
        assert template.name == "test"
        assert template.template == "Hello, {name}!"
        assert template.variables == ["name"]
        assert template.description == "A test template"
        
        # Get a non-existent template
        template = manager.get_template("nonexistent")
        
        # Check that the template was not retrieved
        assert template is None


def test_prompt_manager_format_prompt():
    """Test that a prompt manager formats prompts correctly."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a prompt manager
        manager = PromptManager(persist_dir=temp_dir)
        
        # Add a template
        manager.add_template(
            name="test",
            template="Hello, {name}! Your age is {age}.",
            variables=["name", "age"],
            description="A test template",
        )
        
        # Format a prompt
        result = manager.format_prompt("test", name="Alice", age=30)
        
        # Check that the prompt was formatted
        assert result == "Hello, Alice! Your age is 30."
        
        # Format a prompt with a non-existent template
        with pytest.raises(ValueError):
            manager.format_prompt("nonexistent", name="Alice", age=30)
        
        # Format a prompt with missing variables
        with pytest.raises(ValueError):
            manager.format_prompt("test", name="Alice")


def test_prompt_manager_list_templates():
    """Test that a prompt manager lists templates correctly."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a prompt manager
        manager = PromptManager(persist_dir=temp_dir)
        
        # Add some templates
        manager.add_template(
            name="test1",
            template="Hello, {name}!",
            variables=["name"],
            description="Test template 1",
        )
        
        manager.add_template(
            name="test2",
            template="Goodbye, {name}!",
            variables=["name"],
            description="Test template 2",
        )
        
        # List the templates
        templates = manager.list_templates()
        
        # Check that the templates were listed
        assert len(templates) >= 2  # May include default templates
        
        # Find our test templates
        test1 = next((t for t in templates if t["name"] == "test1"), None)
        test2 = next((t for t in templates if t["name"] == "test2"), None)
        
        assert test1 is not None
        assert test2 is not None
        
        assert test1["description"] == "Test template 1"
        assert test2["description"] == "Test template 2"
        
        assert "name" in test1
        assert "variables" in test1
        assert "created_at" in test1
        assert "updated_at" in test1


def test_prompt_manager_delete_template():
    """Test that a prompt manager deletes templates correctly."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a prompt manager
        manager = PromptManager(persist_dir=temp_dir)
        
        # Add a template
        manager.add_template(
            name="test",
            template="Hello, {name}!",
            variables=["name"],
            description="A test template",
        )
        
        # Check that the template was saved
        assert os.path.exists(os.path.join(temp_dir, "test.json"))
        
        # Delete the template
        result = manager.delete_template("test")
        
        # Check that the template was deleted
        assert result is True
        assert "test" not in manager.templates
        assert not os.path.exists(os.path.join(temp_dir, "test.json"))
        
        # Delete a non-existent template
        result = manager.delete_template("nonexistent")
        
        # Check that the operation failed
        assert result is False


def test_prompt_manager_update_template():
    """Test that a prompt manager updates templates correctly."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a prompt manager
        manager = PromptManager(persist_dir=temp_dir)
        
        # Add a template
        manager.add_template(
            name="test",
            template="Hello, {name}!",
            variables=["name"],
            description="A test template",
        )
        
        # Get the original timestamp
        original_updated_at = manager.templates["test"].updated_at
        
        # Wait a moment to ensure the timestamp changes
        time.sleep(0.1)
        
        # Update the template
        result = manager.update_template(
            name="test",
            template="Goodbye, {name}!",
            description="Updated test template",
        )
        
        # Check that the template was updated
        assert result is True
        assert manager.templates["test"].template == "Goodbye, {name}!"
        assert manager.templates["test"].variables == ["name"]
        assert manager.templates["test"].description == "Updated test template"
        assert manager.templates["test"].updated_at > original_updated_at
        
        # Update a non-existent template
        result = manager.update_template(
            name="nonexistent",
            template="Hello, {name}!",
        )
        
        # Check that the operation failed
        assert result is False


@patch("dukat.core.prompt_manager.dspy.ChainOfThought")
def test_prompt_manager_create_dspy_module_chain_of_thought(mock_cot):
    """Test that a prompt manager creates DSPy modules correctly."""
    # Set up the mock
    mock_module = MagicMock()
    mock_cot.return_value = mock_module
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a prompt manager
        manager = PromptManager(persist_dir=temp_dir)
        
        # Add a template
        manager.add_template(
            name="test",
            template="Hello, {name}!",
            variables=["name"],
            description="A test template",
        )
        
        # Create a DSPy module
        module = manager.create_dspy_module(
            template_name="test",
            signature="question -> answer",
            module_type="chain_of_thought",
        )
        
        # Check that the module was created
        mock_cot.assert_called_once_with("question -> answer")
        assert module == mock_module
        
        # Create a module with a non-existent template
        with pytest.raises(ValueError):
            manager.create_dspy_module(
                template_name="nonexistent",
                signature="question -> answer",
            )
        
        # Create a module with an invalid type
        with pytest.raises(ValueError):
            manager.create_dspy_module(
                template_name="test",
                signature="question -> answer",
                module_type="invalid",
            )


@patch("dukat.core.prompt_manager.dspy.Predict")
def test_prompt_manager_create_dspy_module_predict(mock_predict):
    """Test that a prompt manager creates DSPy Predict modules correctly."""
    # Set up the mock
    mock_module = MagicMock()
    mock_predict.return_value = mock_module
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a prompt manager
        manager = PromptManager(persist_dir=temp_dir)
        
        # Add a template
        manager.add_template(
            name="test",
            template="Hello, {name}!",
            variables=["name"],
            description="A test template",
        )
        
        # Create a DSPy module
        module = manager.create_dspy_module(
            template_name="test",
            signature="question -> answer",
            module_type="predict",
        )
        
        # Check that the module was created
        mock_predict.assert_called_once_with("question -> answer")
        assert module == mock_module


@patch("dukat.core.prompt_manager.dspy.ReAct")
def test_prompt_manager_create_dspy_module_react(mock_react):
    """Test that a prompt manager creates DSPy ReAct modules correctly."""
    # Set up the mock
    mock_module = MagicMock()
    mock_react.return_value = mock_module
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a prompt manager
        manager = PromptManager(persist_dir=temp_dir)
        
        # Add a template
        manager.add_template(
            name="test",
            template="Hello, {name}!",
            variables=["name"],
            description="A test template",
        )
        
        # Create a DSPy module
        module = manager.create_dspy_module(
            template_name="test",
            signature="question -> answer",
            module_type="react",
        )
        
        # Check that the module was created
        mock_react.assert_called_once_with("question -> answer")
        assert module == mock_module


@patch("dukat.core.prompt_manager.PromptManager")
def test_get_prompt_manager(mock_manager_class):
    """Test that the get_prompt_manager function works correctly."""
    # Set up the mock
    mock_manager = MagicMock()
    mock_manager_class.return_value = mock_manager
    
    # Get a prompt manager
    manager = get_prompt_manager(persist_dir="/tmp/test")
    
    # Check that the manager was created correctly
    mock_manager_class.assert_called_once_with("/tmp/test")
    
    # Check that the manager is correct
    assert manager == mock_manager
    
    # Get the manager again
    manager2 = get_prompt_manager()
    
    # Check that the manager was not created again
    assert mock_manager_class.call_count == 1
    
    # Check that the same manager is returned
    assert manager2 == manager
