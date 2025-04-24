"""Tests for the working memory module.

This module contains tests for the working memory functionality.

Version: 0.1.0
Created: 2025-04-22
"""

import os
import tempfile
import time
import json

import pytest

from augment_adam.memory.working import Message, WorkingMemory


def test_message_init():
    """Test that a message initializes correctly."""
    # Create a message with minimal arguments
    message = Message(content="Hello, world!")
    
    assert message.content == "Hello, world!"
    assert message.role == "user"
    assert isinstance(message.timestamp, int)
    assert message.metadata == {}
    
    # Create a message with all arguments
    timestamp = int(time.time())
    metadata = {"key": "value"}
    
    message = Message(
        content="Hello, again!",
        role="assistant",
        timestamp=timestamp,
        metadata=metadata,
    )
    
    assert message.content == "Hello, again!"
    assert message.role == "assistant"
    assert message.timestamp == timestamp
    assert message.metadata == metadata


def test_message_to_dict():
    """Test that a message converts to a dictionary correctly."""
    timestamp = int(time.time())
    metadata = {"key": "value"}
    
    message = Message(
        content="Hello, world!",
        role="user",
        timestamp=timestamp,
        metadata=metadata,
    )
    
    data = message.to_dict()
    
    assert data["content"] == "Hello, world!"
    assert data["role"] == "user"
    assert data["timestamp"] == timestamp
    assert data["metadata"] == metadata


def test_message_from_dict():
    """Test that a message is created from a dictionary correctly."""
    timestamp = int(time.time())
    metadata = {"key": "value"}
    
    data = {
        "content": "Hello, world!",
        "role": "user",
        "timestamp": timestamp,
        "metadata": metadata,
    }
    
    message = Message.from_dict(data)
    
    assert message.content == "Hello, world!"
    assert message.role == "user"
    assert message.timestamp == timestamp
    assert message.metadata == metadata


def test_message_str():
    """Test that a message converts to a string correctly."""
    message = Message(content="Hello, world!", role="user")
    
    assert str(message) == "user: Hello, world!"


def test_working_memory_init():
    """Test that working memory initializes correctly."""
    # Create working memory with minimal arguments
    memory = WorkingMemory()
    
    assert len(memory.messages) == 0
    assert memory.max_messages == 100
    assert memory.context == {}
    assert memory.conversation_id.startswith("conv_")
    
    # Create working memory with all arguments
    memory = WorkingMemory(
        max_messages=50,
        conversation_id="test_conversation",
    )
    
    assert len(memory.messages) == 0
    assert memory.max_messages == 50
    assert memory.context == {}
    assert memory.conversation_id == "test_conversation"


def test_working_memory_add_message():
    """Test that working memory adds messages correctly."""
    memory = WorkingMemory(conversation_id="test_conversation")
    
    # Add a message
    message = memory.add_message(
        content="Hello, world!",
        role="user",
        metadata={"key": "value"},
    )
    
    assert len(memory.messages) == 1
    assert memory.messages[0] == message
    assert message.content == "Hello, world!"
    assert message.role == "user"
    assert message.metadata["key"] == "value"
    assert message.metadata["conversation_id"] == "test_conversation"
    
    # Add another message
    message = memory.add_message(
        content="Hello, again!",
        role="assistant",
    )
    
    assert len(memory.messages) == 2
    assert memory.messages[1] == message
    assert message.content == "Hello, again!"
    assert message.role == "assistant"
    assert message.metadata["conversation_id"] == "test_conversation"


def test_working_memory_get_messages():
    """Test that working memory retrieves messages correctly."""
    memory = WorkingMemory()
    
    # Add some messages
    memory.add_message(content="Message 1", role="user")
    memory.add_message(content="Message 2", role="assistant")
    memory.add_message(content="Message 3", role="user")
    memory.add_message(content="Message 4", role="assistant")
    
    # Get all messages
    messages = memory.get_messages()
    
    assert len(messages) == 4
    assert messages[0].content == "Message 1"
    assert messages[1].content == "Message 2"
    assert messages[2].content == "Message 3"
    assert messages[3].content == "Message 4"
    
    # Get a limited number of messages
    messages = memory.get_messages(n=2)
    
    assert len(messages) == 2
    assert messages[0].content == "Message 3"
    assert messages[1].content == "Message 4"
    
    # Get messages by role
    messages = memory.get_messages(roles=["user"])
    
    assert len(messages) == 2
    assert messages[0].content == "Message 1"
    assert messages[1].content == "Message 3"
    
    # Get messages in reverse order
    messages = memory.get_messages(reverse=True)
    
    assert len(messages) == 4
    assert messages[0].content == "Message 4"
    assert messages[1].content == "Message 3"
    assert messages[2].content == "Message 2"
    assert messages[3].content == "Message 1"
    
    # Get a limited number of messages in reverse order
    messages = memory.get_messages(n=2, reverse=True)
    
    assert len(messages) == 2
    assert messages[0].content == "Message 4"
    assert messages[1].content == "Message 3"
    
    # Get messages by role in reverse order
    messages = memory.get_messages(roles=["user"], reverse=True)
    
    assert len(messages) == 2
    assert messages[0].content == "Message 3"
    assert messages[1].content == "Message 1"


