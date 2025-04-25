#!/usr/bin/env python
"""Agent Coordination Example.

This script demonstrates how to coordinate multiple agents.

Usage:
    python -m examples.agent_coordination_example
"""

import logging
import argparse
import asyncio
from typing import Dict, List, Any

from augment_adam.models import create_model
from augment_adam.ai_agent import create_agent
from augment_adam.ai_agent.coordination import AgentCoordinator, AgentTeam, Workflow, WorkflowStep
from augment_adam.utils.hardware_optimizer import get_optimal_model_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_specialized_agents():
    """Create specialized agents for different tasks."""
    # Get optimal settings
    settings = get_optimal_model_settings("huggingface", "small_context")
    
    # Create model
    model = create_model(
        model_type="huggingface",
        model_size="small_context",
        **settings
    )
    
    # Create research agent
    research_agent = create_agent(
        agent_type="conversational",
        name="Research Agent",
        description="An agent specialized in research and information gathering",
        model=model,
        system_prompt="""You are a Research Agent specialized in gathering and analyzing information.

Your goal is to provide accurate, well-researched information on any topic.
Focus on facts and cite sources when possible.
Be thorough and comprehensive in your research.

When you don't know something, admit it rather than making up information.
Always be objective and avoid personal opinions or biases.
""",
        output_format="text"
    )
    
    # Create writing agent
    writing_agent = create_agent(
        agent_type="conversational",
        name="Writing Agent",
        description="An agent specialized in writing and content creation",
        model=model,
        system_prompt="""You are a Writing Agent specialized in creating high-quality content.

Your goal is to write clear, engaging, and well-structured content.
Focus on clarity, coherence, and proper grammar.
Adapt your writing style to the specific needs of the task.

When writing, consider the audience and purpose of the content.
Use appropriate tone, vocabulary, and structure for the context.
""",
        output_format="text"
    )
    
    # Create coding agent
    coding_agent = create_agent(
        agent_type="coding",
        name="Coding Agent",
        description="An agent specialized in writing and reviewing code",
        model=model,
        system_prompt="""You are a Coding Agent specialized in writing and reviewing code.

Your goal is to write clean, efficient, and well-documented code.
Focus on best practices, readability, and maintainability.
Consider performance, security, and edge cases.

When writing code, include comments to explain complex logic.
When reviewing code, look for bugs, inefficiencies, and improvements.
""",
        output_format="text"
    )
    
    return {
        "research_agent": research_agent,
        "writing_agent": writing_agent,
        "coding_agent": coding_agent
    }


def demo_basic_coordination():
    """Demonstrate basic agent coordination."""
    print("\n=== Basic Agent Coordination ===\n")
    
    # Create agents
    agents = create_specialized_agents()
    
    # Create coordinator
    coordinator = AgentCoordinator("Demo Coordinator")
    
    # Register agents
    for agent_id, agent in agents.items():
        coordinator.register_agent(agent_id, agent)
    
    # Define a task
    task = "Create a Python function to calculate the Fibonacci sequence"
    
    print(f"Task: {task}\n")
    
    # Start with research agent
    print("Step 1: Research Agent researches the Fibonacci sequence")
    research_message = coordinator.send_message(
        from_agent_id="coordinator",
        to_agent_id="research_agent",
        message=f"Please explain the Fibonacci sequence and how it works: {task}"
    )
    
    research_response = coordinator.process_message(research_message)
    print(f"Research Agent: {research_response['message']}\n")
    
    # Send to coding agent
    print("Step 2: Coding Agent implements the function based on research")
    coding_message = coordinator.send_message(
        from_agent_id="research_agent",
        to_agent_id="coding_agent",
        message=f"Based on this research, please implement a Python function for the Fibonacci sequence:\n\n{research_response['message']}"
    )
    
    coding_response = coordinator.process_message(coding_message)
    print(f"Coding Agent: {coding_response['message']}\n")
    
    # Send to writing agent for documentation
    print("Step 3: Writing Agent creates documentation")
    writing_message = coordinator.send_message(
        from_agent_id="coding_agent",
        to_agent_id="writing_agent",
        message=f"Please write documentation for this Fibonacci function:\n\n{coding_response['message']}"
    )
    
    writing_response = coordinator.process_message(writing_message)
    print(f"Writing Agent: {writing_response['message']}\n")
    
    print("Basic coordination complete!")


