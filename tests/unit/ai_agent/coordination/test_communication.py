"""
Unit test for the communication classes.

This module contains tests for the communication classes, which are core components
of the agent coordination system.
"""

import unittest
import time
from unittest.mock import patch, MagicMock

import pytest
from augment_adam.testing.utils.tag_utils import safe_tag, reset_tag_registry
from augment_adam.ai_agent.coordination.communication import (
    AgentMessage, MessageType, MessagePriority,
    AgentCommunicationChannel, DirectCommunicationChannel,
    BroadcastCommunicationChannel, TopicCommunicationChannel
)
from augment_adam.ai_agent.coordination.registry import AgentRegistry, Agent


@safe_tag("testing.unit.ai_agent.coordination.communication")
class TestAgentMessage(unittest.TestCase):
    """
    Tests for the AgentMessage class.
    """
    
    def setUp(self):
        """Set up the test case."""
        # Reset the tag registry to avoid conflicts
        reset_tag_registry()
        
        # Create a test message
        self.message = AgentMessage(
            sender_id="agent1",
            recipient_id="agent2",
            content="Test message",
            message_type=MessageType.NOTIFICATION,
            priority=MessagePriority.NORMAL,
            in_reply_to="message1",
            metadata={"key": "value"}
        )
    
    def test_initialization(self):
        """Test initialization of a message."""
        # Verify the message was initialized correctly
        self.assertEqual(self.message.sender_id, "agent1")
        self.assertEqual(self.message.recipient_id, "agent2")
        self.assertEqual(self.message.content, "Test message")
        self.assertEqual(self.message.message_type, MessageType.NOTIFICATION)
        self.assertEqual(self.message.priority, MessagePriority.NORMAL)
        self.assertEqual(self.message.in_reply_to, "message1")
        self.assertEqual(self.message.metadata, {"key": "value"})
        self.assertIsNotNone(self.message.id)
        self.assertIsNotNone(self.message.timestamp)
        self.assertIsNone(self.message.expires_at)
    
    def test_is_expired(self):
        """Test checking if a message is expired."""
        # Initially, the message is not expired
        self.assertFalse(self.message.is_expired())
        
        # Set an expiration time in the past
        self.message.expires_at = time.time() - 3600  # 1 hour ago
        
        # Now the message is expired
        self.assertTrue(self.message.is_expired())
        
        # Set an expiration time in the future
        self.message.expires_at = time.time() + 3600  # 1 hour from now
        
        # The message is not expired
        self.assertFalse(self.message.is_expired())
    
    def test_is_broadcast(self):
        """Test checking if a message is a broadcast."""
        # Initially, the message is not a broadcast
        self.assertFalse(self.message.is_broadcast())
        
        # Set the recipient to None
        self.message.recipient_id = None
        
        # Now the message is a broadcast
        self.assertTrue(self.message.is_broadcast())
        
        # Set the recipient back but change the message type to BROADCAST
        self.message.recipient_id = "agent2"
        self.message.message_type = MessageType.BROADCAST
        
        # The message is still a broadcast
        self.assertTrue(self.message.is_broadcast())
    
    def test_to_dict(self):
        """Test converting a message to a dictionary."""
        # Convert to dictionary
        message_dict = self.message.to_dict()
        
        # Verify the dictionary
        self.assertEqual(message_dict["id"], self.message.id)
        self.assertEqual(message_dict["sender_id"], "agent1")
        self.assertEqual(message_dict["recipient_id"], "agent2")
        self.assertEqual(message_dict["content"], "Test message")
        self.assertEqual(message_dict["message_type"], "NOTIFICATION")
        self.assertEqual(message_dict["priority"], "NORMAL")
        self.assertEqual(message_dict["in_reply_to"], "message1")
        self.assertEqual(message_dict["metadata"], {"key": "value"})
        self.assertEqual(message_dict["timestamp"], self.message.timestamp)
        self.assertIsNone(message_dict["expires_at"])
    
    def test_from_dict(self):
        """Test creating a message from a dictionary."""
        # Create a dictionary
        message_dict = {
            "id": "test-id",
            "sender_id": "agent3",
            "recipient_id": "agent4",
            "content": "Dictionary message",
            "message_type": "REQUEST",
            "priority": "HIGH",
            "timestamp": time.time(),
            "in_reply_to": "message2",
            "metadata": {"key2": "value2"},
            "expires_at": time.time() + 3600
        }
        
        # Create a message from the dictionary
        message = AgentMessage.from_dict(message_dict)
        
        # Verify the message
        self.assertEqual(message.id, "test-id")
        self.assertEqual(message.sender_id, "agent3")
        self.assertEqual(message.recipient_id, "agent4")
        self.assertEqual(message.content, "Dictionary message")
        self.assertEqual(message.message_type, MessageType.REQUEST)
        self.assertEqual(message.priority, MessagePriority.HIGH)
        self.assertEqual(message.in_reply_to, "message2")
        self.assertEqual(message.metadata, {"key2": "value2"})
        self.assertEqual(message.timestamp, message_dict["timestamp"])
        self.assertEqual(message.expires_at, message_dict["expires_at"])
        
        # Test with invalid message type
        message_dict["message_type"] = "INVALID"
        message = AgentMessage.from_dict(message_dict)
        self.assertEqual(message.message_type, MessageType.CUSTOM)
        
        # Test with invalid priority
        message_dict["priority"] = "INVALID"
        message = AgentMessage.from_dict(message_dict)
        self.assertEqual(message.priority, MessagePriority.NORMAL)


