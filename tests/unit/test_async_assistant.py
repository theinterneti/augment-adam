"""Unit tests for the AsyncAssistant class.

This module contains tests for the asynchronous assistant implementation.

Version: 0.1.0
Created: 2025-04-24
Updated: 2025-04-25
"""

import pytest
import asyncio
import os
import tempfile
import json
from unittest.mock import AsyncMock, MagicMock, patch, call

from dukat.core.async_assistant import AsyncAssistant, get_async_assistant
from dukat.memory.working import Message
from dukat.core.task_queue import TaskStatus


@pytest.fixture
def mock_model_manager():
    """Create a mock model manager."""
    mock_manager = MagicMock()
    mock_manager.generate_chat_response = MagicMock(
        return_value="This is a test response")
    return mock_manager


@pytest.fixture
def mock_working_memory():
    """Create a mock working memory."""
    mock_memory = MagicMock()
    mock_memory.conversation_id = "test-conversation-id"
    mock_memory.add_message = MagicMock(return_value=Message(
        content="Test message",
        role="user",
        metadata={"conversation_id": "test-conversation-id"}
    ))
    mock_memory.get_messages = MagicMock(return_value=[
        Message(content="Hello", role="user",
                metadata={"conversation_id": "test-conversation-id"}),
        Message(content="Hi there", role="assistant",
                metadata={"conversation_id": "test-conversation-id"})
    ])
    mock_memory.get_last_message = MagicMock(return_value=Message(
        content="Hi there",
        role="assistant",
        metadata={"conversation_id": "test-conversation-id"}
    ))
    mock_memory.format_history = MagicMock(
        return_value="user: Hello\nassistant: Hi there")
    mock_memory.clear_messages = MagicMock()
    mock_memory.new_conversation = MagicMock(
        return_value="new-conversation-id")
    mock_memory.save = MagicMock(return_value=True)
    return mock_memory


@pytest.fixture
def async_assistant(mock_model_manager, mock_working_memory):
    """Create an AsyncAssistant instance with mocked dependencies."""
    with patch("dukat.core.async_assistant.get_model_manager", return_value=mock_model_manager), \
            patch("dukat.core.async_assistant.WorkingMemory", return_value=mock_working_memory):

        assistant = AsyncAssistant(
            model_name="test-model",
            ollama_host="http://test-host",
            max_messages=50,
            conversation_id="test-conversation-id"
        )

        # Set mocked dependencies directly
        assistant.model_manager = mock_model_manager
        assistant.memory = mock_working_memory

        return assistant


@pytest.mark.asyncio
async def test_get_async_assistant():
    """Test getting an async assistant."""
    # Mock the get_task_queue and queue.start functions
    mock_queue = MagicMock()
    mock_queue.running = False
    mock_queue.start = AsyncMock()

    with patch("dukat.core.async_assistant.get_task_queue", return_value=mock_queue), \
            patch("dukat.core.async_assistant.AsyncAssistant") as mock_assistant_class:

        # Get an async assistant
        assistant = await get_async_assistant(
            model_name="test-model",
            ollama_host="http://test-host",
            max_messages=50,
            conversation_id="test-conv",
        )

        # Check that the queue was started
        mock_queue.start.assert_called_once()

        # Check that the assistant was created with the correct parameters
        mock_assistant_class.assert_called_once_with(
            model_name="test-model",
            ollama_host="http://test-host",
            max_messages=50,
            conversation_id="test-conv",
        )


@pytest.mark.asyncio
async def test_add_message(async_assistant):
    """Test adding a message to the conversation."""
    # Mock the _schedule_indexing_task method
    async_assistant._schedule_indexing_task = AsyncMock()

    # Add a message
    message = await async_assistant.add_message(
        content="Test message",
        role="user",
        metadata={"test": "metadata"}
    )

    # Check that the message was added to memory
    async_assistant.memory.add_message.assert_called_once_with(
        content="Test message",
        role="user",
        metadata={"test": "metadata"}
    )

    # Check that indexing was scheduled
    async_assistant._schedule_indexing_task.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_generate_response(async_assistant):
    """Test generating a response."""
    # Mock the add_task and wait_for_task functions
    mock_task = MagicMock()
    mock_task.task_id = "test-task-id"

    with patch("dukat.core.async_assistant.add_task", AsyncMock(return_value=mock_task)), \
            patch("dukat.core.async_assistant.wait_for_task", AsyncMock(return_value="This is a test response")), \
            patch.object(async_assistant, "add_message", AsyncMock()):

        # Generate a response
        response = await async_assistant.generate_response(
            system_prompt="You are a helpful assistant",
            max_tokens=100,
            temperature=0.5,
            timeout=20.0,
            priority=5
        )

        # Check that the response was generated
        assert response == "This is a test response"

        # Check that the task was added
        from dukat.core.async_assistant import add_task
        add_task.assert_called_once()

        # Check that the response was added to memory
        async_assistant.add_message.assert_called_once_with(
            content="This is a test response",
            role="assistant"
        )


