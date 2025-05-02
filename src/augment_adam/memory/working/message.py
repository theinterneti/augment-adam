"""Message class for working memory.

This module provides the Message class for representing messages in a conversation.
"""

from typing import Dict, Any, Optional
import time
import uuid
import datetime


class Message:
    """Message in a conversation.

    Attributes:
        id: Unique identifier for the message.
        content: The content of the message.
        role: The role of the sender (user, assistant, system).
        created_at: The time the message was created.
        updated_at: The time the message was last updated.
        metadata: Additional metadata for the message.
    """

    def __init__(
        self,
        content: str,
        role: str = "user",
        id: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the message.

        Args:
            content: The content of the message.
            role: The role of the sender (user, assistant, system).
            id: Unique identifier for the message.
            created_at: The time the message was created.
            updated_at: The time the message was last updated.
            metadata: Additional metadata for the message.
        """
        self.id = id or f"msg-{str(uuid.uuid4())}"
        self.content = content
        self.role = role
        self.created_at = created_at or datetime.datetime.now().isoformat()
        self.updated_at = updated_at or self.created_at
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary.

        Returns:
            A dictionary representation of the message.
        """
        return {
            "id": self.id,
            "content": self.content,
            "role": self.role,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
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
            id=data.get("id"),
            content=data["content"],
            role=data["role"],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            metadata=data.get("metadata", {}),
        )

    def format_for_conversation(self) -> str:
        """Format the message for display in a conversation.

        Returns:
            A string representation of the message in the format "role: content".
        """
        return f"{self.role}: {self.content}"