def test_working_memory_get_last_message():
    """Test that working memory retrieves the last message correctly."""
    memory = WorkingMemory()
    
    # Get the last message when there are no messages
    message = memory.get_last_message()
    
    assert message is None
    
    # Add some messages
    memory.add_message(content="Message 1", role="user")
    memory.add_message(content="Message 2", role="assistant")
    memory.add_message(content="Message 3", role="user")
    
    # Get the last message
    message = memory.get_last_message()
    
    assert message is not None
    assert message.content == "Message 3"
    assert message.role == "user"
    
    # Get the last message by role
    message = memory.get_last_message(role="assistant")
    
    assert message is not None
    assert message.content == "Message 2"
    assert message.role == "assistant"
    
    # Get the last message by a role that doesn't exist
    message = memory.get_last_message(role="system")
    
    assert message is None


def test_working_memory_clear_messages():
    """Test that working memory clears messages correctly."""
    memory = WorkingMemory()
    
    # Add some messages
    memory.add_message(content="Message 1", role="user")
    memory.add_message(content="Message 2", role="assistant")
    
    assert len(memory.messages) == 2
    
    # Clear the messages
    memory.clear_messages()
    
    assert len(memory.messages) == 0


def test_working_memory_context():
    """Test that working memory manages context correctly."""
    memory = WorkingMemory()
    
    # Set a context item
    memory.set_context("key1", "value1")
    
    assert memory.context["key1"] == "value1"
    
    # Get a context item
    value = memory.get_context("key1")
    
    assert value == "value1"
    
    # Get a context item with a default value
    value = memory.get_context("key2", "default")
    
    assert value == "default"
    
    # Set another context item
    memory.set_context("key2", "value2")
    
    assert memory.context["key2"] == "value2"
    
    # Remove a context item
    result = memory.remove_context("key1")
    
    assert result is True
    assert "key1" not in memory.context
    
    # Remove a context item that doesn't exist
    result = memory.remove_context("key3")
    
    assert result is False
    
    # Clear all context items
    memory.clear_context()
    
    assert memory.context == {}


def test_working_memory_format_history():
    """Test that working memory formats history correctly."""
    memory = WorkingMemory()
    
    # Add some messages
    memory.add_message(content="Hello", role="user")
    memory.add_message(content="Hi there", role="assistant")
    memory.add_message(content="How are you?", role="user")
    memory.add_message(content="I'm doing well", role="assistant")
    
    # Format the history with roles
    history = memory.format_history()
    
    assert history == "user: Hello\nassistant: Hi there\nuser: How are you?\nassistant: I'm doing well"
    
    # Format the history without roles
    history = memory.format_history(include_roles=False)
    
    assert history == "Hello\nHi there\nHow are you?\nI'm doing well"
    
    # Format the history with a custom separator
    history = memory.format_history(separator=" | ")
    
    assert history == "user: Hello | assistant: Hi there | user: How are you? | assistant: I'm doing well"
    
    # Format a limited history
    history = memory.format_history(n=2)
    
    assert history == "user: How are you?\nassistant: I'm doing well"


def test_working_memory_to_dict():
    """Test that working memory converts to a dictionary correctly."""
    memory = WorkingMemory(
        max_messages=50,
        conversation_id="test_conversation",
    )
    
    # Add some messages
    memory.add_message(content="Message 1", role="user")
    memory.add_message(content="Message 2", role="assistant")
    
    # Set some context
    memory.set_context("key1", "value1")
    memory.set_context("key2", "value2")
    
    # Convert to a dictionary
    data = memory.to_dict()
    
    assert data["max_messages"] == 50
    assert data["conversation_id"] == "test_conversation"
    assert len(data["messages"]) == 2
    assert data["messages"][0]["content"] == "Message 1"
    assert data["messages"][1]["content"] == "Message 2"
    assert data["context"]["key1"] == "value1"
    assert data["context"]["key2"] == "value2"


