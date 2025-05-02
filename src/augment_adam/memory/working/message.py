"""Message class for working memory.

This module provides the Message class for representing messages in a conversation.
"""

from typing import Dict, Any, Optional
import time


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
