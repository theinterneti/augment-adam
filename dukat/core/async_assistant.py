"""Asynchronous assistant implementation for Dukat.

This module provides an asynchronous version of the Assistant class
that integrates with the task queue system for background processing.

Version: 0.1.0
Created: 2025-04-24
"""

import asyncio
import logging
import uuid
import json
import os
from typing import Dict, Any, List, Optional, Union, Tuple

from dukat.core.model_manager import get_model_manager, ModelManager
from dukat.memory.working import WorkingMemory, Message
from dukat.core.task_queue import (
    add_task,
    get_task,
    cancel_task,
    wait_for_task,
    get_queue_stats,
    get_task_queue,
    TaskStatus,
)

logger = logging.getLogger(__name__)


class AsyncAssistant:
    """Asynchronous assistant class for Dukat.
    
    This class integrates the model manager, working memory, and task queue
    to provide an asynchronous assistant experience.
    
    Attributes:
        model_manager: The model manager instance.
        memory: The working memory instance.
        conversation_id: The ID of the current conversation.
    """
    
    def __init__(
        self,
        model_name: str = "llama3:8b",
        ollama_host: str = "http://localhost:11434",
        max_messages: int = 100,
        conversation_id: Optional[str] = None,
    ):
        """Initialize the assistant.
        
        Args:
            model_name: The name of the model to use.
            ollama_host: The host address for the Ollama API.
            max_messages: Maximum number of messages to keep in memory.
            conversation_id: The ID of the conversation to continue.
        """
        # Initialize components
        self.model_manager = get_model_manager(model_name, ollama_host)
        self.memory = WorkingMemory(max_messages=max_messages, conversation_id=conversation_id)
        
        # Set or generate conversation ID
        self.conversation_id = self.memory.conversation_id
        
        # Task tracking
        self.active_tasks: Dict[str, str] = {}  # Maps task_id to task_type
        
        logger.info(f"Initialized AsyncAssistant with conversation_id: {self.conversation_id}")
    
    async def add_message(
        self,
        content: Union[str, Message],
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """Add a message to the conversation.
        
        Args:
            content: The content of the message or a Message object.
            role: The role of the sender (user, assistant, system).
            metadata: Additional metadata for the message.
            
        Returns:
            The added message.
        """
        # Add the message to memory
        message = self.memory.add_message(content=content, role=role, metadata=metadata)
        
        # Schedule indexing task in the background
        await self._schedule_indexing_task(message)
        
        return message
    
    async def generate_response(
        self,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        timeout: Optional[float] = 30.0,
        priority: int = 10,  # Higher priority for response generation
    ) -> str:
        """Generate a response asynchronously.
        
        Args:
            system_prompt: Optional system prompt to use.
            max_tokens: Maximum number of tokens to generate.
            temperature: Temperature for generation.
            timeout: Maximum time to wait for generation.
            priority: Priority of the generation task.
            
        Returns:
            The generated response.
        """
        # Create a task for response generation
        task = await add_task(
            func=self._generate_response,
            args=[system_prompt, max_tokens, temperature],
            task_id=f"response_{uuid.uuid4().hex[:8]}",
            priority=priority,
            timeout=timeout,
        )
        
        # Track the task
        self.active_tasks[task.task_id] = "response_generation"
        
        # Wait for the task to complete
        response = await wait_for_task(task.task_id, timeout=timeout)
        
        # If the task timed out or failed, return an error message
        if response is None:
            task_info = await get_task(task.task_id)
            if task_info and task_info.status == TaskStatus.FAILED:
                error_msg = f"I'm sorry, I encountered an error: {task_info.error}"
                await self.add_message(content=error_msg, role="assistant")
                return error_msg
            else:
                timeout_msg = "I'm sorry, I'm taking too long to respond. Please try again."
                await self.add_message(content=timeout_msg, role="assistant")
                return timeout_msg
        
        # Add the response to memory
        await self.add_message(content=response, role="assistant")
        
        return response
    
    async def _generate_response(
        self,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Internal method to generate a response.
        
        Args:
            system_prompt: Optional system prompt to use.
            max_tokens: Maximum number of tokens to generate.
            temperature: Temperature for generation.
            
        Returns:
            The generated response.
        """
        try:
            # Get conversation history
            messages = self.memory.get_messages()
            
            # Format the messages for the model
            formatted_messages = []
            
            # Add system prompt if provided
            if system_prompt:
                formatted_messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation history
            for message in messages:
                formatted_messages.append({
                    "role": message.role,
                    "content": message.content,
                })
            
            # Generate response
            response = self.model_manager.generate_chat_response(
                messages=formatted_messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    async def _schedule_indexing_task(self, message: Message) -> None:
        """Schedule a task to index a message.
        
        Args:
            message: The message to index.
        """
        # Create a task for indexing
        task = await add_task(
            func=self._index_message,
            args=[message],
            task_id=f"index_{uuid.uuid4().hex[:8]}",
            priority=5,  # Lower priority than response generation
            retry_count=3,
            retry_delay=1.0,
        )
        
        # Track the task
        self.active_tasks[task.task_id] = "message_indexing"
    
    async def _index_message(self, message: Message) -> bool:
        """Index a message for retrieval.
        
        Args:
            message: The message to index.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # In a real implementation, this would index the message in a vector database
            # For now, we'll just log it
            logger.info(f"Indexed message: {message.content[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing message: {str(e)}")
            raise
    
    async def search_memory(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search memory for relevant messages.
        
        Args:
            query: The search query.
            n_results: Maximum number of results to return.
            filter_metadata: Metadata filters to apply.
            
        Returns:
            A list of relevant messages.
        """
        # Create a task for searching
        task = await add_task(
            func=self._search_memory,
            args=[query, n_results, filter_metadata],
            task_id=f"search_{uuid.uuid4().hex[:8]}",
            priority=7,
            timeout=10.0,
        )
        
        # Track the task
        self.active_tasks[task.task_id] = "memory_search"
        
        # Wait for the task to complete
        results = await wait_for_task(task.task_id, timeout=10.0)
        
        # If the task timed out or failed, return an empty list
        if results is None:
            return []
        
        return results
    
    async def _search_memory(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Internal method to search memory.
        
        Args:
            query: The search query.
            n_results: Maximum number of results to return.
            filter_metadata: Metadata filters to apply.
            
        Returns:
            A list of relevant messages.
        """
        try:
            # In a real implementation, this would search a vector database
            # For now, we'll just return messages that contain the query
            results = []
            for message in self.memory.get_messages():
                if query.lower() in message.content.lower():
                    results.append({
                        "content": message.content,
                        "role": message.role,
                        "timestamp": message.timestamp,
                        "metadata": message.metadata,
                    })
                    
                    if len(results) >= n_results:
                        break
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching memory: {str(e)}")
            raise
    
    async def clear_messages(self) -> None:
        """Clear all messages from memory."""
        self.memory.clear_messages()
        logger.info("Cleared all messages")
    
    async def new_conversation(self) -> str:
        """Start a new conversation.
        
        Returns:
            The ID of the new conversation.
        """
        self.conversation_id = self.memory.new_conversation()
        logger.info(f"Started new conversation with ID: {self.conversation_id}")
        return self.conversation_id
    
    async def save_conversation(self, file_path: str) -> bool:
        """Save the conversation to a file.
        
        Args:
            file_path: The path to save the file.
            
        Returns:
            True if successful, False otherwise.
        """
        # Create a task for saving
        task = await add_task(
            func=self._save_conversation,
            args=[file_path],
            task_id=f"save_{uuid.uuid4().hex[:8]}",
            priority=5,
            retry_count=3,
        )
        
        # Track the task
        self.active_tasks[task.task_id] = "conversation_save"
        
        # Wait for the task to complete
        result = await wait_for_task(task.task_id, timeout=10.0)
        
        # If the task timed out or failed, return False
        if result is None:
            return False
        
        return result
    
    async def _save_conversation(self, file_path: str) -> bool:
        """Internal method to save the conversation.
        
        Args:
            file_path: The path to save the file.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Save the conversation
            return self.memory.save(file_path)
            
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
            raise
    
    async def load_conversation(self, file_path: str) -> bool:
        """Load a conversation from a file.
        
        Args:
            file_path: The path to load the file from.
            
        Returns:
            True if successful, False otherwise.
        """
        # Create a task for loading
        task = await add_task(
            func=self._load_conversation,
            args=[file_path],
            task_id=f"load_{uuid.uuid4().hex[:8]}",
            priority=5,
            retry_count=3,
        )
        
        # Track the task
        self.active_tasks[task.task_id] = "conversation_load"
        
        # Wait for the task to complete
        result = await wait_for_task(task.task_id, timeout=10.0)
        
        # If the task timed out or failed, return False
        if result is None:
            return False
        
        # Update the conversation ID
        if result:
            self.conversation_id = self.memory.conversation_id
        
        return result
    
    async def _load_conversation(self, file_path: str) -> bool:
        """Internal method to load a conversation.
        
        Args:
            file_path: The path to load the file from.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Load the conversation
            loaded_memory = WorkingMemory.load(file_path)
            
            if loaded_memory:
                # Replace the current memory
                self.memory = loaded_memory
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error loading conversation: {str(e)}")
            raise
    
    async def get_active_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active tasks.
        
        Returns:
            A dictionary mapping task IDs to task information.
        """
        task_info = {}
        
        for task_id, task_type in self.active_tasks.items():
            task = await get_task(task_id)
            
            if task:
                task_info[task_id] = {
                    "type": task_type,
                    "status": task.status.value,
                    "created_at": task.created_at,
                    "started_at": task.started_at,
                    "completed_at": task.completed_at,
                    "error": task.error,
                }
        
        return task_info
    
    async def cancel_active_tasks(self) -> int:
        """Cancel all active tasks.
        
        Returns:
            The number of tasks cancelled.
        """
        cancelled_count = 0
        
        for task_id in list(self.active_tasks.keys()):
            cancelled = await cancel_task(task_id)
            
            if cancelled:
                cancelled_count += 1
                del self.active_tasks[task_id]
        
        return cancelled_count
    
    async def get_messages(
        self,
        n: Optional[int] = None,
        roles: Optional[List[str]] = None,
        reverse: bool = False,
    ) -> List[Message]:
        """Get messages from the conversation.
        
        Args:
            n: Maximum number of messages to return.
            roles: Only return messages with these roles.
            reverse: Whether to return messages in reverse order.
            
        Returns:
            A list of messages.
        """
        return self.memory.get_messages(n=n, roles=roles, reverse=reverse)
    
    async def get_last_message(self, role: Optional[str] = None) -> Optional[Message]:
        """Get the last message in the conversation.
        
        Args:
            role: Only return a message with this role.
            
        Returns:
            The last message, or None if there are no messages.
        """
        return self.memory.get_last_message(role=role)
    
    async def format_history(
        self,
        n: Optional[int] = None,
        include_roles: bool = True,
        separator: str = "\n",
    ) -> str:
        """Format the conversation history as a string.
        
        Args:
            n: Maximum number of messages to include.
            include_roles: Whether to include roles in the output.
            separator: The separator between messages.
            
        Returns:
            The formatted conversation history.
        """
        return self.memory.format_history(n=n, include_roles=include_roles, separator=separator)
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics about the task queue.
        
        Returns:
            A dictionary with queue statistics.
        """
        return await get_queue_stats()


async def get_async_assistant(
    model_name: str = "llama3:8b",
    ollama_host: str = "http://localhost:11434",
    max_messages: int = 100,
    conversation_id: Optional[str] = None,
) -> AsyncAssistant:
    """Get an asynchronous assistant instance.
    
    Args:
        model_name: The name of the model to use.
        ollama_host: The host address for the Ollama API.
        max_messages: Maximum number of messages to keep in memory.
        conversation_id: The ID of the conversation to continue.
        
    Returns:
        An AsyncAssistant instance.
    """
    # Make sure the task queue is started
    queue = get_task_queue()
    if not queue.running:
        await queue.start()
    
    # Create and return the assistant
    return AsyncAssistant(
        model_name=model_name,
        ollama_host=ollama_host,
        max_messages=max_messages,
        conversation_id=conversation_id,
    )