@safe_tag("testing.unit.ai_agent.coordination.communication")
class TestDirectCommunicationChannel(unittest.TestCase):
    """
    Tests for the DirectCommunicationChannel class.
    """
    
    def setUp(self):
        """Set up the test case."""
        # Reset the tag registry to avoid conflicts
        reset_tag_registry()
        
        # Create a test channel
        self.channel = DirectCommunicationChannel()
        
        # Create test messages
        self.message1 = AgentMessage(
            sender_id="agent1",
            recipient_id="agent2",
            content="Message 1",
            priority=MessagePriority.NORMAL
        )
        
        self.message2 = AgentMessage(
            sender_id="agent1",
            recipient_id="agent2",
            content="Message 2",
            priority=MessagePriority.HIGH
        )
        
        self.message3 = AgentMessage(
            sender_id="agent1",
            recipient_id="agent2",
            content="Message 3",
            priority=MessagePriority.LOW
        )
        
        self.broadcast_message = AgentMessage(
            sender_id="agent1",
            recipient_id=None,
            content="Broadcast message",
            message_type=MessageType.BROADCAST
        )
        
        self.expired_message = AgentMessage(
            sender_id="agent1",
            recipient_id="agent2",
            content="Expired message",
            expires_at=time.time() - 3600  # 1 hour ago
        )
    
    def test_initialization(self):
        """Test initialization of a channel."""
        # Verify the channel was initialized correctly
        self.assertEqual(self.channel.name, "direct_channel")
        self.assertEqual(self.channel.message_queues, {})
    
    def test_send_message(self):
        """Test sending a message."""
        # Send a message
        result = self.channel.send_message(self.message1)
        
        # Verify the message was sent
        self.assertTrue(result)
        self.assertIn("agent2", self.channel.message_queues)
        self.assertEqual(self.channel.message_queues["agent2"].qsize(), 1)
        
        # Send another message
        result = self.channel.send_message(self.message2)
        
        # Verify the message was sent
        self.assertTrue(result)
        self.assertEqual(self.channel.message_queues["agent2"].qsize(), 2)
        
        # Try to send a broadcast message
        result = self.channel.send_message(self.broadcast_message)
        
        # Verify the message was not sent
        self.assertFalse(result)
        
        # Try to send an expired message
        result = self.channel.send_message(self.expired_message)
        
        # Verify the message was not sent
        self.assertFalse(result)
    
    def test_receive_message(self):
        """Test receiving a message."""
        # Send messages with different priorities
        self.channel.send_message(self.message1)  # NORMAL
        self.channel.send_message(self.message2)  # HIGH
        self.channel.send_message(self.message3)  # LOW
        
        # Receive messages
        message = self.channel.receive_message("agent2")
        
        # Verify the highest priority message was received first
        self.assertEqual(message.content, "Message 2")
        self.assertEqual(message.priority, MessagePriority.HIGH)
        
        # Receive another message
        message = self.channel.receive_message("agent2")
        
        # Verify the next highest priority message was received
        self.assertEqual(message.content, "Message 1")
        self.assertEqual(message.priority, MessagePriority.NORMAL)
        
        # Receive the last message
        message = self.channel.receive_message("agent2")
        
        # Verify the lowest priority message was received last
        self.assertEqual(message.content, "Message 3")
        self.assertEqual(message.priority, MessagePriority.LOW)
        
        # Try to receive a message when there are none
        message = self.channel.receive_message("agent2")
        
        # Verify no message was received
        self.assertIsNone(message)
        
        # Try to receive a message for an agent with no queue
        message = self.channel.receive_message("agent3")
        
        # Verify no message was received
        self.assertIsNone(message)
    
    def test_receive_message_with_timeout(self):
        """Test receiving a message with a timeout."""
        # Try to receive a message with a short timeout
        start_time = time.time()
        message = self.channel.receive_message("agent2", timeout=0.1)
        end_time = time.time()
        
        # Verify no message was received and the timeout was respected
        self.assertIsNone(message)
        self.assertLess(end_time - start_time, 0.2)  # Allow some margin for execution time