@pytest.mark.asyncio
async def test_generate_response_error(async_assistant):
    """Test generating a response with an error."""
    # Mock the add_task, wait_for_task, and get_task functions
    mock_task = MagicMock()
    mock_task.task_id = "test-task-id"

    mock_failed_task = MagicMock()
    mock_failed_task.status = TaskStatus.FAILED
    mock_failed_task.error = "Test error"

    with patch("dukat.core.async_assistant.add_task", AsyncMock(return_value=mock_task)), \
            patch("dukat.core.async_assistant.wait_for_task", AsyncMock(return_value=None)), \
            patch("dukat.core.async_assistant.get_task", AsyncMock(return_value=mock_failed_task)), \
            patch.object(async_assistant, "add_message", AsyncMock()):

        # Generate a response
        response = await async_assistant.generate_response()

        # Check that an error message was returned
        assert "I'm sorry, I encountered an error: Test error" in response

        # Check that the error message was added to memory
        async_assistant.add_message.assert_called_once()


@pytest.mark.asyncio
async def test_generate_response_timeout(async_assistant):
    """Test generating a response with a timeout."""
    # Mock the add_task, wait_for_task, and get_task functions
    mock_task = MagicMock()
    mock_task.task_id = "test-task-id"

    with patch("dukat.core.async_assistant.add_task", AsyncMock(return_value=mock_task)), \
            patch("dukat.core.async_assistant.wait_for_task", AsyncMock(return_value=None)), \
            patch("dukat.core.async_assistant.get_task", AsyncMock(return_value=None)), \
            patch.object(async_assistant, "add_message", AsyncMock()):

        # Generate a response
        response = await async_assistant.generate_response()

        # Check that a timeout message was returned
        assert "I'm sorry, I'm taking too long to respond" in response

        # Check that the timeout message was added to memory
        async_assistant.add_message.assert_called_once()


@pytest.mark.asyncio
async def test_internal_generate_response(async_assistant):
    """Test the internal _generate_response method."""
    # Generate a response
    response = await async_assistant._generate_response(
        system_prompt="You are a helpful assistant",
        max_tokens=100,
        temperature=0.5
    )

    # Check that the response was generated
    assert response == "This is a test response"

    # Check that the model manager was called with the correct parameters
    async_assistant.model_manager.generate_chat_response.assert_called_once()

    # Check the formatted messages
    call_args = async_assistant.model_manager.generate_chat_response.call_args
    formatted_messages = call_args[1]["messages"]

    # Check that the system prompt was included
    assert formatted_messages[0]["role"] == "system"
    assert formatted_messages[0]["content"] == "You are a helpful assistant"


@pytest.mark.asyncio
async def test_schedule_indexing_task(async_assistant):
    """Test scheduling an indexing task."""
    # Create a test message
    message = Message(
        content="Test message",
        role="user",
        metadata={"conversation_id": "test-conversation-id"}
    )

    # Mock the add_task function
    mock_task = MagicMock()
    mock_task.task_id = "test-task-id"

    with patch("dukat.core.async_assistant.add_task", AsyncMock(return_value=mock_task)):
        # Schedule indexing
        await async_assistant._schedule_indexing_task(message)

        # Check that the task was added
        from dukat.core.async_assistant import add_task
        add_task.assert_called_once()

        # Check that the task was tracked
        assert "test-task-id" in async_assistant.active_tasks
        assert async_assistant.active_tasks["test-task-id"] == "message_indexing"


@pytest.mark.asyncio
async def test_index_message(async_assistant):
    """Test indexing a message."""
    # Create a test message
    message = Message(
        content="Test message",
        role="user",
        metadata={"conversation_id": "test-conversation-id"}
    )

    # Index the message
    result = await async_assistant._index_message(message)

    # Check that indexing was successful
    assert result is True


