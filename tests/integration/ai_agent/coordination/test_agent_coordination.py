"""
Integration test for the agent coordination system.

This module contains integration tests for the agent coordination system,
verifying that the different components work together correctly.
"""

import unittest
import time
from unittest.mock import patch, MagicMock

import pytest
from augment_adam.testing.utils.tag_utils import safe_tag, reset_tag_registry
from augment_adam.ai_agent.coordination.registry import (
    AgentRegistry, Agent, AgentCapability, get_agent_registry
)
from augment_adam.ai_agent.coordination.communication import (
    AgentMessage, MessageType, MessagePriority,
    DirectCommunicationChannel, BroadcastCommunicationChannel
)
from augment_adam.ai_agent.coordination.task import (
    Task, TaskStatus, TaskPriority, TaskResult,
    RoundRobinDistributor, CapabilityBasedDistributor
)
from augment_adam.ai_agent.coordination.aggregation import (
    SimpleAggregator, WeightedAggregator
)
from augment_adam.ai_agent.coordination.coordinator import (
    AgentCoordinator, get_agent_coordinator
)


class MockAgent(Agent):
    """Mock agent for testing."""
    
    def __init__(self, id, name, capabilities=None):
        """Initialize the mock agent."""
        super().__init__(id=id, name=name)
        self.capabilities = capabilities or set()
        self.is_active = True
        self.load = 0.0
        self.processed_tasks = []
        self.received_messages = []
    
    def has_capability(self, capability):
        """Check if the agent has a capability."""
        return capability in self.capabilities
    
    def process_task(self, task):
        """Process a task."""
        self.processed_tasks.append(task)
        return TaskResult(
            task_id=task.id,
            agent_id=self.id,
            output=f"Result from {self.name} for task {task.name}",
            status=TaskStatus.COMPLETED
        )
    
    def receive_message(self, message):
        """Receive a message."""
        self.received_messages.append(message)
        return AgentMessage(
            sender_id=self.id,
            recipient_id=message.sender_id,
            content=f"Response from {self.name} to message: {message.content}",
            message_type=MessageType.RESPONSE,
            in_reply_to=message.id
        )