@safe_tag("testing.unit.ai_agent.coordination.communication")
class TestBroadcastCommunicationChannel(unittest.TestCase):
    """
    Tests for the BroadcastCommunicationChannel class.
    """
    
    def setUp(self):
        """Set up the test case."""
        # Reset the tag registry to avoid conflicts
        reset_tag_registry()
        
        # Create a mock registry
        self.registry = MagicMock(spec=AgentRegistry)
        
        # Create mock agents
        self.agent1 = MagicMock(spec=Agent)
        self.agent1.id = "agent1"
        self.agent1.is_active = True
        
        self.agent2 = MagicMock(spec=Agent)
        self.agent2.id = "agent2"
        self.agent2.is_active = True
        
        self.agent3 = MagicMock(spec=Agent)
        self.agent3.id = "agent3"
        self.agent3.is_active = True
        
        # Set up the registry to return our mock agents
        self.registry.get_active_agents.return_value = [self.agent1, self.agent2, self.agent3]
        
        # Create a test channel
        self.channel = BroadcastCommunicationChannel(registry=self.registry)
        
        # Create test messages
        self.direct_message = AgentMessage(
            sender_id="agent1",
            recipient_id="agent2",
            content="Direct message"
        )
        
        self.broadcast_message = AgentMessage(
            sender_id="agent1",
            recipient_id=None,
            content="Broadcast message",
            message_type=MessageType.BROADCAST
        )
    
    def test_initialization(self):
        """Test initialization of a channel."""
        # Verify the channel was initialized correctly
        self.assertEqual(self.channel.name, "broadcast_channel")
        self.assertEqual(self.channel.message_queues, {})
        self.assertEqual(self.channel.registry, self.registry)
    
    def test_send_direct_message(self):
        """Test sending a direct message."""
        # Send a direct message
        result = self.channel.send_message(self.direct_message)
        
        # Verify the message was sent
        self.assertTrue(result)
        self.assertIn("agent2", self.channel.message_queues)
        self.assertEqual(self.channel.message_queues["agent2"].qsize(), 1)
    
    def test_send_broadcast_message(self):
        """Test sending a broadcast message."""
        # Send a broadcast message
        result = self.channel.send_message(self.broadcast_message)
        
        # Verify the message was sent to all agents except the sender
        self.assertTrue(result)
        self.assertNotIn("agent1", self.channel.message_queues)  # Sender doesn't receive
        self.assertIn("agent2", self.channel.message_queues)
        self.assertIn("agent3", self.channel.message_queues)
        self.assertEqual(self.channel.message_queues["agent2"].qsize(), 1)
        self.assertEqual(self.channel.message_queues["agent3"].qsize(), 1)
        
        # Verify the registry was called
        self.registry.get_active_agents.assert_called_once()
    
    def test_receive_message(self):
        """Test receiving a message."""
        # Send a broadcast message
        self.channel.send_message(self.broadcast_message)
        
        # Receive messages
        message2 = self.channel.receive_message("agent2")
        message3 = self.channel.receive_message("agent3")
        
        # Verify the messages were received
        self.assertEqual(message2.content, "Broadcast message")
        self.assertEqual(message3.content, "Broadcast message")
        
        # Try to receive a message when there are none
        message = self.channel.receive_message("agent2")
        
        # Verify no message was received
        self.assertIsNone(message)


