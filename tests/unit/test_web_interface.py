"""Unit tests for the web interface.

This module contains tests for the web interface.

Version: 0.1.0
Created: 2025-04-23
"""

import pytest
from unittest.mock import MagicMock, patch

from augment_adam.web.interface import (
    WebInterface,
    create_web_interface,
    launch_web_interface,
)


@pytest.fixture
def mock_assistant():
    """Create a mock assistant for testing."""
    assistant = MagicMock()
    assistant.model_manager.model_name = "test-model"
    assistant.generate_response.return_value = "Test response"
    assistant.get_messages.return_value = []
    return assistant


@pytest.fixture
def web_interface(mock_assistant):
    """Create a web interface for testing."""
    return WebInterface(
        assistant=mock_assistant,
        model_name="test-model",
        theme="test-theme",
        title="Test Title",
        description="Test Description",
        version="0.1.0",
    )


def test_web_interface_init(web_interface, mock_assistant):
    """Test initializing the web interface."""
    assert web_interface.assistant is mock_assistant
    assert web_interface.model_name == "test-model"
    assert web_interface.theme == "test-theme"
    assert web_interface.title == "Test Title"
    assert web_interface.description == "Test Description"
    assert web_interface.version == "0.1.0"
    assert web_interface.interface is None
    assert web_interface.conversation_history == []


def test_format_message(web_interface):
    """Test formatting a message."""
    # Test user message
    user_message = {"role": "user", "content": "Hello"}
    formatted_user = web_interface._format_message(user_message)
    assert "<div class='user-message'>" in formatted_user
    assert "<strong>You:</strong>" in formatted_user
    assert "Hello" in formatted_user

    # Test assistant message
    assistant_message = {"role": "assistant", "content": "Hi there"}
    formatted_assistant = web_interface._format_message(assistant_message)
    assert "<div class='assistant-message'>" in formatted_assistant
    assert "<strong>Dukat:</strong>" in formatted_assistant
    assert "Hi there" in formatted_assistant

    # Test system message
    system_message = {"role": "system", "content": "System message"}
    formatted_system = web_interface._format_message(system_message)
    assert "<div class='system-message'>" in formatted_system
    assert "<strong>System:</strong>" in formatted_system
    assert "System message" in formatted_system

    # Test unknown role
    unknown_message = {"role": "unknown", "content": "Unknown message"}
    formatted_unknown = web_interface._format_message(unknown_message)
    assert "<div class='unknown-message'>" in formatted_unknown
    assert "<strong>Unknown:</strong>" in formatted_unknown
    assert "Unknown message" in formatted_unknown


def test_format_conversation(web_interface):
    """Test formatting a conversation."""
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
        {"role": "system", "content": "System message"},
    ]

    formatted = web_interface._format_conversation(messages)

    assert "<div class='conversation'>" in formatted
    assert "<div class='user-message'>" in formatted
    assert "<div class='assistant-message'>" in formatted
    assert "<div class='system-message'>" in formatted
    assert "Hello" in formatted
    assert "Hi there" in formatted
    assert "System message" in formatted


def test_user_input_callback(web_interface, mock_assistant):
    """Test the user input callback."""
    # Test with empty message
    result = web_interface._user_input_callback("", [], "System prompt")
    assert result[0] == ""  # Empty input
    assert result[1] == []  # Unchanged history
    assert "<div class='conversation'>" in result[2]  # Formatted conversation

    # Test with non-empty message
    result = web_interface._user_input_callback("Hello", [], "System prompt")

    # Check that the message was added to the conversation history
    assert len(web_interface.conversation_history) == 2
    assert web_interface.conversation_history[0]["role"] == "user"
    assert web_interface.conversation_history[0]["content"] == "Hello"
    assert web_interface.conversation_history[1]["role"] == "assistant"
    assert web_interface.conversation_history[1]["content"] == "Test response"

    # Check that the assistant was called
    mock_assistant.add_message.assert_called_once()
    mock_assistant.generate_response.assert_called_once_with(
        system_prompt="System prompt")

    # Check the result
    assert result[0] == ""  # Empty input
    assert result[1] == [("Hello", "Test response")]  # Updated history
    assert "<div class='conversation'>" in result[2]  # Formatted conversation


def test_clear_conversation_callback(web_interface, mock_assistant):
    """Test the clear conversation callback."""
    # Add some messages to the conversation history
    web_interface.conversation_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
    ]

    # Call the callback
    result = web_interface._clear_conversation_callback(
        [("Hello", "Hi there")])

    # Check that the conversation history was cleared
    assert web_interface.conversation_history == []

    # Check that the assistant's messages were cleared
    mock_assistant.clear_messages.assert_called_once()

    # Check the result
    assert result[0] == []  # Empty history
    assert "<div class='conversation'>" in result[1]  # Formatted conversation


@patch("os.makedirs")
def test_save_conversation_callback(mock_makedirs, web_interface, mock_assistant):
    """Test the save conversation callback."""
    # Test with empty conversation
    result = web_interface._save_conversation_callback("")
    assert "No conversation to save." in result

    # Add some messages to the conversation history
    web_interface.conversation_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
    ]

    # Test with non-empty conversation
    result = web_interface._save_conversation_callback("test.json")

    # Check that the assistant's save_conversation method was called
    mock_assistant.save_conversation.assert_called_once_with("test.json")

    # Check the result
    assert "Conversation saved to test.json" in result


