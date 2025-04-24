#!/usr/bin/env python
"""Minimal Example.

This script demonstrates a minimal working example without dependencies.

Usage:
    python -m examples.minimal_example
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


class MinimalAgent:
    """Minimal agent implementation."""
    
    def __init__(self, name: str, system_prompt: str):
        """Initialize the Minimal Agent."""
        self.name = name
        self.system_prompt = system_prompt
        logger.info(f"Initialized Minimal Agent: {name}")
    
    def process(self, user_input: str) -> Dict[str, Any]:
        """Process user input and generate a response."""
        # Simple mock responses
        if "hello" in user_input.lower():
            response = "Hello! I'm a minimal AI assistant. How can I help you today?"
        elif "help" in user_input.lower():
            response = "I'm here to help! What do you need assistance with?"
        elif "weather" in user_input.lower():
            response = "I don't have access to real-time weather data, but I can help you find weather information online."
        elif "agent" in user_input.lower() or "framework" in user_input.lower():
            response = """The Augment Adam agent framework provides:
1. Specialized agents with system prompts
2. Tool integration for specific tasks
3. Agent coordination for complex workflows
4. MCP server deployment
5. Asynchronous processing for long-running tasks"""
        else:
            response = f"You said: {user_input}\n\nI'm a minimal AI assistant and can provide simple responses for demonstration purposes."
        
        return {
            "response": response,
            "processing_time": 0.1
        }


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Minimal Example")
    
    args = parser.parse_args()
    
    # Create agent
    system_prompt = """You are a helpful AI assistant.
    
Your goal is to provide helpful, accurate, and concise responses to user queries.
Always be respectful and professional in your responses.
"""
    
    agent = MinimalAgent(
        name="Minimal Assistant",
        system_prompt=system_prompt
    )
    
    logger.info("Created minimal agent")
    
    # Interactive loop
    print(f"\nWelcome to the {agent.name} demo!")
    print("Type 'exit' to quit.\n")
    print("Try asking about the agent framework, weather, or just say hello.\n")
    
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
