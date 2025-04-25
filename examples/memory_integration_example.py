"""Example of memory integration in an agent.

This example demonstrates how to use the memory integration components
to create an agent with a sophisticated memory system.

Version: 0.1.0
Created: 2025-05-01
"""

import logging
import sys
from typing import Dict, List, Any, Optional

from augment_adam.ai_agent.memory_integration import (
    MemoryManager,
    ContextMemory,
    EpisodicMemory,
    SemanticMemory,
    MemoryConfiguration,
    get_memory_configuration,
)
from augment_adam.context_engine import get_context_manager
from augment_adam.models import create_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def main():
    """Run the memory integration example."""
    # Create a model
    model = create_model(model_type="anthropic", model_name="claude-3-sonnet-20240229")

    # Get memory configuration
    memory_config = get_memory_configuration()

    # Configure memory for a research agent
    agent_name = "research_agent"
    agent_role = "researcher"
    model_name = model.get_model_info()["name"]

    memory_components = memory_config.configure_memory_for_agent(
        agent_name=agent_name, role=agent_role, model_name=model_name
    )

    # Extract components
    memory_manager = memory_components["memory_manager"]
    context_window = memory_components["context_window"]
    working_memory = memory_components["working_memory"]
    episodic_memory = memory_components["episodic_memory"]
    semantic_memory = memory_components["semantic_memory"]
    token_budgets = memory_components["token_budgets"]

    # Print configuration
    logger.info(f"Agent: {agent_name}")
    logger.info(f"Role: {agent_role}")
    logger.info(f"Model: {model_name}")
    logger.info(f"Context window size: {context_window.max_tokens} tokens")
    logger.info(f"Working memory size: {working_memory.max_size} items")
    logger.info(f"Episodic memory size: {episodic_memory.max_size} episodes")
    logger.info(f"Semantic memory size: {semantic_memory.max_size} concepts")
    logger.info(f"Token budgets: {token_budgets}")

    # Add some items to working memory
    working_memory.add("User asked about quantum computing")
    working_memory.add("Agent explained quantum bits")
    working_memory.add("User asked about quantum entanglement")

    # Add an episode to episodic memory
    episodic_memory.add_episode(
        content="User: What is quantum computing?\nAgent: Quantum computing is a type of computing that uses quantum bits or qubits...",
        title="Quantum Computing Discussion",
        metadata={"topic": "quantum computing", "sentiment": "curious"},
    )

    # Add a concept to semantic memory
    semantic_memory.add_concept(
        name="Quantum Computing",
        description="A type of computing that uses quantum bits or qubits",
        content="Quantum computing is a type of computing that uses quantum-mechanical phenomena, such as superposition and entanglement, to perform operations on data. Unlike classical computing, which uses bits that are either 0 or 1, quantum computing uses quantum bits or qubits, which can exist in multiple states simultaneously.",
        metadata={"field": "computer science", "subfield": "quantum information"},
    )

    # Simulate a query
    query = "Tell me more about quantum entanglement"

    # Retrieve relevant information from memory
    working_memory_items = working_memory.get(3)  # Get last 3 items
    logger.info(f"Working memory items: {working_memory_items}")

    episodic_results = episodic_memory.search_episodes(query, n_results=2)
    logger.info(f"Episodic memory results: {[ep[0].title for ep in episodic_results]}")

    semantic_results = semantic_memory.search_concepts(query, n_results=2)
    logger.info(f"Semantic memory results: {[con[0].name for con in semantic_results]}")

    # Compose context for the model
    context_manager = get_context_manager()

    # Add working memory to context
    for item in working_memory_items:
        context_window.add_item(
            context_manager.create_context_item(
                content=item, source="working_memory", relevance=0.9
            )
        )

    # Add episodic memory to context
    for episode, score in episodic_results:
        context_window.add_item(
            context_manager.create_context_item(
                content=episode.content, source="episodic_memory", relevance=score
            )
        )

    # Add semantic memory to context
    for concept, score in semantic_results:
        context_window.add_item(
            context_manager.create_context_item(
                content=f"{concept.name}: {concept.description}\n\n{concept.content}",
                source="semantic_memory",
                relevance=score,
            )
        )

    # Create prompt with context
    prompt = f"""
    Context:
    {context_window.get_content()}
    
    User query: {query}
    
    Please respond to the user's query based on the provided context.
    """

    # Generate response
    response = model.generate(prompt)

    # Print response
    logger.info(f"Response: {response}")

    # Update memory with the interaction
    working_memory.add(f"User asked: {query}")
    working_memory.add(f"Agent responded: {response[:100]}...")

    # Add the interaction to episodic memory
    episodic_memory.add_episode(
        content=f"User: {query}\nAgent: {response}",
        title="Quantum Entanglement Discussion",
        metadata={"topic": "quantum entanglement", "sentiment": "informative"},
    )

    # Extract and store concepts from the interaction
    semantic_memory.add_concept(
        name="Quantum Entanglement",
        description="A quantum phenomenon where pairs of particles become correlated",
        content="Quantum entanglement is a physical phenomenon that occurs when a group of particles are generated, interact, or share spatial proximity in a way such that the quantum state of each particle of the group cannot be described independently of the state of the others, including when the particles are separated by a large distance.",
        metadata={"field": "physics", "subfield": "quantum mechanics"},
    )

    logger.info("Memory integration example completed")


if __name__ == "__main__":
    main()