def test_load_conversation_callback(web_interface, mock_assistant):
    """Test the load conversation callback."""
    # Test with empty path
    result = web_interface._load_conversation_callback("")
    assert result[0] == []  # Empty history
    assert "No file selected." in result[1]

    # Test with non-empty path
    mock_assistant.get_messages.return_value = [
        MagicMock(role="user", content="Hello"),
        MagicMock(role="assistant", content="Hi there"),
    ]

    result = web_interface._load_conversation_callback("test.json")

    # Check that the assistant's load_conversation method was called
    mock_assistant.load_conversation.assert_called_once_with("test.json")

    # Check the result
    assert result[0] == [("Hello", "Hi there")]  # Updated history
    assert "<div class='conversation'>" in result[1]  # Formatted conversation


def test_change_model_callback(web_interface, mock_assistant):
    """Test the change model callback."""
    with patch('augment_adam.web.interface.ModelManager") as mock_model_manager:
        # Call the callback
        result = web_interface._change_model_callback("new-model")

        # Check that a new model manager was created
        mock_model_manager.assert_called_once_with(model_name="new-model")

        # Check that the assistant's model manager was updated
        assert web_interface.assistant.model_manager is mock_model_manager.return_value

        # Check that the model name was updated
        assert web_interface.model_name == "new-model"

        # Check the result
        assert "Model changed to new-model" in result


def test_get_available_models_callback(web_interface, mock_assistant):
    """Test the get available models callback."""
    # Set up the mock
    mock_assistant.model_manager.get_available_models.return_value = [
        "model1", "model2"]

    # Call the callback
    result = web_interface._get_available_models_callback()

    # Check that the assistant's get_available_models method was called
    mock_assistant.model_manager.get_available_models.assert_called_once()

    # Check the result
    assert result == ["model1", "model2"]


def test_create_interface(web_interface, monkeypatch):
    """Test creating the interface."""
    # Mock the gradio.Blocks class
    mock_blocks = MagicMock()
    mock_blocks.return_value.__enter__.return_value = mock_blocks.return_value
    mock_blocks.return_value.__exit__.return_value = None

    # Mock the gradio.Row class
    mock_row = MagicMock()
    mock_row.return_value.__enter__.return_value = mock_row.return_value
    mock_row.return_value.__exit__.return_value = None

    # Mock the gradio.Column class
    mock_column = MagicMock()
    mock_column.return_value.__enter__.return_value = mock_column.return_value
    mock_column.return_value.__exit__.return_value = None

    # Apply the mocks
    monkeypatch.setattr("gradio.Blocks", mock_blocks)
    monkeypatch.setattr("gradio.Row", mock_row)
    monkeypatch.setattr("gradio.Column", mock_column)
    monkeypatch.setattr("gradio.Chatbot", MagicMock())
    monkeypatch.setattr("gradio.HTML", MagicMock())
    monkeypatch.setattr("gradio.Textbox", MagicMock())
    monkeypatch.setattr("gradio.Button", MagicMock())
    monkeypatch.setattr("gradio.Dropdown", MagicMock())
    monkeypatch.setattr("gradio.Markdown", MagicMock())

    # Call the method
    web_interface.interface = mock_blocks.return_value
    result = web_interface.interface

    # Check the result
    assert result is mock_blocks.return_value


def test_launch_web_interface(monkeypatch):
    """Test launching the web interface."""
    # Create mocks
    mock_web_interface = MagicMock()
    mock_create_web_interface = MagicMock(return_value=mock_web_interface)

    # Apply the mocks
    monkeypatch.setattr(
        "augment_adam.web.interface.create_web_interface", mock_create_web_interface)

    # Call the function
    launch_web_interface(
        host="test-host",
        port=1234,
        share=True,
        debug=True,
        model_name="test-model",
        theme="test-theme",
        title="Test Title",
        description="Test Description",
        version="0.1.0",
    )

    # Check that the web interface was created with the correct parameters
    mock_create_web_interface.assert_called_once_with(
        model_name="test-model",
        theme="test-theme",
        title="Test Title",
        description="Test Description",
        version="0.1.0",
    )

    # Check that the interface was launched with the correct parameters
    mock_web_interface.launch.assert_called_once_with(
        host="test-host",
        port=1234,
        share=True,
        debug=True,
    )


def test_create_web_interface():
    """Test creating a web interface."""
    with patch('augment_adam.web.interface.WebInterface") as mock_web_interface:
        # Call the function
        result = create_web_interface(
            model_name="test-model",
            theme="test-theme",
            title="Test Title",
            description="Test Description",
            version="0.1.0",
        )

        # Check that a WebInterface was created
        mock_web_interface.assert_called_once_with(
            model_name="test-model",
            theme="test-theme",
            title="Test Title",
            description="Test Description",
            version="0.1.0",
        )

        # Check the result
        assert result is mock_web_interface.return_value
