#!/usr/bin/env python
"""Basic Agent Example.

This script demonstrates how to create a basic agent without external dependencies.

Usage:
    python -m examples.basic_agent_example
"""

import logging
import argparse
import os
import sys
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add parent directory to path to allow importing from augment_adam
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import after path setup
from augment_adam.ai_agent.base_agent import BaseAgent
from augment_adam.models.model_interface import ModelInterface


class MockModel(ModelInterface):
    """Mock model for demonstration purposes."""
    
    def __init__(self, model_name: str = "mock-model", **kwargs):
        """Initialize the Mock Model."""
        self.model_name = model_name
        logger.info(f"Initialized Mock Model: {model_name}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text based on a prompt."""
        # Simple mock response
        if "hello" in prompt.lower():
            return "Hello! I'm a mock AI assistant. How can I help you today?"
        elif "help" in prompt.lower():
            return "I'm here to help! What do you need assistance with?"
        elif "weather" in prompt.lower():
            return "I don't have access to real-time weather data, but I can help you find weather information online."
        else:
            return f"You said: {prompt}\n\nI'm a mock AI assistant and can provide simple responses for demonstration purposes."
    
    def get_token_count(self, text: str) -> int:
        """Get the number of tokens in a text."""
        # Simple approximation
        return len(text.split())
    
    def get_embedding(self, text: str) -> list:
        """Get the embedding for a text."""
        # Mock embedding
        return [0.1] * 10
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        return {
            "name": self.model_name,
            "provider": "Mock",
            "type": "text",
            "max_tokens": 1024,
            "embedding_dimensions": 10
        }


def create_basic_agent():
    """Create a basic agent with a mock model."""
    # Create mock model
    model = MockModel()
    
    # Create system prompt
    system_prompt = """You are a helpful AI assistant.
    
Your goal is to provide helpful, accurate, and concise responses to user queries.
Always be respectful and professional in your responses.

When providing information, try to be specific and provide examples when possible.
If you don't know something, admit it rather than making up information.
"""
    
    # Create agent
    agent = BaseAgent(
        name="Basic Assistant",
        description="A helpful AI assistant",
        model=model,
        system_prompt=system_prompt
    )
    
    return agent


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Basic Agent Example")
    
    args = parser.parse_args()
    
    # Create agent
    agent = create_basic_agent()
    logger.info("Created basic agent")
    
    # Interactive loop
    print(f"\nWelcome to the {agent.name} demo!")
    print("Type 'exit' to quit.\n")
    
    while True:
        # Get user input
        user_input = input("You: ")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            break
        
        # Process input
        result = agent.process(user_input)
        
        # Display response
        print(f"\n{agent.name}: {result['response']}\n")


if __name__ == "__main__":
    main()
