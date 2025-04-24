"""Integration tests for the FAISS-based memory systems.

This module contains integration tests for the FAISS-based memory systems,
testing how they interact with each other.

Version: 0.1.0
Created: 2025-04-24
"""

import pytest
import os
import tempfile

from dukat.memory.working import WorkingMemory, Message
from dukat.memory.faiss_episodic import FAISSEpisodicMemory
from dukat.memory.faiss_semantic import FAISSSemanticMemory, Concept


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
def faiss_episodic_memory(temp_dir):
    """Create a FAISS episodic memory instance for testing."""
    persist_dir = os.path.join(temp_dir, "faiss_episodic")
    return FAISSEpisodicMemory(
        persist_dir=persist_dir,
        collection_name="test_episodes",
    )


@pytest.fixture
def faiss_semantic_memory(temp_dir):
    """Create a FAISS semantic memory instance for testing."""
    persist_dir = os.path.join(temp_dir, "faiss_semantic")
    return FAISSSemanticMemory(
        persist_dir=persist_dir,
        collection_name="test_concepts",
    )


def test_working_to_episodic_memory(working_memory, faiss_episodic_memory):
    """Test transferring information from working memory to episodic memory."""
    # Add messages to working memory
    working_memory.add_message(Message(role="user", content="Hello, how are you?"))
    working_memory.add_message(Message(role="assistant", content="I'm doing well, thank you!"))
    working_memory.add_message(Message(role="user", content="What's the weather like today?"))
    working_memory.add_message(Message(
        role="assistant",
        content="I don't have access to real-time weather information."
    ))

    # Get the conversation history
    history = working_memory.format_history()

    # Add the episode to episodic memory
    episode = faiss_episodic_memory.add_episode(
        content=history,
        title="Weather Conversation",
        metadata={"topic": "weather", "sentiment": "neutral"}
    )

    # Retrieve the episode
    retrieved_episode = faiss_episodic_memory.get_episode(episode.id)

    # Check that the episode was stored correctly
    assert retrieved_episode is not None
    assert retrieved_episode.title == "Weather Conversation"
    assert "Hello, how are you?" in retrieved_episode.content
    assert "I'm doing well, thank you!" in retrieved_episode.content
    assert "What's the weather like today?" in retrieved_episode.content
    assert "I don't have access to real-time weather information." in retrieved_episode.content


def test_episodic_to_semantic_memory(faiss_episodic_memory, faiss_semantic_memory):
    """Test extracting concepts from episodic memory and storing them in semantic memory."""
    # Create and add episodes to episodic memory
    faiss_episodic_memory.add_episode(
        title="Python Programming",
        content="Python is a high-level programming language known for its readability and versatility.",
        metadata={"topic": "programming", "language": "python"}
    )

    faiss_episodic_memory.add_episode(
        title="Machine Learning",
        content="Machine learning is a subset of AI that enables systems to learn from data.",
        metadata={"topic": "ai", "subtopic": "machine learning"}
    )

    # Extract concepts from episodes and add to semantic memory
    # In a real system, this might be done by an AI model
    python_concept = Concept(
        name="Python",
        description="A high-level programming language",
        content="Python is a high-level programming language known for its readability and versatility. It supports multiple programming paradigms, including procedural, object-oriented, and functional programming.",
        metadata={"type": "language", "paradigm": "multi-paradigm"}
    )

    ml_concept = Concept(
        name="Machine Learning",
        description="A subset of AI for learning from data",
        content="Machine learning is a subset of artificial intelligence that enables systems to learn from data, identify patterns, and make decisions with minimal human intervention.",
        metadata={"type": "technology", "field": "artificial intelligence"}
    )

    # Add concepts to semantic memory
    faiss_semantic_memory.add_concept(
        name=python_concept.name,
        description=python_concept.description,
        content=python_concept.content,
        metadata=python_concept.metadata
    )

    faiss_semantic_memory.add_concept(
        name=ml_concept.name,
        description=ml_concept.description,
        content=ml_concept.content,
        metadata=ml_concept.metadata
    )

    # Check that concepts were stored correctly by searching for them
    python_results = faiss_semantic_memory.search_concepts(
        "Python programming language")
    ml_results = faiss_semantic_memory.search_concepts("Machine learning AI")

    assert len(python_results) > 0
    assert any(concept.name == "Python" for concept, _ in python_results)

    assert len(ml_results) > 0
    assert any(concept.name == "Machine Learning" for concept, _ in ml_results)

    # Search for related concepts
    ai_concepts = faiss_semantic_memory.search_concepts("artificial intelligence")
    programming_concepts = faiss_semantic_memory.search_concepts(
        "programming language")

    # Check search results
    assert len(ai_concepts) > 0
    assert any(concept.name == "Machine Learning" for concept, _ in ai_concepts)

    assert len(programming_concepts) > 0
    assert any(concept.name == "Python" for concept, _ in programming_concepts)


