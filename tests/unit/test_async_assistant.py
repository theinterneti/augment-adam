"""Unit tests for the AsyncAssistant class.

This module contains tests for the asynchronous assistant implementation.

Version: 0.1.0
Created: 2025-04-24
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from dukat.core.async_assistant import get_async_assistant


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