@safe_tag("testing.unit.ai_agent.coordination.communication")
class TestTopicCommunicationChannel(unittest.TestCase):
    """
    Tests for the TopicCommunicationChannel class.
    """
    
    def setUp(self):
        """Set up the test case."""
        # Reset the tag registry to avoid conflicts
        reset_tag_registry()
        
        # Create a test channel
        self.channel = TopicCommunicationChannel()
        
        # Create test messages
        self.topic_message1 = AgentMessage(
            sender_id="agent1",
            recipient_id=None,
            content="Topic message 1",
            metadata={"topic": "topic1"}
        )
        
        self.topic_message2 = AgentMessage(
            sender_id="agent1",
            recipient_id=None,
            content="Topic message 2",
            metadata={"topic": "topic2"}
        )
        
        self.no_topic_message = AgentMessage(
            sender_id="agent1",
            recipient_id="agent2",
            content="No topic message"
        )
    
    def test_initialization(self):
        """Test initialization of a channel."""
        # Verify the channel was initialized correctly
        self.assertEqual(self.channel.name, "topic_channel")
        self.assertEqual(self.channel.topic_queues, {})
        self.assertEqual(self.channel.subscriptions, {})
        self.assertEqual(self.channel.agent_queues, {})
    
    def test_subscribe_unsubscribe(self):
        """Test subscribing and unsubscribing from topics."""
        # Subscribe to topics
        self.channel.subscribe("agent2", "topic1")
        self.channel.subscribe("agent2", "topic2")
        self.channel.subscribe("agent3", "topic1")
        
        # Verify the subscriptions
        self.assertIn("agent2", self.channel.subscriptions)
        self.assertIn("agent3", self.channel.subscriptions)
        self.assertEqual(len(self.channel.subscriptions["agent2"]), 2)
        self.assertEqual(len(self.channel.subscriptions["agent3"]), 1)
        self.assertIn("topic1", self.channel.subscriptions["agent2"])
        self.assertIn("topic2", self.channel.subscriptions["agent2"])
        self.assertIn("topic1", self.channel.subscriptions["agent3"])
        
        # Unsubscribe from a topic
        self.channel.unsubscribe("agent2", "topic1")
        
        # Verify the subscription was removed
        self.assertEqual(len(self.channel.subscriptions["agent2"]), 1)
        self.assertNotIn("topic1", self.channel.subscriptions["agent2"])
        self.assertIn("topic2", self.channel.subscriptions["agent2"])
        
        # Unsubscribe from all topics
        self.channel.unsubscribe_all("agent2")
        
        # Verify all subscriptions were removed
        self.assertEqual(len(self.channel.subscriptions["agent2"]), 0)
    
    def test_publish(self):
        """Test publishing a message to a topic."""
        # Subscribe to topics
        self.channel.subscribe("agent2", "topic1")
        self.channel.subscribe("agent3", "topic1")
        self.channel.subscribe("agent3", "topic2")
        
        # Publish a message to topic1
        result = self.channel.publish("topic1", self.topic_message1)
        
        # Verify the message was published
        self.assertTrue(result)
        self.assertIn("agent2", self.channel.agent_queues)
        self.assertIn("agent3", self.channel.agent_queues)
        self.assertEqual(self.channel.agent_queues["agent2"].qsize(), 1)
        self.assertEqual(self.channel.agent_queues["agent3"].qsize(), 1)
        
        # Publish a message to topic2
        result = self.channel.publish("topic2", self.topic_message2)
        
        # Verify the message was published
        self.assertTrue(result)
        self.assertEqual(self.channel.agent_queues["agent2"].qsize(), 1)  # No change
        self.assertEqual(self.channel.agent_queues["agent3"].qsize(), 2)  # Increased
        
        # Publish to a topic with no subscribers
        result = self.channel.publish("topic3", self.topic_message1)
        
        # Verify the result
        self.assertFalse(result)
    
    def test_send_message(self):
        """Test sending a message."""
        # Subscribe to topics
        self.channel.subscribe("agent2", "topic1")
        
        # Send a message with a topic
        result = self.channel.send_message(self.topic_message1)
        
        # Verify the message was sent
        self.assertTrue(result)
        self.assertIn("agent2", self.channel.agent_queues)
        self.assertEqual(self.channel.agent_queues["agent2"].qsize(), 1)
        
        # Send a message without a topic
        result = self.channel.send_message(self.no_topic_message)
        
        # Verify the message was not sent
        self.assertFalse(result)
    
    def test_receive_message(self):
        """Test receiving a message."""
        # Subscribe to a topic
        self.channel.subscribe("agent2", "topic1")
        
        # Send a message
        self.channel.send_message(self.topic_message1)
        
        # Receive the message
        message = self.channel.receive_message("agent2")
        
        # Verify the message was received
        self.assertEqual(message.content, "Topic message 1")
        
        # Try to receive a message when there are none
        message = self.channel.receive_message("agent2")
        
        # Verify no message was received
        self.assertIsNone(message)
    
if __name__ == "__main__":
    unittest.main()
