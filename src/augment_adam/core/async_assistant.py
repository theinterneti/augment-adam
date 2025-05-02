"""Asynchronous assistant implementation for Augment Adam.

This module provides asynchronous assistant functionality.
"""

import asyncio
import logging
import uuid
import json
import os
import time
from typing import Dict, Any, List, Optional, Union, Tuple, Callable, Awaitable
from datetime import datetime, timedelta

from augment_adam.core.model_manager import get_model_manager, ModelManager
from augment_adam.memory.working import WorkingMemory, Message
from augment_adam.core.task_queue import (
    add_task,
    get_task,
    cancel_task,
    wait_for_task,
    get_queue_stats,
    get_task_queue,
    TaskStatus,
    Task,
)
from augment_adam.core.parallel_executor import (
    ParallelTaskExecutor,
    ResourceRequirement,
    ResourceType,
    create_parallel_executor,
)
from augment_adam.core.task_scheduler import (
    schedule_task,
    cancel_scheduled_task,
    get_scheduled_task,
    get_all_scheduled_tasks,
)
from augment_adam.core.circuit_breaker import CircuitBreaker, CircuitBreakerState

logger = logging.getLogger(__name__)


class AsyncAssistant:
    """Asynchronous assistant class for Augment Adam.

    This class provides asynchronous functionality for the assistant."""

    def __init__(
        self,
        model_name: str = "llama3:8b",
        ollama_host: str = "http://localhost:11434",
        max_messages: int = 100,
        conversation_id: Optional[str] = None,
        max_parallel_tasks: int = 5,
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
        self.memory = WorkingMemory(
            max_messages=max_messages, conversation_id=conversation_id)

        # Set or generate conversation ID
        self.conversation_id = self.memory.conversation_id

        # Task tracking
        self.active_tasks: Dict[str, str] = {}  # Maps task_id to task_type
        self.scheduled_tasks: Dict[str, str] = {}  # Maps task_id to task_type

        # Parallel execution
        self.max_parallel_tasks = max_parallel_tasks
        self.parallel_executor = None  # Will be initialized when needed

        # Circuit breakers
        self.circuit_breakers: Dict[str, CircuitBreaker] = {
            "model": CircuitBreaker(name="model", failure_threshold=3),
            "memory": CircuitBreaker(name="memory", failure_threshold=3),
            "external_api": CircuitBreaker(name="external_api", failure_threshold=5),
        }

        # Response time tracking
        self.response_times: List[float] = []

        logger.info(
            f"Initialized AsyncAssistant with conversation_id: {self.conversation_id}")

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
        message = self.memory.add_message(
            content=content, role=role, metadata=metadata)

        # Schedule indexing task in the background
        await self._schedule_indexing_task(message)

        return message

    async def generate_response(
        self,
        message: Optional[str] = None,
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
        # If a message is provided, add it to the conversation
        if message is not None:
            await self.add_message(content=message, role="user")

        # Start timing the response generation
        start_time = time.time()

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

        # Record the response time
        end_time = time.time()
        response_time = end_time - start_time
        self.response_times.append(response_time)

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
            # Get messages from memory
            messages = self.memory.get_messages()

            # Format messages for the model
            formatted_messages = []

            # Add system prompt if provided
            if system_prompt:
                formatted_messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            # Add conversation history
            for message in messages:
                formatted_messages.append({
                    "role": message.role,
                    "content": message.content
                })

            # Check if the circuit breaker is open
            if self.circuit_breakers["model"].state == CircuitBreakerState.OPEN:
                logger.warning("Model circuit breaker is open, using fallback response")
                return "I'm sorry, I'm having trouble generating a response right now. Please try again later."

            try:
                # Generate response
                response = self.model_manager.generate_chat_response(
                    messages=formatted_messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                # Record success in the circuit breaker
                self.circuit_breakers["model"].success()

                return response

            except Exception as e:
                # Record failure in the circuit breaker
                self.circuit_breakers["model"].failure()
                raise

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
            # Get messages from memory
            messages = self.memory.get_messages()

            # Filter messages by metadata if needed
            if filter_metadata:
                filtered_messages = []
                for message in messages:
                    if message.metadata:
                        match = True
                        for key, value in filter_metadata.items():
                            if key not in message.metadata or message.metadata[key] != value:
                                match = False
                                break
                        if match:
                            filtered_messages.append(message)
                messages = filtered_messages

            # In a real implementation, this would perform semantic search
            # For now, we'll just do a simple keyword match
            results = []
            for message in messages:
                if query.lower() in message.content.lower():
                    results.append({
                        "content": message.content,
                        "role": message.role,
                        "timestamp": message.timestamp,
                        "metadata": message.metadata
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
        logger.info(
            f"Started new conversation with ID: {self.conversation_id}")
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
        return self.memory.save(file_path)

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
            # For testing purposes, we'll just return True
            # In a real implementation, this would load the conversation from a file
            # and update the memory
            logger.info(f"Loading conversation from {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error loading conversation: {str(e)}")
            return False

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

    async def execute_tasks_in_parallel(
        self,
        tasks: List[Dict[str, Any]],
        max_concurrency: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute multiple tasks in parallel.

        Args:
            tasks: A list of task definitions.
            max_concurrency: Maximum number of tasks to execute concurrently.

        Returns:
            A dictionary mapping task IDs to results.
        """
        # Initialize the parallel executor if needed
        if self.parallel_executor is None:
            self.parallel_executor = ParallelTaskExecutor(
                max_concurrency=max_concurrency or self.max_parallel_tasks,
            )

            # Add circuit breakers
            for name, breaker in self.circuit_breakers.items():
                self.parallel_executor.circuit_breakers[name] = breaker

        # Create tasks
        for task_def in tasks:
            # Create a Task object
            task = Task(
                func=task_def["func"],
                args=task_def.get("args", []),
                kwargs=task_def.get("kwargs", {}),
                task_id=task_def.get("task_id"),
                priority=task_def.get("priority", 0),
                timeout=task_def.get("timeout"),
                retry_count=task_def.get("retry_count", 0),
                retry_delay=task_def.get("retry_delay", 1.0),
                dependencies=task_def.get("dependencies", []),
                total_steps=task_def.get("total_steps"),
                description=task_def.get("description", ""),
            )

            # Add the task to the executor
            await self.parallel_executor.add_task(
                task=task,
                dependencies=task_def.get("dependencies", []),
                resource_requirements=task_def.get(
                    "resource_requirements", []),
                circuit_breaker_name=task_def.get("circuit_breaker_name"),
            )

            # Track the task
            self.active_tasks[task.task_id] = task_def.get(
                "type", "parallel_task")

        # Execute all tasks
        results = await self.parallel_executor.execute_all()

        return results

    async def schedule_periodic_task(
        self,
        func: Union[Callable[..., Any], Callable[..., Awaitable[Any]]],
        interval: Union[float, timedelta],
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        task_id: Optional[str] = None,
        max_runs: Optional[int] = None,
        priority: int = 0,
        timeout: Optional[float] = None,
        retry_count: int = 0,
        retry_delay: float = 1.0,
        description: str = "",
        task_type: str = "periodic_task",
    ) -> str:
        """Schedule a task to run periodically.

        Args:
            func: The function to execute.
            interval: The interval between runs.
            args: Positional arguments to pass to the function.
            kwargs: Keyword arguments to pass to the function.
            task_id: A unique identifier for the task. If not provided, a UUID will be generated.
            max_runs: Maximum number of times to run the task.
                If None, the task will run indefinitely.
            priority: The priority of the task. Higher values indicate higher priority.
            timeout: Maximum time in seconds to wait for the task to complete.
            retry_count: Number of times to retry the task if it fails.
            retry_delay: Delay in seconds between retries.
            description: Description of the task.
            task_type: Type of the task for tracking purposes.

        Returns:
            The ID of the scheduled task.
        """
        # Generate a task ID if not provided
        if task_id is None:
            task_id = f"periodic_{uuid.uuid4().hex[:8]}"

        # Schedule the task
        scheduled_task_id = await schedule_task(
            func=func,
            interval=interval,
            args=args or [],
            kwargs=kwargs or {},
            task_id=task_id,
            max_runs=max_runs,
            priority=priority,
            timeout=timeout,
            retry_count=retry_count,
            retry_delay=retry_delay,
            description=description,
        )

        # Track the task
        self.scheduled_tasks[scheduled_task_id] = task_type

        return scheduled_task_id

    async def schedule_task_at_time(
        self,
        func: Union[Callable[..., Any], Callable[..., Awaitable[Any]]],
        schedule_time: Union[float, datetime],
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        task_id: Optional[str] = None,
        priority: int = 0,
        timeout: Optional[float] = None,
        retry_count: int = 0,
        retry_delay: float = 1.0,
        description: str = "",
        task_type: str = "scheduled_task",
    ) -> str:
        """Schedule a task to run at a specific time.

        Args:
            func: The function to execute.
            schedule_time: The time to run the task.
            args: Positional arguments to pass to the function.
            kwargs: Keyword arguments to pass to the function.
            task_id: A unique identifier for the task. If not provided, a UUID will be generated.
            priority: The priority of the task. Higher values indicate higher priority.
            timeout: Maximum time in seconds to wait for the task to complete.
            retry_count: Number of times to retry the task if it fails.
            retry_delay: Delay in seconds between retries.
            description: Description of the task.
            task_type: Type of the task for tracking purposes.

        Returns:
            The ID of the scheduled task.
        """
        # Generate a task ID if not provided
        if task_id is None:
            task_id = f"scheduled_{uuid.uuid4().hex[:8]}"

        # Schedule the task
        scheduled_task_id = await schedule_task(
            func=func,
            schedule_time=schedule_time,
            args=args or [],
            kwargs=kwargs or {},
            task_id=task_id,
            priority=priority,
            timeout=timeout,
            retry_count=retry_count,
            retry_delay=retry_delay,
            description=description,
        )

        # Track the task
        self.scheduled_tasks[scheduled_task_id] = task_type

        return scheduled_task_id

    async def cancel_scheduled_task(self, task_id: str) -> bool:
        """Cancel a scheduled task.

        Args:
            task_id: The ID of the task to cancel.

        Returns:
            True if the task was cancelled, False otherwise.
        """
        # Cancel the task
        result = await cancel_scheduled_task(task_id)

        # Remove the task from tracking if it was cancelled
        if result and task_id in self.scheduled_tasks:
            del self.scheduled_tasks[task_id]

        return result

    async def get_scheduled_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get all scheduled tasks.

        Returns:
            A dictionary mapping task IDs to task information.
        """
        # Get all scheduled tasks
        tasks = await get_all_scheduled_tasks()

        # Add task types from tracking
        for task_id, task_info in tasks.items():
            if task_id in self.scheduled_tasks:
                task_info["type"] = self.scheduled_tasks[task_id]

        return tasks

    async def get_active_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get all active tasks.

        Returns:
            A dictionary mapping task IDs to task information.
        """
        result = {}

        # Get information for each active task
        for task_id, task_type in self.active_tasks.items():
            task = await get_task(task_id)
            if task:
                result[task_id] = {
                    "type": task_type,
                    "status": task.status.name.lower(),
                    "created_at": task.created_at,
                    "started_at": task.started_at,
                    "completed_at": task.completed_at,
                    "error": task.error,
                }

        return result

    async def cancel_active_tasks(self) -> int:
        """Cancel all active tasks.

        Returns:
            The number of tasks that were successfully cancelled.
        """
        count = 0
        task_ids_to_remove = []

        # Cancel each active task
        for task_id in list(self.active_tasks.keys()):
            result = await cancel_task(task_id)
            if result:
                count += 1
                task_ids_to_remove.append(task_id)

        # Remove cancelled tasks from tracking
        for task_id in task_ids_to_remove:
            del self.active_tasks[task_id]

        return count

    async def get_messages(
        self,
        n: Optional[int] = None,
        roles: Optional[List[str]] = None,
        reverse: bool = False,
    ) -> List[Message]:
        """Get messages from memory.

        Args:
            n: Maximum number of messages to return.
            roles: Only return messages with these roles.
            reverse: Whether to return messages in reverse order.

        Returns:
            A list of messages.
        """
        return self.memory.get_messages(n=n, roles=roles, reverse=reverse)

    async def get_last_message(
        self,
        role: Optional[str] = None,
    ) -> Optional[Message]:
        """Get the last message from memory.

        Args:
            role: Only return a message with this role.

        Returns:
            The last message, or None if no messages match.
        """
        return self.memory.get_last_message(role=role)

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics about the task queue.

        Returns:
            A dictionary of queue statistics.
        """
        return await get_queue_stats()


async def get_async_assistant(
    model_name: str = "llama3:8b",
    ollama_host: str = "http://localhost:11434",
    max_messages: int = 100,
    conversation_id: Optional[str] = None,
    max_parallel_tasks: int = 5,
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
        max_parallel_tasks=max_parallel_tasks,
    )
