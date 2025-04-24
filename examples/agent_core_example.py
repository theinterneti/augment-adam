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
from augment_adam.ai_agent.smc.potential import RegexPotential, GrammarPotential, SemanticPotential
from augment_adam.ai_agent.smc.advanced_potentials import (
    CoherencePotential, FactualPotential, StylePotential, ConstraintPotential,
    ContextAwarePotential, FORMAL_STYLE, CONVERSATIONAL_STYLE, TECHNICAL_STYLE, CREATIVE_STYLE,
    length_constraint, required_elements_constraint, forbidden_content_constraint
)
from augment_adam.context_engine import get_context_manager
from augment_adam.context_engine.retrieval import MemoryRetriever, WebRetriever
from augment_adam.context_engine.composition import ContextComposer, ContextOptimizer
from augment_adam.context_engine.chunking import IntelligentChunker, Summarizer
from augment_adam.context_engine.prompt import PromptComposer, PromptTemplates
from augment_adam.models import create_model

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


def demo_conversational_agent(model_type=None, model_name=None, model_kwargs=None):
    """Demonstrate the Conversational Agent.

    Args:
        model_type: The type of model to use
        model_name: The name of the model to use
        model_kwargs: Additional model parameters
    """
    model_kwargs = model_kwargs or {}
    logger.info("Demonstrating Conversational Agent")

    # Create a model for embedding functions
    model = create_model(model_type=model_type, model_name=model_name, **model_kwargs)

    # Create potentials for controlled generation
    potentials = [
        # Basic potentials
        RegexPotential(
            pattern=r".*[.!?]$",
            name="sentence_ending_potential"
        ),

        # Style potential for conversational text
        StylePotential(
            style_patterns=CONVERSATIONAL_STYLE,
            name="conversational_style_potential"
        ),

        # Constraint potentials
        ConstraintPotential(
            constraints=[
                length_constraint(min_length=10, max_length=200),
                forbidden_content_constraint(["offensive", "inappropriate", "harmful"])
            ],
            name="constraint_potential"
        )
    ]

    # Add coherence potential if the model supports embeddings
    try:
        # Create a coherence potential using the model's embedding function
        coherence_potential = CoherencePotential(
            embedding_fn=model.get_embedding,
            reference_text="Hello! I'm a helpful and friendly AI assistant. How can I help you today?",
            name="coherence_potential"
        )
        potentials.append(coherence_potential)
    except (AttributeError, NotImplementedError):
        logger.warning("Model doesn't support embeddings, skipping coherence potential")

    # Create a conversational agent
    agent = create_agent(
        agent_type="conversational",
        name="Conversational Agent",
        description="A conversational AI agent",
        model_type=model_type,
        model_name=model_name,
        potentials=potentials,
        num_particles=50,
        **model_kwargs
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


def demo_task_agent(model_type=None, model_name=None, model_kwargs=None):
    """Demonstrate the Task Agent.

    Args:
        model_type: The type of model to use
        model_name: The name of the model to use
        model_kwargs: Additional model parameters
    """
    model_kwargs = model_kwargs or {}
    logger.info("Demonstrating Task Agent")

    # Create a task agent
    agent = create_agent(
        agent_type="task",
        name="Task Agent",
        description="A task-focused AI agent",
        model_type=model_type,
        model_name=model_name,
        num_particles=50,
        **model_kwargs
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


def demo_research_agent(model_type=None, model_name=None, model_kwargs=None):
    """Demonstrate the Research Agent.

    Args:
        model_type: The type of model to use
        model_name: The name of the model to use
        model_kwargs: Additional model parameters
    """
    model_kwargs = model_kwargs or {}
    logger.info("Demonstrating Research Agent")

    # Create a research agent
    agent = create_agent(
        agent_type="research",
        name="Research Agent",
        description="A research-focused AI agent",
        model_type=model_type,
        model_name=model_name,
        num_particles=50,
        **model_kwargs
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


def demo_creative_agent(model_type=None, model_name=None, model_kwargs=None):
    """Demonstrate the Creative Agent.

    Args:
        model_type: The type of model to use
        model_name: The name of the model to use
        model_kwargs: Additional model parameters
    """
    model_kwargs = model_kwargs or {}
    logger.info("Demonstrating Creative Agent")

    # Create a model for embedding functions
    model = create_model(model_type=model_type, model_name=model_name, **model_kwargs)

    # Create potentials for controlled generation
    potentials = [
        # Style potential for creative text
        StylePotential(
            style_patterns=CREATIVE_STYLE,
            name="creative_style_potential"
        ),

        # Constraint potentials
        ConstraintPotential(
            constraints=[
                # Creative text can be longer
                length_constraint(min_length=50, max_length=500),
                # Require creative elements
                required_elements_constraint(
                    ["imagine", "beautiful", "creative", "unique", "inspiring"],
                    threshold=2
                )
            ],
            name="creative_constraint_potential"
        )
    ]

    # Add factual potential for certain topics
    factual_potential = FactualPotential(
        facts=[
            "creativity involves imagination",
            "art is a form of expression",
            "stories have characters and plots",
            "poetry uses rhythm and metaphor"
        ],
        threshold=1,
        name="factual_potential"
    )
    potentials.append(factual_potential)

    # Create a creative agent
    agent = create_agent(
        agent_type="creative",
        name="Creative Agent",
        description="A creative-focused AI agent",
        model_type=model_type,
        model_name=model_name,
        potentials=potentials,
        num_particles=50,
        **model_kwargs
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


def demo_coding_agent(model_type=None, model_name=None, model_kwargs=None):
    """Demonstrate the Coding Agent.

    Args:
        model_type: The type of model to use
        model_name: The name of the model to use
        model_kwargs: Additional model parameters
    """
    model_kwargs = model_kwargs or {}
    logger.info("Demonstrating Coding Agent")

    # Create a model for embedding functions
    model = create_model(model_type=model_type, model_name=model_name, **model_kwargs)

    # Create potentials for controlled generation
    potentials = [
        # Style potential for technical/code text
        StylePotential(
            style_patterns=TECHNICAL_STYLE,
            name="technical_style_potential"
        ),

        # Grammar potential for code structure
        RegexPotential(
            pattern=r"(def |class |import |from |if |for |while |return |with |try |except |finally )",
            name="code_keyword_potential"
        ),

        # Constraint potentials for code
        ConstraintPotential(
            constraints=[
                # Code should be properly indented
                required_elements_constraint(
                    ["    ", "def ", "return ", "import ", "class "],
                    threshold=2
                ),
                # Avoid certain anti-patterns
                forbidden_content_constraint(["goto", "exec(", "eval("])
            ],
            name="code_constraint_potential"
        )
    ]

    # Add factual potential for coding knowledge
    factual_potential = FactualPotential(
        facts=[
            "functions are defined with def",
            "classes are defined with class",
            "python uses indentation for blocks",
            "variables are assigned with =",
            "comments start with #"
        ],
        threshold=2,
        name="code_factual_potential"
    )
    potentials.append(factual_potential)

    # Create a coding agent
    agent = create_agent(
        agent_type="coding",
        name="Coding Agent",
        description="A code-focused AI agent",
        model_type=model_type,
        model_name=model_name,
        potentials=potentials,
        num_particles=50,
        **model_kwargs
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
    parser.add_argument(
        "--model-type",
        choices=["huggingface", "ollama", "openai", "anthropic"],
        default="huggingface",
        help="The type of model to use (local models: huggingface, ollama; cloud models: openai, anthropic)"
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default=None,
        help="The name of the model to use (if not specified, use default for model type)"
    )
    parser.add_argument(
        "--model-size",
        type=str,
        choices=["small", "medium", "large", "xl", "code", "small_context", "tiny_context", "medium_context", "long_context"],
        default=None,
        help="The size of the model to use (if not specified, use default)"
    )
    parser.add_argument(
        "--load-in-4bit",
        action="store_true",
        help="Load Hugging Face model in 4-bit precision (reduces memory usage)"
    )
    parser.add_argument(
        "--load-in-8bit",
        action="store_true",
        help="Load Hugging Face model in 8-bit precision (reduces memory usage)"
    )
    parser.add_argument(
        "--device",
        type=str,
        choices=["cpu", "cuda", "mps"],
        default=None,
        help="Device to run the model on (default: auto-detect)"
    )
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="Use model cache for faster loading and generation"
    )
    parser.add_argument(
        "--context-window-size",
        type=int,
        default=None,
        help="Size of the context window (if not specified, use model default)"
    )
    parser.add_argument(
        "--use-monte-carlo",
        action="store_true",
        help="Use Monte Carlo sampling for generation (automatically enabled for small models)"
    )
    parser.add_argument(
        "--monte-carlo-particles",
        type=int,
        default=None,
        help="Number of particles for Monte Carlo sampling (default: 50 for medium/large models, 100 for small models)"
    )

    args = parser.parse_args()

    logger.info("Starting Agent Core example")

    # Initialize Context Engine
    initialize_context_engine()

    # Create model
    model_type = args.model_type
    model_name = args.model_name
    model_size = args.model_size

    # Prepare model kwargs
    model_kwargs = {}

    # Add Hugging Face specific parameters if using Hugging Face
    if model_type == "huggingface":
        if args.load_in_4bit:
            model_kwargs["load_in_4bit"] = True
        if args.load_in_8bit:
            model_kwargs["load_in_8bit"] = True
        if args.device:
            model_kwargs["device"] = args.device

    # Add common parameters
    if args.use_cache:
        model_kwargs["use_cache"] = True
    if args.context_window_size:
        model_kwargs["context_window_size"] = args.context_window_size
    if args.use_monte_carlo:
        model_kwargs["use_monte_carlo"] = True
    if args.monte_carlo_particles:
        model_kwargs["monte_carlo_particles"] = args.monte_carlo_particles

    logger.info(f"Using model type: {model_type}, model size: {model_size or 'default'}, model name: {model_name or 'auto'}")
    if model_kwargs:
        logger.info(f"Model parameters: {model_kwargs}")

    # Add model_size to kwargs
    if model_size:
        model_kwargs["model_size"] = model_size

    # Demonstrate the specified agent type
    if args.agent == "conversational" or args.agent == "all":
        demo_conversational_agent(model_type, model_name, model_kwargs)

    if args.agent == "task" or args.agent == "all":
        demo_task_agent(model_type, model_name, model_kwargs)

    if args.agent == "research" or args.agent == "all":
        demo_research_agent(model_type, model_name, model_kwargs)

    if args.agent == "creative" or args.agent == "all":
        demo_creative_agent(model_type, model_name, model_kwargs)

    if args.agent == "coding" or args.agent == "all":
        demo_coding_agent(model_type, model_name, model_kwargs)

    logger.info("Finished Agent Core example")


if __name__ == "__main__":
    main()