@pytest.mark.asyncio
async def test_search_memory(async_assistant):
    """Test searching memory."""
    # Mock the add_task and wait_for_task functions
    mock_task = MagicMock()
    mock_task.task_id = "test-task-id"

    mock_results = [
        {
            "content": "Test message",
            "role": "user",
            "timestamp": 1234567890,
            "metadata": {"test": "metadata"}
        }
    ]

    with patch("dukat.core.async_assistant.add_task", AsyncMock(return_value=mock_task)), \
            patch("dukat.core.async_assistant.wait_for_task", AsyncMock(return_value=mock_results)):

        # Search memory
        results = await async_assistant.search_memory(
            query="test",
            n_results=5,
            filter_metadata={"test": "metadata"}
        )

        # Check that the search was performed
        assert results == mock_results

        # Check that the task was added
        from dukat.core.async_assistant import add_task
        add_task.assert_called_once()

        # Check that the task was tracked
        assert "test-task-id" in async_assistant.active_tasks
        assert async_assistant.active_tasks["test-task-id"] == "memory_search"


@pytest.mark.asyncio
async def test_search_memory_timeout(async_assistant):
    """Test searching memory with a timeout."""
    # Mock the add_task and wait_for_task functions
    mock_task = MagicMock()
    mock_task.task_id = "test-task-id"

    with patch("dukat.core.async_assistant.add_task", AsyncMock(return_value=mock_task)), \
            patch("dukat.core.async_assistant.wait_for_task", AsyncMock(return_value=None)):

        # Search memory
        results = await async_assistant.search_memory(query="test")

        # Check that an empty list was returned
        assert results == []


@pytest.mark.asyncio
async def test_internal_search_memory(async_assistant):
    """Test the internal _search_memory method."""
    # Search memory
    results = await async_assistant._search_memory(
        query="Hello",
        n_results=5
    )

    # Check that the search was performed
    assert len(results) == 1
    assert results[0]["content"] == "Hello"
    assert results[0]["role"] == "user"


@pytest.mark.asyncio
async def test_clear_messages(async_assistant):
    """Test clearing messages."""
    # Clear messages
    await async_assistant.clear_messages()

    # Check that messages were cleared
    async_assistant.memory.clear_messages.assert_called_once()


@pytest.mark.asyncio
async def test_new_conversation(async_assistant):
    """Test starting a new conversation."""
    # Start a new conversation
    conversation_id = await async_assistant.new_conversation()

    # Check that a new conversation was started
    assert conversation_id == "new-conversation-id"
    assert async_assistant.conversation_id == "new-conversation-id"
    async_assistant.memory.new_conversation.assert_called_once()


@pytest.mark.asyncio
async def test_save_conversation(async_assistant):
    """Test saving a conversation."""
    # Mock the add_task and wait_for_task functions
    mock_task = MagicMock()
    mock_task.task_id = "test-task-id"

    with patch("dukat.core.async_assistant.add_task", AsyncMock(return_value=mock_task)), \
            patch("dukat.core.async_assistant.wait_for_task", AsyncMock(return_value=True)):

        # Save the conversation
        result = await async_assistant.save_conversation("test_conversation.json")

        # Check that the conversation was saved
        assert result is True

        # Check that the task was added
        from dukat.core.async_assistant import add_task
        add_task.assert_called_once()

        # Check that the task was tracked
        assert "test-task-id" in async_assistant.active_tasks
        assert async_assistant.active_tasks["test-task-id"] == "conversation_save"


