"""
Unit test for the TaskDistributor classes.

This module contains tests for the TaskDistributor classes, which are core components
of the agent coordination system.
"""

import unittest
from unittest.mock import patch, MagicMock

import pytest
from augment_adam.testing.utils.tag_utils import safe_tag, reset_tag_registry
from augment_adam.ai_agent.coordination.task import (
    Task, TaskStatus, TaskPriority, TaskDistributor,
    RoundRobinDistributor, CapabilityBasedDistributor, LoadBalancedDistributor
)
from augment_adam.ai_agent.coordination.registry import AgentRegistry, Agent, AgentCapability


@safe_tag("testing.unit.ai_agent.coordination.task_distributor")
class TestTaskDistributor(unittest.TestCase):
    """
    Tests for the TaskDistributor classes.
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
        self.agent1.name = "Agent 1"
        self.agent1.is_active = True
        self.agent1.load = 0.5
        self.agent1.has_capability.return_value = True
        
        self.agent2 = MagicMock(spec=Agent)
        self.agent2.id = "agent2"
        self.agent2.name = "Agent 2"
        self.agent2.is_active = True
        self.agent2.load = 0.2
        self.agent2.has_capability.return_value = True
        
        self.agent3 = MagicMock(spec=Agent)
        self.agent3.id = "agent3"
        self.agent3.name = "Agent 3"
        self.agent3.is_active = True
        self.agent3.load = 0.8
        self.agent3.has_capability.return_value = False
        
        # Set up the registry to return our mock agents
        self.registry.get_active_agents.return_value = [self.agent1, self.agent2, self.agent3]
        
        # Create distributors
        self.round_robin = RoundRobinDistributor(registry=self.registry)
        self.capability_based = CapabilityBasedDistributor(registry=self.registry)
        self.load_balanced = LoadBalancedDistributor(registry=self.registry)
        
        # Create a test task
        self.task = Task(
            name="test-task",
            description="A test task"
        )
        
        # Create a task with required capabilities
        self.capability_task = Task(
            name="capability-task",
            description="A task requiring capabilities"
        )
        self.capability_task.required_capabilities.add(AgentCapability.REASONING)
    
    def test_round_robin_distributor(self):
        """Test the RoundRobinDistributor."""
        # Distribute a task
        agent_id = self.round_robin.distribute(self.task)
        
        # Verify an agent was assigned
        self.assertIsNotNone(agent_id)
        self.assertIn(agent_id, ["agent1", "agent2", "agent3"])
        
        # Distribute another task
        agent_id2 = self.round_robin.distribute(self.task)
        
        # Verify a different agent was assigned
        self.assertIsNotNone(agent_id2)
        self.assertIn(agent_id2, ["agent1", "agent2", "agent3"])
        self.assertNotEqual(agent_id, agent_id2)
        
        # Distribute a third task
        agent_id3 = self.round_robin.distribute(self.task)
        
        # Verify the third agent was assigned
        self.assertIsNotNone(agent_id3)
        self.assertIn(agent_id3, ["agent1", "agent2", "agent3"])
        self.assertNotEqual(agent_id, agent_id3)
        self.assertNotEqual(agent_id2, agent_id3)
        
        # Distribute a fourth task (should wrap around)
        agent_id4 = self.round_robin.distribute(self.task)
        
        # Verify we wrapped around to the first agent
        self.assertEqual(agent_id4, agent_id)
        
        # Test with no active agents
        self.registry.get_active_agents.return_value = []
        
        # Distribute a task
        agent_id = self.round_robin.distribute(self.task)
        
        # Verify no agent was assigned
        self.assertIsNone(agent_id)
    
    def test_capability_based_distributor(self):
        """Test the CapabilityBasedDistributor."""
        # Distribute a task with no required capabilities
        agent_id = self.capability_based.distribute(self.task)
        
        # Verify an agent was assigned
        self.assertIsNotNone(agent_id)
        self.assertIn(agent_id, ["agent1", "agent2", "agent3"])
        
        # Distribute a task with required capabilities
        agent_id = self.capability_based.distribute(self.capability_task)
        
        # Verify an agent with the required capabilities was assigned
        self.assertIsNotNone(agent_id)
        self.assertIn(agent_id, ["agent1", "agent2"])
        self.assertNotEqual(agent_id, "agent3")  # agent3 doesn't have the required capability
        
        # Test with no agents having the required capabilities
        self.agent1.has_capability.return_value = False
        self.agent2.has_capability.return_value = False
        
        # Distribute a task
        agent_id = self.capability_based.distribute(self.capability_task)
        
        # Verify no agent was assigned
        self.assertIsNone(agent_id)
        
        # Test with no active agents
        self.registry.get_active_agents.return_value = []
        
        # Distribute a task
        agent_id = self.capability_based.distribute(self.task)
        
        # Verify no agent was assigned
        self.assertIsNone(agent_id)
    
    def test_load_balanced_distributor(self):
        """Test the LoadBalancedDistributor."""
        # Distribute a task
        agent_id = self.load_balanced.distribute(self.task)
        
        # Verify the agent with the lowest load was assigned
        self.assertEqual(agent_id, "agent2")  # agent2 has the lowest load (0.2)
        
        # Increase agent2's load
        self.agent2.load = 0.9
        
        # Distribute another task
        agent_id = self.load_balanced.distribute(self.task)
        
        # Verify the agent with the lowest load was assigned
        self.assertEqual(agent_id, "agent1")  # agent1 now has the lowest load (0.5)
        
        # Distribute a task with required capabilities
        agent_id = self.load_balanced.distribute(self.capability_task)
        
        # Verify an agent with the required capabilities was assigned
        self.assertIsNotNone(agent_id)
        self.assertIn(agent_id, ["agent1", "agent2"])
        self.assertNotEqual(agent_id, "agent3")  # agent3 doesn't have the required capability
        
        # Test with no agents having the required capabilities
        self.agent1.has_capability.return_value = False
        self.agent2.has_capability.return_value = False
        
        # Distribute a task
        agent_id = self.load_balanced.distribute(self.capability_task)
        
        # Verify no agent was assigned
        self.assertIsNone(agent_id)
        
        # Test with no active agents
        self.registry.get_active_agents.return_value = []
        
        # Distribute a task
        agent_id = self.load_balanced.distribute(self.task)
        
        # Verify no agent was assigned
        self.assertIsNone(agent_id)
    
    def test_custom_distributor(self):
        """Test creating a custom TaskDistributor."""
        # Create a custom distributor
        class CustomDistributor(TaskDistributor):
            def distribute(self, task):
                # Always assign to agent1
                return "agent1"
        
        # Create an instance of the custom distributor
        custom = CustomDistributor(name="custom-distributor", registry=self.registry)
        
        # Verify the distributor was initialized correctly
        self.assertEqual(custom.name, "custom-distributor")
        self.assertEqual(custom.registry, self.registry)
        
        # Distribute a task
        agent_id = custom.distribute(self.task)
        
        # Verify the task was assigned to agent1
        self.assertEqual(agent_id, "agent1")
    
if __name__ == "__main__":
    unittest.main()
