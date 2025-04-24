"""Compatibility tests for the agent coordination framework with different model providers."""

import unittest
import os
import sys
import importlib
from unittest.mock import MagicMock, patch
import logging

from augment_adam.ai_agent.coordination import AgentCoordinator, AgentTeam, Workflow, WorkflowStep
from augment_adam.models.model_interface import ModelInterface


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MockHuggingFaceModel(ModelInterface):
    """Mock HuggingFace model for compatibility testing."""
    
    def __init__(self, model_name="mock-hf-model"):
        """Initialize the mock HuggingFace model."""
        self.model_name = model_name
        self.provider = "huggingface"
        logger.info(f"Initialized Mock HuggingFace Model: {model_name}")
    
    def generate(self, prompt, **kwargs):
        """Generate text based on a prompt."""
        return f"[HuggingFace] Response to: {prompt[:50]}..."
    
    def get_token_count(self, text):
        """Get the number of tokens in a text."""
        return len(text.split())
    
    def get_embedding(self, text):
        """Get the embedding for a text."""
        return [0.1] * 10
    
    def get_model_info(self):
        """Get information about the model."""
        return {
            "name": self.model_name,
            "provider": self.provider,
            "type": "text",
            "max_tokens": 1024,
            "embedding_dimensions": 10
        }


class MockOllamaModel(ModelInterface):
    """Mock Ollama model for compatibility testing."""
    
    def __init__(self, model_name="mock-ollama-model"):
        """Initialize the mock Ollama model."""
        self.model_name = model_name
        self.provider = "ollama"
        logger.info(f"Initialized Mock Ollama Model: {model_name}")
    
    def generate(self, prompt, **kwargs):
        """Generate text based on a prompt."""
        return f"[Ollama] Response to: {prompt[:50]}..."
    
    def get_token_count(self, text):
        """Get the number of tokens in a text."""
        return len(text.split())
    
    def get_embedding(self, text):
        """Get the embedding for a text."""
        return [0.1] * 10
    
    def get_model_info(self):
        """Get information about the model."""
        return {
            "name": self.model_name,
            "provider": self.provider,
            "type": "text",
            "max_tokens": 1024,
            "embedding_dimensions": 10
        }


class MockOpenAIModel(ModelInterface):
    """Mock OpenAI model for compatibility testing."""
    
    def __init__(self, model_name="mock-openai-model"):
        """Initialize the mock OpenAI model."""
        self.model_name = model_name
        self.provider = "openai"
        logger.info(f"Initialized Mock OpenAI Model: {model_name}")
    
    def generate(self, prompt, **kwargs):
        """Generate text based on a prompt."""
        return f"[OpenAI] Response to: {prompt[:50]}..."
    
    def get_token_count(self, text):
        """Get the number of tokens in a text."""
        return len(text.split())
    
    def get_embedding(self, text):
        """Get the embedding for a text."""
        return [0.1] * 10
    
    def get_model_info(self):
        """Get information about the model."""
        return {
            "name": self.model_name,
            "provider": self.provider,
            "type": "text",
            "max_tokens": 1024,
            "embedding_dimensions": 10
        }


class MockAnthropicModel(ModelInterface):
    """Mock Anthropic model for compatibility testing."""
    
    def __init__(self, model_name="mock-anthropic-model"):
        """Initialize the mock Anthropic model."""
        self.model_name = model_name
        self.provider = "anthropic"
        logger.info(f"Initialized Mock Anthropic Model: {model_name}")
    
    def generate(self, prompt, **kwargs):
        """Generate text based on a prompt."""
        return f"[Anthropic] Response to: {prompt[:50]}..."
    
    def get_token_count(self, text):
        """Get the number of tokens in a text."""
        return len(text.split())
    
    def get_embedding(self, text):
        """Get the embedding for a text."""
        return [0.1] * 10
    
    def get_model_info(self):
        """Get information about the model."""
        return {
            "name": self.model_name,
            "provider": self.provider,
            "type": "text",
            "max_tokens": 1024,
            "embedding_dimensions": 10
        }


class MockAgent:
    """Mock agent for compatibility testing."""
    
    def __init__(self, name, model):
        """Initialize the mock agent."""
        self.name = name
        self.model = model
    
    def process(self, input_text, context=None):
        """Process input and generate a response."""
        response = self.model.generate(input_text)
        
        return {
            "response": f"{self.name} ({self.model.provider}): {response}"
        }
    
    async def process_async(self, input_text, context=None):
        """Process input asynchronously."""
        response = self.model.generate(input_text)
        
        return {
            "response": f"{self.name} ({self.model.provider}): {response}",
            "async": True
        }
    
    def get_info(self):
        """Get information about the agent."""
        return {
            "name": self.name,
            "model": self.model.get_model_info()
        }


