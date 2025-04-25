#!/usr/bin/env python
"""Simple Agent Example.

This script demonstrates how to create and use agents with system prompts,
output instructions, and specialized tools.

Usage:
    python -m examples.simple_agent_example
"""

import logging
import argparse
from typing import Dict, Any

from augment_adam.models import create_model
from augment_adam.ai_agent import create_agent
from augment_adam.utils.hardware_optimizer import get_optimal_model_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_simple_agent(model_type="huggingface", model_size="small_context"):
    """Create a simple agent with system prompt and output instructions."""
    # Get optimal settings
    settings = get_optimal_model_settings(model_type, model_size)
    
    # Create model
    model = create_model(
        model_type=model_type,
        model_size=model_size,
        **settings
    )
    
    # Create agent with custom system prompt
    system_prompt = """You are a helpful AI assistant.
    
Your goal is to provide helpful, accurate, and concise responses to user queries.
Always be respectful and professional in your responses.

When providing information, try to be specific and provide examples when possible.
If you don't know something, admit it rather than making up information.
"""
    
    agent = create_agent(
        agent_type="conversational",
        name="Simple Assistant",
        description="A helpful AI assistant",
        model=model,
        system_prompt=system_prompt,
        output_format="text",  # Can be "text" or "json"
        strict_output=False,
        temperature=0.7
    )
    
    return agent


def create_json_agent(model_type="huggingface", model_size="small_context"):
    """Create an agent with JSON output format."""
    # Get optimal settings
    settings = get_optimal_model_settings(model_type, model_size)
    
    # Create model
    model = create_model(
        model_type=model_type,
        model_size=model_size,
        **settings
    )
    
    # Create agent with JSON output format
    system_prompt = """You are a helpful AI assistant that responds in JSON format.
    
Your goal is to provide helpful, accurate, and concise responses to user queries.
Always be respectful and professional in your responses.

IMPORTANT: You must respond in valid JSON format with the following structure:
{
    "response": "Your response text here",
    "confidence": 0.9,  // A value between 0 and 1
    "sources": []       // Optional list of sources
}
"""
    
    agent = create_agent(
        agent_type="conversational",
        name="JSON Assistant",
        description="A helpful AI assistant that responds in JSON format",
        model=model,
        system_prompt=system_prompt,
        output_format="json",
        strict_output=True,
        temperature=0.7
    )
    
    return agent


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Simple Agent Example")
    parser.add_argument("--json", action="store_true", help="Use JSON output format")
    
    args = parser.parse_args()
    
    # Create agent
    if args.json:
        agent = create_json_agent()
        logger.info("Created JSON agent")
    else:
        agent = create_simple_agent()
        logger.info("Created simple agent")
    
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
        if isinstance(result, Dict) and "response" in result:
            print(f"\n{agent.name}: {result['response']}\n")
        else:
            print(f"\n{agent.name}: {result}\n")


if __name__ == "__main__":
    main()
