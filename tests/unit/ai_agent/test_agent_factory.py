"""Unit tests for the AgentFactory class."""

import unittest
from unittest.mock import patch

from augment_adam.ai_agent.agent_factory import (
    AgentFactory, create_agent, get_agent_factory, get_default_agent
)
from augment_adam.ai_agent.base_agent import BaseAgent
from augment_adam.ai_agent.types.conversational_agent import ConversationalAgent
from augment_adam.ai_agent.types.task_agent import TaskAgent
from augment_adam.ai_agent.types.research_agent import ResearchAgent
from augment_adam.ai_agent.types.creative_agent import CreativeAgent
from augment_adam.ai_agent.types.coding_agent import CodingAgent
from augment_adam.core.errors import ValidationError


class TestAgentFactory(unittest.TestCase):
    """Tests for the AgentFactory class."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = AgentFactory()
    
    def test_initialization(self):
        """Test factory initialization."""
        self.assertIn("base", self.factory.agent_types)
        self.assertIn("conversational", self.factory.agent_types)
        self.assertIn("task", self.factory.agent_types)
        self.assertIn("research", self.factory.agent_types)
        self.assertIn("creative", self.factory.agent_types)
        self.assertIn("coding", self.factory.agent_types)
    
    def test_create_base_agent(self):
        """Test creating a base agent."""
        agent = self.factory.create_agent(
            agent_type="base",
            name="Test Agent",
            description="A test agent"
        )
        
        self.assertIsInstance(agent, BaseAgent)
        self.assertEqual(agent.name, "Test Agent")
        self.assertEqual(agent.description, "A test agent")
    
    def test_create_conversational_agent(self):
        """Test creating a conversational agent."""
        agent = self.factory.create_agent(
            agent_type="conversational",
            name="Test Conversational Agent",
            description="A test conversational agent"
        )
        
        self.assertIsInstance(agent, ConversationalAgent)
        self.assertEqual(agent.name, "Test Conversational Agent")
        self.assertEqual(agent.description, "A test conversational agent")
    
    def test_create_task_agent(self):
        """Test creating a task agent."""
        agent = self.factory.create_agent(
            agent_type="task",
            name="Test Task Agent",
            description="A test task agent"
        )
        
        self.assertIsInstance(agent, TaskAgent)
        self.assertEqual(agent.name, "Test Task Agent")
        self.assertEqual(agent.description, "A test task agent")
    
    def test_create_research_agent(self):
        """Test creating a research agent."""
        agent = self.factory.create_agent(
            agent_type="research",
            name="Test Research Agent",
            description="A test research agent"
        )
        
        self.assertIsInstance(agent, ResearchAgent)
        self.assertEqual(agent.name, "Test Research Agent")
        self.assertEqual(agent.description, "A test research agent")
    
    def test_create_creative_agent(self):
        """Test creating a creative agent."""
        agent = self.factory.create_agent(
            agent_type="creative",
            name="Test Creative Agent",
            description="A test creative agent"
        )
        
        self.assertIsInstance(agent, CreativeAgent)
        self.assertEqual(agent.name, "Test Creative Agent")
        self.assertEqual(agent.description, "A test creative agent")
    
    def test_create_coding_agent(self):
        """Test creating a coding agent."""
        agent = self.factory.create_agent(
            agent_type="coding",
            name="Test Coding Agent",
            description="A test coding agent"
        )
        
        self.assertIsInstance(agent, CodingAgent)
        self.assertEqual(agent.name, "Test Coding Agent")
        self.assertEqual(agent.description, "A test coding agent")
    
    def test_create_agent_with_default_name(self):
        """Test creating an agent with a default name."""
        agent = self.factory.create_agent(agent_type="base")
        
        self.assertEqual(agent.name, "Base Agent")
    
    def test_create_agent_with_default_description(self):
        """Test creating an agent with a default description."""
        agent = self.factory.create_agent(agent_type="base")
        
        self.assertEqual(agent.description, "A base AI agent")
    
    def test_create_agent_with_invalid_type(self):
        """Test creating an agent with an invalid type."""
        with self.assertRaises(ValidationError):
            self.factory.create_agent(agent_type="invalid")
    
    def test_create_agent_function(self):
        """Test the create_agent function."""
        with patch('augment_adam.ai_agent.agent_factory.get_agent_factory') as mock_get_factory:
            mock_factory = MagicMock()
            mock_get_factory.return_value = mock_factory
            
            create_agent(
                agent_type="base",
                name="Test Agent",
                description="A test agent"
            )
            
            mock_factory.create_agent.assert_called_once_with(
                agent_type="base",
                name="Test Agent",
                description="A test agent",
                memory_type=None,
                context_window_size=4096,
                potentials=None,
                num_particles=100
            )
    
    def test_get_agent_factory(self):
        """Test the get_agent_factory function."""
        factory1 = get_agent_factory()
        factory2 = get_agent_factory()
        
        self.assertIs(factory1, factory2)
    
    def test_get_default_agent(self):
        """Test the get_default_agent function."""
        with patch('augment_adam.ai_agent.agent_factory.create_agent') as mock_create_agent:
            mock_agent = MagicMock()
            mock_create_agent.return_value = mock_agent
            
            # Reset the default agent
            import augment_adam.ai_agent.agent_factory
            augment_adam.ai_agent.agent_factory._default_agent = None
            
            agent1 = get_default_agent()
            agent2 = get_default_agent()
            
            self.assertIs(agent1, agent2)
            mock_create_agent.assert_called_once_with(
                agent_type="conversational",
                name="Default Agent",
                description="The default AI agent"
            )


if __name__ == '__main__':
    unittest.main()