@pytest.mark.asyncio
async def test_internal_save_conversation(async_assistant):
    """Test the internal _save_conversation method."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name

    try:
        # Save the conversation
        result = await async_assistant._save_conversation(file_path)

        # Check that the conversation was saved
        assert result is True
        async_assistant.memory.save.assert_called_once_with(file_path)

    finally:
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)


@pytest.mark.asyncio
async def test_load_conversation(async_assistant):
    """Test loading a conversation."""
    # Mock the add_task and wait_for_task functions
    mock_task = MagicMock()
    mock_task.task_id = "test-task-id"

    with patch("dukat.core.async_assistant.add_task", AsyncMock(return_value=mock_task)), \
            patch("dukat.core.async_assistant.wait_for_task", AsyncMock(return_value=True)):

        # Load the conversation
        result = await async_assistant.load_conversation("test_conversation.json")

        # Check that the conversation was loaded
        assert result is True

        # Check that the task was added
        from dukat.core.async_assistant import add_task
        add_task.assert_called_once()

        # Check that the task was tracked
        assert "test-task-id" in async_assistant.active_tasks
        assert async_assistant.active_tasks["test-task-id"] == "conversation_load"


@pytest.mark.asyncio
async def test_internal_load_conversation(async_assistant):
    """Test the internal _load_conversation method."""
    # Mock the WorkingMemory.load method
    mock_loaded_memory = MagicMock()
    mock_loaded_memory.conversation_id = "loaded-conversation-id"

    with patch("dukat.core.async_assistant.WorkingMemory.load", return_value=mock_loaded_memory):
        # Load the conversation
        result = await async_assistant._load_conversation("test_conversation.json")

        # Check that the conversation was loaded
        assert result is True
        assert async_assistant.memory is mock_loaded_memory


@pytest.mark.asyncio
async def test_get_active_tasks(async_assistant):
    """Test getting active tasks."""
    # Add some active tasks
    async_assistant.active_tasks = {
        "task1": "response_generation",
        "task2": "message_indexing"
    }

    # Mock the get_task function
    mock_task1 = MagicMock()
    mock_task1.status = TaskStatus.COMPLETED
    mock_task1.created_at = 1234567890
    mock_task1.started_at = 1234567891
    mock_task1.completed_at = 1234567892
    mock_task1.error = None

    mock_task2 = MagicMock()
    mock_task2.status = TaskStatus.RUNNING
    mock_task2.created_at = 1234567893
    mock_task2.started_at = 1234567894
    mock_task2.completed_at = None
    mock_task2.error = None

    with patch("dukat.core.async_assistant.get_task", AsyncMock(side_effect=[mock_task1, mock_task2])):
        # Get active tasks
        tasks = await async_assistant.get_active_tasks()

        # Check that the tasks were retrieved
        assert len(tasks) == 2
        assert tasks["task1"]["type"] == "response_generation"
        assert tasks["task1"]["status"] == "completed"
        assert tasks["task2"]["type"] == "message_indexing"
        assert tasks["task2"]["status"] == "running"


@pytest.mark.asyncio
async def test_cancel_active_tasks(async_assistant):
    """Test cancelling active tasks."""
    # Add some active tasks
    async_assistant.active_tasks = {
        "task1": "response_generation",
        "task2": "message_indexing"
    }

    # Mock the cancel_task function
    with patch("dukat.core.async_assistant.cancel_task", AsyncMock(side_effect=[True, False])):
        # Cancel active tasks
        count = await async_assistant.cancel_active_tasks()

        # Check that the tasks were cancelled
        assert count == 1
        assert len(async_assistant.active_tasks) == 1
        assert "task2" in async_assistant.active_tasks


@pytest.mark.asyncio
async def test_get_messages(async_assistant):
    """Test getting messages."""
    # Get messages
    messages = await async_assistant.get_messages(n=5, roles=["user"], reverse=True)

    # Check that messages were retrieved
    async_assistant.memory.get_messages.assert_called_once_with(
        n=5, roles=["user"], reverse=True)
    assert len(messages) == 2


@pytest.mark.asyncio
async def test_get_last_message(async_assistant):
    """Test getting the last message."""
    # Get the last message
    message = await async_assistant.get_last_message(role="assistant")

    # Check that the message was retrieved
    async_assistant.memory.get_last_message.assert_called_once_with(
        role="assistant")
    assert message.content == "Hi there"
    assert message.role == "assistant"


@pytest.mark.asyncio
async def test_format_history(async_assistant):
    """Test formatting conversation history."""
    # Format history
    history = await async_assistant.format_history(n=5, include_roles=True, separator="\n\n")

    # Check that history was formatted
    async_assistant.memory.format_history.assert_called_once_with(
        n=5, include_roles=True, separator="\n\n")
    assert history == "user: Hello\nassistant: Hi there"


@pytest.mark.asyncio
async def test_get_queue_stats(async_assistant):
    """Test getting queue statistics."""
    # Mock the get_queue_stats function
    mock_stats = {
        "queue_size": 2,
        "max_queue_size": 100,
        "workers": 5,
        "max_workers": 10,
        "running": True,
        "tasks": {
            "total": 10,
            "pending": 2,
            "running": 3,
            "completed": 4,
            "failed": 1,
            "cancelled": 0
        }
    }

    with patch("dukat.core.async_assistant.get_queue_stats", AsyncMock(return_value=mock_stats)):
        # Get queue stats
        stats = await async_assistant.get_queue_stats()

        # Check that stats were retrieved
        assert stats == mock_stats
