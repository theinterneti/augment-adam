"""Integration tests for the memory systems.

This module contains integration tests for the memory systems,
testing how they interact with each other.

Version: 0.1.0
Created: 2025-04-22
"""

import pytest
import os
import tempfile

from augment_adam.memory.working import WorkingMemory, Message
from augment_adam.memory.episodic import EpisodicMemory
from augment_adam.memory.semantic import SemanticMemory, Concept


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def working_memory():
    """Create a working memory instance for testing."""
    return WorkingMemory()


@pytest.fixture
def episodic_memory(temp_dir):
    """Create an episodic memory instance for testing."""
    persist_dir = os.path.join(temp_dir, "episodic")
    return EpisodicMemory(persist_dir=persist_dir)


@pytest.fixture
def semantic_memory(temp_dir):
    """Create a semantic memory instance for testing."""
    persist_dir = os.path.join(temp_dir, "semantic")
    return SemanticMemory(persist_dir=persist_dir)


def test_working_to_episodic_memory(working_memory, episodic_memory):
    """Test transferring a conversation from working memory to episodic memory."""
    # Add messages to working memory
    working_memory.add_message(
        Message(role="user", content="Hello, how are you?"))
    working_memory.add_message(
        Message(role="assistant", content="I'm doing well, thank you!"))
    working_memory.add_message(
        Message(role="user", content="What's the weather like today?"))
    working_memory.add_message(Message(
        role="assistant", content="I don't have access to real-time weather information."))

    # Get the conversation history
    history = working_memory.format_history()

    # Add the episode to episodic memory
    episode = episodic_memory.add_episode(
        content=history,
        title="Weather Conversation",
        metadata={"topic": "weather", "sentiment": "neutral"}
    )

    # Retrieve the episode
    retrieved_episode = episodic_memory.get_episode(episode.id)

    # Check that the episode was stored correctly
    assert retrieved_episode is not None
    assert retrieved_episode.title == "Weather Conversation"
    assert "Hello, how are you?" in retrieved_episode.content
    assert "I'm doing well, thank you!" in retrieved_episode.content
    assert "What's the weather like today?" in retrieved_episode.content
    assert "I don't have access to real-time weather information." in retrieved_episode.content


def test_episodic_to_semantic_memory(episodic_memory, semantic_memory):
    """Test extracting concepts from episodic memory and storing them in semantic memory."""
    # Create and add episodes to episodic memory
    episodic_memory.add_episode(
        title="Python Programming",
        content="Python is a high-level programming language known for its readability and versatility.",
        metadata={"topic": "programming", "language": "python"}
    )

    episodic_memory.add_episode(
        title="Machine Learning",
        content="Machine learning is a subset of AI that enables systems to learn from data.",
        metadata={"topic": "ai", "subtopic": "machine learning"}
    )

    # Extract concepts from episodes
    python_concept = Concept(
        name="Python",
        description="A high-level programming language known for its readability and versatility.",
        content="Python is a high-level programming language known for its readability and versatility. It's widely used in data science, web development, and automation.",
        metadata={"category": "programming language",
                  "source": "Python Programming episode"}
    )

    ml_concept = Concept(
        name="Machine Learning",
        description="A subset of AI that enables systems to learn from data.",
        content="Machine learning is a subset of AI that enables systems to learn from data without being explicitly programmed. It uses algorithms to identify patterns and make predictions.",
        metadata={"category": "artificial intelligence",
                  "source": "Machine Learning episode"}
    )

    # Add concepts to semantic memory
    semantic_memory.add_concept(
        name=python_concept.name,
        description=python_concept.description,
        content=python_concept.content,
        metadata=python_concept.metadata
    )
    semantic_memory.add_concept(
        name=ml_concept.name,
        description=ml_concept.description,
        content=ml_concept.content,
        metadata=ml_concept.metadata
    )

    # Check that concepts were stored correctly by searching for them
    python_results = semantic_memory.search_concepts(
        "Python programming language")
    ml_results = semantic_memory.search_concepts("Machine learning AI")

    assert len(python_results) > 0
    assert any(concept.name == "Python" for concept, _ in python_results)

    assert len(ml_results) > 0
    assert any(concept.name == "Machine Learning" for concept, _ in ml_results)

    # Search for related concepts
    ai_concepts = semantic_memory.search_concepts("artificial intelligence")
    programming_concepts = semantic_memory.search_concepts(
        "programming language")

    # Check search results
    assert len(ai_concepts) > 0
    assert any(concept.name == "Machine Learning" for concept, _ in ai_concepts)

    assert len(programming_concepts) > 0
    assert any(concept.name == "Python" for concept, _ in programming_concepts)


