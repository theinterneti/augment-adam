"""
Agent Communication module.

This module provides communication channels for agents to exchange messages.
"""

import uuid
import time
import queue
import threading
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar
from dataclasses import dataclass, field

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.ai_agent.coordination.registry import Agent, AgentRegistry, get_agent_registry


class MessageType(Enum):
    """
    Types of messages that agents can exchange.

    This enum defines the types of messages that agents can exchange, including
    requests, responses, notifications, and other message types.
    """

    REQUEST = auto()
    RESPONSE = auto()
    NOTIFICATION = auto()
    BROADCAST = auto()
    ERROR = auto()
    HEARTBEAT = auto()
    CUSTOM = auto()


class MessagePriority(Enum):
    """
    Priorities for agent messages.

    This enum defines the priorities for agent messages, which are used
    for message queue ordering.
    """

    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class AgentMessage:
    """
    Message exchanged between agents.

    This class represents a message exchanged between agents, including its
    content, sender, recipient, and other properties.

    Attributes:
        id: Unique identifier for the message.
        sender_id: ID of the agent sending the message.
        recipient_id: ID of the agent receiving the message, or None for broadcasts.
        content: The content of the message.
        message_type: The type of message.
        priority: The priority of the message.
        timestamp: When the message was created.
        in_reply_to: ID of the message this is replying to, if any.
        metadata: Additional metadata for the message.
        expires_at: When the message expires, if applicable.

    TODO(Issue #8): Add support for message encryption
    TODO(Issue #8): Implement message validation
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    recipient_id: Optional[str] = None
    content: Any = None
    message_type: MessageType = MessageType.NOTIFICATION
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    in_reply_to: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[float] = None

    def is_expired(self) -> bool:
        """
        Check if the message is expired.

        Returns:
            True if the message is expired, False otherwise.
        """
        if self.expires_at is None:
            return False

        return time.time() > self.expires_at

    def is_broadcast(self) -> bool:
        """
        Check if the message is a broadcast.

        Returns:
            True if the message is a broadcast, False otherwise.
        """
        return self.recipient_id is None or self.message_type == MessageType.BROADCAST

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary.

        Returns:
            Dictionary representation of the message.
        """
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "content": self.content,
            "message_type": self.message_type.name,
            "priority": self.priority.name,
            "timestamp": self.timestamp,
            "in_reply_to": self.in_reply_to,
            "metadata": self.metadata,
            "expires_at": self.expires_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """
        Create a message from a dictionary.

        Args:
            data: Dictionary representation of the message.

        Returns:
            Agent message.
        """
        # Convert message_type from string to enum
        message_type = data.get("message_type", MessageType.NOTIFICATION.name)
        if isinstance(message_type, str):
            try:
                message_type = MessageType[message_type]
            except KeyError:
                message_type = MessageType.CUSTOM

        # Convert priority from string to enum
        priority = data.get("priority", MessagePriority.NORMAL.name)
        if isinstance(priority, str):
            try:
                priority = MessagePriority[priority]
            except KeyError:
                priority = MessagePriority.NORMAL

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            sender_id=data.get("sender_id", ""),
            recipient_id=data.get("recipient_id"),
            content=data.get("content"),
            message_type=message_type,
            priority=priority,
            timestamp=data.get("timestamp", time.time()),
            in_reply_to=data.get("in_reply_to"),
            metadata=data.get("metadata", {}),
            expires_at=data.get("expires_at"),
        )