class TestModelCompatibility(unittest.TestCase):
    """Compatibility tests for the agent coordination framework with different model providers."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create models
        self.hf_model = MockHuggingFaceModel()
        self.ollama_model = MockOllamaModel()
        self.openai_model = MockOpenAIModel()
        self.anthropic_model = MockAnthropicModel()
        
        # Create agents
        self.hf_agent = MockAgent("HuggingFace Agent", self.hf_model)
        self.ollama_agent = MockAgent("Ollama Agent", self.ollama_model)
        self.openai_agent = MockAgent("OpenAI Agent", self.openai_model)
        self.anthropic_agent = MockAgent("Anthropic Agent", self.anthropic_model)
        
        # Create coordinator
        self.coordinator = AgentCoordinator("Compatibility Coordinator")
        
        # Register agents
        self.coordinator.register_agent("hf", self.hf_agent)
        self.coordinator.register_agent("ollama", self.ollama_agent)
        self.coordinator.register_agent("openai", self.openai_agent)
        self.coordinator.register_agent("anthropic", self.anthropic_agent)
        
        # Create team
        self.team = AgentTeam(
            name="Compatibility Team",
            description="A team for compatibility testing",
            coordinator=self.coordinator
        )
        
        # Add roles
        self.team.add_role(
            role_name="researcher",
            agent_id="hf",
            description="Researches topics"
        )
        
        self.team.add_role(
            role_name="developer",
            agent_id="ollama",
            description="Writes code"
        )
        
        self.team.add_role(
            role_name="reviewer",
            agent_id="openai",
            description="Reviews code"
        )
        
        self.team.add_role(
            role_name="writer",
            agent_id="anthropic",
            description="Creates documentation"
        )
    
    def test_mixed_model_workflow(self):
        """Test a workflow with mixed model providers."""
        # Define a task
        task = "Create a function to calculate the Fibonacci sequence"
        
        # Create workflow
        workflow = Workflow(
            name="Mixed Model Workflow",
            description="Workflow with different model providers"
        )
        
        # Add steps
        workflow.add_process_step(
            role="researcher",
            input=f"Research: {task}",
            description="Research the topic"
        )
        
        workflow.add_message_step(
            from_role="researcher",
            to_role="developer",
            message="Based on this research, please implement: {researcher_result}",
            description="Send research to developer"
        )
        
        workflow.add_message_step(
            from_role="developer",
            to_role="reviewer",
            message="Please review this code: {developer_response}",
            description="Send code to reviewer"
        )
        
        workflow.add_message_step(
            from_role="reviewer",
            to_role="writer",
            message="Please write documentation for this code: {reviewer_response}",
            description="Send review to writer"
        )
        
        # Execute workflow
        result = self.team.execute_workflow(task, workflow.to_list())
        
        # Check the result
        self.assertEqual(result["task"], task)
        self.assertEqual(len(result["results"]), 4)
        
        # Check each step
        self.assertEqual(result["results"][0]["role"], "researcher")
        self.assertIn("HuggingFace", result["results"][0]["output"])
        
        self.assertEqual(result["results"][1]["role"], "researcher")
        self.assertEqual(result["results"][1]["recipient"], "developer")
        self.assertIn("Ollama", result["results"][1]["output"])
        
        self.assertEqual(result["results"][2]["role"], "developer")
        self.assertEqual(result["results"][2]["recipient"], "reviewer")
        self.assertIn("OpenAI", result["results"][2]["output"])
        
        self.assertEqual(result["results"][3]["role"], "reviewer")
        self.assertEqual(result["results"][3]["recipient"], "writer")
        self.assertIn("Anthropic", result["results"][3]["output"])
    
    def test_model_specific_features(self):
        """Test model-specific features."""
        # Test each model provider
        providers = ["hf", "ollama", "openai", "anthropic"]
        
        for provider in providers:
            # Send message to agent
            message = self.coordinator.send_message(
                from_agent_id="hf",
                to_agent_id=provider,
                message=f"Test message for {provider}"
            )
            
            # Process message
            response = self.coordinator.process_message(message)
            
            # Check response
            self.assertIn(provider.upper(), response["message"].upper())
    
    def test_model_provider_independence(self):
        """Test that the coordination framework is independent of model providers."""
        # Create a new model provider
        class MockCustomModel(ModelInterface):
            """Mock custom model for compatibility testing."""
            
            def __init__(self, model_name="mock-custom-model"):
                """Initialize the mock custom model."""
                self.model_name = model_name
                self.provider = "custom"
                logger.info(f"Initialized Mock Custom Model: {model_name}")
            
            def generate(self, prompt, **kwargs):
                """Generate text based on a prompt."""
                return f"[Custom] Response to: {prompt[:50]}..."
            
            def get_token_count(self, text):
                """Get the number of tokens in a text."""
                return len(text.split())
            
            def get_embedding(self, text):
                """Get the embedding for a text."""
                return [0.1] * 10
            
            def get_model_info(self):
                """Get information about the model."""
                return {
                    "name": self.model_name,
                    "provider": self.provider,
                    "type": "text",
                    "max_tokens": 1024,
                    "embedding_dimensions": 10
                }
        
        # Create custom agent
        custom_model = MockCustomModel()
        custom_agent = MockAgent("Custom Agent", custom_model)
        
        # Register custom agent
        self.coordinator.register_agent("custom", custom_agent)
        
        # Add custom role
        self.team.add_role(
            role_name="custom_role",
            agent_id="custom",
            description="Custom role"
        )
        
        # Create workflow with custom role
        workflow = Workflow(
            name="Custom Workflow",
            description="Workflow with custom model provider"
        )
        
        workflow.add_process_step(
            role="custom_role",
            input="Custom input",
            description="Custom step"
        )
        
        # Execute workflow
        result = self.team.execute_workflow("Custom task", workflow.to_list())
        
        # Check the result
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["role"], "custom_role")
        self.assertIn("Custom", result["results"][0]["output"])
    
    def test_model_provider_fallbacks(self):
        """Test fallbacks between model providers."""
        # Create a workflow that tries different model providers
        workflow = Workflow(
            name="Fallback Workflow",
            description="Workflow with fallbacks between model providers"
        )
        
        # Add steps with all providers
        providers = ["researcher", "developer", "reviewer", "writer"]
        
        for provider in providers:
            workflow.add_process_step(
                role=provider,
                input=f"Input for {provider}",
                description=f"Step for {provider}"
            )
        
        # Execute workflow
        result = self.team.execute_workflow("Fallback task", workflow.to_list())
        
        # Check the result
        self.assertEqual(len(result["results"]), 4)
        
        # Check each step
        for i, provider in enumerate(providers):
            self.assertEqual(result["results"][i]["role"], provider)
    
    def test_model_provider_compatibility_matrix(self):
        """Test compatibility matrix between model providers."""
        # Create a compatibility matrix
        providers = ["hf", "ollama", "openai", "anthropic"]
        
        # Test all combinations
        for from_provider in providers:
            for to_provider in providers:
                # Skip same provider
                if from_provider == to_provider:
                    continue
                
                # Send message
                message = self.coordinator.send_message(
                    from_agent_id=from_provider,
                    to_agent_id=to_provider,
                    message=f"Test message from {from_provider} to {to_provider}"
                )
                
                # Process message
                response = self.coordinator.process_message(message)
                
                # Check response
                self.assertIn(to_provider.upper(), response["message"].upper())
                self.assertEqual(response["from"], to_provider)
                self.assertEqual(response["to"], from_provider)
    
    def test_model_provider_specific_workflows(self):
        """Test workflows specific to each model provider."""
        # Test each model provider
        providers = ["hf", "ollama", "openai", "anthropic"]
        
        for provider in providers:
            # Create workflow
            workflow = Workflow(
                name=f"{provider.capitalize()} Workflow",
                description=f"Workflow for {provider}"
            )
            
            # Add steps
            workflow.add_process_step(
                role="researcher" if provider == "hf" else
                "developer" if provider == "ollama" else
                "reviewer" if provider == "openai" else
                "writer",
                input=f"Input for {provider}",
                description=f"Step for {provider}"
            )
            
            # Execute workflow
            result = self.team.execute_workflow(f"{provider} task", workflow.to_list())
            
            # Check the result
            self.assertEqual(len(result["results"]), 1)
            
            # Check provider
            expected_provider = "HuggingFace" if provider == "hf" else \
                               "Ollama" if provider == "ollama" else \
                               "OpenAI" if provider == "openai" else \
                               "Anthropic"
            
            self.assertIn(expected_provider, result["results"][0]["output"])


if __name__ == '__main__':
    unittest.main()