def test_working_memory_from_dict():
    """Test that working memory is created from a dictionary correctly."""
    data = {
        "max_messages": 50,
        "conversation_id": "test_conversation",
        "messages": [
            {
                "content": "Message 1",
                "role": "user",
                "timestamp": int(time.time()),
                "metadata": {"key": "value"},
            },
            {
                "content": "Message 2",
                "role": "assistant",
                "timestamp": int(time.time()),
                "metadata": {},
            },
        ],
        "context": {
            "key1": "value1",
            "key2": "value2",
        },
    }
    
    memory = WorkingMemory.from_dict(data)
    
    assert memory.max_messages == 50
    assert memory.conversation_id == "test_conversation"
    assert len(memory.messages) == 2
    assert memory.messages[0].content == "Message 1"
    assert memory.messages[1].content == "Message 2"
    assert memory.context["key1"] == "value1"
    assert memory.context["key2"] == "value2"


def test_working_memory_save_load():
    """Test that working memory saves and loads correctly."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name
    
    try:
        # Create working memory
        memory = WorkingMemory(
            max_messages=50,
            conversation_id="test_conversation",
        )
        
        # Add some messages
        memory.add_message(content="Message 1", role="user")
        memory.add_message(content="Message 2", role="assistant")
        
        # Set some context
        memory.set_context("key1", "value1")
        memory.set_context("key2", "value2")
        
        # Save the memory
        result = memory.save(file_path)
        
        assert result is True
        assert os.path.exists(file_path)
        
        # Load the memory
        loaded_memory = WorkingMemory.load(file_path)
        
        assert loaded_memory is not None
        assert loaded_memory.max_messages == 50
        assert loaded_memory.conversation_id == "test_conversation"
        assert len(loaded_memory.messages) == 2
        assert loaded_memory.messages[0].content == "Message 1"
        assert loaded_memory.messages[1].content == "Message 2"
        assert loaded_memory.context["key1"] == "value1"
        assert loaded_memory.context["key2"] == "value2"
        
        # Try to load from a non-existent file
        loaded_memory = WorkingMemory.load("nonexistent.json")
        
        assert loaded_memory is None
    
    finally:
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)


def test_working_memory_new_conversation():
    """Test that working memory starts a new conversation correctly."""
    memory = WorkingMemory(
        conversation_id="old_conversation",
    )
    
    # Add some messages
    memory.add_message(content="Message 1", role="user")
    memory.add_message(content="Message 2", role="assistant")
    
    # Set some context
    memory.set_context("key1", "value1")
    
    # Start a new conversation
    new_id = memory.new_conversation()
    
    assert new_id == memory.conversation_id
    assert memory.conversation_id != "old_conversation"
    assert len(memory.messages) == 0
    assert memory.context == {}


def test_working_memory_max_messages():
    """Test that working memory respects the maximum number of messages."""
    memory = WorkingMemory(max_messages=3)
    
    # Add more messages than the maximum
    memory.add_message(content="Message 1", role="user")
    memory.add_message(content="Message 2", role="assistant")
    memory.add_message(content="Message 3", role="user")
    memory.add_message(content="Message 4", role="assistant")
    
    # Check that only the most recent messages are kept
    assert len(memory.messages) == 3
    assert memory.messages[0].content == "Message 2"
    assert memory.messages[1].content == "Message 3"
    assert memory.messages[2].content == "Message 4"


def test_working_memory_get_openai_messages():
    """Test that working memory formats messages for OpenAI correctly."""
    memory = WorkingMemory()
    
    # Add some messages
    memory.add_message(content="Hello", role="user")
    memory.add_message(content="Hi there", role="assistant")
    memory.add_message(content="How are you?", role="user")
    memory.add_message(content="I'm doing well", role="assistant")
    
    # Get OpenAI messages
    messages = memory.get_openai_messages()
    
    assert len(messages) == 4
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Hi there"
    assert messages[2]["role"] == "user"
    assert messages[2]["content"] == "How are you?"
    assert messages[3]["role"] == "assistant"
    assert messages[3]["content"] == "I'm doing well"
    
    # Get a limited number of OpenAI messages
    messages = memory.get_openai_messages(n=2)
    
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "How are you?"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "I'm doing well"


def test_working_memory_get_anthropic_messages():
    """Test that working memory formats messages for Anthropic correctly."""
    memory = WorkingMemory()
    
    # Add some messages
    memory.add_message(content="Hello", role="user")
    memory.add_message(content="Hi there", role="assistant")
    memory.add_message(content="How are you?", role="user")
    memory.add_message(content="I'm doing well", role="assistant")
    
    # Get Anthropic messages
    messages = memory.get_anthropic_messages()
    
    assert len(messages) == 4
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Hi there"
    assert messages[2]["role"] == "user"
    assert messages[2]["content"] == "How are you?"
    assert messages[3]["role"] == "assistant"
    assert messages[3]["content"] == "I'm doing well"
    
    # Get a limited number of Anthropic messages
    messages = memory.get_anthropic_messages(n=2)
    
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "How are you?"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "I'm doing well"
