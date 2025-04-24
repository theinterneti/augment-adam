"""Integration tests for the AI Agent module."""

import unittest
from unittest.mock import patch

from augment_adam.ai_agent import create_agent
from augment_adam.ai_agent.smc.potential import RegexPotential
from augment_adam.context_engine import get_context_manager
from augment_adam.context_engine.retrieval import MemoryRetriever
from augment_adam.context_engine.composition import ContextComposer
from augment_adam.context_engine.prompt import PromptComposer, PromptTemplates


class TestAgentIntegration(unittest.TestCase):
    """Integration tests for the AI Agent module."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize the context engine
        self.context_manager = get_context_manager()
        
        # Register a memory retriever
        self.context_manager.register_retriever(
            "memory",
            MemoryRetriever()
        )
        
        # Register a context composer
        self.context_manager.register_composer(
            "default",
            ContextComposer()
        )
        
        # Register a prompt composer
        prompt_templates = PromptTemplates()
        self.context_manager.register_prompt_composer(
            "default",
            PromptComposer(prompt_templates.get_all_templates())
        )
        
        # Create a potential for testing
        self.potential = RegexPotential(
            pattern=r".*",
            name="test_potential"
        )
    
    def test_conversational_agent(self):
        """Test the conversational agent."""
        # Create a conversational agent
        agent = create_agent(
            agent_type="conversational",
            name="Test Conversational Agent",
            description="A test conversational agent",
            potentials=[self.potential],
            num_particles=10
        )
        
        # Mock the SMC sampler to return a predictable result
        agent.smc_sampler.sample = lambda prompt, max_tokens: "Hello! How can I help you today?"
        
        # Process an input
        result = agent.process("Hello")
        
        # Check the result
        self.assertEqual(result["response"], "Hello! How can I help you today?")
        
        # Check that the conversation history was updated
        self.assertEqual(len(agent.conversation_history), 2)
        self.assertEqual(agent.conversation_history[0]["role"], "user")
        self.assertEqual(agent.conversation_history[0]["content"], "Hello")
        self.assertEqual(agent.conversation_history[1]["role"], "assistant")
        self.assertEqual(agent.conversation_history[1]["content"], "Hello! How can I help you today?")
    
    def test_task_agent(self):
        """Test the task agent."""
        # Create a task agent
        agent = create_agent(
            agent_type="task",
            name="Test Task Agent",
            description="A test task agent",
            potentials=[self.potential],
            num_particles=10
        )
        
        # Mock the SMC sampler to return a predictable result
        agent.smc_sampler.sample = lambda prompt, max_tokens: "I'll help you with that task."
        
        # Mock the planning engine to return a predictable result
        agent.planning_engine.create_plan = lambda task_description: {
            "description": task_description,
            "steps": [
                {
                    "step_number": 1,
                    "description": "Step 1",
                    "details": "Details for step 1",
                    "outcome": "Outcome for step 1"
                },
                {
                    "step_number": 2,
                    "description": "Step 2",
                    "details": "Details for step 2",
                    "outcome": "Outcome for step 2"
                }
            ],
            "estimated_time": "30 minutes"
        }
        
        # Process an input
        result = agent.process("Can you help me plan a birthday party?")
        
        # Check the result
        self.assertEqual(result["response"], "I'll help you with that task.")
        
        # Check that the task was created
        self.assertIsNotNone(agent.current_task)
        self.assertEqual(agent.current_task["description"], "Can you help me plan a birthday party?")
        self.assertEqual(agent.current_task["status"], "in_progress")
        self.assertEqual(agent.current_task["steps_completed"], 0)
        self.assertEqual(agent.current_task["steps_total"], 2)
    
    def test_research_agent(self):
        """Test the research agent."""
        # Create a research agent
        agent = create_agent(
            agent_type="research",
            name="Test Research Agent",
            description="A test research agent",
            potentials=[self.potential],
            num_particles=10
        )
        
        # Mock the SMC sampler to return a predictable result
        agent.smc_sampler.sample = lambda prompt, max_tokens: "Here's what I found about that topic."
        
        # Process an input
        result = agent.process("Tell me about artificial intelligence.")
        
        # Check the result
        self.assertEqual(result["response"], "Here's what I found about that topic.")
        
        # Check that the research topic was identified
        self.assertEqual(result["research_topic"], "technology")
    
    def test_creative_agent(self):
        """Test the creative agent."""
        # Create a creative agent
        agent = create_agent(
            agent_type="creative",
            name="Test Creative Agent",
            description="A test creative agent",
            potentials=[self.potential],
            num_particles=10
        )
        
        # Mock the SMC sampler to return a predictable result
        agent.smc_sampler.sample = lambda prompt, max_tokens: "Once upon a time, there was a creative AI..."
        
        # Process an input
        result = agent.process("Tell me a story.")
        
        # Check the result
        self.assertEqual(result["response"], "Once upon a time, there was a creative AI...")
        
        # Check that the creative mode was set
        self.assertEqual(result["creative_mode"], "storytelling")
    
    def test_coding_agent(self):
        """Test the coding agent."""
        # Create a coding agent
        agent = create_agent(
            agent_type="coding",
            name="Test Coding Agent",
            description="A test coding agent",
            potentials=[self.potential],
            num_particles=10
        )
        
        # Mock the SMC sampler to return a predictable result
        code_response = "```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```"
        agent.smc_sampler.sample = lambda prompt, max_tokens: code_response
        
        # Process an input
        result = agent.process("Write a Python function to calculate the Fibonacci sequence.")
        
        # Check the result
        self.assertEqual(result["response"], code_response)
        
        # Check that the language was detected
        self.assertEqual(result["language"], "python")
        
        # Check that the code task was identified
        self.assertEqual(result["code_task"], "implementation")
        
        # Check that the code blocks were extracted
        self.assertEqual(len(result["code_blocks"]), 1)
        self.assertEqual(result["code_blocks"][0], "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)")


if __name__ == '__main__':
    unittest.main()
