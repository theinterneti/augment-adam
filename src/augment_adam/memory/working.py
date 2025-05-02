"""Working memory for the Augment Adam assistant.

This module provides the working memory functionality for
managing short-term context during conversations.

Version: 0.1.0
Created: 2025-04-22
Updated: 2025-04-24
"""

from typing import Dict, Any, List, Optional, Union, Deque
import logging
from datetime import datetime
import time
from collections import deque
import json

logger = logging.getLogger(__name__)


class Message:
    """Message in a conversation.

    Attributes:
        content: The content of the message.
        role: The role of the sender (user, assistant, system).
        timestamp: The time the message was created.
        metadata: Additional metadata for the message.
    """

    def __init__(
        self,
        content: str,
        role: str = "user",
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the message.

        Args:
            content: The content of the message.
            role: The role of the sender (user, assistant, system).
            timestamp: The time the message was created.
            metadata: Additional metadata for the message.
        """
        self.content = content
        self.role = role
        self.timestamp = timestamp or time.time()
        self.metadata = metadata or {}

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
            A Message instance.
        """
        return cls(
            content=data["content"],
            role=data["role"],
            timestamp=data["timestamp"],
            metadata=data["metadata"],
        )


class WorkingMemory:
    """Working memory for the Augment Adam assistant.

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
        if isinstance(content, Message):
            message = content
        else:
            message = Message(
                content=content,
                role=role,
                metadata=metadata or {},
            )

        # Add conversation ID to metadata
        if "conversation_id" not in message.metadata:
            message.metadata["conversation_id"] = self.conversation_id

        self.messages.append(message)
        return message

    def get_messages(
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
        messages = list(self.messages)

        # Filter by role if needed
        if roles:
            messages = [m for m in messages if m.role in roles]

        # Reverse if needed
        if reverse:
            messages.reverse()

        # Limit to n if needed
        if n is not None:
            messages = messages[:n]

        return messages

    def get_last_message(
        self,
        role: Optional[str] = None,
    ) -> Optional[Message]:
        """Get the last message from memory.

        Args:
            role: Only return a message with this role.

        Returns:
            The last message, or None if no messages match.
        """
        if not self.messages:
            return None

        if role is None:
            return self.messages[-1]

        for message in reversed(self.messages):
            if message.role == role:
                return message

        return None

    def clear_messages(self) -> None:
        """Clear all messages from memory."""
        self.messages.clear()
        logger.info("Cleared all messages")

    def clear_context(self) -> None:
        """Clear all context items from memory."""
        self.context.clear()
        logger.info("Cleared all context items")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the working memory to a dictionary.

        Returns:
            A dictionary representation of the working memory.
        """
        return {
            "conversation_id": self.conversation_id,
            "max_messages": self.max_messages,
            "messages": [m.to_dict() for m in self.messages],
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkingMemory":
        """Create a working memory from a dictionary.

        Args:
            data: A dictionary representation of the working memory.

        Returns:
            A WorkingMemory instance.
        """
        memory = cls(
            max_messages=data["max_messages"],
            conversation_id=data["conversation_id"],
        )

        # Add messages
        for message_data in data["messages"]:
            memory.add_message(Message.from_dict(message_data))

        # Add context
        memory.context = data["context"]

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
            A WorkingMemory instance, or None if loading failed.
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
