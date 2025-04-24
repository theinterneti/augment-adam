"""Example of using the Agent Core with the Context Engine.

This script demonstrates how to use the Agent Core with the Context Engine.

Version: 0.1.0
Created: 2025-04-27
"""

import logging
import sys
import os

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


def main():
    """Run the example."""
    logger.info("Starting Agent Core example")
    
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
    
    # Create potentials for controlled generation
    sentence_ending_potential = RegexPotential(
        pattern=r".*[.!?]$",
        name="sentence_ending_potential"
    )
    
    # Create a conversational agent
    agent = create_agent(
        agent_type="conversational",
        name="Example Agent",
        description="An example conversational agent",
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
    
    logger.info("Finished Agent Core example")


if __name__ == "__main__":
    main()
