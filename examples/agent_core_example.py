"""Example of using the Agent Core with the Context Engine.

This script demonstrates how to use the Agent Core with the Context Engine.

Version: 0.1.0
Created: 2025-04-27
"""

import logging
import sys
import os
import argparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from augment_adam.ai_agent import create_agent
from augment_adam.ai_agent.smc.potential import RegexPotential, GrammarPotential
from augment_adam.context_engine import get_context_manager
from augment_adam.context_engine.retrieval import MemoryRetriever, WebRetriever
from augment_adam.context_engine.composition import ContextComposer, ContextOptimizer
from augment_adam.context_engine.chunking import IntelligentChunker, Summarizer
from augment_adam.context_engine.prompt import PromptComposer, PromptTemplates

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def initialize_context_engine():
    """Initialize the Context Engine.

    Returns:
        The initialized Context Engine
    """
    # Initialize Context Engine
    context_manager = get_context_manager()

    # Register retrievers
    context_manager.register_retriever("memory", MemoryRetriever())
    context_manager.register_retriever("web", WebRetriever())

    # Register composers
    context_manager.register_composer("default", ContextComposer())
    context_manager.register_composer("optimizer", ContextOptimizer(Summarizer()))

    # Register chunkers
    context_manager.register_chunker("intelligent", IntelligentChunker())

    # Register prompt composers
    prompt_templates = PromptTemplates()
    context_manager.register_prompt_composer(
        "default",
        PromptComposer(prompt_templates.get_all_templates())
    )

    logger.info("Initialized Context Engine")
    return context_manager


def demo_conversational_agent():
    """Demonstrate the Conversational Agent."""
    logger.info("Demonstrating Conversational Agent")

    # Create potentials for controlled generation
    sentence_ending_potential = RegexPotential(
        pattern=r".*[.!?]$",
        name="sentence_ending_potential"
    )

    # Create a conversational agent
    agent = create_agent(
        agent_type="conversational",
        name="Conversational Agent",
        description="A conversational AI agent",
        potentials=[sentence_ending_potential],
        num_particles=50
    )

    # Process some inputs
    inputs = [
        "Hello, how are you?",
        "Tell me about yourself.",
        "What can you do?",
        "Thank you for your help."
    ]

    for input_text in inputs:
        logger.info(f"Processing input: {input_text}")

        # Process input
        result = agent.process(input_text)

        # Print response
        print(f"User: {input_text}")
        print(f"Agent: {result['response']}")
        print()


def demo_task_agent():
    """Demonstrate the Task Agent."""
    logger.info("Demonstrating Task Agent")

    # Create a task agent
    agent = create_agent(
        agent_type="task",
        name="Task Agent",
        description="A task-focused AI agent",
        num_particles=50
    )

    # Process some inputs
    inputs = [
        "Can you help me plan a birthday party?",
        "I need about 20 people.",
        "Let's move on to the next step.",
        "What's the final plan?"
    ]

    for input_text in inputs:
        logger.info(f"Processing input: {input_text}")

        # Process input
        result = agent.process(input_text)

        # Print response
        print(f"User: {input_text}")
        print(f"Agent: {result['response']}")

        # Print task information if available
        if "task" in result:
            task = result["task"]
            if task:
                print(f"Task: {task.get('description', '')}")
                print(f"Status: {task.get('status', '')}")
                print(f"Progress: {task.get('steps_completed', 0)}/{task.get('steps_total', 0)}")

        print()


def demo_research_agent():
    """Demonstrate the Research Agent."""
    logger.info("Demonstrating Research Agent")

    # Create a research agent
    agent = create_agent(
        agent_type="research",
        name="Research Agent",
        description="A research-focused AI agent",
        num_particles=50
    )

    # Add some sources
    agent.add_source(
        {"author": "Smith", "year": "2023", "title": "Advances in AI Research"},
        "technology"
    )
    agent.add_source(
        {"author": "Johnson", "year": "2022", "title": "The Future of Technology"},
        "technology"
    )

    # Process some inputs
    inputs = [
        "Tell me about recent advances in artificial intelligence.",
        "How does machine learning work?",
        "What are the ethical implications of AI?"
    ]

    for input_text in inputs:
        logger.info(f"Processing input: {input_text}")

        # Process input
        result = agent.process(input_text)

        # Print response
        print(f"User: {input_text}")
        print(f"Agent: {result['response']}")

        # Print research information
        print(f"Research Topic: {result.get('research_topic', '')}")
        print(f"Knowledge Extracted: {result.get('knowledge_extracted', 0)}")

        print()


def demo_creative_agent():
    """Demonstrate the Creative Agent."""
    logger.info("Demonstrating Creative Agent")

    # Create a creative agent
    agent = create_agent(
        agent_type="creative",
        name="Creative Agent",
        description="A creative-focused AI agent",
        num_particles=50
    )

    # Process some inputs
    inputs = [
        "Write a poem about the ocean.",
        "Tell me a short story about a robot.",
        "Describe a beautiful sunset."
    ]

    for input_text in inputs:
        logger.info(f"Processing input: {input_text}")

        # Process input
        result = agent.process(input_text)

        # Print response
        print(f"User: {input_text}")
        print(f"Agent: {result['response']}")

        # Print creative information
        print(f"Creative Mode: {result.get('creative_mode', '')}")

        # Print reflection if available
        if "reflection" in result:
            reflection = result["reflection"]
            if reflection and "overall" in reflection:
                print(f"Reflection: {reflection['overall']}")

        print()


def demo_coding_agent():
    """Demonstrate the Coding Agent."""
    logger.info("Demonstrating Coding Agent")

    # Create a coding agent
    agent = create_agent(
        agent_type="coding",
        name="Coding Agent",
        description="A code-focused AI agent",
        num_particles=50
    )

    # Process some inputs
    inputs = [
        "Write a Python function to calculate the Fibonacci sequence.",
        "How would I optimize this code?",
        "Can you explain how recursion works in programming?"
    ]

    for input_text in inputs:
        logger.info(f"Processing input: {input_text}")

        # Process input
        result = agent.process(input_text)

        # Print response
        print(f"User: {input_text}")
        print(f"Agent: {result['response']}")

        # Print code information
        print(f"Language: {result.get('language', '')}")
        print(f"Code Task: {result.get('code_task', '')}")

        # Print decisions if available
        if "decisions" in result:
            decisions = result["decisions"]
            if decisions and "recommendation" in decisions:
                recommendation = decisions["recommendation"]
                print(f"Recommendation: {recommendation.get('action', '')} (Score: {recommendation.get('overall_score', 0.0):.2f})")

        print()


def main():
    """Run the example."""
    parser = argparse.ArgumentParser(description="Agent Core Example")
    parser.add_argument(
        "--agent",
        choices=["conversational", "task", "research", "creative", "coding", "all"],
        default="all",
        help="The type of agent to demonstrate"
    )

    args = parser.parse_args()

    logger.info("Starting Agent Core example")

    # Initialize Context Engine
    initialize_context_engine()

    # Demonstrate the specified agent type
    if args.agent == "conversational" or args.agent == "all":
        demo_conversational_agent()

    if args.agent == "task" or args.agent == "all":
        demo_task_agent()

    if args.agent == "research" or args.agent == "all":
        demo_research_agent()

    if args.agent == "creative" or args.agent == "all":
        demo_creative_agent()

    if args.agent == "coding" or args.agent == "all":
        demo_coding_agent()

    logger.info("Finished Agent Core example")


if __name__ == "__main__":
    main()