def test_full_memory_cycle(working_memory, episodic_memory, semantic_memory):
    """Test a full cycle of information through all memory systems."""
    # 1. Add conversation to working memory
    working_memory.add_message(Message(role="user", content="What is DSPy?"))
    working_memory.add_message(Message(
        role="assistant",
        content="DSPy is a framework for programming with foundation models. "
                "It allows you to build LLM-powered systems that can be optimized "
                "based on feedback and examples."
    ))
    working_memory.add_message(
        Message(role="user", content="How does it compare to LangChain?"))
    working_memory.add_message(Message(
        role="assistant",
        content="Unlike LangChain which focuses on chaining components together, "
                "DSPy focuses on optimizing prompts and modules through a process "
                "called 'teleprompting'. This allows DSPy programs to improve "
                "automatically based on examples and feedback."
    ))

    # 2. Create an episode from the conversation
    history = working_memory.format_history()

    # 3. Add the episode to episodic memory
    episodic_memory.add_episode(
        title="DSPy Framework Discussion",
        content=history,
        metadata={"topic": "programming", "subtopic": "llm frameworks"}
    )

    # 4. Extract concepts from the episode
    dspy_concept = Concept(
        name="DSPy",
        description="A framework for programming with foundation models that allows optimization based on feedback and examples.",
        content="DSPy is a framework for programming with foundation models that allows optimization based on feedback and examples. It provides a structured way to build LLM-powered systems that can improve over time.",
        metadata={"category": "llm framework",
                  "source": "DSPy Framework Discussion episode"}
    )

    teleprompter_concept = Concept(
        name="Teleprompter",
        description="A technique in DSPy that optimizes prompts and modules automatically based on examples and feedback.",
        content="Teleprompter is a technique in DSPy that optimizes prompts and modules automatically based on examples and feedback. It allows DSPy programs to improve their performance without manual tuning.",
        metadata={"category": "llm technique",
                  "source": "DSPy Framework Discussion episode"}
    )

    # 5. Add concepts to semantic memory
    semantic_memory.add_concept(
        name=dspy_concept.name,
        description=dspy_concept.description,
        content=dspy_concept.content,
        metadata=dspy_concept.metadata
    )
    semantic_memory.add_concept(
        name=teleprompter_concept.name,
        description=teleprompter_concept.description,
        content=teleprompter_concept.content,
        metadata=teleprompter_concept.metadata
    )

    # 6. Retrieve information for a new conversation
    # Search for relevant concepts
    framework_concepts = semantic_memory.search_concepts("llm framework")

    # Find relevant episodes
    framework_episodes = episodic_memory.search_episodes("DSPy framework")

    # Check that we can retrieve the information
    assert any(concept.name == "DSPy" for concept, _ in framework_concepts)
    assert any("DSPy Framework Discussion" in episode.title for episode,
               _ in framework_episodes)

    # 7. Use the retrieved information in a new conversation
    working_memory.clear_messages()
    working_memory.add_message(
        Message(role="user", content="Tell me about DSPy and how it works."))

    # Simulate retrieving information from semantic and episodic memory
    dspy_info = next(
        (concept for concept, _ in framework_concepts if concept.name == "DSPy"), None)

    # Search for teleprompter concept
    teleprompter_results = semantic_memory.search_concepts("Teleprompter DSPy")
    teleprompter_info = next(
        (concept for concept, _ in teleprompter_results if concept.name == "Teleprompter"), None)

    # Create a response using the retrieved information
    response = f"Based on my knowledge: {dspy_info.description} "
    response += f"A key feature is {teleprompter_info.name}: {teleprompter_info.description}"

    working_memory.add_message(Message(role="assistant", content=response))

    # Check that the response contains the correct information
    last_message = working_memory.get_last_message()
    assert "DSPy" in last_message.content
    assert "Teleprompter" in last_message.content
    assert "optimization" in last_message.content
