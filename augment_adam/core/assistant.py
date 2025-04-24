"""Core assistant implementation for Augment Adam.

This module provides the main Assistant class that integrates
the model manager, memory system, and other components.

Version: 0.1.0
Created: 2025-04-22
Updated: 2025-04-24
"""

from typing import Dict, Any, List, Optional, Union
import logging
import time
from datetime import datetime
import uuid

import dspy

from augment_adam.core.model_manager import ModelManager
from augment_adam.memory.base import BaseMemory
from augment_adam.memory.working import Message, WorkingMemory

logger = logging.getLogger(__name__)


class Assistant:
    """Main assistant class for Augment Adam.

    This class integrates the model manager, memory system, and other
    components to provide a complete assistant experience.

    Attributes:
        model_manager: The model manager instance.
        memory: The memory system instance.
        conversation_id: The ID of the current conversation.
    """

    def __init__(
        self,
        model_name: str = "llama3:8b",
        ollama_host: str = "http://localhost:11434",
        persist_dir: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ):
        """Initialize the assistant.

        Args:
            model_name: The name of the model to use.
            ollama_host: The host address for the Ollama API.
            persist_dir: Directory to persist memory data.
            conversation_id: The ID of the conversation to continue.
        """
        # Initialize components
        self.model_manager = ModelManager(model_name, ollama_host)
        self.memory = BaseMemory(persist_dir) if persist_dir else None

        # Set or generate conversation ID
        self.conversation_id = conversation_id or f"conv_{uuid.uuid4().hex[:8]}"

        # Create DSPy modules
        self.chat_module = self.model_manager.create_module(
            "history, question -> response"
        )

        # Initialize working memory
        self.working_memory = WorkingMemory(
            conversation_id=self.conversation_id)

        # Track response times for analytics
        self.response_times = []

        logger.info(
            f"Initialized Assistant with conversation_id: {self.conversation_id}")

    def ask(
        self,
        question: str,
        include_history: bool = True,
        max_history_items: int = 5,
    ) -> str:
        """Ask a question to the assistant.

        Args:
            question: The question to ask.
            include_history: Whether to include conversation history.
            max_history_items: Maximum number of history items to include.

        Returns:
            The assistant's response.
        """
        logger.info(f"Received question: {question[:50]}...")

        # Store the question in memory
        self.memory.add(
            text=question,
            metadata={
                "type": "user_message",
                "conversation_id": self.conversation_id,
            },
        )

        # Get conversation history if needed
        history = ""
        if include_history:
            history_items = self.memory.retrieve(
                query="",
                n_results=max_history_items * 2,  # Get more to filter
                filter_metadata={"conversation_id": self.conversation_id},
            )

            # Format history items
            formatted_items = []
            for item in history_items:
                item_type = item["metadata"].get("type", "")
                if item_type == "user_message":
                    formatted_items.append(f"User: {item['text']}")
                elif item_type == "assistant_message":
                    formatted_items.append(f"Assistant: {item['text']}")

            history = "\\n".join(formatted_items[-max_history_items*2:])

        # Generate response using DSPy
        try:
            prediction = self.chat_module(history=history, question=question)
            response = prediction.response
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            response = f"I'm sorry, I encountered an error: {str(e)}"

        # Store the response in memory
        self.memory.add(
            text=response,
            metadata={
                "type": "assistant_message",
                "conversation_id": self.conversation_id,
            },
        )

        logger.info(f"Generated response: {response[:50]}...")
        return response

    def new_conversation(self) -> str:
        """Start a new conversation.

        Returns:
            The ID of the new conversation.
        """
        self.conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        logger.info(
            f"Started new conversation with ID: {self.conversation_id}")
        return self.conversation_id

    def get_conversation_history(
        self,
        max_items: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get the history of the current conversation.

        Args:
            max_items: Maximum number of history items to return.

        Returns:
            A list of conversation messages with metadata.
        """
        history_items = self.memory.retrieve(
            query="",
            n_results=max_items * 2,  # Get more to filter
            filter_metadata={"conversation_id": self.conversation_id},
        )

        # Format and sort history items
        formatted_items = []
        for item in history_items:
            formatted_items.append({
                "id": item["id"],
                "text": item["text"],
                "type": item["metadata"].get("type", ""),
                "timestamp": item["metadata"].get("timestamp", ""),
            })

        # Sort by timestamp
        formatted_items.sort(key=lambda x: x["timestamp"])

        return formatted_items[-max_items:]

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation.

        Args:
            message: The message to add.
        """
        # @mocked-in-tests
        # Add to working memory
        self.working_memory.add_message(message)

        # Also add to persistent memory
        self.memory.add(
            text=message.content,
            metadata={
                "type": f"{message.role}_message",
                "conversation_id": self.conversation_id,
                "timestamp": message.timestamp,
                **message.metadata,
            },
        )

        logger.info(
            f"Added {message.role} message to conversation {self.conversation_id}")

    def get_messages(self, n: Optional[int] = None) -> List[Message]:
        """Get messages from the conversation.

        Args:
            n: Maximum number of messages to return.

        Returns:
            A list of messages.
        """
        # @mocked-in-tests
        return self.working_memory.get_messages(n=n)

    def clear_messages(self) -> None:
        """Clear all messages from the conversation."""
        # @mocked-in-tests
        self.working_memory.clear_messages()
        logger.info(
            f"Cleared messages from conversation {self.conversation_id}")

    def generate_response(
        self,
        message: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Generate a response to a message.

        Args:
            message: The message to respond to. If None, uses the last user message.
            system_prompt: The system prompt to use.
            temperature: The temperature to use for generation.
            max_tokens: The maximum number of tokens to generate.

        Returns:
            The generated response.
        """
        # @mocked-in-tests
        # If message is provided, add it to the conversation
        if message is not None:
            self.add_message(Message(role="user", content=message))

        # Get the last user message if none was provided
        if message is None:
            last_message = self.working_memory.get_last_message(role="user")
            if last_message is None:
                return "I don't have any messages to respond to."
            message = last_message.content

        # Add system prompt to context if provided
        if system_prompt:
            self.working_memory.set_context("system_prompt", system_prompt)

        # Get conversation history
        history = self.working_memory.format_history(n=5)

        # Generate response using DSPy
        try:
            start_time = time.time()
            prediction = self.chat_module(
                history=history,
                question=message,
            )
            response = prediction.response
            generation_time = time.time() - start_time

            # Track response time
            self.response_times.append(generation_time)

            # Add the response to the conversation
            self.add_message(Message(role="assistant", content=response))

            logger.info(f"Generated response in {generation_time:.2f}s")
            return response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            error_response = f"I'm sorry, I encountered an error: {str(e)}"

            # Add the error response to the conversation
            self.add_message(Message(role="assistant", content=error_response))

            return error_response

    def save_conversation(self, file_path: str) -> bool:
        """Save the conversation to a file.

        Args:
            file_path: The path to save the file.

        Returns:
            True if successful, False otherwise.
        """
        # @mocked-in-tests
        return self.working_memory.save(file_path)

    def load_conversation(self, file_path: str) -> bool:
        """Load a conversation from a file.

        Args:
            file_path: The path to load the file from.

        Returns:
            True if successful, False otherwise.
        """
        # @mocked-in-tests
        loaded_memory = WorkingMemory.load(file_path)
        if loaded_memory is None:
            return False

        self.working_memory = loaded_memory
        self.conversation_id = loaded_memory.conversation_id

        logger.info(f"Loaded conversation from {file_path}")
        return True
