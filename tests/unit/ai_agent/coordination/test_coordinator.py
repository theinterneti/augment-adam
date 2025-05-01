"""Unit tests for the AgentCoordinator class."""

import unittest
from unittest.mock import MagicMock, patch
import asyncio

from augment_adam.ai_agent.coordination.coordinator import AgentCoordinator


class TestAgentCoordinator(unittest.TestCase):
    """Tests for the AgentCoordinator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock agents
        self.agent1 = MagicMock()
        self.agent1.name = "Agent 1"
        self.agent1.process.return_value = {"response": "Response from Agent 1"}
        
        self.agent2 = MagicMock()
        self.agent2.name = "Agent 2"
        self.agent2.process.return_value = {"response": "Response from Agent 2"}
        
        # Create coordinator with mock agents
        self.coordinator = AgentCoordinator(
            name="Test Coordinator",
            agents={
                "agent1": self.agent1,
                "agent2": self.agent2
            }
        )
    
    def test_initialization(self):
        """Test coordinator initialization."""
        self.assertEqual(self.coordinator.name, "Test Coordinator")
        self.assertEqual(len(self.coordinator.agents), 2)
        self.assertEqual(len(self.coordinator.message_history), 0)
    
    def test_register_agent(self):
        """Test registering an agent."""
        # Create a new mock agent
        agent3 = MagicMock()
        agent3.name = "Agent 3"
        
        # Register the agent
        self.coordinator.register_agent("agent3", agent3)
        
        # Check that the agent was registered
        self.assertEqual(len(self.coordinator.agents), 3)
        self.assertIn("agent3", self.coordinator.agents)
        self.assertEqual(self.coordinator.agents["agent3"], agent3)
    
    def test_unregister_agent(self):
        """Test unregistering an agent."""
        # Unregister an agent
        result = self.coordinator.unregister_agent("agent1")
        
        # Check that the agent was unregistered
        self.assertTrue(result)
        self.assertEqual(len(self.coordinator.agents), 1)
        self.assertNotIn("agent1", self.coordinator.agents)
        
        # Try to unregister a non-existent agent
        result = self.coordinator.unregister_agent("non_existent")
        
        # Check that the result is False
        self.assertFalse(result)
    
    def test_get_agent(self):
        """Test getting an agent."""
        # Get an existing agent
        agent = self.coordinator.get_agent("agent1")
        
        # Check that the correct agent was returned
        self.assertEqual(agent, self.agent1)
        
        # Try to get a non-existent agent
        agent = self.coordinator.get_agent("non_existent")
        
        # Check that None was returned
        self.assertIsNone(agent)
    
    def test_send_message(self):
        """Test sending a message."""
        # Send a message
        message = self.coordinator.send_message(
            from_agent_id="agent1",
            to_agent_id="agent2",
            message="Test message",
            metadata={"key": "value"}
        )
        
        # Check the message
        self.assertEqual(message["from"], "agent1")
        self.assertEqual(message["to"], "agent2")
        self.assertEqual(message["message"], "Test message")
        self.assertEqual(message["metadata"], {"key": "value"})
        
        # Check that the message was added to the history
        self.assertEqual(len(self.coordinator.message_history), 1)
        self.assertEqual(self.coordinator.message_history[0], message)
        
        # Try to send a message from a non-existent agent
        with self.assertRaises(ValueError):
            self.coordinator.send_message(
                from_agent_id="non_existent",
                to_agent_id="agent2",
                message="Test message"
            )
        
        # Try to send a message to a non-existent agent
        with self.assertRaises(ValueError):
            self.coordinator.send_message(
                from_agent_id="agent1",
                to_agent_id="non_existent",
                message="Test message"
            )
    
    def test_process_message(self):
        """Test processing a message."""
        # Create a message
        message = {
            "id": "test_id",
            "from": "agent1",
            "to": "agent2",
            "message": "Test message",
            "metadata": {"key": "value"},
            "timestamp": 0
        }
        
        # Process the message
        response = self.coordinator.process_message(message)
        
        # Check the response
        self.assertEqual(response["from"], "agent2")
        self.assertEqual(response["to"], "agent1")
        self.assertEqual(response["message"], "Response from Agent 2")
        self.assertEqual(response["in_response_to"], "test_id")
        
        # Check that the agent's process method was called
        self.agent2.process.assert_called_once_with("Test message")
        
        # Check that the response was added to the history
        self.assertEqual(len(self.coordinator.message_history), 1)
        self.assertEqual(self.coordinator.message_history[0], response)
        
        # Try to process a message for a non-existent agent
        message["to"] = "non_existent"
        with self.assertRaises(ValueError):
            self.coordinator.process_message(message)
    
    @patch('asyncio.get_event_loop')
    async def test_process_message_async(self, mock_get_event_loop):
        """Test processing a message asynchronously."""
        # Create a mock loop
        mock_loop = MagicMock()
        mock_get_event_loop.return_value = mock_loop
        
        # Mock the run_in_executor method
        mock_loop.run_in_executor.return_value = {"response": "Response from Agent 2"}
        
        # Create a message
        message = {
            "id": "test_id",
            "from": "agent1",
            "to": "agent2",
            "message": "Test message",
            "metadata": {"key": "value"},
            "timestamp": 0
        }
        
        # Process the message asynchronously
        response = await self.coordinator.process_message_async(message)
        
        # Check the response
        self.assertEqual(response["from"], "agent2")
        self.assertEqual(response["to"], "agent1")
        self.assertEqual(response["message"], "Response from Agent 2")
        self.assertEqual(response["in_response_to"], "test_id")
        
        # Check that the loop's run_in_executor method was called
        mock_loop.run_in_executor.assert_called_once()
        
        # Check that the response was added to the history
        self.assertEqual(len(self.coordinator.message_history), 1)
        self.assertEqual(self.coordinator.message_history[0], response)
        
        # Try to process a message for a non-existent agent
        message["to"] = "non_existent"
        with self.assertRaises(ValueError):
            await self.coordinator.process_message_async(message)
    
    def test_get_conversation(self):
        """Test getting a conversation between two agents."""
        # Add some messages to the history
        self.coordinator.message_history = [
            {
                "id": "1",
                "from": "agent1",
                "to": "agent2",
                "message": "Message 1",
                "timestamp": 1
            },
            {
                "id": "2",
                "from": "agent2",
                "to": "agent1",
                "message": "Message 2",
                "timestamp": 2
            },
            {
                "id": "3",
                "from": "agent1",
                "to": "agent3",
                "message": "Message 3",
                "timestamp": 3
            }
        ]
        
        # Get the conversation between agent1 and agent2
        conversation = self.coordinator.get_conversation("agent1", "agent2")
        
        # Check the conversation
        self.assertEqual(len(conversation), 2)
        self.assertEqual(conversation[0]["id"], "1")
        self.assertEqual(conversation[1]["id"], "2")
        
        # Get the conversation with a limit
        conversation = self.coordinator.get_conversation("agent1", "agent2", limit=1)
        
        # Check the conversation
        self.assertEqual(len(conversation), 1)
        self.assertEqual(conversation[0]["id"], "2")  # Should be the most recent
    
    def test_get_agent_messages(self):
        """Test getting messages involving an agent."""
        # Add some messages to the history
        self.coordinator.message_history = [
            {
                "id": "1",
                "from": "agent1",
                "to": "agent2",
                "message": "Message 1",
                "timestamp": 1
            },
            {
                "id": "2",
                "from": "agent2",
                "to": "agent1",
                "message": "Message 2",
                "timestamp": 2
            },
            {
                "id": "3",
                "from": "agent1",
                "to": "agent3",
                "message": "Message 3",
                "timestamp": 3
            }
        ]
        
        # Get messages involving agent1
        messages = self.coordinator.get_agent_messages("agent1")
        
        # Check the messages
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]["id"], "1")
        self.assertEqual(messages[1]["id"], "2")
        self.assertEqual(messages[2]["id"], "3")
        
        # Get messages with a limit
        messages = self.coordinator.get_agent_messages("agent1", limit=2)
        
        # Check the messages
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["id"], "2")  # Should be the most recent
        self.assertEqual(messages[1]["id"], "3")
    
    def test_clear_history(self):
        """Test clearing the message history."""
        # Add some messages to the history
        self.coordinator.message_history = [
            {"id": "1"},
            {"id": "2"}
        ]
        
        # Clear the history
        self.coordinator.clear_history()
        
        # Check that the history is empty
        self.assertEqual(len(self.coordinator.message_history), 0)
    
    def test_get_all_agents(self):
        """Test getting all agents."""
        # Get all agents
        agents = self.coordinator.get_all_agents()
        
        # Check the agents
        self.assertEqual(len(agents), 2)
        self.assertEqual(agents["agent1"], self.agent1)
        self.assertEqual(agents["agent2"], self.agent2)
        
        # Check that the returned dictionary is a copy
        agents["agent3"] = MagicMock()
        self.assertEqual(len(self.coordinator.agents), 2)
    
    def test_coordinate_task(self):
        """Test coordinating a task."""
        # Mock the agent's process method to simulate needing help
        self.agent1.process.side_effect = [
            {"response": "I need help with this task"},
            {"response": "Final response"}
        ]
        
        # Coordinate a task
        result = self.coordinator.coordinate_task(
            task="Test task",
            primary_agent_id="agent1",
            helper_agent_ids=["agent2"],
            max_rounds=3
        )
        
        # Check the result
        self.assertEqual(result["task"], "Test task")
        self.assertEqual(result["primary_agent"], "agent1")
        self.assertEqual(result["helper_agents"], ["agent2"])
        self.assertEqual(result["rounds"], 2)
        self.assertEqual(result["response"], "Final response")
        
        # Check that the primary agent's process method was called twice
        self.assertEqual(self.agent1.process.call_count, 2)
        
        # Check that the helper agent's process method was called once
        self.agent2.process.assert_called_once()
        
        # Try to coordinate a task with a non-existent primary agent
        with self.assertRaises(ValueError):
            self.coordinator.coordinate_task(
                task="Test task",
                primary_agent_id="non_existent",
                helper_agent_ids=["agent2"]
            )
        
        # Try to coordinate a task with a non-existent helper agent
        with self.assertRaises(ValueError):
            self.coordinator.coordinate_task(
                task="Test task",
                primary_agent_id="agent1",
                helper_agent_ids=["non_existent"]
            )
    
    @patch('asyncio.create_task')
    @patch('asyncio.gather')
    async def test_coordinate_task_async(self, mock_gather, mock_create_task):
        """Test coordinating a task asynchronously."""
        # Mock the agent's process_async method
        self.agent1.process_async = MagicMock()
        self.agent1.process_async.side_effect = [
            {"response": "I need help with this task"},
            {"response": "Final response"}
        ]
        
        # Mock the helper agent's process_async method
        self.agent2.process_async = MagicMock()
        self.agent2.process_async.return_value = {"response": "Helper response"}
        
        # Mock gather to return a list of responses
        mock_gather.return_value = [{"message": "Helper response"}]
        
        # Coordinate a task asynchronously
        result = await self.coordinator.coordinate_task_async(
            task="Test task",
            primary_agent_id="agent1",
            helper_agent_ids=["agent2"],
            max_rounds=3
        )
        
        # Check the result
        self.assertEqual(result["task"], "Test task")
        self.assertEqual(result["primary_agent"], "agent1")
        self.assertEqual(result["helper_agents"], ["agent2"])
        self.assertEqual(result["rounds"], 2)
        self.assertEqual(result["response"], "Final response")
        
        # Check that the primary agent's process_async method was called twice
        self.assertEqual(self.agent1.process_async.call_count, 2)
        
        # Check that gather was called once
        mock_gather.assert_called_once()
        
        # Try to coordinate a task with a non-existent primary agent
        with self.assertRaises(ValueError):
            await self.coordinator.coordinate_task_async(
                task="Test task",
                primary_agent_id="non_existent",
                helper_agent_ids=["agent2"]
            )
        
        # Try to coordinate a task with a non-existent helper agent
        with self.assertRaises(ValueError):
            await self.coordinator.coordinate_task_async(
                task="Test task",
                primary_agent_id="agent1",
                helper_agent_ids=["non_existent"]
            )


if __name__ == '__main__':
    unittest.main()