@tag("ai_agent.coordination")
class AgentCommunicationChannel:
    """
    Base class for agent communication channels.

    This class defines the interface for agent communication channels, which
    enable agents to exchange messages.

    Attributes:
        name: The name of the communication channel.
        metadata: Additional metadata for the channel.

    TODO(Issue #8): Add support for channel persistence
    TODO(Issue #8): Implement channel validation
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the communication channel.

        Args:
            name: The name of the communication channel.
        """
        self.name = name
        self.metadata: Dict[str, Any] = {}

    def send_message(self, message: AgentMessage) -> bool:
        """
        Send a message through the channel.

        Args:
            message: The message to send.

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        raise NotImplementedError("Subclasses must implement send_message")

    def receive_message(self, agent_id: str, timeout: Optional[float] = None) -> Optional[AgentMessage]:
        """
        Receive a message from the channel.

        Args:
            agent_id: The ID of the agent receiving the message.
            timeout: The maximum time to wait for a message, or None to wait indefinitely.

        Returns:
            The received message, or None if no message was received.
        """
        raise NotImplementedError("Subclasses must implement receive_message")

    def has_messages(self, agent_id: str) -> bool:
        """
        Check if there are messages for an agent.

        Args:
            agent_id: The ID of the agent.

        Returns:
            True if there are messages for the agent, False otherwise.
        """
        raise NotImplementedError("Subclasses must implement has_messages")

    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the channel.

        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the channel.

        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.

        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("ai_agent.coordination")
class DirectCommunicationChannel(AgentCommunicationChannel):
    """
    Communication channel for direct agent-to-agent messaging.

    This class implements a communication channel for direct agent-to-agent
    messaging, where messages are sent directly from one agent to another.

    Attributes:
        name: The name of the communication channel.
        metadata: Additional metadata for the channel.
        message_queues: Dictionary of message queues, keyed by agent ID.

    TODO(Issue #8): Add support for message persistence
    TODO(Issue #8): Implement message validation
    """

    def __init__(self, name: str = "direct_channel") -> None:
        """
        Initialize the direct communication channel.

        Args:
            name: The name of the communication channel.
        """
        super().__init__(name)
        self.message_queues: Dict[str, queue.PriorityQueue] = {}
        self.lock = threading.RLock()

    def _get_queue(self, agent_id: str) -> queue.PriorityQueue:
        """
        Get the message queue for an agent, creating it if it doesn't exist.

        Args:
            agent_id: The ID of the agent.

        Returns:
            The message queue for the agent.
        """
        with self.lock:
            if agent_id not in self.message_queues:
                self.message_queues[agent_id] = queue.PriorityQueue()

            return self.message_queues[agent_id]

    def send_message(self, message: AgentMessage) -> bool:
        """
        Send a message through the channel.

        Args:
            message: The message to send.

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        # Check if the message is expired
        if message.is_expired():
            return False

        # Check if the message is a broadcast
        if message.is_broadcast():
            return False  # Direct channel doesn't support broadcasts

        # Get the recipient's queue
        recipient_queue = self._get_queue(message.recipient_id)

        # Add the message to the queue with priority
        priority = 4 - message.priority.value  # Invert priority for queue (lower value = higher priority)
        recipient_queue.put((priority, message.id, message))

        return True

    def receive_message(self, agent_id: str, timeout: Optional[float] = None) -> Optional[AgentMessage]:
        """
        Receive a message from the channel.

        Args:
            agent_id: The ID of the agent receiving the message.
            timeout: The maximum time to wait for a message, or None to wait indefinitely.

        Returns:
            The received message, or None if no message was received.
        """
        # Get the agent's queue
        agent_queue = self._get_queue(agent_id)

        try:
            # Get a message from the queue
            priority, message_id, message = agent_queue.get(block=timeout is not None, timeout=timeout)
            agent_queue.task_done()

            # Check if the message is expired
            if message.is_expired():
                return self.receive_message(agent_id, timeout)

            return message
        except queue.Empty:
            return None

    def has_messages(self, agent_id: str) -> bool:
        """
        Check if there are messages for an agent.

        Args:
            agent_id: The ID of the agent.

        Returns:
            True if there are messages for the agent, False otherwise.
        """
        # Get the agent's queue
        agent_queue = self._get_queue(agent_id)

        return not agent_queue.empty()


@tag("ai_agent.coordination")
class BroadcastCommunicationChannel(AgentCommunicationChannel):
    """
    Communication channel for broadcasting messages to all agents.

    This class implements a communication channel for broadcasting messages
    to all agents, where messages are sent to all registered agents.

    Attributes:
        name: The name of the communication channel.
        metadata: Additional metadata for the channel.
        message_queues: Dictionary of message queues, keyed by agent ID.
        registry: The agent registry to use for broadcasting.

    TODO(Issue #8): Add support for message persistence
    TODO(Issue #8): Implement message validation
    """

    def __init__(self, name: str = "broadcast_channel", registry: Optional[AgentRegistry] = None) -> None:
        """
        Initialize the broadcast communication channel.

        Args:
            name: The name of the communication channel.
            registry: The agent registry to use for broadcasting.
        """
        super().__init__(name)
        self.message_queues: Dict[str, queue.PriorityQueue] = {}
        self.registry = registry or get_agent_registry()
        self.lock = threading.RLock()

    def _get_queue(self, agent_id: str) -> queue.PriorityQueue:
        """
        Get the message queue for an agent, creating it if it doesn't exist.

        Args:
            agent_id: The ID of the agent.

        Returns:
            The message queue for the agent.
        """
        with self.lock:
            if agent_id not in self.message_queues:
                self.message_queues[agent_id] = queue.PriorityQueue()

            return self.message_queues[agent_id]

    def send_message(self, message: AgentMessage) -> bool:
        """
        Send a message through the channel.

        Args:
            message: The message to send.

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        # Check if the message is expired
        if message.is_expired():
            return False

        # If the message has a specific recipient, send it directly
        if not message.is_broadcast():
            recipient_queue = self._get_queue(message.recipient_id)
            priority = 4 - message.priority.value  # Invert priority for queue
            recipient_queue.put((priority, message.id, message))
            return True

        # Otherwise, broadcast to all active agents
        success = False
        for agent in self.registry.get_active_agents():
            # Skip the sender
            if agent.id == message.sender_id:
                continue

            # Get the agent's queue
            agent_queue = self._get_queue(agent.id)

            # Add the message to the queue with priority
            priority = 4 - message.priority.value  # Invert priority for queue
            agent_queue.put((priority, message.id, message))
            success = True

        return success

    def receive_message(self, agent_id: str, timeout: Optional[float] = None) -> Optional[AgentMessage]:
        """
        Receive a message from the channel.

        Args:
            agent_id: The ID of the agent receiving the message.
            timeout: The maximum time to wait for a message, or None to wait indefinitely.

        Returns:
            The received message, or None if no message was received.
        """
        # Get the agent's queue
        agent_queue = self._get_queue(agent_id)

        try:
            # Get a message from the queue
            priority, message_id, message = agent_queue.get(block=timeout is not None, timeout=timeout)
            agent_queue.task_done()

            # Check if the message is expired
            if message.is_expired():
                return self.receive_message(agent_id, timeout)

            return message
        except queue.Empty:
            return None

    def has_messages(self, agent_id: str) -> bool:
        """
        Check if there are messages for an agent.

        Args:
            agent_id: The ID of the agent.

        Returns:
            True if there are messages for the agent, False otherwise.
        """
        # Get the agent's queue
        agent_queue = self._get_queue(agent_id)

        return not agent_queue.empty()


@tag("ai_agent.coordination")
class TopicCommunicationChannel(AgentCommunicationChannel):
    """
    Communication channel for topic-based messaging.

    This class implements a communication channel for topic-based messaging,
    where agents can subscribe to topics and receive messages published to those topics.

    Attributes:
        name: The name of the communication channel.
        metadata: Additional metadata for the channel.
        topic_queues: Dictionary of message queues, keyed by topic.
        subscriptions: Dictionary of topic subscriptions, keyed by agent ID.

    TODO(Issue #8): Add support for message persistence
    TODO(Issue #8): Implement message validation
    """

    def __init__(self, name: str = "topic_channel") -> None:
        """
        Initialize the topic communication channel.

        Args:
            name: The name of the communication channel.
        """
        super().__init__(name)
        self.topic_queues: Dict[str, queue.PriorityQueue] = {}
        self.subscriptions: Dict[str, Set[str]] = {}  # agent_id -> set of topics
        self.agent_queues: Dict[str, queue.PriorityQueue] = {}
        self.lock = threading.RLock()

    def _get_topic_queue(self, topic: str) -> queue.PriorityQueue:
        """
        Get the message queue for a topic, creating it if it doesn't exist.

        Args:
            topic: The topic.

        Returns:
            The message queue for the topic.
        """
        with self.lock:
            if topic not in self.topic_queues:
                self.topic_queues[topic] = queue.PriorityQueue()

            return self.topic_queues[topic]

    def _get_agent_queue(self, agent_id: str) -> queue.PriorityQueue:
        """
        Get the message queue for an agent, creating it if it doesn't exist.

        Args:
            agent_id: The ID of the agent.

        Returns:
            The message queue for the agent.
        """
        with self.lock:
            if agent_id not in self.agent_queues:
                self.agent_queues[agent_id] = queue.PriorityQueue()

            return self.agent_queues[agent_id]

    def subscribe(self, agent_id: str, topic: str) -> bool:
        """
        Subscribe an agent to a topic.

        Args:
            agent_id: The ID of the agent.
            topic: The topic to subscribe to.

        Returns:
            True if the agent was subscribed, False otherwise.
        """
        with self.lock:
            if agent_id not in self.subscriptions:
                self.subscriptions[agent_id] = set()

            self.subscriptions[agent_id].add(topic)
            return True

    def unsubscribe(self, agent_id: str, topic: str) -> bool:
        """
        Unsubscribe an agent from a topic.

        Args:
            agent_id: The ID of the agent.
            topic: The topic to unsubscribe from.

        Returns:
            True if the agent was unsubscribed, False otherwise.
        """
        with self.lock:
            if agent_id not in self.subscriptions:
                return False

            if topic not in self.subscriptions[agent_id]:
                return False

            self.subscriptions[agent_id].remove(topic)
            return True

    def unsubscribe_all(self, agent_id: str) -> bool:
        """
        Unsubscribe an agent from all topics.

        Args:
            agent_id: The ID of the agent.

        Returns:
            True if the agent was unsubscribed, False otherwise.
        """
        with self.lock:
            if agent_id not in self.subscriptions:
                return False

            # Clear the set instead of removing the key
            self.subscriptions[agent_id].clear()
            return True

    def get_subscriptions(self, agent_id: str) -> Set[str]:
        """
        Get the topics an agent is subscribed to.

        Args:
            agent_id: The ID of the agent.

        Returns:
            Set of topics the agent is subscribed to.
        """
        with self.lock:
            return self.subscriptions.get(agent_id, set()).copy()

    def get_subscribers(self, topic: str) -> Set[str]:
        """
        Get the agents subscribed to a topic.

        Args:
            topic: The topic.

        Returns:
            Set of agent IDs subscribed to the topic.
        """
        with self.lock:
            subscribers = set()
            for agent_id, topics in self.subscriptions.items():
                if topic in topics:
                    subscribers.add(agent_id)

            return subscribers

    def publish(self, topic: str, message: AgentMessage) -> bool:
        """
        Publish a message to a topic.

        Args:
            topic: The topic to publish to.
            message: The message to publish.

        Returns:
            True if the message was published successfully, False otherwise.
        """
        # Check if the message is expired
        if message.is_expired():
            return False

        # Add topic to message metadata
        message.metadata["topic"] = topic

        # Get subscribers
        subscribers = self.get_subscribers(topic)

        # If there are no subscribers, return False
        if not subscribers:
            return False

        # Send the message to all subscribers
        success = False
        for agent_id in subscribers:
            # Skip the sender
            if agent_id == message.sender_id:
                continue

            # Get the agent's queue
            agent_queue = self._get_agent_queue(agent_id)

            # Add the message to the queue with priority
            priority = 4 - message.priority.value  # Invert priority for queue
            # Use message ID as a tiebreaker for priority queue comparison
            agent_queue.put((priority, message.id, message))
            success = True

        return success

    def send_message(self, message: AgentMessage) -> bool:
        """
        Send a message through the channel.

        Args:
            message: The message to send.

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        # Check if the message is expired
        if message.is_expired():
            return False

        # Check if the message has a topic
        topic = message.metadata.get("topic")
        if topic is None:
            return False

        # Publish the message to the topic
        return self.publish(topic, message)

    def receive_message(self, agent_id: str, timeout: Optional[float] = None) -> Optional[AgentMessage]:
        """
        Receive a message from the channel.

        Args:
            agent_id: The ID of the agent receiving the message.
            timeout: The maximum time to wait for a message, or None to wait indefinitely.

        Returns:
            The received message, or None if no message was received.
        """
        # Get the agent's queue
        agent_queue = self._get_agent_queue(agent_id)

        try:
            # Get a message from the queue
            priority, message_id, message = agent_queue.get(block=timeout is not None, timeout=timeout)
            agent_queue.task_done()

            # Check if the message is expired
            if message.is_expired():
                return self.receive_message(agent_id, timeout)

            return message
        except queue.Empty:
            return None

    def has_messages(self, agent_id: str) -> bool:
        """
        Check if there are messages for an agent.

        Args:
            agent_id: The ID of the agent.

        Returns:
            True if there are messages for the agent, False otherwise.
        """
        # Get the agent's queue
        agent_queue = self._get_agent_queue(agent_id)

        return not agent_queue.empty()
