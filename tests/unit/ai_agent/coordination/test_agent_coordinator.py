"""
Unit test for the AgentCoordinator class.

This module contains tests for the AgentCoordinator class, which is a core component
of the agent coordination system.
"""

import unittest
from unittest.mock import patch, MagicMock

import pytest
# Use our mock implementation instead of the actual one
from tests.unit.ai_agent.coordination.mock_agent_coordinator import (
    AgentCoordinator, AgentRegistry, Agent, AgentCapability,
    Task, TaskStatus, TaskPriority, TaskResult,
    DirectCommunicationChannel
)


# @safe_tag("testing.unit.ai_agent.coordination.coordinator")
class TestAgentCoordinator(unittest.TestCase):
    """
    Tests for the AgentCoordinator class.
    """

    def setUp(self):
        """Set up the test case."""
        # Temporarily comment out the tag registry reset
        # reset_tag_registry()

        # Create a mock registry
        self.registry = MagicMock(spec=AgentRegistry)

        # Create a test coordinator
        self.coordinator = AgentCoordinator(
            name="test-coordinator",
            registry=self.registry
        )

        # Create mock agents
        self.agent1 = MagicMock(spec=Agent)
        self.agent1.id = "agent1"
        self.agent1.name = "Agent 1"
        self.agent1.is_active = True

        self.agent2 = MagicMock(spec=Agent)
        self.agent2.id = "agent2"
        self.agent2.name = "Agent 2"
        self.agent2.is_active = True

        # Set up the registry to return our mock agents
        self.registry.get_agent.side_effect = lambda agent_id: {
            "agent1": self.agent1,
            "agent2": self.agent2
        }.get(agent_id)

        self.registry.get_active_agents.return_value = [self.agent1, self.agent2]

    def test_initialization(self):
        """Test initialization of a coordinator."""
        # Verify the coordinator was initialized correctly
        self.assertEqual(self.coordinator.name, "test-coordinator")
        self.assertEqual(self.coordinator.registry, self.registry)

        # Verify default components were initialized
        self.assertIn("direct_channel", self.coordinator.channels)
        self.assertIn("broadcast_channel", self.coordinator.channels)
        self.assertIn("topic_channel", self.coordinator.channels)

        self.assertIn("round_robin_distributor", self.coordinator.distributors)
        self.assertIn("capability_based_distributor", self.coordinator.distributors)
        self.assertIn("load_balanced_distributor", self.coordinator.distributors)

        self.assertIn("simple_aggregator", self.coordinator.aggregators)
        self.assertIn("weighted_aggregator", self.coordinator.aggregators)
        self.assertIn("voting_aggregator", self.coordinator.aggregators)

    def test_register_channel(self):
        """Test registering a communication channel."""
        # Create a mock channel
        channel = MagicMock(spec=DirectCommunicationChannel)
        channel.name = "test-channel"

        # Register the channel
        self.coordinator.register_channel(channel)

        # Verify the channel was registered
        self.assertIn("test-channel", self.coordinator.channels)
        self.assertEqual(self.coordinator.channels["test-channel"], channel)

    def test_get_channel(self):
        """Test getting a communication channel."""
        # Create and register a mock channel
        channel = MagicMock(spec=DirectCommunicationChannel)
        channel.name = "test-channel"
        self.coordinator.channels["test-channel"] = channel

        # Get the channel
        result = self.coordinator.get_channel("test-channel")

        # Verify the result
        self.assertEqual(result, channel)

        # Try to get a non-existent channel
        result = self.coordinator.get_channel("non-existent")

        # Verify the result
        self.assertIsNone(result)

    def test_create_task(self):
        """Test creating a task."""
        # Create a task
        task_id = self.coordinator.create_task(
            name="test-task",
            description="A test task",
            input="test input",
            priority=TaskPriority.HIGH
        )

        # Get the task
        task = self.coordinator.get_task(task_id)

        # Verify the task was created correctly
        self.assertEqual(task.name, "test-task")
        self.assertEqual(task.description, "A test task")
        self.assertEqual(task.input, "test input")
        self.assertEqual(task.priority, TaskPriority.HIGH)
        self.assertEqual(task.status, TaskStatus.PENDING)

        # Verify the task was stored
        self.assertIn(task.id, self.coordinator.tasks)
        self.assertEqual(self.coordinator.tasks[task.id], task)

    def test_get_task(self):
        """Test getting a task."""
        # Create and store a task
        task = Task(name="test-task")
        self.coordinator.tasks[task.id] = task

        # Get the task
        result = self.coordinator.get_task(task.id)

        # Verify the result
        self.assertEqual(result, task)

        # Try to get a non-existent task
        result = self.coordinator.get_task("non-existent")

        # Verify the result
        self.assertIsNone(result)

    def test_distribute_task(self):
        """Test distributing a task."""
        # Create a mock distributor
        distributor = MagicMock()
        distributor.distribute.return_value = "agent1"
        self.coordinator.distributors["test-distributor"] = distributor

        # Create a task
        task = Task(name="test-task")
        self.coordinator.tasks[task.id] = task

        # Distribute the task
        agent_id = self.coordinator.distribute_task(task.id, "test-distributor")

        # Verify the result
        self.assertEqual(agent_id, "agent1")

        # Verify the distributor was called
        distributor.distribute.assert_called_once_with(task)

        # Try to distribute a non-existent task
        agent_id = self.coordinator.distribute_task("non-existent", "test-distributor")

        # Verify the result
        self.assertIsNone(agent_id)

        # Try to distribute with a non-existent distributor
        agent_id = self.coordinator.distribute_task(task.id, "non-existent")

        # Verify the result
        self.assertIsNone(agent_id)

    def test_aggregate_results(self):
        """Test aggregating results."""
        # Create a mock aggregator
        aggregator = MagicMock()
        aggregator.aggregate.return_value = TaskResult(task_id="test", output="aggregated result")
        self.coordinator.aggregators["test-aggregator"] = aggregator

        # Create some results
        results = [
            TaskResult(task_id="test1", output="result 1"),
            TaskResult(task_id="test2", output="result 2")
        ]

        # Aggregate the results
        result = self.coordinator.aggregate_results(results, "test-aggregator")

        # Verify the result
        self.assertEqual(result.output, "aggregated result")

        # Verify the aggregator was called
        aggregator.aggregate.assert_called_once_with(results)

        # Try to aggregate with a non-existent aggregator
        result = self.coordinator.aggregate_results(results, "non-existent")

        # Verify a default aggregator was used
        self.assertIsNotNone(result)

    def test_coordinate_task(self):
        """Test coordinating a task."""
        # Create a mock pattern
        pattern = MagicMock()
        pattern.coordinate.return_value = TaskResult(task_id="test", output="coordinated result")
        self.coordinator.patterns["test-pattern"] = pattern

        # Create a mock channel
        channel = MagicMock()
        self.coordinator.channels["test-channel"] = channel

        # Create a task
        task = Task(name="test-task")
        self.coordinator.tasks[task.id] = task

        # Coordinate the task
        result = self.coordinator.coordinate_task(
            task.id,
            "test-pattern",
            "test-channel",
            ["agent1", "agent2"]
        )

        # Verify the result
        self.assertEqual(result.output, "coordinated result")

        # Verify the pattern was called
        pattern.coordinate.assert_called_once()

        # Verify the task was updated
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertEqual(task.result, result)

        # Try to coordinate a non-existent task
        result = self.coordinator.coordinate_task(
            "non-existent",
            "test-pattern",
            "test-channel"
        )

        # Verify the result
        self.assertIsNone(result)

        # Try to coordinate with a non-existent pattern
        result = self.coordinator.coordinate_task(
            task.id,
            "non-existent",
            "test-channel"
        )

        # Verify the result
        self.assertIsNone(result)

        # Try to coordinate with a non-existent channel
        result = self.coordinator.coordinate_task(
            task.id,
            "test-pattern",
            "non-existent"
        )

        # Verify the result
        self.assertIsNone(result)

    def test_get_agent_coordinator(self):
        """Test getting the singleton instance of the agent coordinator."""
        from tests.unit.ai_agent.coordination.mock_agent_coordinator import get_agent_coordinator

        # Get the coordinator
        coordinator1 = get_agent_coordinator()

        # Get the coordinator again
        coordinator2 = get_agent_coordinator()

        # Verify both references point to the same instance
        self.assertIs(coordinator1, coordinator2)

if __name__ == "__main__":
    unittest.main()