def test_full_memory_cycle(working_memory, faiss_episodic_memory, faiss_semantic_memory):
    """Test a full cycle of information through all memory systems."""
    # 1. Add conversation to working memory
    working_memory.add_message(Message(role="user", content="What is DSPy?"))
    working_memory.add_message(Message(
        role="assistant",
        content="DSPy is a framework for programming with foundation models. "
                "It allows you to build LLM-powered systems that can be optimized "
                "based on feedback and examples."
    ))
    working_memory.add_message(Message(role="user", content="What is a Teleprompter in DSPy?"))
    working_memory.add_message(Message(
        role="assistant",
        content="In DSPy, a Teleprompter is a module that helps generate prompts "
                "for language models. It can be optimized to produce better prompts "
                "based on examples and feedback."
    ))

    # 2. Get conversation history
    history = working_memory.format_history()

    # 3. Store in episodic memory
    episode = faiss_episodic_memory.add_episode(
        content=history,
        title="DSPy Framework Discussion",
        metadata={"topic": "programming", "subtopic": "llm frameworks"}
    )

    # 4. Extract concepts from the conversation
    dspy_concept = Concept(
        name="DSPy",
        description="A framework for programming with foundation models",
        content="DSPy is a framework for programming with foundation models. "
                "It allows you to build LLM-powered systems that can be optimized "
                "based on feedback and examples.",
        metadata={"type": "framework", "field": "llm"}
    )

    teleprompter_concept = Concept(
        name="Teleprompter",
        description="A DSPy module for generating prompts",
        content="In DSPy, a Teleprompter is a module that helps generate prompts "
                "for language models. It can be optimized to produce better prompts "
                "based on examples and feedback.",
        metadata={"type": "module", "framework": "dspy"}
    )

    # 5. Store concepts in semantic memory
    faiss_semantic_memory.add_concept(
        name=dspy_concept.name,
        description=dspy_concept.description,
        content=dspy_concept.content,
        metadata=dspy_concept.metadata
    )

    faiss_semantic_memory.add_concept(
        name=teleprompter_concept.name,
        description=teleprompter_concept.description,
        content=teleprompter_concept.content,
        metadata=teleprompter_concept.metadata
    )

    # 6. Retrieve information for a new conversation
    # Search for relevant concepts
    framework_concepts = faiss_semantic_memory.search_concepts("llm framework")

    # Find relevant episodes
    framework_episodes = faiss_episodic_memory.search_episodes("DSPy framework")

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
    teleprompter_results = faiss_semantic_memory.search_concepts("Teleprompter DSPy")
    teleprompter_info = next(
        (concept for concept, _ in teleprompter_results if concept.name == "Teleprompter"), None)

    # Add assistant response based on retrieved information
    if dspy_info:
        working_memory.add_message(
            Message(role="assistant", content=f"{dspy_info.content} One of its key components is the {teleprompter_info.name}, which {teleprompter_info.description.lower()}."))

    # Check that the response contains information from semantic memory
    messages = working_memory.get_messages()
    assert len(messages) == 2
    assert "DSPy is a framework for programming with foundation models" in messages[1].content
    assert "Teleprompter" in messages[1].content
