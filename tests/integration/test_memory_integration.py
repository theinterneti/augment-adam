"""Integration tests for the memory systems.

This module contains integration tests for the memory systems,
testing how they interact with each other.

Version: 0.1.0
Created: 2025-04-22
"""

import pytest
import os
import tempfile

from dukat.memory.working import WorkingMemory, Message
from dukat.memory.episodic import EpisodicMemory
from dukat.memory.semantic import SemanticMemory, Concept


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
    episode_id = episodic_memory.add_episode(
        content=history,
        title="Weather Conversation",
        metadata={"topic": "weather", "sentiment": "neutral"}
    )

    # Retrieve the episode
    retrieved_episode = episodic_memory.get_episode(episode_id)

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
        metadata={"category": "programming language",
                  "source": "Python Programming episode"}
    )

    ml_concept = Concept(
        name="Machine Learning",
        description="A subset of AI that enables systems to learn from data.",
        metadata={"category": "artificial intelligence",
                  "source": "Machine Learning episode"}
    )

    # Add concepts to semantic memory
    python_id = semantic_memory.add_concept(python_concept)
    ml_id = semantic_memory.add_concept(ml_concept)

    # Retrieve concepts
    retrieved_python = semantic_memory.get_concept(python_id)
    retrieved_ml = semantic_memory.get_concept(ml_id)

    # Check that concepts were stored correctly
    assert retrieved_python is not None
    assert retrieved_python.name == "Python"
    assert "readability" in retrieved_python.description

    assert retrieved_ml is not None
    assert retrieved_ml.name == "Machine Learning"
    assert "learn from data" in retrieved_ml.description

    # Search for related concepts
    ai_concepts = semantic_memory.search_concepts("artificial intelligence")
    programming_concepts = semantic_memory.search_concepts(
        "programming language")

    # Check search results
    assert len(ai_concepts) > 0
    assert any(c.name == "Machine Learning" for c in ai_concepts)

    assert len(programming_concepts) > 0
    assert any(c.name == "Python" for c in programming_concepts)


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
        metadata={"category": "llm framework",
                  "source": "DSPy Framework Discussion episode"}
    )

    teleprompter_concept = Concept(
        name="Teleprompter",
        description="A technique in DSPy that optimizes prompts and modules automatically based on examples and feedback.",
        metadata={"category": "llm technique",
                  "source": "DSPy Framework Discussion episode"}
    )

    # 5. Add concepts to semantic memory
    semantic_memory.add_concept(dspy_concept)
    semantic_memory.add_concept(teleprompter_concept)

    # 6. Retrieve information for a new conversation
    # Search for relevant concepts
    framework_concepts = semantic_memory.search_concepts("llm framework")

    # Find relevant episodes
    framework_episodes = episodic_memory.search_episodes("DSPy framework")

    # Check that we can retrieve the information
    assert any(c.name == "DSPy" for c in framework_concepts)
    assert any("DSPy Framework Discussion" in e.title for e in framework_episodes)

    # 7. Use the retrieved information in a new conversation
    working_memory.clear_messages()
    working_memory.add_message(
        Message(role="user", content="Tell me about DSPy and how it works."))

    # Simulate retrieving information from semantic and episodic memory
    dspy_info = next((c for c in framework_concepts if c.name == "DSPy"), None)
    teleprompter_info = semantic_memory.get_concept_by_name("Teleprompter")

    # Create a response using the retrieved information
    response = f"Based on my knowledge: {dspy_info.description} "
    response += f"A key feature is {teleprompter_info.name}: {teleprompter_info.description}"

    working_memory.add_message(Message(role="assistant", content=response))

    # Check that the response contains the correct information
    last_message = working_memory.get_last_message()
    assert "DSPy" in last_message.content
    assert "Teleprompter" in last_message.content
    assert "optimization" in last_message.content
