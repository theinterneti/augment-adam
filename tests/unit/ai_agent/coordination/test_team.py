"""Unit tests for the AgentTeam class."""

import unittest
from unittest.mock import MagicMock, patch
import asyncio
import pytest

from augment_adam.ai_agent.coordination.team import AgentTeam
from augment_adam.ai_agent.coordination.coordinator import AgentCoordinator


class TestAgentTeam(unittest.TestCase):
    """Tests for the AgentTeam class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock agents
        self.agent1 = MagicMock()
        self.agent1.name = "Agent 1"
        self.agent1.process.return_value = {"response": "Response from Agent 1"}

        self.agent2 = MagicMock()
        self.agent2.name = "Agent 2"
        self.agent2.process.return_value = {"response": "Response from Agent 2"}

        # Create mock coordinator
        self.coordinator = MagicMock(spec=AgentCoordinator)
        self.coordinator.get_agent.side_effect = lambda agent_id: {
            "agent1": self.agent1,
            "agent2": self.agent2
        }.get(agent_id)

        # Add registry attribute to mock coordinator
        self.coordinator.registry = MagicMock()

        # Create team with mock coordinator
        self.team = AgentTeam(
            name="Test Team",
            description="A test team",
            coordinator=self.coordinator,
            roles={
                "role1": "agent1",
                "role2": "agent2"
            },
            role_descriptions={
                "role1": "Role 1 description",
                "role2": "Role 2 description"
            }
        )

    def test_initialization(self):
        """Test team initialization."""
        self.assertEqual(self.team.name, "Test Team")
        self.assertEqual(self.team.description, "A test team")
        self.assertEqual(self.team.coordinator, self.coordinator)
        self.assertEqual(len(self.team.roles), 2)
        self.assertEqual(self.team.roles["role1"], "agent1")
        self.assertEqual(self.team.roles["role2"], "agent2")
        self.assertEqual(len(self.team.role_descriptions), 2)
        self.assertEqual(self.team.role_descriptions["role1"], "Role 1 description")
        self.assertEqual(self.team.role_descriptions["role2"], "Role 2 description")

    def test_add_role(self):
        """Test adding a role."""
        # Create a new mock agent
        agent3 = MagicMock()
        agent3.name = "Agent 3"

        # Add the role
        self.team.add_role(
            role_name="role3",
            agent_id="agent3",
            description="Role 3 description",
            agent=agent3
        )

        # Check that the role was added
        self.assertEqual(len(self.team.roles), 3)
        self.assertEqual(self.team.roles["role3"], "agent3")
        self.assertEqual(self.team.role_descriptions["role3"], "Role 3 description")

        # Check that the agent was registered with the coordinator
        self.coordinator.registry.register_agent.assert_called_once_with("agent3", agent3)

    def test_remove_role(self):
        """Test removing a role."""
        # Remove a role
        result = self.team.remove_role("role1")

        # Check that the role was removed
        self.assertTrue(result)
        self.assertEqual(len(self.team.roles), 1)
        self.assertNotIn("role1", self.team.roles)
        self.assertNotIn("role1", self.team.role_descriptions)

        # Try to remove a non-existent role
        result = self.team.remove_role("non_existent")

        # Check that the result is False
        self.assertFalse(result)

    def test_get_agent_for_role(self):
        """Test getting the agent for a role."""
        # Get the agent for a role
        agent = self.team.get_agent_for_role("role1")

        # Check that the correct agent was returned
        self.assertEqual(agent, self.agent1)

        # Check that the coordinator's get_agent method was called
        self.coordinator.get_agent.assert_called_with("agent1")

        # Try to get the agent for a non-existent role
        agent = self.team.get_agent_for_role("non_existent")

        # Check that None was returned
        self.assertIsNone(agent)

    def test_get_role_for_agent(self):
        """Test getting the role for an agent."""
        # Get the role for an agent
        role = self.team.get_role_for_agent("agent1")

        # Check that the correct role was returned
        self.assertEqual(role, "role1")

        # Try to get the role for a non-existent agent
        role = self.team.get_role_for_agent("non_existent")

        # Check that None was returned
        self.assertIsNone(role)

    def test_send_message_to_role(self):
        """Test sending a message from one role to another."""
        # Mock the coordinator's send_message method
        self.coordinator.send_message.return_value = {"id": "test_id"}

        # Send a message
        message = self.team.send_message_to_role(
            from_role="role1",
            to_role="role2",
            message="Test message",
            metadata={"key": "value"}
        )

        # Check that the coordinator's send_message method was called
        self.coordinator.send_message.assert_called_once_with(
            from_agent_id="agent1",
            to_agent_id="agent2",
            message="Test message",
            metadata={
                "key": "value",
                "from_role": "role1",
                "to_role": "role2",
                "team": "Test Team"
            }
        )

        # Check that the message was returned
        self.assertEqual(message["id"], "test_id")

        # Try to send a message from a non-existent role
        with self.assertRaises(ValueError):
            self.team.send_message_to_role(
                from_role="non_existent",
                to_role="role2",
                message="Test message"
            )

        # Try to send a message to a non-existent role
        with self.assertRaises(ValueError):
            self.team.send_message_to_role(
                from_role="role1",
                to_role="non_existent",
                message="Test message"
            )

    def test_process_message(self):
        """Test processing a message."""
        # Create a message
        message = {"id": "test_id"}

        # Mock the coordinator's process_message method
        self.coordinator.process_message.return_value = {"id": "response_id"}

        # Process the message
        response = self.team.process_message(message)

        # Check that the coordinator's process_message method was called
        self.coordinator.process_message.assert_called_once_with(message, None)

        # Check that the response was returned
        self.assertEqual(response["id"], "response_id")

    @pytest.mark.asyncio
    async def test_process_message_async(self):
        """Test processing a message asynchronously."""
        # Create a message
        message = {"id": "test_id"}

        # Mock the coordinator's process_message_async method
        self.coordinator.process_message_async = MagicMock()
        self.coordinator.process_message_async.return_value = {"id": "response_id"}

        # Process the message asynchronously
        response = await self.team.process_message_async(message)

        # Check that the coordinator's process_message_async method was called
        self.coordinator.process_message_async.assert_called_once_with(message, None)

        # Check that the response was returned
        self.assertEqual(response["id"], "response_id")

    def test_get_conversation_between_roles(self):
        """Test getting a conversation between two roles."""
        # Mock the coordinator's get_conversation method
        self.coordinator.get_conversation.return_value = [{"id": "1"}, {"id": "2"}]

        # Get the conversation
        conversation = self.team.get_conversation_between_roles("role1", "role2", limit=10)

        # Check that the coordinator's get_conversation method was called
        self.coordinator.get_conversation.assert_called_once_with("agent1", "agent2", 10)

        # Check that the conversation was returned
        self.assertEqual(len(conversation), 2)
        self.assertEqual(conversation[0]["id"], "1")
        self.assertEqual(conversation[1]["id"], "2")

        # Try to get a conversation with a non-existent role
        with self.assertRaises(ValueError):
            self.team.get_conversation_between_roles("non_existent", "role2")

        with self.assertRaises(ValueError):
            self.team.get_conversation_between_roles("role1", "non_existent")

    def test_get_role_messages(self):
        """Test getting messages involving a role."""
        # Mock the coordinator's get_agent_messages method
        self.coordinator.get_agent_messages.return_value = [{"id": "1"}, {"id": "2"}]

        # Get the messages
        messages = self.team.get_role_messages("role1", limit=10)

        # Check that the coordinator's get_agent_messages method was called
        self.coordinator.get_agent_messages.assert_called_once_with("agent1", 10)

        # Check that the messages were returned
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["id"], "1")
        self.assertEqual(messages[1]["id"], "2")

        # Try to get messages for a non-existent role
        with self.assertRaises(ValueError):
            self.team.get_role_messages("non_existent")

    def test_execute_workflow(self):
        """Test executing a workflow."""
        # Create a workflow
        workflow = [
            {
                "role": "role1",
                "action": "process",
                "input": "Input 1"
            },
            {
                "role": "role2",
                "action": "process",
                "input": "Input 2"
            }
        ]

        # Execute the workflow
        result = self.team.execute_workflow("Test task", workflow)

        # Check the result
        self.assertEqual(result["task"], "Test task")
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["role"], "role1")
        self.assertEqual(result["results"][0]["action"], "process")
        self.assertEqual(result["results"][0]["input"], "Input 1")
        self.assertEqual(result["results"][0]["output"], "Response from Agent 1")
        self.assertEqual(result["results"][1]["role"], "role2")
        self.assertEqual(result["results"][1]["action"], "process")
        self.assertEqual(result["results"][1]["input"], "Input 2")
        self.assertEqual(result["results"][1]["output"], "Response from Agent 2")

        # Check that the agents' process methods were called
        self.agent1.process.assert_called_once_with("Input 1")
        self.agent2.process.assert_called_once_with("Input 2")

        # Test a workflow with a send_message action
        workflow = [
            {
                "role": "role1",
                "action": "send_message",
                "recipient": "role2",
                "input": "Message from role1 to role2"
            }
        ]

        # Mock the send_message_to_role and process_message methods
        self.team.send_message_to_role = MagicMock(return_value={"id": "message_id"})
        self.team.process_message = MagicMock(return_value={"message": "Response to message"})

        # Execute the workflow
        result = self.team.execute_workflow("Test task", workflow)

        # Check the result
        self.assertEqual(result["task"], "Test task")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["role"], "role1")
        self.assertEqual(result["results"][0]["action"], "send_message")
        self.assertEqual(result["results"][0]["recipient"], "role2")
        self.assertEqual(result["results"][0]["input"], "Message from role1 to role2")
        self.assertEqual(result["results"][0]["output"], "Response to message")

        # Check that the send_message_to_role and process_message methods were called
        self.team.send_message_to_role.assert_called_once_with(
            from_role="role1",
            to_role="role2",
            message="Message from role1 to role2"
        )
        self.team.process_message.assert_called_once_with({"id": "message_id"})

        # Test a workflow with an unknown action
        workflow = [
            {
                "role": "role1",
                "action": "unknown",
                "input": "Input"
            }
        ]

        # Execute the workflow
        with self.assertRaises(ValueError):
            self.team.execute_workflow("Test task", workflow)

        # Test a workflow with a non-existent role
        workflow = [
            {
                "role": "non_existent",
                "action": "process",
                "input": "Input"
            }
        ]

        # Execute the workflow
        with self.assertRaises(ValueError):
            self.team.execute_workflow("Test task", workflow)

        # Test a workflow with a send_message action but no recipient
        workflow = [
            {
                "role": "role1",
                "action": "send_message",
                "input": "Message"
            }
        ]

        # Execute the workflow
        with self.assertRaises(ValueError):
            self.team.execute_workflow("Test task", workflow)

        # Test a workflow with a send_message action but a non-existent recipient
        workflow = [
            {
                "role": "role1",
                "action": "send_message",
                "recipient": "non_existent",
                "input": "Message"
            }
        ]

        # Execute the workflow
        with self.assertRaises(ValueError):
            self.team.execute_workflow("Test task", workflow)

    @pytest.mark.asyncio
    async def test_execute_workflow_async(self):
        """Test executing a workflow asynchronously."""
        # Create a workflow
        workflow = [
            {
                "role": "role1",
                "action": "process",
                "input": "Input 1"
            },
            {
                "role": "role2",
                "action": "process",
                "input": "Input 2"
            }
        ]

        # Mock the agents' process_async methods
        self.agent1.process_async = MagicMock()
        self.agent1.process_async.return_value = {"response": "Response from Agent 1"}

        self.agent2.process_async = MagicMock()
        self.agent2.process_async.return_value = {"response": "Response from Agent 2"}

        # Execute the workflow asynchronously
        result = await self.team.execute_workflow_async("Test task", workflow)

        # Check the result
        self.assertEqual(result["task"], "Test task")
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["role"], "role1")
        self.assertEqual(result["results"][0]["action"], "process")
        self.assertEqual(result["results"][0]["input"], "Input 1")
        self.assertEqual(result["results"][0]["output"], "Response from Agent 1")
        self.assertEqual(result["results"][1]["role"], "role2")
        self.assertEqual(result["results"][1]["action"], "process")
        self.assertEqual(result["results"][1]["input"], "Input 2")
        self.assertEqual(result["results"][1]["output"], "Response from Agent 2")

        # Check that the agents' process_async methods were called
        self.agent1.process_async.assert_called_once_with("Input 1")
        self.agent2.process_async.assert_called_once_with("Input 2")

        # Test a workflow with a send_message action
        workflow = [
            {
                "role": "role1",
                "action": "send_message",
                "recipient": "role2",
                "input": "Message from role1 to role2"
            }
        ]

        # Mock the send_message_to_role and process_message_async methods
        self.team.send_message_to_role = MagicMock(return_value={"id": "message_id"})
        self.team.process_message_async = MagicMock()
        self.team.process_message_async.return_value = {"message": "Response to message"}

        # Execute the workflow asynchronously
        result = await self.team.execute_workflow_async("Test task", workflow)

        # Check the result
        self.assertEqual(result["task"], "Test task")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["role"], "role1")
        self.assertEqual(result["results"][0]["action"], "send_message")
        self.assertEqual(result["results"][0]["recipient"], "role2")
        self.assertEqual(result["results"][0]["input"], "Message from role1 to role2")
        self.assertEqual(result["results"][0]["output"], "Response to message")

        # Check that the send_message_to_role and process_message_async methods were called
        self.team.send_message_to_role.assert_called_once_with(
            from_role="role1",
            to_role="role2",
            message="Message from role1 to role2"
        )
        self.team.process_message_async.assert_called_once_with({"id": "message_id"})

    def test_get_team_info(self):
        """Test getting team information."""
        # Mock the agents' get_info methods
        self.agent1.get_info = MagicMock(return_value={"name": "Agent 1"})
        self.agent2.get_info = MagicMock(return_value={"name": "Agent 2"})

        # Mock the coordinator's get_all_agents method
        self.coordinator.get_all_agents.return_value = {
            "agent1": self.agent1,
            "agent2": self.agent2
        }

        # Get team info
        info = self.team.get_team_info()

        # Check the info
        self.assertEqual(info["name"], "Test Team")
        self.assertEqual(info["description"], "A test team")
        self.assertEqual(len(info["roles"]), 2)
        self.assertEqual(info["roles"]["role1"]["agent_id"], "agent1")
        self.assertEqual(info["roles"]["role1"]["description"], "Role 1 description")
        self.assertEqual(info["roles"]["role2"]["agent_id"], "agent2")
        self.assertEqual(info["roles"]["role2"]["description"], "Role 2 description")
        self.assertEqual(len(info["agents"]), 2)
        self.assertEqual(info["agents"]["agent1"]["name"], "Agent 1")
        self.assertEqual(info["agents"]["agent2"]["name"], "Agent 2")

        # Check that the coordinator's get_all_agents method was called
        self.coordinator.get_all_agents.assert_called_once()

        # Check that the agents' get_info methods were called
        self.agent1.get_info.assert_called_once()
        self.agent2.get_info.assert_called_once()


if __name__ == '__main__':
    unittest.main()