def demo_agent_team():
    """Demonstrate agent team with roles."""
    print("\n=== Agent Team with Roles ===\n")
    
    # Create agents
    agents = create_specialized_agents()
    
    # Create team
    team = AgentTeam(
        name="Development Team",
        description="A team for software development tasks"
    )
    
    # Add roles
    team.add_role(
        role_name="researcher",
        agent_id="research_agent",
        description="Researches topics and gathers information",
        agent=agents["research_agent"]
    )
    
    team.add_role(
        role_name="developer",
        agent_id="coding_agent",
        description="Writes and reviews code",
        agent=agents["coding_agent"]
    )
    
    team.add_role(
        role_name="technical_writer",
        agent_id="writing_agent",
        description="Creates documentation and explanations",
        agent=agents["writing_agent"]
    )
    
    # Define a task
    task = "Create a Python class for managing a simple to-do list"
    
    print(f"Task: {task}\n")
    
    # Create workflow
    workflow = Workflow(
        name="Development Workflow",
        description="Workflow for creating a software component"
    )
    
    # Add steps
    workflow.add_process_step(
        role="researcher",
        input=f"Research best practices for implementing a to-do list class in Python: {task}",
        description="Research best practices"
    )
    
    workflow.add_message_step(
        from_role="researcher",
        to_role="developer",
        message="Based on my research, please implement a Python class for a to-do list: {researcher_result}",
        description="Send research to developer"
    )
    
    workflow.add_message_step(
        from_role="developer",
        to_role="technical_writer",
        message="Please write documentation for this to-do list class: {developer_response}",
        description="Send implementation to technical writer"
    )
    
    # Execute workflow
    print("Executing workflow...")
    result = team.execute_workflow(task, workflow.to_list())
    
    # Print results
    print("\nWorkflow Results:\n")
    
    for step_result in result["results"]:
        print(f"Step: {step_result['role']} - {step_result['action']}")
        if "recipient" in step_result:
            print(f"To: {step_result['recipient']}")
        print(f"Input: {step_result['input'][:100]}...")
        print(f"Output: {step_result['output'][:100]}...")
        print()
    
    print("Team workflow complete!")


async def demo_async_coordination():
    """Demonstrate asynchronous agent coordination."""
    print("\n=== Asynchronous Agent Coordination ===\n")
    
    # Create agents
    agents = create_specialized_agents()
    
    # Create coordinator
    coordinator = AgentCoordinator("Async Coordinator")
    
    # Register agents
    for agent_id, agent in agents.items():
        coordinator.register_agent(agent_id, agent)
    
    # Define multiple tasks
    tasks = [
        "Explain the concept of recursion in programming",
        "Write a short poem about artificial intelligence",
        "Create a Python function to check if a string is a palindrome"
    ]
    
    print(f"Tasks: {tasks}\n")
    
    # Process tasks in parallel
    print("Processing tasks in parallel...")
    
    async def process_task(task_index, task):
        print(f"Starting task {task_index + 1}: {task}")
        
        # Determine which agent to use
        if "programming" in task or "Python" in task:
            agent_id = "coding_agent"
        elif "poem" in task or "write" in task:
            agent_id = "writing_agent"
        else:
            agent_id = "research_agent"
        
        # Get agent
        agent = coordinator.get_agent(agent_id)
        
        # Process task
        start_message = {
            "id": f"task_{task_index}",
            "from": "coordinator",
            "to": agent_id,
            "message": task,
            "metadata": {"task_index": task_index},
            "timestamp": 0
        }
        
        response = await coordinator.process_message_async(start_message)
        
        print(f"Completed task {task_index + 1}")
        return {
            "task_index": task_index,
            "task": task,
            "agent": agent_id,
            "response": response["message"]
        }
    
    # Create tasks
    task_futures = [process_task(i, task) for i, task in enumerate(tasks)]
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*task_futures)
    
    # Print results
    print("\nTask Results:\n")
    
    for result in sorted(results, key=lambda x: x["task_index"]):
        print(f"Task {result['task_index'] + 1}: {result['task']}")
        print(f"Agent: {result['agent']}")
        print(f"Response: {result['response'][:100]}...")
        print()
    
    print("Async coordination complete!")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Agent Coordination Example")
    parser.add_argument("--basic", action="store_true", help="Run basic coordination demo")
    parser.add_argument("--team", action="store_true", help="Run agent team demo")
    parser.add_argument("--async", dest="async_demo", action="store_true", help="Run async coordination demo")
    
    args = parser.parse_args()
    
    # Run demos
    if args.basic or not (args.team or args.async_demo):
        demo_basic_coordination()
    
    if args.team:
        demo_agent_team()
    
    if args.async_demo:
        asyncio.run(demo_async_coordination())


if __name__ == "__main__":
    main()
