"""Working memory for the Dukat assistant.

This module provides the working memory functionality for
managing short-term context during conversations.

Version: 0.1.0
Created: 2025-04-22
"""

from typing import Dict, Any, List, Optional, Union, Deque
import logging
from datetime import datetime
import time
from collections import deque
import json

logger = logging.getLogger(__name__)


class Message:
    """A message in a conversation.

    This class represents a message in a conversation, with
    metadata about the sender, timestamp, etc.

    Attributes:
        content: The content of the message.
        role: The role of the sender (user, assistant, system).
        timestamp: The timestamp when the message was created.
        metadata: Additional metadata for the message.
    """

    def __init__(
        self,
        content: str,
        role: str = "user",
        timestamp: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a message.

        Args:
            content: The content of the message.
            role: The role of the sender (user, assistant, system).
            timestamp: The timestamp when the message was created.
            metadata: Additional metadata for the message.
        """
        self.content = content
        self.role = role
        self.timestamp = timestamp or int(time.time())
        self.metadata = metadata or {}

        logger.debug(
            f"Created message with role {role} and timestamp {self.timestamp}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary.

        Returns:
            A dictionary representation of the message.
        """
        return {
            "content": self.content,
            "role": self.role,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create a message from a dictionary.

        Args:
            data: A dictionary representation of the message.

        Returns:
            A new Message instance.
        """
        return cls(
            content=data["content"],
            role=data["role"],
            timestamp=data.get("timestamp"),
            metadata=data.get("metadata", {}),
        )

    def __str__(self) -> str:
        """Get a string representation of the message.

        Returns:
            A string representation of the message.
        """
        return f"{self.role}: {self.content}"


class WorkingMemory:
    """Working memory for the Dukat assistant.

    This class manages short-term context during conversations,
    including message history and active context.

    Attributes:
        messages: Deque of messages in the conversation.
        max_messages: Maximum number of messages to keep.
        context: Dictionary of active context items.
        conversation_id: The ID of the current conversation.
    """

    def __init__(
        self,
        max_messages: int = 100,
        conversation_id: Optional[str] = None,
    ):
        """Initialize the working memory.

        Args:
            max_messages: Maximum number of messages to keep.
            conversation_id: The ID of the current conversation.
        """
        self.messages: Deque[Message] = deque(maxlen=max_messages)
        self.max_messages = max_messages
        self.context: Dict[str, Any] = {}
        self.conversation_id = conversation_id or f"conv_{int(time.time())}"

        logger.info(
            f"Initialized working memory with conversation_id: {self.conversation_id}")

    def add_message(
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
        # Check if content is already a Message object
        if isinstance(content, Message):
            message = content
        else:
            # Create the message
            message = Message(
                content=content,
                role=role,
                metadata=metadata or {},
            )

        # Add conversation ID to metadata
        message.metadata["conversation_id"] = self.conversation_id

        # Add the message to the deque
        self.messages.append(message)

        logger.debug(
            f"Added {message.role} message: {message.content[:50] if len(message.content) > 50 else message.content}...")
        return message

    def get_messages(
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
        # Filter by role if needed
        if roles:
            messages = [m for m in self.messages if m.role in roles]
        else:
            messages = list(self.messages)

        # Reverse if needed
        if reverse:
            messages = messages[::-1]

        # Limit if needed
        if n is not None:
            messages = messages[-n:] if not reverse else messages[:n]

        return messages

    def get_last_message(self, role: Optional[str] = None) -> Optional[Message]:
        """Get the last message in the conversation.

        Args:
            role: Only return a message with this role.

        Returns:
            The last message, or None if there are no messages.
        """
        if not self.messages:
            return None

        if role:
            for message in reversed(self.messages):
                if message.role == role:
                    return message
            return None

        return self.messages[-1]

    def clear_messages(self) -> None:
        """Clear all messages from the conversation."""
        self.messages.clear()
        logger.info("Cleared all messages")

    def set_context(self, key: str, value: Any) -> None:
        """Set a context item.

        Args:
            key: The key for the context item.
            value: The value for the context item.
        """
        self.context[key] = value
        logger.debug(f"Set context item: {key}")

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context item.

        Args:
            key: The key for the context item.
            default: The default value to return if the key is not found.

        Returns:
            The value of the context item, or the default value.
        """
        return self.context.get(key, default)

    def remove_context(self, key: str) -> bool:
        """Remove a context item.

        Args:
            key: The key for the context item.

        Returns:
            True if the item was removed, False if it was not found.
        """
        if key in self.context:
            del self.context[key]
            logger.debug(f"Removed context item: {key}")
            return True

        return False

    def clear_context(self) -> None:
        """Clear all context items."""
        self.context.clear()
        logger.info("Cleared all context items")

    def format_history(
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
        messages = self.get_messages(n=n)

        if include_roles:
            return separator.join([f"{m.role}: {m.content}" for m in messages])
        else:
            return separator.join([m.content for m in messages])

    def to_dict(self) -> Dict[str, Any]:
        """Convert the working memory to a dictionary.

        Returns:
            A dictionary representation of the working memory.
        """
        return {
            "messages": [m.to_dict() for m in self.messages],
            "max_messages": self.max_messages,
            "context": self.context,
            "conversation_id": self.conversation_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkingMemory":
        """Create a working memory from a dictionary.

        Args:
            data: A dictionary representation of the working memory.

        Returns:
            A new WorkingMemory instance.
        """
        memory = cls(
            max_messages=data.get("max_messages", 100),
            conversation_id=data.get("conversation_id"),
        )

        # Add messages
        for message_data in data.get("messages", []):
            message = Message.from_dict(message_data)
            memory.messages.append(message)

        # Add context
        memory.context = data.get("context", {})

        return memory

    def save(self, file_path: str) -> bool:
        """Save the working memory to a file.

        Args:
            file_path: The path to save the file.

        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(file_path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)

            logger.info(f"Saved working memory to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving working memory: {str(e)}")
            return False

    @classmethod
    def load(cls, file_path: str) -> Optional["WorkingMemory"]:
        """Load a working memory from a file.

        Args:
            file_path: The path to load the file from.

        Returns:
            A new WorkingMemory instance, or None if the file could not be loaded.
        """
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            memory = cls.from_dict(data)
            logger.info(f"Loaded working memory from {file_path}")
            return memory

        except Exception as e:
            logger.error(f"Error loading working memory: {str(e)}")
            return None

    def new_conversation(self) -> str:
        """Start a new conversation.

        Returns:
            The ID of the new conversation.
        """
        self.conversation_id = f"conv_{int(time.time())}"
        self.clear_messages()
        self.clear_context()

        logger.info(
            f"Started new conversation with ID: {self.conversation_id}")
        return self.conversation_id

    def get_openai_messages(self, n: Optional[int] = None) -> List[Dict[str, str]]:
        """Get messages in OpenAI format.

        Args:
            n: Maximum number of messages to return.

        Returns:
            A list of messages in OpenAI format.
        """
        messages = self.get_messages(n=n)

        return [
            {"role": m.role, "content": m.content}
            for m in messages
        ]

    def get_anthropic_messages(self, n: Optional[int] = None) -> List[Dict[str, str]]:
        """Get messages in Anthropic format.

        Args:
            n: Maximum number of messages to return.

        Returns:
            A list of messages in Anthropic format.
        """
        messages = self.get_messages(n=n)

        return [
            {"role": "user" if m.role == "user" else "assistant", "content": m.content}
            for m in messages
        ]
