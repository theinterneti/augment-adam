#!/usr/bin/env python
"""Worker Agent Example.

This script demonstrates how to create and use worker agents for async processing.

Usage:
    python -m examples.worker_agent_example
"""

import logging
import argparse
import asyncio
from typing import Dict, Any, List

from augment_adam.models import create_model
from augment_adam.ai_agent import create_agent
from augment_adam.utils.hardware_optimizer import get_optimal_model_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_worker_agent(model_type="huggingface", model_size="small_context"):
    """Create a worker agent for async processing."""
    # Get optimal settings
    settings = get_optimal_model_settings(model_type, model_size)
    
    # Create model
    model = create_model(
        model_type=model_type,
        model_size=model_size,
        **settings
    )
    
    # Create worker agent
    system_prompt = """You are a worker agent designed to process tasks asynchronously.
    
Your goal is to provide helpful, accurate, and concise responses to user queries.
Always be respectful and professional in your responses.

When processing tasks, be thorough and provide detailed responses.
"""
    
    agent = create_agent(
        agent_type="worker",
        name="Worker Agent",
        description="A worker agent for async processing",
        model=model,
        system_prompt=system_prompt,
        output_format="text",
        max_concurrent_tasks=3  # Process up to 3 tasks concurrently
    )
    
    return agent


async def run_worker_demo():
    """Run the worker agent demo."""
    # Create worker agent
    agent = create_worker_agent()
    logger.info("Created worker agent")
    
    # Start the worker
    await agent.start()
    logger.info("Started worker agent")
    
    # Submit some tasks
    tasks = [
        "Explain the concept of quantum computing in simple terms.",
        "Write a short poem about artificial intelligence.",
        "List 5 interesting facts about space exploration.",
        "Provide a recipe for chocolate chip cookies.",
        "Explain how neural networks work."
    ]
    
    task_ids = []
    for task in tasks:
        task_id = await agent.submit_task(task)
        task_ids.append(task_id)
        logger.info(f"Submitted task: {task_id}")
    
    # Wait for tasks to complete
    print("\nWaiting for tasks to complete...\n")
    
    completed = set()
    while len(completed) < len(task_ids):
        for task_id in task_ids:
            if task_id in completed:
                continue
            
            status = agent.get_task_status(task_id)
            if status["status"] == "completed":
                completed.add(task_id)
                print(f"\nTask {task_id} completed:")
                print(f"Query: {status['user_input']}")
                print(f"Response: {status['result']['response']}")
                print("-" * 50)
        
        await asyncio.sleep(1)
    
    # Stop the worker
    await agent.stop()
    logger.info("Stopped worker agent")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Worker Agent Example")
    
    args = parser.parse_args()
    
    # Run the worker demo
    asyncio.run(run_worker_demo())


if __name__ == "__main__":
    main()