@safe_tag("testing.integration.ai_agent.coordination")
class TestAgentCoordination(unittest.TestCase):
    """
    Integration tests for the agent coordination system.
    """
    
    def setUp(self):
        """Set up the test case."""
        # Reset the tag registry to avoid conflicts
        reset_tag_registry()
        
        # Create a registry
        self.registry = AgentRegistry()
        
        # Create agents
        self.agent1 = MockAgent(
            id="agent1",
            name="Agent 1",
            capabilities={AgentCapability.REASONING, AgentCapability.PLANNING}
        )
        
        self.agent2 = MockAgent(
            id="agent2",
            name="Agent 2",
            capabilities={AgentCapability.TEXT_GENERATION, AgentCapability.SUMMARIZATION}
        )
        
        self.agent3 = MockAgent(
            id="agent3",
            name="Agent 3",
            capabilities={AgentCapability.REASONING, AgentCapability.TEXT_GENERATION}
        )
        
        # Register the agents
        self.registry.register_agent(self.agent1)
        self.registry.register_agent(self.agent2)
        self.registry.register_agent(self.agent3)
        
        # Create communication channels
        self.direct_channel = DirectCommunicationChannel()
        self.broadcast_channel = BroadcastCommunicationChannel(registry=self.registry)
        
        # Create distributors
        self.round_robin = RoundRobinDistributor(registry=self.registry)
        self.capability_based = CapabilityBasedDistributor(registry=self.registry)
        
        # Create aggregators
        self.simple_aggregator = SimpleAggregator()
        self.weighted_aggregator = WeightedAggregator(
            weights={"agent1": 0.5, "agent2": 0.3, "agent3": 0.2}
        )
        
        # Create a coordinator
        self.coordinator = AgentCoordinator(
            name="test-coordinator",
            registry=self.registry
        )
        
        # Register components with the coordinator
        self.coordinator.register_channel(self.direct_channel)
        self.coordinator.register_channel(self.broadcast_channel)
        self.coordinator.register_distributor(self.round_robin)
        self.coordinator.register_distributor(self.capability_based)
        self.coordinator.register_aggregator(self.simple_aggregator)
        self.coordinator.register_aggregator(self.weighted_aggregator)
    
    def test_task_distribution_and_execution(self):
        """Test distributing and executing a task."""
        # Create a task
        task = Task(
            name="test-task",
            description="A test task",
            input="Test input",
            required_capabilities={AgentCapability.REASONING}
        )
        
        # Add the task to the coordinator
        task_id = self.coordinator.add_task(task)
        
        # Distribute the task using capability-based distribution
        agent_id = self.coordinator.distribute_task(task_id, "capability_based_distributor")
        
        # Verify the task was assigned to an agent with the required capability
        self.assertIn(agent_id, ["agent1", "agent3"])
        
        # Get the assigned agent
        agent = self.registry.get_agent(agent_id)
        
        # Execute the task
        result = agent.process_task(task)
        
        # Update the task with the result
        task.complete(result)
        
        # Verify the task was completed
        self.assertTrue(task.is_completed())
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertEqual(task.result, result)
        self.assertIn(f"Result from {agent.name}", task.result.output)
    
    def test_multi_agent_task_execution(self):
        """Test executing a task with multiple agents."""
        # Create a task
        task = Task(
            name="multi-agent-task",
            description="A task for multiple agents",
            input="Test input"
        )
        
        # Add the task to the coordinator
        task_id = self.coordinator.add_task(task)
        
        # Execute the task with all agents
        results = []
        for agent in self.registry.get_active_agents():
            result = agent.process_task(task)
            results.append(result)
        
        # Aggregate the results
        aggregated_result = self.simple_aggregator.aggregate(results)
        
        # Update the task with the aggregated result
        task.complete(aggregated_result)
        
        # Verify the task was completed
        self.assertTrue(task.is_completed())
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertEqual(task.result, aggregated_result)
        
        # Verify the aggregated result contains output from all agents
        for agent in self.registry.get_active_agents():
            self.assertIn(agent.name, task.result.output)
    
    def test_agent_communication(self):
        """Test communication between agents."""
        # Create a message
        message = AgentMessage(
            sender_id="agent1",
            recipient_id="agent2",
            content="Hello, Agent 2!",
            message_type=MessageType.NOTIFICATION
        )
        
        # Send the message
        self.direct_channel.send_message(message)
        
        # Receive the message
        received_message = self.direct_channel.receive_message("agent2")
        
        # Verify the message was received
        self.assertEqual(received_message.content, "Hello, Agent 2!")
        self.assertEqual(received_message.sender_id, "agent1")
        
        # Process the message
        agent2 = self.registry.get_agent("agent2")
        response = agent2.receive_message(received_message)
        
        # Send the response
        self.direct_channel.send_message(response)
        
        # Receive the response
        received_response = self.direct_channel.receive_message("agent1")
        
        # Verify the response was received
        self.assertEqual(received_response.content, "Response from Agent 2 to message: Hello, Agent 2!")
        self.assertEqual(received_response.sender_id, "agent2")
        self.assertEqual(received_response.in_reply_to, message.id)
    
    def test_broadcast_communication(self):
        """Test broadcast communication."""
        # Create a broadcast message
        message = AgentMessage(
            sender_id="agent1",
            recipient_id=None,
            content="Broadcast message",
            message_type=MessageType.BROADCAST
        )
        
        # Send the broadcast message
        self.broadcast_channel.send_message(message)
        
        # Receive the message by other agents
        received_by_agent2 = self.broadcast_channel.receive_message("agent2")
        received_by_agent3 = self.broadcast_channel.receive_message("agent3")
        
        # Verify the message was received by other agents
        self.assertEqual(received_by_agent2.content, "Broadcast message")
        self.assertEqual(received_by_agent3.content, "Broadcast message")
        
        # Verify the sender didn't receive the message
        received_by_agent1 = self.broadcast_channel.receive_message("agent1")
        self.assertIsNone(received_by_agent1)
    
    def test_coordinator_task_workflow(self):
        """Test a complete task workflow using the coordinator."""
        # Create a task
        task_id = self.coordinator.create_task(
            name="workflow-task",
            description="A task for testing the workflow",
            input="Test input",
            required_capabilities={AgentCapability.TEXT_GENERATION}
        )
        
        # Get the task
        task = self.coordinator.get_task(task_id)
        
        # Verify the task was created
        self.assertEqual(task.name, "workflow-task")
        self.assertEqual(task.status, TaskStatus.PENDING)
        
        # Distribute the task
        agent_id = self.coordinator.distribute_task(task_id, "capability_based_distributor")
        
        # Verify the task was assigned to an agent with the required capability
        self.assertIn(agent_id, ["agent2", "agent3"])
        
        # Get the assigned agent
        agent = self.registry.get_agent(agent_id)
        
        # Execute the task
        result = agent.process_task(task)
        
        # Update the task with the result
        self.coordinator.update_task_result(task_id, result)
        
        # Get the updated task
        updated_task = self.coordinator.get_task(task_id)
        
        # Verify the task was completed
        self.assertTrue(updated_task.is_completed())
        self.assertEqual(updated_task.status, TaskStatus.COMPLETED)
        self.assertEqual(updated_task.result, result)
    
    def test_coordinator_multi_agent_workflow(self):
        """Test a multi-agent workflow using the coordinator."""
        # Create a task
        task_id = self.coordinator.create_task(
            name="multi-agent-workflow",
            description="A task for testing multi-agent workflow",
            input="Test input"
        )
        
        # Get the task
        task = self.coordinator.get_task(task_id)
        
        # Create subtasks
        subtask1_id = self.coordinator.create_subtask(
            parent_task_id=task_id,
            name="subtask1",
            description="First subtask",
            input="Subtask 1 input",
            required_capabilities={AgentCapability.REASONING}
        )
        
        subtask2_id = self.coordinator.create_subtask(
            parent_task_id=task_id,
            name="subtask2",
            description="Second subtask",
            input="Subtask 2 input",
            required_capabilities={AgentCapability.TEXT_GENERATION}
        )
        
        # Distribute the subtasks
        agent1_id = self.coordinator.distribute_task(subtask1_id, "capability_based_distributor")
        agent2_id = self.coordinator.distribute_task(subtask2_id, "capability_based_distributor")
        
        # Get the assigned agents
        agent1 = self.registry.get_agent(agent1_id)
        agent2 = self.registry.get_agent(agent2_id)
        
        # Get the subtasks
        subtask1 = self.coordinator.get_task(subtask1_id)
        subtask2 = self.coordinator.get_task(subtask2_id)
        
        # Execute the subtasks
        result1 = agent1.process_task(subtask1)
        result2 = agent2.process_task(subtask2)
        
        # Update the subtasks with the results
        self.coordinator.update_task_result(subtask1_id, result1)
        self.coordinator.update_task_result(subtask2_id, result2)
        
        # Aggregate the results
        results = [result1, result2]
        aggregated_result = self.weighted_aggregator.aggregate(results)
        
        # Update the parent task with the aggregated result
        self.coordinator.update_task_result(task_id, aggregated_result)
        
        # Get the updated tasks
        updated_task = self.coordinator.get_task(task_id)
        updated_subtask1 = self.coordinator.get_task(subtask1_id)
        updated_subtask2 = self.coordinator.get_task(subtask2_id)
        
        # Verify the tasks were completed
        self.assertTrue(updated_subtask1.is_completed())
        self.assertTrue(updated_subtask2.is_completed())
        self.assertTrue(updated_task.is_completed())
        
        # Verify the parent task has the aggregated result
        self.assertEqual(updated_task.result, aggregated_result)
    
if __name__ == "__main__":
    unittest.main()
